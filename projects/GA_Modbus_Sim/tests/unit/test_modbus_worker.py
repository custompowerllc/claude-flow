"""
Unit tests for ModbusWorker functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.core.modbus_worker import ModbusWorker


class TestModbusWorker:
    """Test cases for the ModbusWorker class."""
    
    def test_modbus_worker_initialization(self):
        """Test that ModbusWorker initializes with correct default values."""
        worker = ModbusWorker()
        
        assert worker.running is False
        assert worker.port is None
        assert worker.baudrate == 9600
        assert worker.parity == 'E'
        assert worker.slave_id == 2
        assert worker.interval == 1.0
        assert worker.client is None
        assert len(worker.register_map) > 0
    
    def test_configure_modbus_parameters(self):
        """Test that configure() properly sets Modbus parameters."""
        worker = ModbusWorker()
        
        worker.configure(
            port="/dev/ttyUSB0",
            baudrate=19200,
            parity='N',
            slave_id=1,
            interval=0.5
        )
        
        assert worker.port == "/dev/ttyUSB0"
        assert worker.baudrate == 19200
        assert worker.parity == 'N'
        assert worker.slave_id == 1
        assert worker.interval == 0.5
    
    def test_configure_partial_parameters(self):
        """Test that configure() with partial parameters keeps defaults for others."""
        worker = ModbusWorker()
        original_baudrate = worker.baudrate
        original_parity = worker.parity
        
        worker.configure(port="/dev/ttyUSB0", slave_id=3)
        
        assert worker.port == "/dev/ttyUSB0"
        assert worker.slave_id == 3
        # Should keep original values for unspecified parameters
        assert worker.baudrate == original_baudrate
        assert worker.parity == original_parity
    
    def test_process_register_data_cell_voltages(self):
        """Test that _process_register_data correctly scales cell voltage values."""
        worker = ModbusWorker()
        
        # Mock register values (in mV)
        raw_values = [
            3456,  # afe_cell_volt1: 3456 mV -> 3.456 V
            3457,  # afe_cell_volt2: 3457 mV -> 3.457 V
            3455,  # afe_cell_volt3: 3455 mV -> 3.455 V
            # ... continue for other registers
        ] + [0] * 27  # Fill remaining 27 registers with zeros
        
        result = worker._process_register_data(raw_values)
        
        # Test that cell voltages are properly scaled from mV to V
        assert result['afe_cell_volt1'] == 3.456
        assert result['afe_cell_volt2'] == 3.457
        assert result['afe_cell_volt3'] == 3.455
    
    def test_process_register_data_pack_voltage(self):
        """Test that pack voltage is correctly scaled."""
        worker = ModbusWorker()
        
        # Create mock data with pack voltage at register 18 (index 8)
        raw_values = [0] * 8 + [27652] + [0] * 21  # 27652 mV -> 27.652 V
        
        result = worker._process_register_data(raw_values)
        
        assert result['afe_pack_volt'] == 27.652
    
    def test_process_register_data_current(self):
        """Test that current values are correctly scaled."""
        worker = ModbusWorker()
        
        # Create mock data with current at register 22 (index 12)
        raw_values = [0] * 12 + [2345] + [0] * 17  # 2345 mA -> 2.345 A
        
        result = worker._process_register_data(raw_values)
        
        assert result['afe_current'] == 2.345
    
    def test_process_register_data_temperature(self):
        """Test that temperature values are correctly scaled."""
        worker = ModbusWorker()
        
        # Create mock data with temperature at register 20 (index 10)
        raw_values = [0] * 10 + [255] + [0] * 19  # 255 -> 25.5 °C
        
        result = worker._process_register_data(raw_values)
        
        assert result['afe_temp1'] == 25.5
    
    def test_start_monitoring(self):
        """Test that start_monitoring sets running flag and starts thread."""
        worker = ModbusWorker()
        
        with patch.object(worker, 'start') as mock_start:
            worker.start_monitoring()
            
            assert worker.running is True
            mock_start.assert_called_once()
    
    def test_stop_monitoring_with_connected_client(self):
        """Test that stop_monitoring properly closes connected client."""
        worker = ModbusWorker()
        worker.running = True
        
        # Mock connected client
        mock_client = Mock()
        mock_client.connected = True
        worker.client = mock_client
        
        with patch.object(worker, 'wait') as mock_wait:
            worker.stop_monitoring()
            
            assert worker.running is False
            mock_client.close.assert_called_once()
            mock_wait.assert_called_once()
    
    def test_stop_monitoring_without_client(self):
        """Test that stop_monitoring works when no client is connected."""
        worker = ModbusWorker()
        worker.running = True
        worker.client = None
        
        with patch.object(worker, 'wait') as mock_wait:
            worker.stop_monitoring()
            
            assert worker.running is False
            mock_wait.assert_called_once()
    
    @patch('src.core.modbus_worker.ModbusSerialClient')
    def test_run_successful_connection(self, mock_client_class):
        """Test successful Modbus connection and data reading."""
        worker = ModbusWorker()
        worker.port = "/dev/ttyUSB0"
        worker.running = True
        
        # Mock client instance
        mock_client = Mock()
        mock_client.connect.return_value = True
        mock_client.connected = True
        mock_client_class.return_value = mock_client
        
        # Mock successful register reading
        mock_response = Mock()
        mock_response.isError.return_value = False
        mock_response.registers = [3456, 3457] + [0] * 28  # Mock register values
        mock_client.read_input_registers.return_value = mock_response
        
        # Mock signals
        worker.statusChanged = Mock()
        worker.dataReceived = Mock()
        worker.errorOccurred = Mock()
        
        # Stop after first iteration
        def stop_after_first():
            worker.running = False
        worker.msleep = Mock(side_effect=stop_after_first)
        
        worker.run()
        
        # Verify connection attempt
        mock_client.connect.assert_called_once()
        worker.statusChanged.emit.assert_called_with("Connected")
        
        # Verify data reading
        mock_client.read_input_registers.assert_called_with(
            address=9, count=30, slave=worker.slave_id
        )
        
        # Verify data was emitted
        worker.dataReceived.emit.assert_called_once()
        args = worker.dataReceived.emit.call_args[0]
        data = args[0]
        assert 'timestamp' in data
        assert isinstance(data['timestamp'], datetime)
    
    @patch('src.core.modbus_worker.ModbusSerialClient')
    def test_run_connection_failure(self, mock_client_class):
        """Test handling of connection failure."""
        worker = ModbusWorker()
        worker.port = "/dev/ttyUSB0"
        worker.running = True
        
        # Mock client that fails to connect
        mock_client = Mock()
        mock_client.connect.return_value = False
        mock_client_class.return_value = mock_client
        
        # Mock signals
        worker.errorOccurred = Mock()
        
        worker.run()
        
        # Verify error was emitted
        worker.errorOccurred.emit.assert_called_with("Failed to connect to /dev/ttyUSB0")


class TestCellDeltaSpikeFilter:
    """Test cases for the cell delta spike detection filter."""
    
    def test_filter_initialization(self):
        """Test that filter is properly initialized."""
        worker = ModbusWorker()
        
        assert worker.cell_delta_history == []
        assert worker.cell_delta_window == 5
        assert worker.filter_enabled is True
    
    def test_filter_disabled_returns_original_value(self):
        """Test that when filter is disabled, original value is returned."""
        worker = ModbusWorker()
        worker.filter_enabled = False
        
        result = worker.filter_cell_delta(99)
        assert result == 99
        
        # History should remain empty when disabled
        assert worker.cell_delta_history == []
    
    def test_filter_insufficient_data_returns_original(self):
        """Test that with less than 3 values, original value is returned."""
        worker = ModbusWorker()
        
        # First value
        result1 = worker.filter_cell_delta(7)
        assert result1 == 7
        assert len(worker.cell_delta_history) == 1
        
        # Second value
        result2 = worker.filter_cell_delta(8)
        assert result2 == 8
        assert len(worker.cell_delta_history) == 2
    
    def test_filter_normal_values_no_filtering(self):
        """Test that normal values are not filtered."""
        worker = ModbusWorker()
        
        # Build up normal sequence
        normal_values = [7, 8, 9, 10, 11]
        results = []
        
        for value in normal_values:
            result = worker.filter_cell_delta(value)
            results.append(result)
        
        # All values should pass through unchanged
        assert results == normal_values
        assert worker.cell_delta_history == normal_values
    
    def test_filter_detects_and_removes_spike(self):
        """Test the main spike detection functionality."""
        worker = ModbusWorker()
        
        # Build baseline with normal values
        worker.filter_cell_delta(7)  # value 7
        worker.filter_cell_delta(8)  # value 8
        worker.filter_cell_delta(9)  # value 9, avg so far = 7.5
        
        # Now inject a spike - should be filtered
        # Spike value 99 vs average of [7,8,9] = 8.0
        # 99 - 8 = 91, which is > 8 * 2 = 16, so it's a spike
        result = worker.filter_cell_delta(99)
        
        # Should return average of previous values (7,8,9) = 8
        assert result == 8
        
        # History should contain the filtered value, not the spike
        assert worker.cell_delta_history == [7, 8, 9, 8]
    
    def test_filter_spike_recovery(self):
        """Test that normal values work after spike is filtered."""
        worker = ModbusWorker()
        
        # Build baseline
        worker.filter_cell_delta(7)
        worker.filter_cell_delta(8)
        worker.filter_cell_delta(9)
        
        # Inject spike
        worker.filter_cell_delta(99)  # Should be filtered to ~8
        
        # Next normal value should pass through
        result = worker.filter_cell_delta(10)
        assert result == 10
        
        # History should be [8, 9, 8, 10] (spike replaced with 8)
        assert worker.cell_delta_history == [8, 9, 8, 10]
    
    def test_filter_window_size_management(self):
        """Test that history window is properly maintained."""
        worker = ModbusWorker()
        worker.cell_delta_window = 3  # Small window for testing
        
        # Add more values than window size
        values = [5, 6, 7, 8, 9, 10]
        for value in values:
            worker.filter_cell_delta(value)
        
        # History should only contain last 3 values
        assert len(worker.cell_delta_history) == 3
        assert worker.cell_delta_history == [8, 9, 10]
    
    def test_filter_edge_case_zero_average(self):
        """Test behavior when average is zero or negative."""
        worker = ModbusWorker()
        
        # Build sequence with zeros
        worker.filter_cell_delta(0)
        worker.filter_cell_delta(0)
        worker.filter_cell_delta(0)
        
        # Large value should pass through when avg is 0
        result = worker.filter_cell_delta(100)
        assert result == 100  # Should not filter when avg <= 0
    
    def test_filter_negative_values(self):
        """Test filter behavior with negative values."""
        worker = ModbusWorker()
        
        # Build baseline with negative values
        worker.filter_cell_delta(-5)
        worker.filter_cell_delta(-6)
        worker.filter_cell_delta(-4)
        
        # Average is -5, spike would be something like -50
        # abs(-50 - (-5)) = 45, vs abs(-5) * 2 = 10
        result = worker.filter_cell_delta(-50)
        assert result == -5  # Should filter to average
    
    def test_filter_realistic_spike_scenario(self):
        """Test the specific scenario from the GitHub issue."""
        worker = ModbusWorker()
        
        # Scenario: 7mV → 8mV → 99mV → 22mV → 21mV
        sequence = [7, 8, 99, 22, 21]
        expected = [7, 8, 7, 22, 21]  # 99 should become ~7
        results = []
        
        for value in sequence:
            result = worker.filter_cell_delta(value)
            results.append(result)
        
        assert results == expected
    
    def test_filter_multiple_consecutive_spikes(self):
        """Test behavior with multiple consecutive spikes."""
        worker = ModbusWorker()
        
        # Build baseline
        worker.filter_cell_delta(10)
        worker.filter_cell_delta(11)
        worker.filter_cell_delta(12)
        
        # Multiple spikes
        result1 = worker.filter_cell_delta(100)  # Spike 1
        result2 = worker.filter_cell_delta(95)   # Spike 2
        result3 = worker.filter_cell_delta(13)   # Normal value
        
        # Both spikes should be filtered
        assert result1 == 11  # Average of [10,11,12]
        assert result2 == 11  # Average of [11,12,11]
        assert result3 == 13  # Normal value passes through
    
    def test_filter_configuration(self):
        """Test filter configuration options."""
        worker = ModbusWorker()
        
        # Test changing window size
        worker.cell_delta_window = 7
        assert worker.cell_delta_window == 7
        
        # Test enabling/disabling
        worker.filter_enabled = False
        assert worker.filter_enabled is False
        
        worker.filter_enabled = True
        assert worker.filter_enabled is True
    
    def test_filter_integration_with_data_processing(self):
        """Test that filter integrates properly with data processing."""
        worker = ModbusWorker()
        
        # Mock data with cell_delta
        test_data = {
            'cell_delta': 99,  # This should be filtered
            'pack_voltage': 25.6,
            'cell_volt1': 3.2
        }
        
        # Build some history first
        worker.filter_cell_delta(7)
        worker.filter_cell_delta(8)
        worker.filter_cell_delta(9)
        
        # Simulate the filtering that happens in run()
        if worker.filter_enabled and 'cell_delta' in test_data:
            test_data['cell_delta'] = worker.filter_cell_delta(test_data['cell_delta'])
        
        # Spike should be filtered
        assert test_data['cell_delta'] == 8  # Average of [7,8,9]
        
        # Other data should be unchanged
        assert test_data['pack_voltage'] == 25.6
        assert test_data['cell_volt1'] == 3.2
    
    def test_filter_high_baseline_spike(self):
        """Test spike detection when baseline is already high (22mV -> 99mV)."""
        worker = ModbusWorker()
        
        # Build baseline at higher level (around 22mV)
        values = [20, 21, 22, 23, 22]
        for value in values:
            worker.filter_cell_delta(value)
        
        # Now test spike from 22mV baseline to 99mV
        # Average should be around 21.5, so 99 is > 2x average
        result = worker.filter_cell_delta(99)
        
        # Should filter to average of recent values
        assert result == 21  # Average of [21,22,23,22] ≈ 22
        
        # Verify history was updated with filtered value
        assert worker.cell_delta_history[-1] == 21
    
    def test_filter_gradual_increase_vs_spike(self):
        """Test that gradual increases are not filtered as spikes."""
        worker = ModbusWorker()
        
        # Gradual increase from 7mV to 30mV
        gradual_sequence = [7, 9, 12, 15, 18, 22, 26, 30]
        results = []
        
        for value in gradual_sequence:
            result = worker.filter_cell_delta(value)
            results.append(result)
        
        # All gradual increases should pass through
        assert results == gradual_sequence
        
        # Now test a real spike after gradual increase
        spike_result = worker.filter_cell_delta(99)
        
        # This should be filtered as it's a spike relative to ~26mV average
        assert spike_result < 99  # Should be filtered
        assert spike_result <= 30  # Should be around recent average
    
    def test_filter_spike_threshold_boundary(self):
        """Test behavior at the exact 2x threshold boundary."""
        worker = ModbusWorker()
        
        # Build stable baseline at 20mV
        for _ in range(5):
            worker.filter_cell_delta(20)
        
        # The spike threshold is when difference > 2x average
        # For avg=20, spike is when: abs(value - 20) > 40
        # So value > 60 or value < -20
        
        # Test value at exactly the threshold (60mV)
        result_60 = worker.filter_cell_delta(60)
        assert result_60 == 60  # Should pass through (difference = 40 = 2x)
        
        # Reset for next test
        worker.cell_delta_history = []
        for _ in range(5):
            worker.filter_cell_delta(20)
        
        # Test value just above threshold (61mV)
        result_above = worker.filter_cell_delta(61)
        assert result_above == 20  # Should be filtered (difference = 41 > 40)
    
    def test_filter_recovery_after_high_baseline_spike(self):
        """Test recovery after filtering a spike from high baseline."""
        worker = ModbusWorker()
        
        # High baseline scenario
        baseline = [22, 23, 24, 22, 23]
        for value in baseline:
            worker.filter_cell_delta(value)
        
        # Spike
        worker.filter_cell_delta(99)  # Will be filtered
        
        # Recovery - should accept values near the baseline
        recovery_values = [25, 24, 23]
        results = []
        
        for value in recovery_values:
            result = worker.filter_cell_delta(value)
            results.append(result)
        
        # All recovery values should pass through
        assert results == recovery_values
    
    def test_filter_input_validation(self):
        """Test input validation for non-numeric values."""
        worker = ModbusWorker()
        
        # Test invalid inputs
        assert worker.filter_cell_delta(None) is None
        assert worker.filter_cell_delta("invalid") == "invalid"
        assert worker.filter_cell_delta([1, 2, 3]) == [1, 2, 3]
        
        # Test valid inputs still work
        assert worker.filter_cell_delta(7) == 7
        assert worker.filter_cell_delta(7.5) == 7.5
    
    def test_filter_empty_history_edge_case(self):
        """Test edge case where history might be unexpectedly empty."""
        worker = ModbusWorker()
        
        # Manually create edge case scenario
        worker.cell_delta_history = []
        
        # Should handle gracefully
        result = worker.filter_cell_delta(10)
        assert result == 10
        assert len(worker.cell_delta_history) == 1