"""
Export Merged Solar Data
This script exports the complete merged dataset to CSV
"""
from datetime import datetime
import psycopg2

import pandas as pd

import os

# =============================================
# DATABASE CONFIGURATION
# =============================================
DB_CONFIG = {
    "dbname": "solar_irradiance",
    "user": "postgres",
    "password": "123456789",
    "host": "localhost",
    "port": "5432"
}

def export_merged_data():
    """Export complete merged solar data to CSV."""

    print("\n" + "="*70)
    print("EXPORTING MERGED SOLAR DATA FOR TESSA")
    print("="*70 + "\n")

    try:
        # Connect to database
        print("Connecting to database...")
        conn = psycopg2.connect(**DB_CONFIG)
        print("[OK] Connected successfully!\n")

        # =============================================
        # OPTION 1: Export from VIEW (Recommended)
        # =============================================
        print("Fetching data from merged view...")
        query = """
            SELECT
                location_name,
                country,
                latitude,
                longitude,
                date,
                year,
                month,
                day,
                day_of_week,
                ghi_kwh_m2,
                clear_sky_ghi_kwh_m2,
                temperature_c,
                wind_speed_ms,
                relative_humidity_pct,
                estimated_daily_generation_kwh,
                data_quality
            FROM v_solar_data_complete
            ORDER BY location_name, date
        """

        df = pd.read_sql_query(query, conn)

        # Data quality summary
        print(f"[OK] Retrieved {len(df):,} records")
        print(f"    Locations: {df['location_name'].nunique()}")
        print(f"    Date range: {df['date'].min()} to {df['date'].max()}")
        print(f"    Countries: {', '.join(df['country'].unique())}")

        # Check data quality
        print("\n--- Data Quality Summary ---")
        quality_summary = df['data_quality'].value_counts()
        for quality, count in quality_summary.items():
            percentage = (count / len(df)) * 100
            print(f"    {quality}: {count:,} records ({percentage:.1f}%)")

        # Missing values summary
        print("\n--- Missing Values ---")
        missing = df.isnull().sum()
        missing = missing[missing > 0]
        if len(missing) > 0:
            for col, count in missing.items():
                percentage = (count / len(df)) * 100
                print(f"    {col}: {count:,} ({percentage:.1f}%)")
        else:
            print("    No missing values!")

        # =============================================
        # EXPORT TO CSV
        # =============================================
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"solar_data_merged_for_tessa_{timestamp}.csv"

        print("\n--- Exporting to CSV ---")
        df.to_csv(output_file, index=False)
        print(f"[OK] Data exported to: {output_file}")
        print(f"    File size: {os.path.getsize(output_file) / 1024 / 1024:.2f} MB")

        # =============================================
        # CREATE DATA DICTIONARY
        # =============================================
        data_dict = f"""
╔══════════════════════════════════════════════════════════════════════════╗
║              SOLAR DATA DICTIONARY FOR PREPROCESSING                     ║
╚══════════════════════════════════════════════════════════════════════════╝

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Total Records: {len(df):,}
Locations: {df['location_name'].nunique()}
Date Range: {df['date'].min()} to {df['date'].max()}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
COLUMN DESCRIPTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

LOCATION INFORMATION:
--------------------
location_name               : City/location identifier (e.g., 'Nairobi_Kenya')
country                     : Country name
latitude                    : Latitude in decimal degrees (-90 to 90)
longitude                   : Longitude in decimal degrees (-180 to 180)

DATE/TIME INFORMATION:
---------------------
date                        : Measurement date (YYYY-MM-DD)
year                        : Year (YYYY)
month                       : Month (1-12)
day                         : Day of month (1-31)
day_of_week                 : Day name (Monday, Tuesday, etc.)

SOLAR IRRADIANCE DATA:
---------------------
ghi_kwh_m2                  : Global Horizontal Irradiance (kWh/m²/day)
                             Primary solar measurement - all sky conditions

clear_sky_ghi_kwh_m2        : Clear sky GHI (kWh/m²/day)
                             Theoretical maximum under clear sky
                             Used for cloud cover estimation

ENVIRONMENTAL DATA:
------------------
temperature_c               : Air temperature at 2 meters (°C)
wind_speed_ms              : Wind speed at 10 meters (m/s)
relative_humidity_pct      : Relative humidity (0-100%)

CALCULATED FIELDS:
-----------------
estimated_daily_generation_kwh : Estimated solar generation (kWh/day)
                                 Based on: 10m² panels, 20% efficiency, 85% system efficiency
                                 Formula: GHI × Area × Efficiency × System_Loss

DATA QUALITY:
------------
data_quality               : Quality flag for each record
                            - 'good': Valid data
                            - 'missing': NULL values
                            - 'invalid': Negative values
                            - 'suspect': Unusually high values (>10 kWh/m²/day)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DATA SOURCE & METHODOLOGY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Source API         : NASA POWER (Prediction Of Worldwide Energy Resources)
URL                : https://power.larc.nasa.gov/
Community          : Renewable Energy (RE)
Data Type          : Daily averages
Spatial Resolution : 0.5° × 0.5° (approximately 50km × 50km)
Temporal Coverage  : {df['date'].min()} to {df['date'].max()}
Update Frequency   : Daily
Data Reliability   : Satellite-derived, validated against ground stations

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LOCATION DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        # Add location-specific statistics
        for location in df['location_name'].unique():
            loc_data = df[df['location_name'] == location]
            data_dict += f"""
{location}:
    Country: {loc_data['country'].iloc[0]}
    Coordinates: ({loc_data['latitude'].iloc[0]:.4f}, {loc_data['longitude'].iloc[0]:.4f})
    Records: {len(loc_data):,}
    Avg GHI: {loc_data['ghi_kwh_m2'].mean():.2f} kWh/m²/day
    Avg Temperature: {loc_data['temperature_c'].mean():.1f}°C
    Data Quality: {(loc_data['data_quality'] == 'good').sum() / len(loc_data) * 100:.1f}% good
