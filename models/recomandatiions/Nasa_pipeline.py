"""
NASA POWER API Solar Irradiance Data Pipeline - PostgreSQL Version (Windows Compatible)
Model 2: Solar Generation Prediction
"""
from datetime import datetime, timedelta
import json
import time

from typing import Dict

import requests
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import os



class NASAPowerAPI:
    """
    Handles NASA POWER API data fetching for solar irradiance parameters.
    """

    BASE_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"

    PARAMETERS = [
        "ALLSKY_SFC_SW_DWN",
        "CLRSKY_SFC_SW_DWN",
        "T2M",
        "WS10M",
        "RH2M"
    ]

    def __init__(self):
        self.session = requests.Session()

    def fetch_solar_data(self, latitude: float, longitude: float,
                        start_date: str, end_date: str) -> Dict:
        params = {
            "parameters": ",".join(self.PARAMETERS),
            "community": "RE",
            "longitude": longitude,
            "latitude": latitude,
            "start": start_date,
            "end": end_date,
            "format": "JSON"
        }

        try:
            print(f"Fetching data for ({latitude}, {longitude}) from {start_date} to {end_date}...")
            response = self.session.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            print(f"[OK] Data fetched successfully!")
            return data

        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Error fetching data: {e}")
            return None

    def parse_nasa_response(self, response_data: Dict, location_name: str) -> pd.DataFrame:
        if not response_data or 'properties' not in response_data:
            return pd.DataFrame()

        parameters = response_data['properties']['parameter']
        records = []
        dates = list(parameters[self.PARAMETERS[0]].keys())

        for date in dates:
            record = {
                'date': datetime.strptime(date, '%Y%m%d').date(),
                'location_name': location_name,
                'latitude': response_data['geometry']['coordinates'][1],
                'longitude': response_data['geometry']['coordinates'][0],
            }

            for param in self.PARAMETERS:
                if param in parameters:
                    value = parameters[param].get(date, None)
                    record[param] = None if value == -999 else value

            records.append(record)

        df = pd.DataFrame(records)

        df.rename(columns={
            'ALLSKY_SFC_SW_DWN': 'ghi_kwh_m2',
            'CLRSKY_SFC_SW_DWN': 'clear_sky_ghi_kwh_m2',
            'T2M': 'temperature_c',
            'WS10M': 'wind_speed_ms',
            'RH2M': 'relative_humidity_pct'
        }, inplace=True)

        return df


class PostgreSQLDatabase:
    """
    Manages PostgreSQL database for storing solar irradiance data.
    """

    def __init__(self, dbname: str = "solar_irradiance",
                 user: str = "postgres",
                 password: str = "123456789",
                 host: str = "localhost",
                 port: str = "5432"):
        self.conn_params = {
            "dbname": 'solar_irradiance',
            "user": 'postgres',
            "password": '123456789',
            "host": 'localhost',
            "port": '5432'
        }
        self.conn = None
        self.connect()

    def connect(self):
        try:
            self.conn = psycopg2.connect(**self.conn_params)
            self.conn.autocommit = False
            print(f"[OK] Connected to PostgreSQL database: {self.conn_params['dbname']}")
        except psycopg2.Error as e:
            print(f"[ERROR] Error connecting to database: {e}")
            print("\nMake sure you:")
            print("1. Created the 'solar_irradiance' database in pgAdmin")
            print("2. Updated the password in this script")
            print("3. PostgreSQL server is running")
            raise

    def add_location(self, location_name: str, latitude: float,
                    longitude: float, country: str = None, region: str = None) -> int:
        cursor = self.conn.cursor()

        # CRITICAL FIX: Convert numpy types to Python native types
        latitude = float(latitude)
        longitude = float(longitude)

        try:
            cursor.execute("""
                INSERT INTO locations (location_name, latitude, longitude, country, region)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING location_id
            """, (location_name, latitude, longitude, country, region))

            location_id = cursor.fetchone()[0]
            self.conn.commit()
            return location_id

        except psycopg2.IntegrityError:
            self.conn.rollback()
            cursor.execute("""
                SELECT location_id FROM locations WHERE location_name = %s
            """, (location_name,))
            return cursor.fetchone()[0]

        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"[ERROR] Error adding location: {e}")
            raise

    def insert_daily_data(self, df: pd.DataFrame):
        if df.empty:
            return

        cursor = self.conn.cursor()

        try:
            location_name = df['location_name'].iloc[0]
            # CRITICAL FIX: Convert numpy types to Python native types
            latitude = float(df['latitude'].iloc[0])
            longitude = float(df['longitude'].iloc[0])

            location_id = self.add_location(location_name, latitude, longitude)

            data_to_insert = []
            for _, row in df.iterrows():
                # Convert all values to Python native types and handle NaN
                data_to_insert.append((
                    int(location_id),
                    row['date'],
                    float(row['ghi_kwh_m2']) if pd.notna(row['ghi_kwh_m2']) else None,
                    float(row['clear_sky_ghi_kwh_m2']) if pd.notna(row['clear_sky_ghi_kwh_m2']) else None,
                    float(row['temperature_c']) if pd.notna(row['temperature_c']) else None,
                    float(row['wind_speed_ms']) if pd.notna(row['wind_speed_ms']) else None,
                    float(row['relative_humidity_pct']) if pd.notna(row['relative_humidity_pct']) else None
                ))

            insert_query = """
                INSERT INTO solar_irradiance_daily
                (location_id, date, ghi_kwh_m2, clear_sky_ghi_kwh_m2,
                 temperature_c, wind_speed_ms, relative_humidity_pct)
                VALUES %s
                ON CONFLICT (location_id, date) DO UPDATE SET
                    ghi_kwh_m2 = EXCLUDED.ghi_kwh_m2,
                    clear_sky_ghi_kwh_m2 = EXCLUDED.clear_sky_ghi_kwh_m2,
                    temperature_c = EXCLUDED.temperature_c,
                    wind_speed_ms = EXCLUDED.wind_speed_ms,
                    relative_humidity_pct = EXCLUDED.relative_humidity_pct
            """

            execute_values(cursor, insert_query, data_to_insert)
            self.conn.commit()

            print(f"[OK] Inserted/Updated {len(data_to_insert)} daily records for {location_name}")

        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"[ERROR] Error inserting data: {e}")
            raise

    def get_location_data(self, location_name: str,
                         start_date: str = None, end_date: str = None) -> pd.DataFrame:
        query = """
            SELECT l.location_name, l.latitude, l.longitude,
                   s.date, s.ghi_kwh_m2, s.clear_sky_ghi_kwh_m2,
                   s.temperature_c, s.wind_speed_ms, s.relative_humidity_pct
            FROM solar_irradiance_daily s
            JOIN locations l ON s.location_id = l.location_id
            WHERE l.location_name = %s
        """

        params = [location_name]

        if start_date and end_date:
            query += " AND s.date BETWEEN %s AND %s"
            params.extend([start_date, end_date])

        query += " ORDER BY s.date"

        return pd.read_sql_query(query, self.conn, params=params)

    def refresh_monthly_aggregates(self):
        cursor = self.conn.cursor()

        try:
            cursor.execute("SELECT refresh_monthly_aggregates()")
            self.conn.commit()
            print("[OK] Monthly aggregates refreshed")
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"[WARNING] Could not refresh monthly aggregates: {e}")
            print("This is OK - monthly aggregates are optional")

    def get_summary_stats(self):
        query = """
            SELECT * FROM v_location_solar_summary
            ORDER BY avg_ghi DESC
        """
        try:
            return pd.read_sql_query(query, self.conn)
        except Exception as e:
            print(f"[WARNING] Could not get summary stats: {e}")
            return pd.DataFrame()

    def close(self):
        if self.conn:
            self.conn.close()
            print("[OK] Database connection closed")


