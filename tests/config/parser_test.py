"""
Test unit for the config parser module. This file verifies that settings parsing works as expected.
"""
import pytest

from URModbus.config.parser import parse_Settings


class TestParseSettings:
    """Tests for the parse_Settings function."""
    
    def test_parse_settings_returns_dict(self):
        """Test that parse_Settings returns a dictionary."""
        result = parse_Settings()
        
        assert isinstance(result, dict)
    
    def test_parse_settings_contains_all_constants(self):
        """Test that parse_Settings extracts all non-callable attributes from constants.py."""
        result = parse_Settings()
        
        # Check for key settings that should be parsed
        expected_settings = [
            "MODE",
            "AUTO_LOAD",
            "TERMINAL_PORT",
            "TERMINAL_HOST",
            "ROBOT_SLEEP_TIME", 
            "UR5_IP",
            "CONTAINER",
            "DATA_DIR",
            "AUTOGEN_DIR",
            "TEST_FILE",
            "PROCESS_FILE",
            "MOTS",
            "LOGO"
        ]
        
        for setting in expected_settings:
            assert setting in result, f"Missing setting: {setting}"
    
    def test_parse_settings_has_correct_structure(self):
        """Test that each setting has type, default, and description."""
        result = parse_Settings()
        
        for setting_name, setting_info in result.items():
            assert "type" in setting_info, f"Missing 'type' for {setting_name}"
            assert "default" in setting_info, f"Missing 'default' for {setting_name}"
            assert "description" in setting_info, f"Missing 'description' for {setting_name}"
    
    def test_parse_settings_incorrect_type(self):
        """Test that parse_Settings identifies settings with incorrect types."""
        result = parse_Settings()
        
        # Check some known types
        assert result["DATA_DIR"]["type"] == str
        assert result["TERMINAL_PORT"]["type"] == int
        assert result["MODE"]["type"] == str
        assert result["ROBOT_SLEEP_TIME"]["type"] == float
        assert result["AUTO_LOAD"]["type"] == bool
    
    def test_parse_settings_correct_defaults(self):
        """Test that parse_Settings extracts correct default values."""
        result = parse_Settings()
        
        # Check some known defaults
        assert result["DATA_DIR"]["default"] == '"./data"'
        assert result["TERMINAL_PORT"]["default"] == 9999
        assert result["MODE"]["default"] == '"AUTO"'
        assert result["ROBOT_SLEEP_TIME"]["default"] == 0.1 
        assert result["AUTO_LOAD"]["default"] == True
    
    def test_parse_settings_descriptions_contain_comments(self):
        """Test that parse_Settings extracts descriptions from comments."""
        result = parse_Settings()
        
        # Check that some settings have non-empty descriptions
        assert "ROBOT_SLEEP_TIME" in result
        desc = result["ROBOT_SLEEP_TIME"]["description"]
        assert len(desc) > 0
    
    def test_parse_settings_no_static_methods(self):
        """Test that parse_Settings stops before static methods."""
        result = parse_Settings()
        
        # updateSetting should not be parsed as a setting
        assert "updateSetting" not in result
    
    def test_parse_settings_ignores_private_attributes(self):
        """Test that parse_Settings ignores attributes starting with underscore."""
        result = parse_Settings()
        
        # All keys should be public (not start with _)
        for key in result.keys():
            assert not key.startswith("_"), f"Found private attribute: {key}"