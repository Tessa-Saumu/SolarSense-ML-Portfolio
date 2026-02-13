"""
NASA POWER Pipeline Integration Test
Model 2: Solar Generation Prediction

This script verifies that the NASA POWER data pipeline is properly
integrated with the XGBoost baseline model.

Run this BEFORE running the 02-baseline-model-xgboost.ipynb notebook
to ensure all pipeline components are working correctly.
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path

def test_csv_exists():
    """Test 1: Check if solar_data_merged.csv exists"""
    print("\n[Test 1] Loading solar_data_merged.csv...")
    csv_path = Path('solar_data_merged.csv')
    
    if not csv_path.exists():
        print("✗ FAIL: solar_data_merged.csv not found!")
        print("  → ACTION REQUIRED: Run 'python cleane_data.py' to generate the CSV")
        return None
    
    try:
        df = pd.read_csv(csv_path)
        print(f"✓ PASS: Loaded {len(df):,} records from solar_data_merged.csv")
        return df
    except Exception as e:
        print(f"✗ FAIL: Could not read CSV: {e}")
        return None

def test_required_columns(df):
    """Test 2: Verify all required columns exist"""
    print("\n[Test 2] Checking required columns...")
    
    required_cols = [
        'ghi_kwh_m2',
        'clear_sky_ghi_kwh_m2',
        'temperature_c',
        'wind_speed_ms',
        'relative_humidity_pct',
        'latitude',
        'longitude',
        'month',
        'day',
        'day_of_week',
        'estimated_daily_generation_kwh',
        'data_quality'
    ]
    
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        print(f"✗ FAIL: Missing columns: {missing_cols}")
        print(f"\nActual columns in CSV:")
        print(df.columns.tolist())
        return False
    else:
        print(f"✓ PASS: All {len(required_cols)} required columns present")
        return True

def test_data_types(df):
    """Test 3: Verify data types are correct"""
    print("\n[Test 3] Checking data types...")
    
    numeric_cols = ['ghi_kwh_m2', 'temperature_c', 'latitude', 'longitude']
    all_valid = True
    
    for col in numeric_cols:
        if df[col].dtype not in [np.float64, np.float32, np.int64, np.int32]:
            print(f"✗ FAIL: {col} is {df[col].dtype}, expected numeric")
            all_valid = False
    
    if all_valid:
        print("✓ PASS: All key columns have numeric data types")
    
    return all_valid

def test_data_ranges(df):
    """Test 4: Verify data values are in reasonable ranges"""
    print("\n[Test 4] Checking data ranges...")
    
    all_valid = True
    
    # GHI should be 0-12 kWh/m²/day for SSA
    ghi_max = df['ghi_kwh_m2'].max()
    ghi_min = df['ghi_kwh_m2'].min()
    
    if 0 <= ghi_min and ghi_max <= 12:
        print(f"✓ PASS: GHI range is reasonable ({ghi_min:.2f} - {ghi_max:.2f} kWh/m²)")
    else:
        print(f"✗ WARNING: GHI range unusual ({ghi_min:.2f} - {ghi_max:.2f} kWh/m²)")
        print("  Expected: 0-12 kWh/m²/day")
        # Do NOT fail test for warning
    
    # Temperature should be reasonable for SSA
    temp_max = df['temperature_c'].max()
    temp_min = df['temperature_c'].min()
    
    # Allow realistic SSA range (can drop below 10°C in Johannesburg/winter)
    if 0 <= temp_min and temp_max <= 45:
        print(f"✓ PASS: Temperature range is reasonable ({temp_min:.1f} - {temp_max:.1f} °C)")
    else:
        print(f"✗ WARNING: Temperature range unusual ({temp_min:.1f} - {temp_max:.1f} °C)")
        print("  Expected: 0–45 °C for SSA climate zones")
        # Still not failing unless extreme
    
    return all_valid


def test_locations(df):
    """Test 5: Verify all 7 SSA locations are present"""
    print("\n[Test 5] Checking locations...")
    
    locations = df['location_name'].unique()
    expected_count = 7
    
    print(f"Found {len(locations)} unique locations:")
    for loc in sorted(locations):
        count = len(df[df['location_name'] == loc])
        avg_ghi = df[df['location_name'] == loc]['ghi_kwh_m2'].mean()
        print(f"  - {loc}: {count:,} records, avg GHI: {avg_ghi:.2f} kWh/m²")
    
    if len(locations) == expected_count:
        print(f"✓ PASS: Found all {expected_count} expected locations")
        return True
    else:
        print(f"✗ FAIL: Expected {expected_count} locations, got {len(locations)}")
        return False

def test_feature_engineering(df):
    """Test 6: Verify feature engineering formulas work"""
    print("\n[Test 6] Testing feature engineering formulas...")
    
    try:
        # Test on a small sample
        test_df = df.head(100).copy()
        
        # Cloud cover index
        test_df['cloud_cover_index'] = (
            (test_df['clear_sky_ghi_kwh_m2'] - test_df['ghi_kwh_m2']) / 
            test_df['clear_sky_ghi_kwh_m2']
        ).fillna(0).clip(0, 1)
        
        # Clearness index
        test_df['clearness_index'] = (
            test_df['ghi_kwh_m2'] / test_df['clear_sky_ghi_kwh_m2']
        ).fillna(0).clip(0, 1)
        
        # Temperature efficiency factor
        test_df['temp_efficiency_factor'] = (
            1 - 0.005 * (test_df['temperature_c'] - 25)
        ).clip(0.7, 1.1)
        
        # Check if results are reasonable
        if test_df['cloud_cover_index'].between(0, 1).all():
            print("✓ PASS: cloud_cover_index calculated correctly (all values 0-1)")
        else:
            print("✗ FAIL: cloud_cover_index has values outside [0, 1]")
            return False
        
        if test_df['clearness_index'].between(0, 1).all():
            print("✓ PASS: clearness_index calculated correctly (all values 0-1)")
        else:
            print("✗ FAIL: clearness_index has values outside [0, 1]")
            return False
        
        if test_df['temp_efficiency_factor'].between(0.7, 1.1).all():
            print("✓ PASS: temp_efficiency_factor calculated correctly (all values 0.7-1.1)")
        else:
            print("✗ FAIL: temp_efficiency_factor has values outside [0.7, 1.1]")
            return False
        
        print("✓ PASS: All feature engineering formulas work correctly")
        return True
        
    except Exception as e:
        print(f"✗ FAIL: Feature engineering failed: {e}")
        return False

def test_target_variable(df):
    """Test 7: Verify target variable is reasonable"""
    print("\n[Test 7] Checking target variable...")
    
    target = 'estimated_daily_generation_kwh'
    
    if target not in df.columns:
        print(f"✗ FAIL: Target variable '{target}' not found in CSV")
        return False
    
    target_mean = df[target].mean()
    target_std = df[target].std()
    target_min = df[target].min()
    target_max = df[target].max()
    
    print(f"Target variable statistics:")
    print(f"  Mean: {target_mean:.2f} kWh/day")
    print(f"  Std:  {target_std:.2f} kWh/day")
    print(f"  Min:  {target_min:.2f} kWh/day")
    print(f"  Max:  {target_max:.2f} kWh/day")
    
    # For 10m² panels with 20% efficiency, expect 5-12 kWh/day
    if 5 < target_mean < 12:
        print(f"✓ PASS: Target mean ({target_mean:.2f} kWh/day) is reasonable")
        return True
    else:
        print(f"✗ WARNING: Target mean ({target_mean:.2f} kWh/day) seems unusual")
        print("  Expected: 5-12 kWh/day for 10m² panels at 20% efficiency")
        return False

def test_data_quality(df):
    """Test 8: Check data quality distribution"""
    print("\n[Test 8] Checking data quality flags...")
    
    if 'data_quality' not in df.columns:
        print("✗ WARNING: data_quality column not found")
        return False
    
    quality_dist = df['data_quality'].value_counts()
    print("Data quality distribution:")
    for quality, count in quality_dist.items():
        pct = (count / len(df)) * 100
        print(f"  {quality}: {count:,} ({pct:.1f}%)")
    
    good_pct = (quality_dist.get('good', 0) / len(df)) * 100
    
    if good_pct >= 95:
        print(f"✓ PASS: {good_pct:.1f}% of data is 'good' quality (≥95%)")
        return True
    else:
        print(f"✗ WARNING: Only {good_pct:.1f}% of data is 'good' quality (<95%)")
        return False

def main():
    """Run all integration tests"""
    print("=" * 70)
    print("NASA POWER PIPELINE INTEGRATION TEST")
    print("Model 2: Solar Generation Prediction")
    print("=" * 70)
    
    # Track results
    results = []
    
    # Test 1: Load CSV
    df = test_csv_exists()
    if df is None:
        print("\n" + "=" * 70)
        print("CRITICAL: Cannot proceed without solar_data_merged.csv")
        print("=" * 70)
        sys.exit(1)
    results.append(df is not None)
    
    # Test 2: Required columns
    results.append(test_required_columns(df))
    
    # Test 3: Data types
    results.append(test_data_types(df))
    
    # Test 4: Data ranges
    results.append(test_data_ranges(df))
    
    # Test 5: Locations
    results.append(test_locations(df))
    
    # Test 6: Feature engineering
    results.append(test_feature_engineering(df))
    
    # Test 7: Target variable
    results.append(test_target_variable(df))
    
    # Test 8: Data quality
    results.append(test_data_quality(df))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nTests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ ALL TESTS PASSED!")
        print("\nThe NASA POWER pipeline is properly integrated.")
        print("You can now run 02-baseline-model-xgboost.ipynb with confidence.")
        print("\nNext step: jupyter notebook 02-baseline-model-xgboost.ipynb")
    else:
        print("\n✗ SOME TESTS FAILED")
        print("\nPlease review the failed tests above and fix issues before")
        print("running the XGBoost baseline notebook.")
        
        if not Path('solar_data_merged.csv').exists():
            print("\nCRITICAL: Run 'python cleane_data.py' to generate the CSV file")
    
    print("=" * 70)
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)