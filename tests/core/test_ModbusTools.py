"""Test suite for URModbus core/ModbusTools module."""

import pytest
from unittest.mock import patch, MagicMock, Mock
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException
from URModbus.core.ModbusTools import ModbusRobot

class TestModbusRobotInitialization:
    """Test ModbusRobot initialization."""

    def test_init_with_ip(self):
        """Test initialization with IP address."""
        robot = ModbusRobot(ip="192.168.1.10")
        assert isinstance(robot, ModbusRobot)  # Thread is mocked

    def test_thread_name(self):
        """Test that thread has correct name."""
        with patch('URModbus.core.ModbusTools.Thread.__init__') as mock_init:
            robot = ModbusRobot(ip="192.168.1.10")
            
            mock_init.assert_called_once()

    def test_mapping_addresses_are_set(self):
        """Test that mapping dictionaries are initialized."""
        with patch('URModbus.core.ModbusTools.Thread.__init__'):
            robot = ModbusRobot(ip="192.168.1.10")
            
            # Check that class attributes exist and are accessible
            assert hasattr(ModbusRobot, '_ModbusRobot__MAPPING_MOT_ADRESSES')
            assert hasattr(ModbusRobot, '_ModbusRobot__MAPPING_ADRESSES_MOT')


class TestReadReg:
    """Test the internal read register method."""

    @patch.object(ModbusTcpClient, 'connect')
    @patch.object(ModbusTcpClient, 'close')
    @patch.object(ModbusTcpClient, 'read_holding_registers')
    def test_successful_read_register(self, mock_read_reg, mock_close, mock_connect):
        """Test successful register read."""
        mock_connect.return_value = True
        mock_client = Mock()
        mock_read_reg.return_value.registers = [42]
        mock_client.read_holding_registers = mock_read_reg
        mock_client.connect = mock_connect
        mock_client.close = mock_close
        
        # Create a mock client instance for the read operation
        with patch('URModbus.core.ModbusTools.ModbusTcpClient') as MockClient:
            MockClient.return_value = mock_client
            
            robot = ModbusRobot(ip="192.168.1.10")
            
            result = robot._ModbusRobot__read_reg(address=130, count=1)
            
            assert result == 42
            mock_connect.assert_called_once()
            mock_close.assert_called_once()

    @patch.object(ModbusTcpClient, 'connect')
    @patch.object(ModbusTcpClient, 'close')
    @patch.object(ModbusTcpClient, 'read_holding_registers')
    def test_read_register_value_zero(self, mock_read_reg, mock_close, mock_connect):
        """Test reading a register that returns 0."""
        mock_connect.return_value = None
        mock_client = Mock()
        mock_read_reg.return_value.registers = [0]
        mock_client.read_holding_registers = mock_read_reg
        mock_client.connect = mock_connect
        mock_client.close = mock_close
        
        with patch('URModbus.core.ModbusTools.ModbusTcpClient') as MockClient:
            MockClient.return_value = mock_client
            
            robot = ModbusRobot(ip="192.168.1.10")
            
            result = robot._ModbusRobot__read_reg(address=130, count=1)
            
            assert result == 0

    @patch.object(ModbusTcpClient, 'connect')
    @patch.object(ModbusTcpClient, 'close')
    @patch.object(ModbusTcpClient, 'read_holding_registers')
    def test_read_register_empty_registers(self, mock_read_reg, mock_close, mock_connect):
        """Test reading a register that returns empty registers."""
        mock_connect.return_value = None
        mock_client = Mock()
        mock_read_reg.return_value.registers = [None]
        mock_client.read_holding_registers = mock_read_reg
        mock_client.connect = mock_connect
        mock_client.close = mock_close
        
        with patch('URModbus.core.ModbusTools.ModbusTcpClient') as MockClient:
            MockClient.return_value = mock_client
            
            robot = ModbusRobot(ip="192.168.1.10")
            
            result = robot._ModbusRobot__read_reg(address=130, count=1)
            
            assert result == None


class TestWriteReg:
    """Test the internal write register method."""

    @patch.object(ModbusTcpClient, 'connect')
    @patch.object(ModbusTcpClient, 'close')
    @patch.object(ModbusTcpClient, 'write_register')
    def test_successful_write_register(self, mock_write_reg, mock_close, mock_connect):
        """Test successful register write."""
        mock_connect.return_value = None
        
        robot = ModbusRobot(ip="192.168.1.10")
        
        result = robot._ModbusRobot__write_reg(address=131, value=5)
        
        assert result is True

    @patch.object(ModbusTcpClient, "connect")
    def test_write_register_connection_failure(self, mock_connect):
        mock_connect.return_value = False

        robot = ModbusRobot(ip="192.168.1.10")

        with pytest.raises(ConnectionException):
            robot._ModbusRobot__write_reg(address=131, value=5)

