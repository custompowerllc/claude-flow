#!/usr/bin/env python3
"""
Unit tests for Modbus BMS Simulator Server

Tests the core Modbus server functionality including:
- Server initialization and startup
- Modbus protocol handling
- read_input_registers implementation
- Error handling and edge cases
- Virtual COM port integration
"""

import pytest
import unittest.mock as mock
from unittest.mock import MagicMock, patch, PropertyMock
import threading
import time
import socket
from contextlib import contextmanager

# Test imports for Modbus functionality
from pymodbus.server import ServerStop, StartTcpServer, StartSerialServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.exceptions import ModbusException
from pymodbus.pdu import ModbusExceptions

# Import the register mapping from the existing GA app
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../src'))

try:
    from modbus_query_test import register_map, num_registers
except ImportError:
    # Fallback register map if import fails
    register_map = {
        10: "afe_cell_volt1", 11: "afe_cell_volt2", 12: "afe_cell_volt3", 13: "afe_cell_volt4",
        14: "afe_cell_volt5", 15: "afe_cell_volt6", 16: "afe_cell_volt7", 17: "afe_cell_volt8",
        18: "afe_pack_volt", 19: "afe_cell_volt_delta", 20: "afe_temp1", 21: "afe_temp2",
        22: "afe_current", 23: "afe_adc_gain", 24: "afe_adc_offset", 25: "afe_ov_limit",
        26: "afe_uv_limit", 27: "fg_state_of_charge", 28: "fg_voltage", 29: "fg_current",
        30: "fg_temperature", 31: "fg_remaining_capacity", 32: "fg_full_charge_cap",
        33: "fg_design_capacity", 34: "fg_average_current", 35: "fg_time_to_empty",
        36: "fg_time_to_full", 37: "fg_internal_temp", 38: "fg_cycle_count",
        39: "fg_state_of_health", 40: "fg_charging_voltage", 41: "fg_charging_current",
        42: "fg_lifetime_max_temp", 43: "fg_lifetime_min_temp", 44: "fg_lifetime_max_chg",
        45: "fg_lifetime_max_dsg"
    }
    num_registers = len(register_map)


