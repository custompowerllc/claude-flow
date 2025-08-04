#!/usr/bin/env python3
"""
Integration tests for Modbus BMS Simulator

Tests end-to-end functionality with mock clients:
- Complete Modbus server + client interaction
- GA Modbus Python App compatibility
- CSV data output validation
- Real-world scenario testing
- Performance and reliability testing
"""

import pytest
import unittest.mock as mock
from unittest.mock import MagicMock, patch
import threading
import time
import csv
import os
import tempfile
from datetime import datetime
import socket
from contextlib import contextmanager

# Test imports for Modbus functionality
try:
    from pymodbus.client import ModbusSerialClient, ModbusTcpClient
    from pymodbus.server import StartTcpServer, ServerStop
    from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
    from pymodbus.datastore import ModbusSequentialDataBlock
    from pymodbus.device import ModbusDeviceIdentification
    PYMODBUS_AVAILABLE = True
except ImportError:
    PYMODBUS_AVAILABLE = False

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


class MockModbusBMSSimulator:
    """Mock BMS Simulator for integration testing"""
    
    def __init__(self, port=5020):
        self.port = port
        self.register_map = register_map
        self.num_registers = num_registers
        self.is_running = False
        self.server_thread = None
        self.server_context = None
        
        # Initialize realistic BMS data
        self.bms_data = self._initialize_bms_data()
        
    def _initialize_bms_data(self):
        """Initialize BMS data with realistic values"""
        data = {}
        
        # 8S LiFePO4 Cell Voltages (3200-3400mV)
        cell_voltages = [3285, 3287, 3283, 3289, 3281, 3286, 3284, 3288]
        for i, voltage in enumerate(cell_voltages):
            data[10 + i] = voltage
        
        # Pack voltage (sum of cells)
        data[18] = sum(cell_voltages)
        
        # Cell voltage delta
        data[19] = max(cell_voltages) - min(cell_voltages)
        
        # Temperature sensors (28.5°C, 28.7°C)
        data[20] = 285
        data[21] = 287
        
        # Pack current (-2.5A discharge)
        data[22] = -2500
        
        # AFE configuration
        data[23] = 1000  # ADC gain
        data[24] = 0     # ADC offset
        data[25] = 3650  # OV limit
        data[26] = 2500  # UV limit
        
        # Fuel gauge data
        data[27] = 75     # SOC 75%
        data[28] = data[18]  # FG voltage matches pack
        data[29] = -2480  # FG current
        data[30] = 285    # FG temperature
        data[31] = 60000  # Remaining capacity (60Ah)
        data[32] = 80000  # Full charge capacity (80Ah)
        data[33] = 80000  # Design capacity (80Ah)
        data[34] = -2500  # Average current
        data[35] = 1440   # Time to empty (24h)
        data[36] = 0      # Time to full
        data[37] = 285    # Internal temp
        data[38] = 450    # Cycle count
        data[39] = 98     # SOH 98%
        data[40] = data[18]  # Charging voltage
        data[41] = 0      # Charging current
        data[42] = 350    # Lifetime max temp
        data[43] = 100    # Lifetime min temp
        data[44] = 5000   # Lifetime max charge
        data[45] = 12000  # Lifetime max discharge
        
        return data
    
    def start_server(self):
        """Start the mock Modbus server"""
        if not PYMODBUS_AVAILABLE:
            self.is_running = True
            return True
        
        try:
            # Create data store with BMS data
            store = ModbusSlaveContext(
                ir=ModbusSequentialDataBlock(0, [0] * 100),  # Input registers
                hr=ModbusSequentialDataBlock(0, [0] * 100),  # Holding registers
                co=ModbusSequentialDataBlock(0, [0] * 100),  # Coils
                di=ModbusSequentialDataBlock(0, [0] * 100)   # Discrete inputs
            )
            
            # Populate input registers with BMS data
            for addr, value in self.bms_data.items():
                # Store at address-1 because pymodbus uses 0-based indexing
                store.setValues(3, addr-1, [value])  # Function code 3 = input registers
            
            self.server_context = ModbusServerContext(slaves=store, single=True)
            
            # Start server in background thread
            def run_server():
                StartTcpServer(
                    context=self.server_context,
                    identity=ModbusDeviceIdentification(),
                    address=("localhost", self.port)
                )
            
            self.server_thread = threading.Thread(target=run_server, daemon=True)
            self.server_thread.start()
            
            # Give server time to start
            time.sleep(0.5)
            self.is_running = True
            return True
            
        except Exception as e:
            print(f"Failed to start server: {e}")
            return False
    
    def stop_server(self):
        """Stop the mock Modbus server"""
        if self.is_running:
            try:
                ServerStop()
                if self.server_thread:
                    self.server_thread.join(timeout=2)
            except Exception:
                pass
            finally:
                self.is_running = False
    
    def update_bms_data(self, updates):
        """Update BMS data registers"""
        self.bms_data.update(updates)
        
        if PYMODBUS_AVAILABLE and self.server_context:
            for addr, value in updates.items():
                self.server_context[0].setValues(3, addr-1, [value])
    
    def get_register_value(self, addr):
        """Get current register value"""
        return self.bms_data.get(addr, 0)


