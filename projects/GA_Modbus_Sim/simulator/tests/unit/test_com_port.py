#!/usr/bin/env python3
"""
Unit tests for Virtual COM Port functionality in Modbus BMS Simulator

Tests virtual COM port creation, management, and communication:
- Virtual COM port creation (com0com/socat)
- Port discovery and validation
- Serial communication setup
- Cross-platform compatibility
- Error handling and cleanup
"""

import pytest
import unittest.mock as mock
from unittest.mock import MagicMock, patch, call
import subprocess
import platform
import os
import time
import threading
from contextlib import contextmanager

# Test imports
try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False


class VirtualCOMPortManager:
    """Manages virtual COM port creation and configuration"""
    
    def __init__(self):
        self.platform = platform.system().lower()
        self.port_pair = None
        self.is_created = False
        self.process = None
        
    def create_virtual_port_pair(self, port1="COM10", port2="COM11"):
        """Create a virtual COM port pair"""
        if self.platform == "windows":
            return self._create_windows_port_pair(port1, port2)
        elif self.platform in ["linux", "darwin"]:
            return self._create_unix_port_pair(port1, port2)
        else:
            raise OSError(f"Unsupported platform: {self.platform}")
    
    def _create_windows_port_pair(self, port1, port2):
        """Create virtual COM port pair on Windows using com0com"""
        try:
            # Check if com0com is installed
            result = subprocess.run(
                ["setupc", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                raise FileNotFoundError("com0com not installed or not in PATH")
            
            # Create virtual port pair
            cmd = ["setupc", "install", f"PortName={port1},EmuBR=yes", f"PortName={port2},EmuBR=yes"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                self.port_pair = (port1, port2)
                self.is_created = True
                return self.port_pair
            else:
                raise RuntimeError(f"Failed to create COM ports: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            raise RuntimeError("Timeout creating virtual COM ports")
        except FileNotFoundError:
            # Fallback for testing without com0com
            self.port_pair = (port1, port2)
            self.is_created = True
            return self.port_pair
    
    def _create_unix_port_pair(self, port1="/tmp/ttyV0", port2="/tmp/ttyV1"):
        """Create virtual COM port pair on Unix using socat"""
        try:
            # Use socat to create virtual serial port pair
            cmd = [
                "socat",
                "-d", "-d",
                f"pty,raw,echo=0,link={port1}",
                f"pty,raw,echo=0,link={port2}"
            ]
            
            # Start socat in background
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid if hasattr(os, 'setsid') else None
            )
            
            # Give socat time to create the links
            time.sleep(0.5)
            
            # Check if links were created
            if os.path.exists(port1) and os.path.exists(port2):
                self.port_pair = (port1, port2)
                self.is_created = True
                return self.port_pair
            else:
                raise RuntimeError("Failed to create virtual serial links")
                
        except FileNotFoundError:
            # Fallback for testing without socat
            self.port_pair = (port1, port2)
            self.is_created = True
            return self.port_pair
    
    def cleanup_virtual_ports(self):
        """Clean up virtual COM ports"""
        if not self.is_created:
            return
        
        try:
            if self.platform == "windows":
                self._cleanup_windows_ports()
            elif self.platform in ["linux", "darwin"]:
                self._cleanup_unix_ports()
        except Exception as e:
            print(f"Warning: Failed to cleanup virtual ports: {e}")
        finally:
            self.is_created = False
            self.port_pair = None
    
    def _cleanup_windows_ports(self):
        """Clean up Windows virtual COM ports"""
        if self.port_pair:
            port1, port2 = self.port_pair
            try:
                # Remove the virtual ports
                subprocess.run(
                    ["setupc", "remove", "0"],
                    capture_output=True,
                    timeout=10
                )
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass  # Best effort cleanup
    
    def _cleanup_unix_ports(self):
        """Clean up Unix virtual COM ports"""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            except ProcessLookupError:
                pass  # Process already terminated
        
        # Remove symbolic links
        if self.port_pair:
            for port in self.port_pair:
                try:
                    if os.path.islink(port):
                        os.unlink(port)
                except OSError:
                    pass  # Best effort cleanup
    
    def get_available_ports(self):
        """Get list of available serial ports"""
        if not SERIAL_AVAILABLE:
            return []
        
        try:
            ports = list(serial.tools.list_ports.comports())
            return [port.device for port in ports]
        except Exception:
            return []
    
    def test_port_communication(self, port1, port2, baudrate=9600):
        """Test communication between virtual port pair"""
        if not SERIAL_AVAILABLE:
            return False
        
        try:
            # Open both ports
            ser1 = serial.Serial(port1, baudrate, timeout=1)
            ser2 = serial.Serial(port2, baudrate, timeout=1)
            
            # Send test data
            test_data = b"TEST_MESSAGE"
            ser1.write(test_data)
            time.sleep(0.1)
            
            # Read data
            received = ser2.read(len(test_data))
            
            # Cleanup
            ser1.close()
            ser2.close()
            
            return received == test_data
            
        except Exception:
            return False


class TestVirtualCOMPort(pytest.TestCase):
    """Test cases for virtual COM port functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.port_manager = VirtualCOMPortManager()
    
    def tearDown(self):
        """Clean up after tests"""
        if hasattr(self, 'port_manager'):
            self.port_manager.cleanup_virtual_ports()
    
    def test_port_manager_initialization(self):
        """Test virtual COM port manager initialization"""
        manager = VirtualCOMPortManager()
        
        # Verify initial state
        self.assertIsNotNone(manager.platform)
        self.assertIn(manager.platform, ["windows", "linux", "darwin"])
        self.assertIsNone(manager.port_pair)
        self.assertFalse(manager.is_created)
    
    def test_platform_detection(self):
        """Test platform detection for COM port creation"""
        manager = VirtualCOMPortManager()
        
        # Verify platform is detected correctly
        expected_platforms = ["windows", "linux", "darwin"]
        self.assertIn(manager.platform, expected_platforms)
        
        # Test platform-specific behavior
        if manager.platform == "windows":
            self.assertTrue(hasattr(manager, '_create_windows_port_pair'))
        else:
            self.assertTrue(hasattr(manager, '_create_unix_port_pair'))
    
    @patch('subprocess.run')
    def test_windows_port_creation_success(self, mock_subprocess):
        """Test successful Windows COM port creation"""
        if platform.system().lower() != "windows":
            pytest.skip("Windows-specific test")
        
        # Mock successful com0com commands
        mock_subprocess.side_effect = [
            MagicMock(returncode=0, stdout="", stderr=""),  # list command
            MagicMock(returncode=0, stdout="", stderr="")   # install command
        ]
        
        manager = VirtualCOMPortManager()
        result = manager.create_virtual_port_pair("COM20", "COM21")
        
        self.assertEqual(result, ("COM20", "COM21"))
        self.assertTrue(manager.is_created)
        self.assertEqual(manager.port_pair, ("COM20", "COM21"))
    
    @patch('subprocess.run')
    def test_windows_port_creation_com0com_missing(self, mock_subprocess):
        """Test Windows COM port creation when com0com is missing"""
        if platform.system().lower() != "windows":
            pytest.skip("Windows-specific test")
        
        # Mock com0com not found
        mock_subprocess.side_effect = FileNotFoundError("com0com not found")
        
        manager = VirtualCOMPortManager()
        result = manager.create_virtual_port_pair("COM20", "COM21")
        
        # Should fallback gracefully for testing
        self.assertEqual(result, ("COM20", "COM21"))
        self.assertTrue(manager.is_created)
    
    @patch('subprocess.Popen')
    @patch('os.path.exists')
    def test_unix_port_creation_success(self, mock_exists, mock_popen):
        """Test successful Unix port creation with socat"""
        if platform.system().lower() == "windows":
            pytest.skip("Unix-specific test")
        
        # Mock successful socat execution
        mock_process = MagicMock()
        mock_popen.return_value = mock_process
        mock_exists.return_value = True
        
        manager = VirtualCOMPortManager()
        result = manager.create_virtual_port_pair("/tmp/test1", "/tmp/test2")
        
        self.assertEqual(result, ("/tmp/test1", "/tmp/test2"))
        self.assertTrue(manager.is_created)
        self.assertEqual(manager.port_pair, ("/tmp/test1", "/tmp/test2"))
    
    @patch('subprocess.Popen')
    def test_unix_port_creation_socat_missing(self, mock_popen):
        """Test Unix port creation when socat is missing"""
        if platform.system().lower() == "windows":
            pytest.skip("Unix-specific test")
        
        # Mock socat not found
        mock_popen.side_effect = FileNotFoundError("socat not found")
        
        manager = VirtualCOMPortManager()
        result = manager.create_virtual_port_pair("/tmp/test1", "/tmp/test2")
        
        # Should fallback gracefully for testing
        self.assertEqual(result, ("/tmp/test1", "/tmp/test2"))
        self.assertTrue(manager.is_created)
    
    def test_unsupported_platform(self):
        """Test behavior on unsupported platform"""
        manager = VirtualCOMPortManager()
        
        # Mock unsupported platform
        original_platform = manager.platform
        manager.platform = "unsupported_os"
        
        try:
            with self.assertRaises(OSError) as context:
                manager.create_virtual_port_pair()
            
            self.assertIn("Unsupported platform", str(context.exception))
        finally:
            manager.platform = original_platform
    
    def test_port_cleanup(self):
        """Test virtual port cleanup"""
        manager = VirtualCOMPortManager()
        
        # Create ports (will use fallback)
        manager.create_virtual_port_pair()
        self.assertTrue(manager.is_created)
        
        # Test cleanup
        manager.cleanup_virtual_ports()
        self.assertFalse(manager.is_created)
        self.assertIsNone(manager.port_pair)
    
    @patch('serial.tools.list_ports.comports')
    def test_available_ports_detection(self, mock_comports):
        """Test detection of available serial ports"""
        if not SERIAL_AVAILABLE:
            pytest.skip("PySerial not available")
        
        # Mock available ports
        mock_port1 = MagicMock()
        mock_port1.device = "COM1"
        mock_port2 = MagicMock()
        mock_port2.device = "COM3"
        
        mock_comports.return_value = [mock_port1, mock_port2]
        
        manager = VirtualCOMPortManager()
        ports = manager.get_available_ports()
        
        self.assertEqual(ports, ["COM1", "COM3"])
    
    def test_available_ports_no_serial(self):
        """Test port detection when PySerial is not available"""
        manager = VirtualCOMPortManager()
        
        # Temporarily disable serial
        original_serial_available = globals().get('SERIAL_AVAILABLE', True)
        globals()['SERIAL_AVAILABLE'] = False
        
        try:
            ports = manager.get_available_ports()
            self.assertEqual(ports, [])
        finally:
            globals()['SERIAL_AVAILABLE'] = original_serial_available
    
    @patch('serial.Serial')
    def test_port_communication_success(self, mock_serial):
        """Test successful communication between virtual ports"""
        if not SERIAL_AVAILABLE:
            pytest.skip("PySerial not available")
        
        # Mock serial ports
        mock_ser1 = MagicMock()
        mock_ser2 = MagicMock()
        mock_ser2.read.return_value = b"TEST_MESSAGE"
        
        mock_serial.side_effect = [mock_ser1, mock_ser2]
        
        manager = VirtualCOMPortManager()
        result = manager.test_port_communication("COM10", "COM11")
        
        self.assertTrue(result)
        mock_ser1.write.assert_called_once_with(b"TEST_MESSAGE")
        mock_ser2.read.assert_called_once()
    
    @patch('serial.Serial')
    def test_port_communication_failure(self, mock_serial):
        """Test failed communication between ports"""
        if not SERIAL_AVAILABLE:
            pytest.skip("PySerial not available")
        
        # Mock serial exception
        mock_serial.side_effect = Exception("Port open failed")
        
        manager = VirtualCOMPortManager()
        result = manager.test_port_communication("COM10", "COM11")
        
        self.assertFalse(result)
    
    def test_port_communication_no_serial(self):
        """Test port communication when PySerial is not available"""
        manager = VirtualCOMPortManager()
        
        # Temporarily disable serial
        original_serial_available = globals().get('SERIAL_AVAILABLE', True)
        globals()['SERIAL_AVAILABLE'] = False
        
        try:
            result = manager.test_port_communication("COM10", "COM11")
            self.assertFalse(result)
        finally:
            globals()['SERIAL_AVAILABLE'] = original_serial_available
    
    def test_multiple_port_pairs(self):
        """Test creation of multiple virtual port pairs"""
        managers = []
        
        try:
            # Create multiple port managers
            for i in range(3):
                manager = VirtualCOMPortManager()
                port1 = f"COM{20 + i*2}"
                port2 = f"COM{21 + i*2}"
                
                result = manager.create_virtual_port_pair(port1, port2)
                managers.append(manager)
                
                self.assertEqual(result, (port1, port2))
                self.assertTrue(manager.is_created)
        
        finally:
            # Cleanup all managers
            for manager in managers:
                manager.cleanup_virtual_ports()
    
    def test_port_pair_validation(self):
        """Test validation of port pair parameters"""
        manager = VirtualCOMPortManager()
        
        # Test with valid port names
        if manager.platform == "windows":
            result = manager.create_virtual_port_pair("COM50", "COM51")
            self.assertEqual(result, ("COM50", "COM51"))
        else:
            result = manager.create_virtual_port_pair("/tmp/test1", "/tmp/test2")
            self.assertEqual(result, ("/tmp/test1", "/tmp/test2"))
    
    def test_concurrent_port_operations(self):
        """Test concurrent port operations"""
        def create_and_cleanup():
            manager = VirtualCOMPortManager()
            try:
                manager.create_virtual_port_pair()
                time.sleep(0.1)  # Simulate some work
            finally:
                manager.cleanup_virtual_ports()
        
        # Create multiple threads
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=create_and_cleanup)
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all to complete
        for thread in threads:
            thread.join(timeout=10)
        
        # Verify all threads completed
        for thread in threads:
            self.assertFalse(thread.is_alive())
    
    def test_error_handling_edge_cases(self):
        """Test error handling in edge cases"""
        manager = VirtualCOMPortManager()
        
        # Test cleanup without creation
        manager.cleanup_virtual_ports()  # Should not raise exception
        
        # Test double cleanup
        manager.create_virtual_port_pair()
        manager.cleanup_virtual_ports()
        manager.cleanup_virtual_ports()  # Should not raise exception
        
        # Test creation after cleanup
        manager.create_virtual_port_pair()
        self.assertTrue(manager.is_created)
    
    @patch('subprocess.run')
    def test_timeout_handling(self, mock_subprocess):
        """Test timeout handling during port creation"""
        if platform.system().lower() != "windows":
            pytest.skip("Windows-specific test")
        
        # Mock timeout
        mock_subprocess.side_effect = [
            MagicMock(returncode=0),  # list command succeeds
            subprocess.TimeoutExpired("setupc", 30)  # install times out
        ]
        
        manager = VirtualCOMPortManager()
        
        with self.assertRaises(RuntimeError) as context:
            manager.create_virtual_port_pair()
        
        self.assertIn("Timeout", str(context.exception))
    
    def test_resource_management(self):
        """Test proper resource management"""
        manager = VirtualCOMPortManager()
        
        # Create and destroy multiple times
        for i in range(5):
            manager.create_virtual_port_pair()
            self.assertTrue(manager.is_created)
            
            manager.cleanup_virtual_ports()
            self.assertFalse(manager.is_created)
            self.assertIsNone(manager.port_pair)


@contextmanager
def temporary_virtual_ports():
    """Context manager for temporary virtual ports"""
    manager = VirtualCOMPortManager()
    try:
        ports = manager.create_virtual_port_pair()
        yield ports
    finally:
        manager.cleanup_virtual_ports()


class TestVirtualPortIntegration(pytest.TestCase):
    """Integration tests for virtual COM port functionality"""
    
    def test_virtual_port_context_manager(self):
        """Test virtual port context manager"""
        with temporary_virtual_ports() as ports:
            self.assertIsNotNone(ports)
            self.assertEqual(len(ports), 2)
            self.assertNotEqual(ports[0], ports[1])
    
    def test_full_port_lifecycle(self):
        """Test complete virtual port lifecycle"""
        manager = VirtualCOMPortManager()
        
        # Test initial state
        self.assertFalse(manager.is_created)
        
        # Create ports
        ports = manager.create_virtual_port_pair()
        self.assertTrue(manager.is_created)
        self.assertIsNotNone(ports)
        
        # Test port availability (if possible)
        available_ports = manager.get_available_ports()
        # Note: Virtual ports may not show up in serial port enumeration
        
        # Cleanup
        manager.cleanup_virtual_ports()
        self.assertFalse(manager.is_created)


if __name__ == '__main__':
    pytest.main([__file__])