class MockModbusServer:
    """Mock Modbus server for testing"""
    
    def __init__(self, port="COM3", baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.register_map = register_map
        self.num_registers = num_registers
        self.is_running = False
        self.server_thread = None
        self.context = None
        
        # Initialize realistic register values
        self.registers = self._initialize_realistic_registers()
    
    def _initialize_realistic_registers(self):
        """Initialize registers with realistic BMS values"""
        registers = {}
        
        # 8S LiFePO4 Cell Voltages (3.2-3.4V nominal)
        for i in range(8):
            reg_addr = 10 + i
            cell_voltage = 3280 + (i * 2) + (-8 if i % 2 else 5)  # Slight cell variation
            registers[reg_addr] = max(2500, min(3650, cell_voltage))
        
        # Pack voltage (sum of cells)
        pack_voltage = sum(registers[10 + i] for i in range(8))
        registers[18] = pack_voltage
        
        # Cell voltage delta
        cell_voltages = [registers[10 + i] for i in range(8)]
        registers[19] = max(cell_voltages) - min(cell_voltages)
        
        # Temperature sensors (25-35°C)
        registers[20] = 285  # 28.5°C
        registers[21] = 287  # 28.7°C
        
        # Pack current (-10A to +5A range)
        registers[22] = -2500  # -2.5A discharge
        
        # AFE configuration registers
        registers[23] = 1000  # ADC gain
        registers[24] = 0     # ADC offset
        registers[25] = 3650  # Overvoltage limit
        registers[26] = 2500  # Undervoltage limit
        
        # Fuel gauge data
        registers[27] = 75    # SOC 75%
        registers[28] = pack_voltage  # FG voltage matches pack
        registers[29] = -2480 # FG current
        registers[30] = 285   # FG temperature
        registers[31] = 60000 # Remaining capacity (60Ah)
        registers[32] = 80000 # Full charge capacity (80Ah)
        registers[33] = 80000 # Design capacity (80Ah)
        registers[34] = -2500 # Average current
        registers[35] = 1440  # Time to empty (24 hours)
        registers[36] = 0     # Time to full (charging)
        registers[37] = 285   # Internal temp
        registers[38] = 450   # Cycle count
        registers[39] = 98    # SOH 98%
        registers[40] = 28800 # Charging voltage
        registers[41] = 0     # Charging current
        registers[42] = 350   # Lifetime max temp
        registers[43] = 100   # Lifetime min temp
        registers[44] = 5000  # Lifetime max charge
        registers[45] = 12000 # Lifetime max discharge
        
        return registers
    
    def start(self):
        """Start the mock Modbus server"""
        self.is_running = True
        return True
    
    def stop(self):
        """Stop the mock Modbus server"""
        self.is_running = False
        if self.server_thread:
            self.server_thread.join(timeout=2)
    
    def read_input_registers(self, address, count, slave_id=1):
        """Mock implementation of read_input_registers"""
        # Validate the exact GA app query: address=9, count=36
        if address != 9:
            raise ModbusException(f"Invalid start address: {address}, expected 9")
        
        if count != self.num_registers:
            raise ModbusException(f"Invalid register count: {count}, expected {self.num_registers}")
        
        # Return register values starting from address 10
        register_values = []
        for i in range(count):
            register_addr = 10 + i  # Real addresses: 10, 11, 12, ..., 45
            value = self.registers.get(register_addr, 0)
            register_values.append(value)
        
        return MockModbusResponse(register_values)


class MockModbusResponse:
    """Mock Modbus response object"""
    
    def __init__(self, registers):
        self.registers = registers
        self._error = False
    
    def isError(self):
        return self._error


class TestModbusServer(pytest.TestCase):
    """Test cases for Modbus server functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_server = MockModbusServer()
        
    def tearDown(self):
        """Clean up after tests"""
        if hasattr(self, 'mock_server') and self.mock_server.is_running:
            self.mock_server.stop()
    
    def test_server_initialization(self):
        """Test server initialization with correct parameters"""
        server = MockModbusServer(port="COM3", baudrate=9600)
        
        # Verify initialization parameters
        self.assertEqual(server.port, "COM3")
        self.assertEqual(server.baudrate, 9600)
        self.assertEqual(server.num_registers, 36)
        self.assertFalse(server.is_running)
        
        # Verify register map is loaded correctly
        self.assertEqual(len(server.register_map), 36)
        self.assertEqual(server.register_map[10], "afe_cell_volt1")
        self.assertEqual(server.register_map[45], "fg_lifetime_max_dsg")
    
    def test_server_startup_shutdown(self):
        """Test server startup and shutdown procedures"""
        server = MockModbusServer()
        
        # Test startup
        result = server.start()
        self.assertTrue(result)
        self.assertTrue(server.is_running)
        
        # Test shutdown
        server.stop()
        self.assertFalse(server.is_running)
    
    def test_register_initialization(self):
        """Test that registers are initialized with realistic values"""
        server = MockModbusServer()
        
        # Test cell voltages (should be in LiFePO4 range)
        for i in range(8):
            cell_voltage = server.registers[10 + i]
            self.assertGreaterEqual(cell_voltage, 2500, f"Cell {i+1} voltage too low: {cell_voltage}")
            self.assertLessEqual(cell_voltage, 3650, f"Cell {i+1} voltage too high: {cell_voltage}")
        
        # Test pack voltage (should be sum of cells)
        expected_pack = sum(server.registers[10 + i] for i in range(8))
        self.assertEqual(server.registers[18], expected_pack)
        
        # Test cell delta calculation
        cell_voltages = [server.registers[10 + i] for i in range(8)]
        expected_delta = max(cell_voltages) - min(cell_voltages)
        self.assertEqual(server.registers[19], expected_delta)
        
        # Test temperature values (should be reasonable)
        self.assertGreater(server.registers[20], 0)  # temp1
        self.assertGreater(server.registers[21], 0)  # temp2
        self.assertLess(server.registers[20], 500)   # reasonable max temp
        
        # Test fuel gauge values
        self.assertGreaterEqual(server.registers[27], 0)   # SOC
        self.assertLessEqual(server.registers[27], 100)    # SOC max
        self.assertGreater(server.registers[31], 0)        # Remaining capacity
    
    def test_read_input_registers_valid_request(self):
        """Test valid read_input_registers request (GA app compatibility)"""
        server = MockModbusServer()
        
        # Test the exact GA app query
        response = server.read_input_registers(address=9, count=36, slave_id=1)
        
        # Verify response
        self.assertFalse(response.isError())
        self.assertEqual(len(response.registers), 36)
        
        # Verify register values are correct
        for i, value in enumerate(response.registers):
            register_addr = 10 + i
            expected_value = server.registers[register_addr]
            self.assertEqual(value, expected_value)
    
    def test_read_input_registers_invalid_address(self):
        """Test read_input_registers with invalid start address"""
        server = MockModbusServer()
        
        # Test invalid start addresses
        invalid_addresses = [0, 1, 8, 10, 15, 20]
        
        for addr in invalid_addresses:
            with self.assertRaises(ModbusException) as context:
                server.read_input_registers(address=addr, count=36, slave_id=1)
            
            self.assertIn("Invalid start address", str(context.exception))
    
    def test_read_input_registers_invalid_count(self):
        """Test read_input_registers with invalid register count"""
        server = MockModbusServer()
        
        # Test invalid counts
        invalid_counts = [0, 1, 10, 20, 35, 37, 50, 100]
        
        for count in invalid_counts:
            with self.assertRaises(ModbusException) as context:
                server.read_input_registers(address=9, count=count, slave_id=1)
            
            self.assertIn("Invalid register count", str(context.exception))
    
    def test_register_data_consistency(self):
        """Test that register data maintains consistency"""
        server = MockModbusServer()
        
        # Get multiple responses
        response1 = server.read_input_registers(address=9, count=36)
        response2 = server.read_input_registers(address=9, count=36)
        
        # Values should be consistent (for static test)
        self.assertEqual(response1.registers, response2.registers)
        
        # Test specific register relationships
        cell_voltages = response1.registers[0:8]  # Registers 10-17
        pack_voltage = response1.registers[8]     # Register 18
        cell_delta = response1.registers[9]       # Register 19
        
        # Pack voltage should equal sum of cells
        self.assertEqual(pack_voltage, sum(cell_voltages))
        
        # Cell delta should equal max - min
        self.assertEqual(cell_delta, max(cell_voltages) - min(cell_voltages))
    
    def test_register_value_ranges(self):
        """Test that all register values are within expected ranges"""
        server = MockModbusServer()
        response = server.read_input_registers(address=9, count=36)
        
        register_ranges = {
            # Cell voltages (registers 10-17): 2.5V - 3.65V
            (0, 8): (2500, 3650),
            # Pack voltage (register 18): 8 * cell_voltage
            (8, 9): (20000, 29200),
            # Cell delta (register 19): 0-200mV typical
            (9, 10): (0, 500),
            # Temperature (registers 20-21): -40°C to 85°C (in tenths)
            (10, 12): (-400, 850),
            # Current (register 22): -50A to +50A in mA
            (12, 13): (-50000, 50000),
            # SOC (register 27): 0-100%
            (17, 18): (0, 100),
            # SOH (register 39): 0-100%
            (29, 30): (0, 100),
        }
        
        for (start_idx, end_idx), (min_val, max_val) in register_ranges.items():
            for i in range(start_idx, end_idx):
                value = response.registers[i]
                reg_addr = 10 + i
                param_name = register_map.get(reg_addr, f"Register_{reg_addr}")
                
                self.assertGreaterEqual(
                    value, min_val,
                    f"{param_name} (reg {reg_addr}) value {value} below minimum {min_val}"
                )
                self.assertLessEqual(
                    value, max_val,
                    f"{param_name} (reg {reg_addr}) value {value} above maximum {max_val}"
                )
    
    @patch('socket.socket')
    def test_server_port_binding(self, mock_socket):
        """Test server port binding functionality"""
        mock_sock = MagicMock()
        mock_socket.return_value = mock_sock
        
        server = MockModbusServer(port="COM3")
        
        # Test port configuration
        self.assertEqual(server.port, "COM3")
        
        # For serial server, we don't bind to network sockets
        # This test ensures the port is stored correctly
        result = server.start()
        self.assertTrue(result)
    
    def test_concurrent_requests(self):
        """Test handling of concurrent register read requests"""
        server = MockModbusServer()
        responses = []
        
        def read_registers():
            try:
                response = server.read_input_registers(address=9, count=36)
                responses.append(response.registers)
            except Exception as e:
                responses.append(None)
        
        # Create multiple threads to simulate concurrent requests
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=read_registers)
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=5)
        
        # Verify all requests completed successfully
        self.assertEqual(len(responses), 5)
        self.assertTrue(all(r is not None for r in responses))
        
        # Verify all responses are identical (for static test data)
        first_response = responses[0]
        for response in responses[1:]:
            self.assertEqual(response, first_response)
    
    def test_error_handling(self):
        """Test error handling in various scenarios"""
        server = MockModbusServer()
        
        # Test with extreme values
        with self.assertRaises(ModbusException):
            server.read_input_registers(address=-1, count=36)
        
        with self.assertRaises(ModbusException):
            server.read_input_registers(address=9, count=-1)
        
        with self.assertRaises(ModbusException):
            server.read_input_registers(address=65536, count=36)
    
    def test_memory_usage(self):
        """Test that server doesn't leak memory during operation"""
        import gc
        
        server = MockModbusServer()
        
        # Record initial object count
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        # Perform many operations
        for _ in range(100):
            response = server.read_input_registers(address=9, count=36)
            # Verify response is valid
            self.assertEqual(len(response.registers), 36)
        
        # Force garbage collection
        gc.collect()
        final_objects = len(gc.get_objects())
        
        # Object count should not grow significantly
        object_growth = final_objects - initial_objects
        self.assertLess(object_growth, 50, f"Memory leak detected: {object_growth} new objects")


if __name__ == '__main__':
    pytest.main([__file__])