class MockModbusClient:
    """Mock Modbus client that simulates GA app behavior"""
    
    def __init__(self, host="localhost", port=5020):
        self.host = host
        self.port = port
        self.client = None
        self.connected = False
        
    def connect(self):
        """Connect to Modbus server"""
        if not PYMODBUS_AVAILABLE:
            self.connected = True
            return True
        
        try:
            self.client = ModbusTcpClient(self.host, port=self.port)
            self.connected = self.client.connect()
            return self.connected
        except Exception:
            return False
    
    def disconnect(self):
        """Disconnect from Modbus server"""
        if self.client:
            self.client.close()
        self.connected = False
    
    def read_bms_registers(self, slave_id=1):
        """Read BMS registers using GA app protocol"""
        if not self.connected:
            return None
        
        if not PYMODBUS_AVAILABLE:
            # Return mock data for testing without pymodbus
            mock_data = {}
            for i, reg_addr in enumerate(range(10, 46)):
                param_name = register_map.get(reg_addr, f"Unknown_{reg_addr}")
                mock_data[param_name] = 3000 + i  # Mock values
            return mock_data
        
        try:
            # Use exact GA app protocol: address=9, count=36
            response = self.client.read_input_registers(
                address=9,
                count=num_registers,
                slave=slave_id
            )
            
            if response.isError():
                return None
            
            # Map register values to parameter names
            mapped_data = {}
            for i, value in enumerate(response.registers):
                register_address = 10 + i
                parameter_name = register_map.get(register_address, f"Unknown Register {register_address}")
                mapped_data[parameter_name] = value
            
            return mapped_data
            
        except Exception as e:
            print(f"Error reading registers: {e}")
            return None


class GAModbusDataLogger:
    """Mock GA Modbus data logger for testing"""
    
    def __init__(self, client):
        self.client = client
        self.csv_file = None
        self.csv_writer = None
        
    def start_logging(self, csv_filename, interval=0.5):
        """Start logging BMS data to CSV"""
        self.csv_file = open(csv_filename, 'w', newline='')
        self.csv_writer = csv.writer(self.csv_file)
        
        # Write header (exact GA app format)
        header = ['Timestamp'] + list(register_map.values())
        self.csv_writer.writerow(header)
        
        return True
    
    def log_data_point(self):
        """Log a single data point"""
        if not self.csv_writer:
            return False
        
        # Read BMS data
        bms_data = self.client.read_bms_registers()
        if not bms_data:
            return False
        
        # Write CSV row (exact GA app format)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row_data = [timestamp]
        
        for reg_addr in range(10, 46):
            param_name = register_map.get(reg_addr, '')
            value = bms_data.get(param_name, '')
            row_data.append(value)
        
        self.csv_writer.writerow(row_data)
        self.csv_file.flush()
        return True
    
    def stop_logging(self):
        """Stop logging and close file"""
        if self.csv_file:
            self.csv_file.close()
            self.csv_file = None
            self.csv_writer = None


