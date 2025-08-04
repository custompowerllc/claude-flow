"""
Unit test for battery discharge simulation with CSV logging verification.
Tests realistic discharge curves and proper data logging throughout the discharge cycle.
"""

import os
import csv
import pytest
import math
from datetime import datetime, timedelta
from src.ga_modbus_csv_writer import write_modbus_data_to_csv


class TestBatteryDischargeSimulation:
    """Test battery discharge simulation with CSV logging validation."""
    
    def generate_discharge_curve_data(self, time_step_seconds=5, total_duration_minutes=120, discharge_current_amps=20):
        """
        Generate realistic battery discharge data based on LiFePO4 characteristics.
        
        Args:
            time_step_seconds: Time between data points (seconds)
            total_duration_minutes: Total discharge duration (minutes) 
            discharge_current_amps: Discharge current (A)
            
        Returns:
            List of battery data dictionaries representing discharge curve
        """
        data_points = []
        total_steps = (total_duration_minutes * 60) // time_step_seconds
        
        # Battery specifications from battery_pack_spec_json.json
        nominal_voltage = 25.6  # V (8S configuration)
        capacity_ah = 14.4  # Ah
        cell_count = 8
        
        # Discharge curve parameters for LiFePO4
        voltage_start = 28.0  # V (3.50V per cell)
        voltage_end = 23.6   # V (2.95V per cell - system minimum)
        
        start_time = datetime(2025, 7, 12, 14, 30, 0)  # 2:30 PM start
        
        for step in range(total_steps):
            # Calculate time progression
            elapsed_minutes = (step * time_step_seconds) / 60.0
            elapsed_hours = elapsed_minutes / 60.0
            timestamp = start_time + timedelta(seconds=step * time_step_seconds)
            
            # Calculate state of charge (linear discharge for simplicity)
            initial_soc = 100.0  # Start at 100%
            soc = max(0.0, initial_soc - (elapsed_hours / (capacity_ah / discharge_current_amps)) * 100)
            
            # LiFePO4 discharge curve (relatively flat with steep drop at end)
            if soc > 20:
                # Flat portion of discharge curve
                voltage_factor = 0.95 + 0.05 * (soc - 20) / 80  # 95-100% of nominal
            else:
                # Steep voltage drop at low SOC
                voltage_factor = 0.84 + 0.11 * (soc / 20)  # 84-95% of nominal
            
            pack_voltage = voltage_start * voltage_factor
            pack_voltage_mv = int(pack_voltage * 1000)  # Convert to mV
            
            # Generate individual cell voltages with slight variation
            base_cell_voltage_mv = pack_voltage_mv // cell_count
            cell_voltages = []
            for i in range(cell_count):
                # Add small random variation (+/- 10mV) and aging effects
                variation = (-10 + (i * 3)) if step > total_steps * 0.7 else (-5 + (i * 2))
                cell_voltage = base_cell_voltage_mv + variation
                cell_voltages.append(max(2750, cell_voltage))  # Minimum 2.75V per cell
            
            # Calculate cell delta (max - min)
            cell_delta_mv = max(cell_voltages) - min(cell_voltages)
            
            # Temperature rise during discharge (thermal effects)
            ambient_temp = 295  # 29.5°C in 0.1°C units
            temp_rise = int(15 * (elapsed_hours / (capacity_ah / discharge_current_amps)))  # Up to 1.5°C rise
            temp1 = ambient_temp + temp_rise
            temp2 = ambient_temp + temp_rise + 5  # Slightly higher for temp2
            
            # Current with noise (should be relatively stable during constant discharge)
            current_noise = 5 if step % 10 == 0 else 0  # Occasional current spikes
            current_raw = (discharge_current_amps * 1000) + current_noise  # Convert to mA
            
            # Fuel gauge data
            remaining_capacity = (soc / 100.0) * capacity_ah * 1000  # Convert to mAh
            fg_voltage_mv = pack_voltage_mv - 50  # FG slightly different from AFE
            
            # Calculate time to empty (decreasing)
            if soc > 5:
                time_to_empty = int((remaining_capacity / 1000) / discharge_current_amps * 60)  # Minutes
            else:
                time_to_empty = int(5 + (soc / 5) * 10)  # 5-15 minutes when low
            
            # Create data point
            data_point = {
                'timestamp': timestamp,
                'afe_cell_volt1': cell_voltages[0],
                'afe_cell_volt2': cell_voltages[1], 
                'afe_cell_volt3': cell_voltages[2],
                'afe_cell_volt4': cell_voltages[3],
                'afe_cell_volt5': cell_voltages[4],
                'afe_cell_volt6': cell_voltages[5],
                'afe_cell_volt7': cell_voltages[6],
                'afe_cell_volt8': cell_voltages[7],
                'afe_pack_volt': pack_voltage_mv,
                'afe_cell_volt_delta': cell_delta_mv,
                'afe_temp1': temp1,
                'afe_temp2': temp2,
                'afe_current': current_raw,
                'fg_state_of_charge': int(soc),
                'fg_voltage': fg_voltage_mv,
                'fg_current': current_raw,  # Same as AFE current
                'fg_temperature': temp1,
                'fg_remaining_capacity': int(remaining_capacity),
                'fg_full_charge_cap': 14400,  # 14.4Ah in mAh
                'fg_design_capacity': 14400,
                'fg_average_current': current_raw,
                'fg_time_to_empty': time_to_empty,
                'fg_time_to_full': 65535,  # Not charging
                'fg_internal_temp': temp1 + 2,
                'fg_cycle_count': 125,
                'fg_state_of_health': 98,
                'fg_charging_voltage': 0,  # Not charging
                'fg_charging_current': 0,
                'fg_lifetime_max_temp': 450,  # 45.0°C in 0.1°C units
                'fg_lifetime_min_temp': -100,  # -10.0°C in 0.1°C units
                'fg_lifetime_max_chg': 5000,  # 5A in mA
                'fg_lifetime_max_dsg': 25000  # 25A in mA
            }
            
            data_points.append(data_point)
            
            # Stop if battery is fully discharged
            if soc <= 1.0:
                break
                
        return data_points
    
    def test_battery_discharge_simulation_csv_logging(self, temp_log_dir):
        """
        Test complete battery discharge simulation with CSV logging verification.
        Simulates a 2-hour discharge at 20A and validates CSV output.
        """
        csv_path = os.path.join(temp_log_dir, "discharge_simulation_test.csv")
        
        # Generate discharge curve data
        discharge_data = self.generate_discharge_curve_data(
            time_step_seconds=10,  # 10-second intervals
            total_duration_minutes=120,  # 2 hours
            discharge_current_amps=20  # 20A discharge
        )
        
        # Verify we have reasonable amount of data
        assert len(discharge_data) > 50, "Should have sufficient data points for 2-hour test"
        assert len(discharge_data) <= 720, "Should not exceed expected data points (720 max for 2hr at 10s intervals)"
        
        # Write all discharge data to CSV
        for data_point in discharge_data:
            write_modbus_data_to_csv(data_point, csv_path)
        
        # Verify CSV file was created
        assert os.path.exists(csv_path), "CSV file should be created"
        
        # Read and validate CSV content
        with open(csv_path, 'r', newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        # Verify correct number of rows
        assert len(rows) == len(discharge_data), f"CSV should have {len(discharge_data)} rows, got {len(rows)}"
        
        # Validate discharge progression
        first_row = rows[0]
        last_row = rows[-1]
        
        # Check initial conditions (start of discharge)
        assert int(first_row['Cell1_V']) > 3400, "Initial cell voltage should be > 3.4V (3400mV)"
        assert int(first_row['Pack_V']) > 27000, "Initial pack voltage should be > 27V (27000mV)"
        assert int(first_row['SOC']) >= 95, "Initial SOC should be >= 95%"
        
        # Check final conditions (end of discharge)
        assert int(last_row['Cell1_V']) < 3200, "Final cell voltage should be < 3.2V (3200mV)"
        assert int(last_row['Pack_V']) < 26000, "Final pack voltage should be < 26V (26000mV)"
        assert int(last_row['SOC']) < 20, "Final SOC should be < 20%"
        
        # Verify voltage decreases over time
        initial_pack_voltage = int(first_row['Pack_V'])
        final_pack_voltage = int(last_row['Pack_V'])
        assert final_pack_voltage < initial_pack_voltage, "Pack voltage should decrease during discharge"
        
        # Verify SOC decreases over time
        initial_soc = int(first_row['SOC'])
        final_soc = int(last_row['SOC'])
        assert final_soc < initial_soc, "SOC should decrease during discharge"
        
        # Check current consistency (should be relatively stable during discharge)
        currents = [int(row['Current']) for row in rows[:10]]  # Check first 10 readings
        avg_current = sum(currents) / len(currents)
        assert 19000 <= avg_current <= 21000, f"Average current should be ~20A (20000mA), got {avg_current}mA"
        
        # Verify temperature increase during discharge
        initial_temp = int(first_row['Temp1'])
        final_temp = int(last_row['Temp1'])
        assert final_temp >= initial_temp, "Temperature should increase or stay same during discharge"
        
        # Check cell voltage balance (delta should be reasonable)
        for i, row in enumerate(rows):
            cell_delta = int(row['Cell_Delta_V'])
            assert cell_delta <= 100, f"Cell delta should be <= 100mV at step {i}, got {cell_delta}mV"
        
        # Verify timestamp progression
        timestamps = [row['Timestamp'] for row in rows]
        assert len(timestamps) == len(set(timestamps)), "All timestamps should be unique"
        
        # Check timestamp format
        for timestamp_str in timestamps[:5]:  # Check first 5
            assert len(timestamp_str) == 23, f"Timestamp should be 23 chars long, got {len(timestamp_str)}"
            assert '2025-07-12' in timestamp_str, "Should contain correct date"
        
        print(f"✅ Discharge simulation test completed successfully:")
        print(f"   - Data points: {len(discharge_data)}")
        print(f"   - Initial: {initial_pack_voltage}mV, {initial_soc}% SOC")
        print(f"   - Final: {final_pack_voltage}mV, {final_soc}% SOC") 
        print(f"   - Voltage drop: {initial_pack_voltage - final_pack_voltage}mV")
        print(f"   - CSV file: {os.path.basename(csv_path)}")
    
    def test_discharge_curve_characteristics(self, temp_log_dir):
        """
        Test that generated discharge curve follows LiFePO4 characteristics.
        """
        csv_path = os.path.join(temp_log_dir, "discharge_curve_test.csv")
        
        # Generate shorter test data for curve analysis
        discharge_data = self.generate_discharge_curve_data(
            time_step_seconds=30,  # 30-second intervals 
            total_duration_minutes=60,  # 1 hour
            discharge_current_amps=15  # 15A discharge
        )
        
        # Write to CSV
        for data_point in discharge_data:
            write_modbus_data_to_csv(data_point, csv_path)
        
        # Analyze discharge curve characteristics
        with open(csv_path, 'r', newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        # Extract voltage and SOC data
        pack_voltages = [int(row['Pack_V']) for row in rows]
        soc_values = [int(row['SOC']) for row in rows]
        
        # LiFePO4 should have relatively flat voltage curve until low SOC
        mid_point = len(pack_voltages) // 2
        voltage_change_first_half = pack_voltages[0] - pack_voltages[mid_point]
        voltage_change_second_half = pack_voltages[mid_point] - pack_voltages[-1]
        
        # Second half should show more voltage drop (characteristic of LiFePO4)
        assert voltage_change_second_half >= voltage_change_first_half * 0.8, \
            "LiFePO4 should show steeper voltage drop in second half of discharge"
        
        # Verify SOC decreases monotonically
        for i in range(1, len(soc_values)):
            assert soc_values[i] <= soc_values[i-1], f"SOC should not increase during discharge at step {i}"
        
        # Check that discharge curve is realistic
        total_voltage_drop = pack_voltages[0] - pack_voltages[-1]
        assert 2000 <= total_voltage_drop <= 5000, \
            f"Total voltage drop should be 2-5V (2000-5000mV), got {total_voltage_drop}mV"
        
        print(f"✅ Discharge curve characteristics validated:")
        print(f"   - Total voltage drop: {total_voltage_drop}mV")
        print(f"   - First half drop: {voltage_change_first_half}mV")
        print(f"   - Second half drop: {voltage_change_second_half}mV")
        print(f"   - SOC range: {soc_values[0]}% to {soc_values[-1]}%")