SSA_LOCATIONS = [
    {"name": "Nairobi_Kenya", "lat": -1.2921, "lon": 36.8219, "country": "Kenya"},
    {"name": "Lagos_Nigeria", "lat": 6.5244, "lon": 3.3792, "country": "Nigeria"},
    {"name": "Accra_Ghana", "lat": 5.6037, "lon": -0.1870, "country": "Ghana"},
    {"name": "Kampala_Uganda", "lat": 0.3476, "lon": 32.5825, "country": "Uganda"},
    {"name": "Dar_es_Salaam_Tanzania", "lat": -6.7924, "lon": 39.2083, "country": "Tanzania"},
    {"name": "Kigali_Rwanda", "lat": -1.9706, "lon": 30.1044, "country": "Rwanda"},
    {"name": "Johannesburg_SA", "lat": -26.2041, "lon": 28.0473, "country": "South Africa"},
]


def main():
    # UPDATE YOUR PASSWORD HERE!
    DB_CONFIG = {
        "dbname": "solar_irradiance",
        "user": "postgres",
        "password": "your_password_here",  # <-- CHANGE THIS
        "host": "localhost",
        "port": "5432"
    }

    print("\n" + "="*60)
    print("NASA POWER Solar Data Pipeline - PostgreSQL Version")
    print("="*60 + "\n")

    api = NASAPowerAPI()

    try:
        db = PostgreSQLDatabase(**DB_CONFIG)
    except psycopg2.OperationalError as e:
        print("\n[ERROR] Could not connect to database. Please check:")
        print("  1. Database 'solar_irradiance' exists in pgAdmin")
        print("  2. Password is correct in DB_CONFIG")
        print("  3. PostgreSQL server is running")
        print(f"\nDetails: {e}")
        return

    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)

    start_str = start_date.strftime('%Y%m%d')
    end_str = end_date.strftime('%Y%m%d')

    print(f"Date Range: {start_str} to {end_str}")
    print(f"Locations: {len(SSA_LOCATIONS)}")
    print("="*60 + "\n")

    for location in SSA_LOCATIONS:
        print(f"\n--- Processing: {location['name']} ---")

        raw_data = api.fetch_solar_data(
            latitude=location['lat'],
            longitude=location['lon'],
            start_date=start_str,
            end_date=end_str
        )

        if raw_data:
            df = api.parse_nasa_response(raw_data, location['name'])

            if not df.empty:
                print(f"Data shape: {df.shape}")
                print(f"Date range: {df['date'].min()} to {df['date'].max()}")
                print(f"Avg GHI: {df['ghi_kwh_m2'].mean():.2f} kWh/m2/day")

                db.insert_daily_data(df)
            else:
                print("[ERROR] No data returned from API")

        time.sleep(2)

    print(f"\n{'='*60}")
    print("Refreshing Monthly Aggregates...")
    print(f"{'='*60}\n")
    db.refresh_monthly_aggregates()

    print(f"\n{'='*60}")
    print("Data Validation Summary")
    print(f"{'='*60}\n")

    summary = db.get_summary_stats()
    if not summary.empty:
        print(summary.to_string(index=False))

    db.close()

    print(f"\n{'='*60}")
    print("[OK] Pipeline completed successfully!")
    print(f"{'='*60}\n")
    print("Next steps:")
    print("1. Open pgAdmin and run: SELECT COUNT(*) FROM solar_irradiance_daily;")
    print("2. Verify you have ~5,117 records (731 days x 7 locations)")
    print("3. Export data for Tessa: python export_for_tessa.py")


if __name__ == "__main__":
    main()