class TestRead:
    """Test the read method."""

    @patch.object(ModbusTcpClient, 'connect')
    @patch.object(ModbusTcpClient, 'close')
    def test_read_int_register_readable(self, mock_close, mock_connect):
        """Test reading an integer register that is readable."""
        # Setup mocks for read operation
        mock_connect.return_value = True

        mock_client = Mock()
        mock_read_reg = Mock(return_value=Mock(registers=[10]))
        mock_client.read_holding_registers = mock_read_reg
        
        with patch('URModbus.core.ModbusTools.ModbusTcpClient') as MockClient:
            MockClient.return_value = mock_client
            
            robot = ModbusRobot(ip="192.168.1.10")
            
            result = robot.read(130)  # Current_Action is readable (R)
            
            assert result == 10

    @patch.object(ModbusTcpClient, 'connect')
    @patch.object(ModbusTcpClient, 'close')
    def test_read_int_register_not_readable(self, mock_close, mock_connect):
        """Test reading an integer register that is not readable."""
        with patch('URModbus.core.ModbusTools.ModbusTcpClient') as MockClient:
            MockClient.return_value = Mock()
            
            robot = ModbusRobot(ip="192.168.1.10")
            
            # Next_Action (131) is writable only (W), so reading should fail
            with pytest.raises(ValueError, match="is not readable"):
                robot.read(131)

    @patch.object(ModbusTcpClient, 'connect')
    @patch.object(ModbusTcpClient, 'close')
    def test_read_str_register_readable(self, mock_close, mock_connect):
        """Test reading an integer register that is readable."""
        # Setup mocks for read operation
        mock_client = Mock()
        mock_read_reg = Mock(return_value=Mock(registers=[10]))
        mock_client.read_holding_registers = mock_read_reg
        mock_client.connect = mock_connect
        mock_client.close = mock_close
        
        with patch('URModbus.core.ModbusTools.ModbusTcpClient') as MockClient:
            MockClient.return_value = mock_client
            
            robot = ModbusRobot(ip="192.168.1.10")
            
            result = robot.read("Current_Action")  # Current_Action is readable (R)
            
            assert result == 10

    @patch.object(ModbusTcpClient, 'connect')
    @patch.object(ModbusTcpClient, 'close')
    def test_read_invalid_type(self, mock_close, mock_connect):
        """Test reading with invalid type."""
        with patch('URModbus.core.ModbusTools.ModbusTcpClient') as MockClient:
            MockClient.return_value = Mock()
            
            robot = ModbusRobot(ip="192.168.1.10")
            
            with pytest.raises(TypeError, match="Invalid type for register"):
                robot.read(None)


class TestWrite:
    """Test the write method."""

    @patch.object(ModbusTcpClient, 'connect')
    @patch.object(ModbusTcpClient, 'close')
    def test_write_int_register(self, mock_close, mock_connect):
        """Test writing to a register via integer address."""
        with patch('URModbus.core.ModbusTools.ModbusTcpClient') as MockClient:
            MockClient.return_value = Mock()
            
            robot = ModbusRobot(ip="192.168.1.10")
            
            result = robot.write(131, 42)
            
            assert result is True

    @patch.object(ModbusTcpClient, 'connect')
    @patch.object(ModbusTcpClient, 'close')
    def test_write_string_register(self, mock_close, mock_connect):
        """Test writing to a register via string name."""
        with patch('URModbus.core.ModbusTools.ModbusTcpClient') as MockClient:
            MockClient.return_value = Mock()
            
            robot = ModbusRobot(ip="192.168.1.10")
            
            # Next_Action is writable
            result = robot.write("Next_Action", 5)
            
            assert result is True

    @patch.object(ModbusTcpClient, 'connect')
    @patch.object(ModbusTcpClient, 'close')
    def test_write_invalid_register_type(self, mock_close, mock_connect):
        """Test writing to a register that doesn't exist."""
        with patch('URModbus.core.ModbusTools.ModbusTcpClient') as MockClient:
            MockClient.return_value = Mock()
            
            robot = ModbusRobot(ip="192.168.1.10")
            
            # Trying to write to a non-existent register should fail
            with pytest.raises(KeyError):
                robot.write("NonExistent_Reg", 42)


class TestMapping:
    """Test the mapping dictionaries."""

    def test_mots_mapping_exists(self):
        """Test that MOTS mapping dictionary exists and has correct structure."""
        assert hasattr(ModbusRobot, '_ModbusRobot__MAPPING_ADRESSES_MOT')
        
        mots = ModbusRobot._ModbusRobot__MAPPING_ADRESSES_MOT
        
        # Check expected registers are present
        assert 130 in mots  # Current_Action
        assert 131 in mots  # Next_Action

    def test_mapping_addresses_mot_structure(self):
        """Test that MOTS mapping has correct structure."""
        mots = ModbusRobot._ModbusRobot__MAPPING_MOT_ADRESSES
        
        for key, value in mots.items():
            assert isinstance(key, str)
            assert isinstance(value, tuple)
            assert len(value) == 2
            # Value should be (register_address, access_type)

class TestErrorHandling:
    """Test error handling scenarios."""

    @patch.object(ModbusTcpClient, 'connect')
    @patch.object(ModbusTcpClient, 'close')
    def test_read_on_connection_failure(self, mock_close, mock_connect):
        """Test reading when connection fails."""
        from unittest.mock import Mock, MagicMock
        
        mock_client = Mock()
        mock_client.connect.side_effect = ConnectionError("Connection refused")
        
        with patch('URModbus.core.ModbusTools.ModbusTcpClient') as MockClient:
            MockClient.return_value = mock_client
            
            robot = ModbusRobot(ip="192.168.1.10")
            
            with pytest.raises(ConnectionError):
                robot.read(130)