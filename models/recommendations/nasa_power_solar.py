"""
NASA POWER API Solar Irradiance Data Pipeline
Model 2: Solar Generation Prediction
Author: Your Name
Date: February 2026

This module fetches solar irradiance data from NASA POWER API and stores it in a SQL database.
"""


from datetime import datetime, timedelta
import sqlite3
import time
from typing import Dict
import requests
import pandas as pd



class NASAPowerAPI:
    """
    Handles NASA POWER API data fetching for solar irradiance parameters.
    """

    BASE_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"

    # Solar parameters we need for generation prediction
    PARAMETERS = [
        "ALLSKY_SFC_SW_DWN",  # All Sky Surface Shortwave Downward Irradiance (kWh/m²/day)
        "CLRSKY_SFC_SW_DWN",  # Clear Sky Surface Shortwave Downward Irradiance (kWh/m²/day)
        "T2M",                 # Temperature at 2 Meters (°C)
        "WS10M",               # Wind Speed at 10 Meters (m/s)
        "RH2M"                 # Relative Humidity at 2 Meters (%)
    ]

    def __init__(self):
        self.session = requests.Session()

    def fetch_solar_data(self, latitude: float, longitude: float,
                        start_date: str, end_date: str) -> Dict:
        """
        Fetch solar irradiance data for a specific location and date range.

        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            start_date: Start date in format 'YYYYMMDD'
            end_date: End date in format 'YYYYMMDD'

        Returns:
            Dictionary containing solar irradiance data
        """
        params = {
            "parameters": ",".join(self.PARAMETERS),
            "community": "RE",  # Renewable Energy community
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
            print("✓ Data fetched successfully!")
            return data

        except requests.exceptions.RequestException as e:
            print(f"✗ Error fetching data: {e}")
            return None

    def parse_nasa_response(self, response_data: Dict, location_name: str) -> pd.DataFrame:
        """
        Parse NASA POWER API response into a clean DataFrame.

        Args:
            response_data: Raw response from NASA API
            location_name: Name of the location for reference

        Returns:
            Cleaned pandas DataFrame
        """
        if not response_data or 'properties' not in response_data:
            return pd.DataFrame()

        parameters = response_data['properties']['parameter']

        # Create a list to store daily records
        records = []

        # Get all dates from the first parameter
        dates = list(parameters[self.PARAMETERS[0]].keys())

        for date in dates:
            record = {
                'date': datetime.strptime(date, '%Y%m%d').date(),
                'location_name': location_name,
                'latitude': response_data['geometry']['coordinates'][1],
                'longitude': response_data['geometry']['coordinates'][0],
            }

            # Add all parameters
            for param in self.PARAMETERS:
                if param in parameters:
                    record[param] = parameters[param].get(date, None)

            records.append(record)

        df = pd.DataFrame(records)

        # Rename columns to more readable names
        df.rename(columns={
            'ALLSKY_SFC_SW_DWN': 'ghi_kwh_m2',  # Global Horizontal Irradiance
            'CLRSKY_SFC_SW_DWN': 'clear_sky_ghi_kwh_m2',
            'T2M': 'temperature_c',
            'WS10M': 'wind_speed_ms',
            'RH2M': 'relative_humidity_pct'
        }, inplace=True)

        return df


class SolarDatabase:
    """
    Manages SQLite database for storing solar irradiance data.
    """

    def __init__(self, db_path: str = "solar_irradiance.db"):
        self.db_path = db_path
        self.conn = None
        self.create_schema()

    def create_schema(self):
        """Create database schema for storing solar data."""
        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()

        # Locations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS locations (
                location_id INTEGER PRIMARY KEY AUTOINCREMENT,
                location_name TEXT UNIQUE NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                country TEXT,
                region TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Daily solar irradiance data
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS solar_irradiance_daily (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                location_id INTEGER NOT NULL,
                date DATE NOT NULL,
                ghi_kwh_m2 REAL,
                clear_sky_ghi_kwh_m2 REAL,
                temperature_c REAL,
                wind_speed_ms REAL,
                relative_humidity_pct REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (location_id) REFERENCES locations(location_id),
                UNIQUE(location_id, date)
            )
        """)

        # Monthly aggregated data for faster queries
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS solar_irradiance_monthly (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                location_id INTEGER NOT NULL,
                year INTEGER NOT NULL,
                month INTEGER NOT NULL,
                avg_ghi_kwh_m2 REAL,
                min_ghi_kwh_m2 REAL,
                max_ghi_kwh_m2 REAL,
                avg_temperature_c REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (location_id) REFERENCES locations(location_id),
                UNIQUE(location_id, year, month)
            )
        """)

        self.conn.commit()
        print("✓ Database schema created successfully!")

    def add_location(self, location_name: str, latitude: float,
                    longitude: float, country: str = None, region: str = None) -> int:
        """Add a new location to the database."""
        cursor = self.conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO locations (location_name, latitude, longitude, country, region)
                VALUES (?, ?, ?, ?, ?)
            """, (location_name, latitude, longitude, country, region))

            self.conn.commit()
            return cursor.lastrowid

        except sqlite3.IntegrityError:
            # Location already exists, get its ID
            cursor.execute("""
                SELECT location_id FROM locations WHERE location_name = ?
            """, (location_name,))
            return cursor.fetchone()[0]

    def insert_daily_data(self, df: pd.DataFrame):
        """Insert daily solar data into database."""
        # First, ensure location exists and get location_id
        if df.empty:
            return

        location_name = df['location_name'].iloc[0]
        latitude = df['latitude'].iloc[0]
        longitude = df['longitude'].iloc[0]

        location_id = self.add_location(location_name, latitude, longitude)

        # Prepare data for insertion
        df_copy = df.copy()
        df_copy['location_id'] = location_id

        # Select only the columns we need
        columns = ['location_id', 'date', 'ghi_kwh_m2', 'clear_sky_ghi_kwh_m2',
                  'temperature_c', 'wind_speed_ms', 'relative_humidity_pct']

        df_insert = df_copy[columns]

        # Insert data (replace if exists)
        df_insert.to_sql(
    'solar_irradiance_daily',
    self.conn,
    if_exists='append',
    index=False,
    method='multi'
)
        self.conn.commit()
        print(f"✓ Inserted {len(df_insert)} daily records for {location_name}")

    def get_location_data(self, location_name: str,
                         start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """Retrieve solar data for a specific location."""
        query = """
            SELECT l.location_name, l.latitude, l.longitude,
                   s.date, s.ghi_kwh_m2, s.clear_sky_ghi_kwh_m2,
                   s.temperature_c, s.wind_speed_ms, s.relative_humidity_pct
            FROM solar_irradiance_daily s
            JOIN locations l ON s.location_id = l.location_id
            WHERE l.location_name = ?
        """

        params = [location_name]

        if start_date and end_date:
            query += " AND s.date BETWEEN ? AND ?"
            params.extend([start_date, end_date])

        query += " ORDER BY s.date"

        return pd.read_sql_query(query, self.conn, params=params)

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()


# Sample Sub-Saharan Africa locations for refrigeration-heavy SMEs
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
    """
    Main pipeline: Fetch data from NASA POWER API and store in database.
    """
    # Initialize API and Database
    api = NASAPowerAPI()
    db = SolarDatabase("solar_irradiance.db")

    # Define date range (last 2 years for model training)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)  # 2 years

    start_str = start_date.strftime('%Y%m%d')
    end_str = end_date.strftime('%Y%m%d')

    print(f"\n{'='*60}")
    print("NASA POWER Solar Data Pipeline")
    print(f"Date Range: {start_str} to {end_str}")
    print(f"{'='*60}\n")

    # Fetch data for each location
    for location in SSA_LOCATIONS:
        print(f"\n--- Processing: {location['name']} ---")

        # Fetch data from NASA API
        raw_data = api.fetch_solar_data(
            latitude=location['lat'],
            longitude=location['lon'],
            start_date=start_str,
            end_date=end_str
        )

        if raw_data:
            # Parse and clean data
            df = api.parse_nasa_response(raw_data, location['name'])

            if not df.empty:
                print(f"Data shape: {df.shape}")
                print(f"Date range: {df['date'].min()} to {df['date'].max()}")
                print(f"Avg GHI: {df['ghi_kwh_m2'].mean():.2f} kWh/m²/day")

                # Store in database
                db.insert_daily_data(df)
            else:
                print("✗ No data returned from API")

        # Be nice to NASA servers
        time.sleep(2)

    # Validate stored data
    print(f"\n{'='*60}")
    print("Data Validation Summary")
    print(f"{'='*60}\n")

    for location in SSA_LOCATIONS:
        df = db.get_location_data(location['name'])
        if not df.empty:
            print(f"{location['name']}: {len(df)} records stored")
            print(f"  → Avg GHI: {df['ghi_kwh_m2'].mean():.2f} kWh/m²/day")
        else:
            print(f"{location['name']}: No data found")

    db.close()
    print("\n✓ Pipeline completed successfully!")


if __name__ == "__main__":
    main()
