"""
Unit tests for CSV writer functionality, specifically cell voltage logging.
"""

import os
import csv
import pytest
from datetime import datetime
from src.ga_modbus_csv_writer import write_modbus_data_to_csv


class TestCSVWriter:
    """Test cases for the CSV writer functionality."""
    
    def test_cell_voltage_csv_logging(self, temp_log_dir, sample_battery_data):
        """Test that cell voltages are correctly written to CSV file during logging."""
        csv_path = os.path.join(temp_log_dir, "test_cell_voltages.csv")
        
        # Write battery data to CSV
        write_modbus_data_to_csv(sample_battery_data, csv_path)
        
        # Verify file was created
        assert os.path.exists(csv_path), "CSV file should be created"
        
        # Read and verify the CSV content
        with open(csv_path, 'r', newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        # Should have exactly one data row
        assert len(rows) == 1, "Should have exactly one data row"
        
        row = rows[0]
        
        # Test cell voltage columns exist and have correct raw integer values (mV)
        expected_cell_voltages = {
            'Cell1_V': '3456',  # Raw mV values as in legacy format
            'Cell2_V': '3457', 
            'Cell3_V': '3455',
            'Cell4_V': '3458',
            'Cell5_V': '3454',
            'Cell6_V': '3459',
            'Cell7_V': '3456',
            'Cell8_V': '3457'
        }
        
        for cell_col, expected_value in expected_cell_voltages.items():
            assert cell_col in row, f"Column {cell_col} should exist in CSV"
            assert row[cell_col] == expected_value, f"{cell_col} should be {expected_value}, got {row[cell_col]}"
        
        # Test pack voltage (raw mV)
        assert row['Pack_V'] == '27652', f"Pack voltage should be 27652 mV, got {row['Pack_V']}"
        
        # Test cell delta voltage (raw mV)
        assert row['Cell_Delta_V'] == '5', f"Cell delta should be 5 mV, got {row['Cell_Delta_V']}"
        
        # Test timestamp format
        assert 'Timestamp' in row, "Timestamp column should exist"
        timestamp_str = row['Timestamp']
        # Should be in format: YYYY-MM-DD HH:MM:SS.mmm
        assert len(timestamp_str) == 23, f"Timestamp should be 23 chars long, got {len(timestamp_str)}"
        assert timestamp_str[4] == '-', "Timestamp should have dash at position 4"
        assert timestamp_str[7] == '-', "Timestamp should have dash at position 7"
        assert timestamp_str[10] == ' ', "Timestamp should have space at position 10"
        assert timestamp_str[19] == '.', "Timestamp should have dot at position 19"
    
    def test_csv_header_creation(self, temp_log_dir):
        """Test that CSV headers are correctly created on first write."""
        csv_path = os.path.join(temp_log_dir, "test_headers.csv")
        
        # Sample minimal data (raw mV values)
        data = {
            'afe_cell_volt1': 3500,  # Raw mV
            'afe_cell_volt2': 3501,  # Raw mV
            'timestamp': datetime(2025, 7, 12, 10, 30, 45)
        }
        
        write_modbus_data_to_csv(data, csv_path)
        
        # Read the file and check headers
        with open(csv_path, 'r', newline='') as f:
            reader = csv.reader(f)
            headers = next(reader)
        
        expected_headers = [
            "Timestamp", "Cell1_V", "Cell2_V", "Cell3_V", "Cell4_V", "Cell5_V", "Cell6_V",
            "Cell7_V", "Cell8_V", "Pack_V", "Cell_Delta_V", "Temp1", "Temp2", "Current",
            "SOC", "FG_Voltage", "FG_Current", "FG_Temp", "Remaining_Cap", "Full_Cap",
            "Design_Cap", "Avg_Current", "Time_Empty", "Time_Full", "Internal_Temp",
            "Cycle_Count", "SOH", "Charging_V", "Charging_I", "Max_Temp", "Min_Temp",
            "Max_Chg_Curr", "Max_Dsg_Curr"
        ]
        
        assert headers == expected_headers, "Headers should match expected format"
    
    def test_csv_append_functionality(self, temp_log_dir):
        """Test that multiple writes append to the same CSV file without duplicating headers."""
        csv_path = os.path.join(temp_log_dir, "test_append.csv")
        
        # First write (raw mV values)
        data1 = {
            'afe_cell_volt1': 3500,  # Raw mV
            'afe_cell_volt2': 3501,  # Raw mV
            'timestamp': datetime(2025, 7, 12, 10, 30, 45)
        }
        write_modbus_data_to_csv(data1, csv_path)
        
        # Second write (raw mV values)
        data2 = {
            'afe_cell_volt1': 3502,  # Raw mV
            'afe_cell_volt2': 3503,  # Raw mV
            'timestamp': datetime(2025, 7, 12, 10, 30, 46)
        }
        write_modbus_data_to_csv(data2, csv_path)
        
        # Read and verify
        with open(csv_path, 'r', newline='') as f:
            lines = f.readlines()
        
        # Should have 1 header line + 2 data lines = 3 total lines
        assert len(lines) == 3, f"Should have 3 lines (1 header + 2 data), got {len(lines)}"
        
        # First line should be headers
        assert lines[0].startswith('Timestamp,'), "First line should be headers"
        
        # Check that both data rows are present
        with open(csv_path, 'r', newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        assert len(rows) == 2, "Should have 2 data rows"
        assert rows[0]['Cell1_V'] == '3500', "First row Cell1_V should be 3500 mV"
        assert rows[1]['Cell1_V'] == '3502', "Second row Cell1_V should be 3502 mV"
    
    def test_missing_data_handling(self, temp_log_dir):
        """Test that missing cell voltage data is handled gracefully with defaults."""
        csv_path = os.path.join(temp_log_dir, "test_missing_data.csv")
        
        # Data with some missing cell voltages (raw mV values)
        data = {
            'afe_cell_volt1': 3500,  # Raw mV
            'afe_cell_volt3': 3502,  # Raw mV
            # Missing cell2, cell4-8
            'timestamp': datetime(2025, 7, 12, 10, 30, 45)
        }
        
        write_modbus_data_to_csv(data, csv_path)
        
        # Read and verify
        with open(csv_path, 'r', newline='') as f:
            reader = csv.DictReader(f)
            row = next(reader)
        
        # Present values should be correct (raw mV)
        assert row['Cell1_V'] == '3500', "Cell1_V should be 3500 mV"
        assert row['Cell3_V'] == '3502', "Cell3_V should be 3502 mV"
        
        # Missing values should default to 0
        assert row['Cell2_V'] == '0', "Missing Cell2_V should default to 0 mV"
        assert row['Cell4_V'] == '0', "Missing Cell4_V should default to 0 mV"
        assert row['Cell5_V'] == '0', "Missing Cell5_V should default to 0 mV"
    
    def test_voltage_precision(self, temp_log_dir):
        """Test that voltage values are logged as raw integers (mV)."""
        csv_path = os.path.join(temp_log_dir, "test_precision.csv")
        
        data = {
            'afe_cell_volt1': 3456,  # Raw mV value
            'afe_cell_volt2': 3400,  # Raw mV value
            'afe_cell_volt3': 3000,  # Raw mV value
            'timestamp': datetime(2025, 7, 12, 10, 30, 45)
        }
        
        write_modbus_data_to_csv(data, csv_path)
        
        # Read and verify
        with open(csv_path, 'r', newline='') as f:
            reader = csv.DictReader(f)
            row = next(reader)
        
        assert row['Cell1_V'] == '3456', "Cell1_V should be 3456 mV"
        assert row['Cell2_V'] == '3400', "Cell2_V should be 3400 mV"
        assert row['Cell3_V'] == '3000', "Cell3_V should be 3000 mV"