"""

        data_dict += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DATA PREPROCESSING NOTES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. MISSING VALUES:
   - NASA POWER uses -999 for missing data (already converted to NULL)
   - Consider interpolation for small gaps (<3 days)
   - Flag or remove records with >20% missing environmental data

2. OUTLIER DETECTION:
   - GHI values >10 kWh/m²/day flagged as 'suspect'
   - Check for negative values (physical impossibility)
   - Verify temperature extremes (<-10°C or >50°C)

3. TEMPORAL PATTERNS:
   - Consider seasonality (dry/wet seasons in SSA)
   - Account for day length variations with latitude
   - Model weekly patterns if present

4. FEATURE ENGINEERING SUGGESTIONS:
   - Cloud cover estimate: (clear_sky_ghi - ghi) / clear_sky_ghi
   - Solar clearness index: ghi / clear_sky_ghi
   - Temperature-adjusted efficiency
   - Moving averages (7-day, 30-day)
   - Season indicators

5. REGIONAL CONSIDERATIONS:
   - East Africa (Kenya, Uganda, Tanzania, Rwanda): Bimodal rainfall
   - West Africa (Nigeria, Ghana): Monsoon patterns
   - Southern Africa (South Africa): More variable seasons

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONTACT & ATTRIBUTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Project: Solar Viability Assessment for SSA Refrigeration SMEs
Model: Model 2 - Solar Generation Prediction
Data Pipeline: NASA POWER API → PostgreSQL → CSV Export
Created By: [Your Name]
Date: {datetime.now().strftime('%Y-%m-%d')}

For questions or issues with this dataset, contact the data pipeline owner.

NASA POWER Citation:
NASA/POWER CERES/MERRA2 Native Resolution Daily Data
Dates: {df['date'].min()} - {df['date'].max()}
Location: Sub-Saharan Africa (Multiple Sites)
Retrieved: {datetime.now().strftime('%Y-%m-%d')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

        dict_file = f"DATA_DICTIONARY_{timestamp}.txt"
        with open(dict_file, 'w', encoding='utf-8') as f:
            f.write(data_dict)

        print(f"[OK] Data dictionary created: {dict_file}")

        # =============================================
        # CREATE SUMMARY STATISTICS
        # =============================================
        print("\n--- Creating Summary Statistics ---")

        # Overall summary
        summary_stats = df.groupby('location_name').agg({
            'ghi_kwh_m2': ['count', 'mean', 'std', 'min', 'max'],
            'temperature_c': ['mean', 'std'],
            'wind_speed_ms': 'mean',
            'relative_humidity_pct': 'mean',
            'estimated_daily_generation_kwh': 'mean'
        }).round(2)

        summary_stats.columns = ['_'.join(col).strip() for col in summary_stats.columns.values]

        summary_file = f"summary_statistics_{timestamp}.csv"
        summary_stats.to_csv(summary_file)
        print(f"[OK] Summary statistics saved: {summary_file}")

        # =============================================
        # CLOSE CONNECTION
        # =============================================
        conn.close()

        # =============================================
        # FINAL SUMMARY
        # =============================================
        print(f"\n{'='*70}")
        print("EXPORT COMPLETE!")
        print(f"{'='*70}\n")

        print("Files created for Tessa:")
        print(f"  1. {output_file}")
        print(f"     → Main dataset ({len(df):,} records)")
        print(f"  2. {dict_file}")
        print("     → Data dictionary with column descriptions")
        print(f"  3. {summary_file}")
        print("     → Summary statistics by location")

        print(f"\n{'='*70}")
        print("NEXT STEPS:")
        print(f"{'='*70}")
        print("1. Review the data dictionary")
        print("2. Share all 3 files with Tessa")
        print("3. Discuss preprocessing strategy")
        print("4. Begin feature engineering for solar prediction model")
        print(f"{'='*70}\n")

    except psycopg2.Error as e:
        print(f"[ERROR] Database error: {e}")
        print("\nTroubleshooting:")
        print("  1. Check database connection settings")
        print("  2. Make sure you ran merge_tables.sql first")
        print("  3. Verify PostgreSQL is running")

    except psycopg2.Error as e:
        print(f"[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    export_merged_data()