class TestModbusIntegration(pytest.TestCase):
    """Integration tests for Modbus BMS Simulator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.simulator = MockModbusBMSSimulator(port=5021)
        self.client = MockModbusClient(port=5021)
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up after tests"""
        if hasattr(self, 'client'):
            self.client.disconnect()
        if hasattr(self, 'simulator'):
            self.simulator.stop_server()
        
        # Cleanup temp files
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except Exception:
            pass
    
    def test_server_client_connection(self):
        """Test basic server-client connection"""
        # Start simulator
        success = self.simulator.start_server()
        self.assertTrue(success)
        self.assertTrue(self.simulator.is_running)
        
        # Connect client
        connected = self.client.connect()
        self.assertTrue(connected)
        self.assertTrue(self.client.connected)
    
    def test_ga_app_compatibility(self):
        """Test compatibility with GA Modbus Python App protocol"""
        # Start simulator
        self.simulator.start_server()
        
        # Connect client
        self.client.connect()
        
        # Read BMS registers using GA app protocol
        bms_data = self.client.read_bms_registers()
        self.assertIsNotNone(bms_data)
        
        # Verify all expected parameters are present
        expected_params = list(register_map.values())
        for param in expected_params:
            self.assertIn(param, bms_data, f"Missing parameter: {param}")
        
        # Verify data types and ranges
        self.assertIsInstance(bms_data['afe_cell_volt1'], int)
        self.assertGreater(bms_data['afe_cell_volt1'], 2500)
        self.assertLess(bms_data['afe_cell_volt1'], 3650)
        
        # Verify pack voltage consistency
        cell_voltages = [
            bms_data['afe_cell_volt1'], bms_data['afe_cell_volt2'],
            bms_data['afe_cell_volt3'], bms_data['afe_cell_volt4'],
            bms_data['afe_cell_volt5'], bms_data['afe_cell_volt6'],
            bms_data['afe_cell_volt7'], bms_data['afe_cell_volt8']
        ]
        expected_pack = sum(cell_voltages)
        self.assertEqual(bms_data['afe_pack_volt'], expected_pack)
    
    def test_csv_data_logging(self):
        """Test CSV data logging functionality"""
        # Start simulator and connect client
        self.simulator.start_server()
        self.client.connect()
        
        # Create CSV logger
        csv_filename = os.path.join(self.temp_dir, "test_bms_data.csv")
        logger = GAModbusDataLogger(self.client)
        
        # Start logging
        success = logger.start_logging(csv_filename)
        self.assertTrue(success)
        
        # Log several data points
        for _ in range(5):
            success = logger.log_data_point()
            self.assertTrue(success)
            time.sleep(0.1)
        
        # Stop logging
        logger.stop_logging()
        
        # Verify CSV file was created and has correct format
        self.assertTrue(os.path.exists(csv_filename))
        
        with open(csv_filename, 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        # Verify header row
        expected_header = ['Timestamp'] + list(register_map.values())
        self.assertEqual(rows[0], expected_header)
        
        # Verify data rows
        self.assertEqual(len(rows), 6)  # Header + 5 data rows
        
        for i in range(1, 6):  # Skip header
            row = rows[i]
            self.assertEqual(len(row), len(expected_header))
            
            # Verify timestamp format
            timestamp = row[0]
            self.assertRegex(timestamp, r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}')
            
            # Verify data values are numeric
            for j in range(1, len(row)):
                if row[j]:  # Skip empty values
                    self.assertTrue(row[j].isdigit() or row[j].lstrip('-').isdigit())
    
    def test_real_time_data_updates(self):
        """Test real-time data updates and consistency"""
        # Start simulator and connect client
        self.simulator.start_server()
        self.client.connect()
        
        # Read initial data
        initial_data = self.client.read_bms_registers()
        self.assertIsNotNone(initial_data)
        initial_soc = initial_data['fg_state_of_charge']
        
        # Update SOC in simulator
        self.simulator.update_bms_data({27: 85})  # Update SOC to 85%
        
        # Read updated data
        time.sleep(0.1)
        updated_data = self.client.read_bms_registers()
        self.assertIsNotNone(updated_data)
        updated_soc = updated_data['fg_state_of_charge']
        
        # Verify update was reflected
        self.assertNotEqual(initial_soc, updated_soc)
        self.assertEqual(updated_soc, 85)
    
    def test_multiple_client_connections(self):
        """Test multiple simultaneous client connections"""
        # Start simulator
        self.simulator.start_server()
        
        # Create multiple clients
        clients = []
        for i in range(3):
            client = MockModbusClient(port=5021)
            connected = client.connect()
            self.assertTrue(connected)
            clients.append(client)
        
        # Each client should be able to read data
        for i, client in enumerate(clients):
            bms_data = client.read_bms_registers()
            self.assertIsNotNone(bms_data, f"Client {i} failed to read data")
            
            # Verify data consistency across clients
            self.assertIn('afe_cell_volt1', bms_data)
            self.assertGreater(bms_data['afe_cell_volt1'], 2500)
        
        # Cleanup clients
        for client in clients:
            client.disconnect()
    
    def test_error_handling(self):
        """Test error handling in various scenarios"""
        # Test connection without server
        client = MockModbusClient(port=9999)  # Non-existent server
        connected = client.connect()
        
        if PYMODBUS_AVAILABLE:
            self.assertFalse(connected)
        else:
            # Mock client always connects in test mode
            self.assertTrue(connected)
        
        # Test reading from disconnected client
        if not connected:
            bms_data = client.read_bms_registers()
            self.assertIsNone(bms_data)
    
    def test_performance_stress(self):
        """Test performance under stress conditions"""
        # Start simulator
        self.simulator.start_server()
        self.client.connect()
        
        # Perform many rapid reads
        start_time = time.time()
        successful_reads = 0
        
        for _ in range(100):
            bms_data = self.client.read_bms_registers()
            if bms_data:
                successful_reads += 1
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Verify performance
        self.assertGreater(successful_reads, 90)  # At least 90% success rate
        self.assertLess(duration, 10.0)  # Complete within 10 seconds
        
        reads_per_second = successful_reads / duration
        self.assertGreater(reads_per_second, 10)  # At least 10 reads/second
    
    def test_data_consistency_over_time(self):
        """Test data consistency over extended period"""
        # Start simulator
        self.simulator.start_server()
        self.client.connect()
        
        # Read data multiple times and verify consistency
        readings = []
        for _ in range(10):
            bms_data = self.client.read_bms_registers()
            self.assertIsNotNone(bms_data)
            readings.append(bms_data)
            time.sleep(0.1)
        
        # Verify pack voltage consistency (should be same for static test)
        pack_voltages = [reading['afe_pack_volt'] for reading in readings]
        self.assertTrue(all(v == pack_voltages[0] for v in pack_voltages))
        
        # Verify cell delta consistency
        cell_deltas = [reading['afe_cell_volt_delta'] for reading in readings]
        self.assertTrue(all(delta >= 0 for delta in cell_deltas))
    
    def test_scenario_simulation(self):
        """Test different battery scenarios"""
        # Start simulator
        self.simulator.start_server()
        self.client.connect()
        
        # Test normal operation
        normal_data = self.client.read_bms_registers()
        self.assertIsNotNone(normal_data)
        normal_current = normal_data['afe_current']
        
        # Test charging scenario (positive current)
        self.simulator.update_bms_data({22: 5000})  # +5A charging
        time.sleep(0.1)
        
        charging_data = self.client.read_bms_registers()
        self.assertEqual(charging_data['afe_current'], 5000)
        
        # Test discharging scenario (negative current)
        self.simulator.update_bms_data({22: -10000})  # -10A discharging
        time.sleep(0.1)
        
        discharging_data = self.client.read_bms_registers()
        self.assertEqual(discharging_data['afe_current'], -10000)
    
    def test_register_boundary_conditions(self):
        """Test register values at boundary conditions"""
        # Start simulator
        self.simulator.start_server()
        self.client.connect()
        
        # Test minimum values
        min_updates = {
            10: 2500,  # Min cell voltage
            27: 0,     # Min SOC
            39: 50     # Min practical SOH
        }
        self.simulator.update_bms_data(min_updates)
        time.sleep(0.1)
        
        min_data = self.client.read_bms_registers()
        self.assertEqual(min_data['afe_cell_volt1'], 2500)
        self.assertEqual(min_data['fg_state_of_charge'], 0)
        self.assertEqual(min_data['fg_state_of_health'], 50)
        
        # Test maximum values
        max_updates = {
            10: 3650,  # Max cell voltage
            27: 100,   # Max SOC
            39: 100    # Max SOH
        }
        self.simulator.update_bms_data(max_updates)
        time.sleep(0.1)
        
        max_data = self.client.read_bms_registers()
        self.assertEqual(max_data['afe_cell_volt1'], 3650)
        self.assertEqual(max_data['fg_state_of_charge'], 100)
        self.assertEqual(max_data['fg_state_of_health'], 100)
    
    def test_memory_usage(self):
        """Test memory usage during extended operation"""
        import gc
        
        # Start simulator
        self.simulator.start_server()
        self.client.connect()
        
        # Record initial memory
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        # Perform many operations
        for _ in range(500):
            bms_data = self.client.read_bms_registers()
            self.assertIsNotNone(bms_data)
        
        # Check memory usage
        gc.collect()
        final_objects = len(gc.get_objects())
        object_growth = final_objects - initial_objects
        
        # Memory growth should be minimal
        self.assertLess(object_growth, 100, f"Memory leak detected: {object_growth} new objects")


@contextmanager
def modbus_test_environment():
    """Context manager for Modbus test environment"""
    simulator = MockModbusBMSSimulator(port=5022)
    client = MockModbusClient(port=5022)
    
    try:
        simulator.start_server()
        client.connect()
        yield simulator, client
    finally:
        client.disconnect()
        simulator.stop_server()


class TestModbusEndToEnd(pytest.TestCase):
    """End-to-end integration tests"""
    
    def test_complete_workflow(self):
        """Test complete workflow from server start to data logging"""
        with modbus_test_environment() as (simulator, client):
            # Verify connection
            self.assertTrue(simulator.is_running)
            self.assertTrue(client.connected)
            
            # Read and verify data
            bms_data = client.read_bms_registers()
            self.assertIsNotNone(bms_data)
            self.assertEqual(len(bms_data), 36)
            
            # Test CSV logging
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
                csv_file = f.name
            
            try:
                logger = GAModbusDataLogger(client)
                logger.start_logging(csv_file)
                
                for _ in range(3):
                    logger.log_data_point()
                    time.sleep(0.1)
                
                logger.stop_logging()
                
                # Verify CSV content
                with open(csv_file, 'r') as f:
                    lines = f.readlines()
                    self.assertEqual(len(lines), 4)  # Header + 3 data lines
                    
            finally:
                os.unlink(csv_file)
    
    def test_concurrent_operations(self):
        """Test concurrent server operations"""
        def client_worker(results, client_id):
            try:
                client = MockModbusClient(port=5023)
                client.connect()
                
                for _ in range(10):
                    data = client.read_bms_registers()
                    if data:
                        results[client_id] = results.get(client_id, 0) + 1
                    time.sleep(0.05)
                
                client.disconnect()
            except Exception as e:
                results[f"error_{client_id}"] = str(e)
        
        simulator = MockModbusBMSSimulator(port=5023)
        simulator.start_server()
        
        try:
            # Run multiple clients concurrently
            results = {}
            threads = []
            
            for i in range(5):
                thread = threading.Thread(target=client_worker, args=(results, i))
                threads.append(thread)
                thread.start()
            
            # Wait for all threads
            for thread in threads:
                thread.join(timeout=10)
            
            # Verify results
            for i in range(5):
                self.assertIn(i, results)
                self.assertGreater(results[i], 5)  # At least 5 successful reads
                
        finally:
            simulator.stop_server()


if __name__ == '__main__':
    pytest.main([__file__])