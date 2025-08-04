#!/usr/bin/env python3
"""
CSV Data Validation Report
Validates the logged BMS data and generates a comprehensive report
"""

import csv
import pandas as pd
from pathlib import Path
import numpy as np

def validate_csv_data(csv_file):
    """Validate the CSV data and generate comprehensive report"""
    
    print("GA BMS Data Validation Report")
    print("=" * 60)
    
    if not Path(csv_file).exists():
        print(f"❌ CSV file not found: {csv_file}")
        return
    
    # Read CSV data
    df = pd.read_csv(csv_file)
    
    print(f"📁 File: {csv_file}")
    print(f"📊 Total Records: {len(df)}")
    print(f"⏱️  First Record: {df['Timestamp'].iloc[0]}")
    print(f"⏱️  Last Record: {df['Timestamp'].iloc[-1]}")
    print()
    
    # Validate Cell Voltages (Groups 1-8)
    print("🔋 CELL VOLTAGE VALIDATION")
    print("-" * 40)
    
    cell_columns = [f'afe_cell_volt{i}' for i in range(1, 9)]
    
    for i, col in enumerate(cell_columns, 1):
        values = df[col]
        mean_val = values.mean()
        min_val = values.min()
        max_val = values.max()
        std_val = values.std()
        
        # Check if values are in typical range (2500-4200 mV)
        in_range = ((values >= 2500) & (values <= 4200)).all()
        status = "✅" if in_range else "⚠️"
        
        print(f"  Cell {i}: {status} Mean={mean_val:.0f}mV, Range=[{min_val}-{max_val}]mV, σ={std_val:.1f}mV")
    
    print()
    
    # Pack voltage validation
    print("📦 PACK VOLTAGE VALIDATION")
    print("-" * 40)
    
    pack_voltages = df['afe_pack_volt']
    expected_pack = df[cell_columns].sum(axis=1)
    pack_diff = abs(pack_voltages - expected_pack)
    
    print(f"  Pack Voltage: Mean={pack_voltages.mean():.0f}mV, Range=[{pack_voltages.min()}-{pack_voltages.max()}]mV")
    print(f"  Sum vs Pack: Max difference={pack_diff.max():.0f}mV (should be close to 0)")
    
    if pack_diff.max() < 100:  # Allow 100mV tolerance
        print("  ✅ Pack voltage calculation is consistent")
    else:
        print("  ⚠️ Pack voltage may have calculation issues")
    
    print()
    
    # Cell delta validation
    print("⚖️ CELL BALANCE VALIDATION")
    print("-" * 40)
    
    cell_deltas = df['afe_cell_volt_delta']
    calculated_deltas = df[cell_columns].max(axis=1) - df[cell_columns].min(axis=1)
    delta_diff = abs(cell_deltas - calculated_deltas)
    
    print(f"  Cell Delta: Mean={cell_deltas.mean():.1f}mV, Range=[{cell_deltas.min()}-{cell_deltas.max()}]mV")
    print(f"  Calculated vs Reported: Max difference={delta_diff.max():.1f}mV")
    
    if delta_diff.max() < 10:  # Allow 10mV tolerance
        print("  ✅ Cell delta calculation is accurate")
    else:
        print("  ⚠️ Cell delta calculation may have issues")
    
    # Balance assessment
    avg_delta = cell_deltas.mean()
    if avg_delta < 50:
        balance_status = "Excellent"
    elif avg_delta < 100:
        balance_status = "Good"
    elif avg_delta < 200:
        balance_status = "Fair"
    else:
        balance_status = "Poor"
    
    print(f"  Balance Status: {balance_status} (avg delta: {avg_delta:.1f}mV)")
    print()
    
    # Current and SOC validation
    print("🔌 CURRENT & STATE VALIDATION")
    print("-" * 40)
    
    current_values = df['afe_current']
    soc_values = df['fg_state_of_charge']
    
    print(f"  Current: Mean={current_values.mean():.0f}mA, Range=[{current_values.min()}-{current_values.max()}]mA")
    print(f"  SOC: Mean={soc_values.mean():.1f}%, Range=[{soc_values.min()}-{soc_values.max()}]%")
    
    # Check if SOC is in valid range
    soc_valid = ((soc_values >= 0) & (soc_values <= 100)).all()
    print(f"  SOC Range: {'✅ Valid' if soc_valid else '❌ Invalid'}")
    
    # Charging/discharging analysis
    charging_records = (current_values > 0).sum()
    discharging_records = (current_values < 0).sum()
    idle_records = (current_values == 0).sum()
    
    print(f"  Charging: {charging_records} records ({charging_records/len(df)*100:.1f}%)")
    print(f"  Discharging: {discharging_records} records ({discharging_records/len(df)*100:.1f}%)")
    print(f"  Idle: {idle_records} records ({idle_records/len(df)*100:.1f}%)")
    print()
    
    # Temperature validation
    print("🌡️ TEMPERATURE VALIDATION")
    print("-" * 40)
    
    temp_columns = ['afe_temp1', 'afe_temp2', 'fg_temperature', 'fg_internal_temp']
    
    for col in temp_columns:
        temps = df[col]
        temp_celsius = temps / 10.0  # Convert from °C*10 to °C
        mean_temp = temp_celsius.mean()
        min_temp = temp_celsius.min()
        max_temp = temp_celsius.max()
        
        # Check if temperature is reasonable (-40°C to +80°C)
        temp_valid = ((temp_celsius >= -40) & (temp_celsius <= 80)).all()
        status = "✅" if temp_valid else "⚠️"
        
        print(f"  {col}: {status} Mean={mean_temp:.1f}°C, Range=[{min_temp:.1f}-{max_temp:.1f}]°C")
    
    print()
    
    # Data continuity validation
    print("📈 DATA CONTINUITY VALIDATION")
    print("-" * 40)
    
    # Check for missing values
    missing_data = df.isnull().sum().sum()
    print(f"  Missing Values: {missing_data} ({'✅ None' if missing_data == 0 else '⚠️ Found'})")
    
    # Check for data logging frequency
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    time_diffs = df['Timestamp'].diff().dt.total_seconds()
    avg_interval = time_diffs[1:].mean()  # Skip first NaN
    
    print(f"  Average Interval: {avg_interval:.2f} seconds")
    print(f"  Expected Interval: 0.50 seconds")
    
    if abs(avg_interval - 0.5) < 0.1:
        print("  ✅ Logging interval is consistent")
    else:
        print("  ⚠️ Logging interval varies from expected")
    
    print()
    
    # Summary
    print("📋 VALIDATION SUMMARY")
    print("-" * 40)
    
    checks_passed = 0
    total_checks = 7
    
    # Count passed checks
    if ((df[cell_columns] >= 2500) & (df[cell_columns] <= 4200)).all().all():
        checks_passed += 1
        print("  ✅ Cell voltages in valid range")
    else:
        print("  ❌ Some cell voltages out of range")
    
    if pack_diff.max() < 100:
        checks_passed += 1
        print("  ✅ Pack voltage consistency")
    else:
        print("  ❌ Pack voltage calculation issues")
        
    if delta_diff.max() < 10:
        checks_passed += 1
        print("  ✅ Cell delta accuracy")
    else:
        print("  ❌ Cell delta calculation issues")
        
    if soc_valid:
        checks_passed += 1
        print("  ✅ SOC values valid")
    else:
        print("  ❌ SOC values out of range")
        
    if ((df[temp_columns] >= -400) & (df[temp_columns] <= 800)).all().all():
        checks_passed += 1
        print("  ✅ Temperature values reasonable")
    else:
        print("  ❌ Some temperatures out of range")
        
    if missing_data == 0:
        checks_passed += 1
        print("  ✅ No missing data")
    else:
        print("  ❌ Missing data found")
        
    if abs(avg_interval - 0.5) < 0.1:
        checks_passed += 1
        print("  ✅ Consistent logging interval")
    else:
        print("  ❌ Inconsistent logging interval")
    
    print()
    print(f"🎯 OVERALL SCORE: {checks_passed}/{total_checks} ({checks_passed/total_checks*100:.0f}%)")
    
    if checks_passed == total_checks:
        print("🎉 EXCELLENT: All validation checks passed!")
    elif checks_passed >= total_checks * 0.8:
        print("👍 GOOD: Most validation checks passed")
    elif checks_passed >= total_checks * 0.6:
        print("⚠️ FAIR: Some issues found")
    else:
        print("❌ POOR: Multiple validation failures")

if __name__ == "__main__":
    import sys
    
    # Find the most recent CSV file
    csv_files = list(Path("test_logs").glob("*.csv"))
    if csv_files:
        latest_csv = max(csv_files, key=lambda x: x.stat().st_mtime)
        validate_csv_data(latest_csv)
    else:
        print("No CSV files found in test_logs directory")