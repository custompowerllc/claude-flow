"""
Tests for temperature conversion functionality.
"""
import pytest
from src.utils.constants import scale_temperature


class TestTemperatureConversion:
    """Test temperature conversion between Celsius and Fahrenheit."""
    
    def test_scale_temperature_celsius_default(self):
        """Test default Celsius conversion."""
        # Water freezing point: 273.15K = 0°C
        result = scale_temperature(2731.5)
        assert abs(result - 0.0) < 0.1, f"Expected ~0°C, got {result}°C"
        
    def test_scale_temperature_celsius_explicit(self):
        """Test explicit Celsius conversion."""
        # Water boiling point: 373.15K = 100°C
        result = scale_temperature(3731.5, 'C')
        assert abs(result - 100.0) < 0.1, f"Expected ~100°C, got {result}°C"
        
    def test_scale_temperature_fahrenheit(self):
        """Test Fahrenheit conversion."""
        # Water freezing point: 273.15K = 0°C = 32°F
        result = scale_temperature(2731.5, 'F')
        assert abs(result - 32.0) < 0.1, f"Expected ~32°F, got {result}°F"
        
    def test_scale_temperature_fahrenheit_boiling(self):
        """Test Fahrenheit conversion for boiling point."""
        # Water boiling point: 373.15K = 100°C = 212°F
        result = scale_temperature(3731.5, 'F')
        assert abs(result - 212.0) < 0.1, f"Expected ~212°F, got {result}°F"
        
    def test_scale_temperature_room_temperature(self):
        """Test typical room temperature conversion."""
        # Room temperature: 293.15K = 20°C = 68°F
        celsius_result = scale_temperature(2931.5, 'C')
        fahrenheit_result = scale_temperature(2931.5, 'F')
        
        assert abs(celsius_result - 20.0) < 0.1, f"Expected ~20°C, got {celsius_result}°C"
        assert abs(fahrenheit_result - 68.0) < 0.1, f"Expected ~68°F, got {fahrenheit_result}°F"
        
    def test_scale_temperature_negative_celsius(self):
        """Test negative temperature in Celsius."""
        # -10°C = 263.15K
        result = scale_temperature(2631.5, 'C')
        assert abs(result - (-10.0)) < 0.1, f"Expected ~-10°C, got {result}°C"
        
    def test_scale_temperature_negative_fahrenheit(self):
        """Test negative temperature conversion to Fahrenheit."""
        # -10°C = 263.15K = 14°F
        result = scale_temperature(2631.5, 'F')
        assert abs(result - 14.0) < 0.1, f"Expected ~14°F, got {result}°F"
        
    def test_scale_temperature_battery_operating_range(self):
        """Test typical battery operating temperature range."""
        # Common battery temperatures: 25°C and 40°C
        temp_25c = scale_temperature(2981.5, 'C')  # 298.15K
        temp_25f = scale_temperature(2981.5, 'F')  # Should be 77°F
        
        temp_40c = scale_temperature(3131.5, 'C')  # 313.15K  
        temp_40f = scale_temperature(3131.5, 'F')  # Should be 104°F
        
        assert abs(temp_25c - 25.0) < 0.1, f"Expected ~25°C, got {temp_25c}°C"
        assert abs(temp_25f - 77.0) < 0.1, f"Expected ~77°F, got {temp_25f}°F"
        assert abs(temp_40c - 40.0) < 0.1, f"Expected ~40°C, got {temp_40c}°C"
        assert abs(temp_40f - 104.0) < 0.1, f"Expected ~104°F, got {temp_40f}°F"
        
    def test_scale_temperature_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Absolute zero: 0K = -273.15°C = -459.67°F
        abs_zero_c = scale_temperature(0, 'C')
        abs_zero_f = scale_temperature(0, 'F')
        
        assert abs(abs_zero_c - (-273.15)) < 0.1, f"Expected ~-273.15°C, got {abs_zero_c}°C"
        assert abs(abs_zero_f - (-459.67)) < 0.5, f"Expected ~-459.67°F, got {abs_zero_f}°F"
        
    def test_scale_temperature_invalid_unit_defaults_celsius(self):
        """Test that invalid unit defaults to Celsius."""
        result = scale_temperature(2981.5, 'X')  # Invalid unit
        expected_celsius = scale_temperature(2981.5, 'C')
        
        assert abs(result - expected_celsius) < 0.01, "Invalid unit should default to Celsius"
        
    def test_scale_temperature_case_sensitivity(self):
        """Test unit parameter case sensitivity."""
        temp_value = 2981.5  # 25°C
        
        # Test lowercase
        result_c_lower = scale_temperature(temp_value, 'c')
        result_f_lower = scale_temperature(temp_value, 'f')
        
        # Should default to Celsius for lowercase 'c' (not explicitly handled)
        # Should default to Celsius for lowercase 'f' (not explicitly handled)
        expected_celsius = scale_temperature(temp_value, 'C')
        
        # Current implementation is case-sensitive, so lowercase defaults to Celsius
        assert abs(result_c_lower - expected_celsius) < 0.01
        assert abs(result_f_lower - expected_celsius) < 0.01
        
    def test_scale_temperature_precision(self):
        """Test precision of temperature conversion."""
        # Test with high precision input
        precise_value = 2981.57  # Precise Kelvin value
        
        celsius_result = scale_temperature(precise_value, 'C')
        fahrenheit_result = scale_temperature(precise_value, 'F')
        
        # Should maintain reasonable precision
        assert isinstance(celsius_result, float)
        assert isinstance(fahrenheit_result, float)
        
        # Verify the conversion is mathematically correct
        expected_celsius = precise_value / 10.0 - 273.15
        expected_fahrenheit = expected_celsius * 9/5 + 32
        
        assert abs(celsius_result - expected_celsius) < 1e-10
        assert abs(fahrenheit_result - expected_fahrenheit) < 1e-10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])