"""Test suite for URModbus core/DashTools module."""

import pytest
from unittest.mock import patch, MagicMock, mock_open
import socket
import threading
from URModbus.core.DashTools import DashRobot


class TestDashRobotInitialization:
    """Test DashRobot initialization."""

    def test_init_with_ip_and_default_port(self):
        """Test initialization with IP and default port."""
        robot = DashRobot(ip="192.168.1.10")
        assert isinstance(robot, threading.Thread)
        assert robot.name == "DashRobot"

    def test_init_with_custom_port(self):
        """Test initialization with custom port."""
        robot = DashRobot(ip="192.168.1.10", port=30000)
        # Port is stored internally, can't easily verify without accessing private attribute
        assert isinstance(robot, threading.Thread)

    def test_init_with_timeout(self):
        """Test initialization with custom timeout."""
        robot = DashRobot(ip="192.168.1.10", timeout=5.0)
        # Timeout is stored internally
        assert isinstance(robot, threading.Thread)

    def test_init_with_all_parameters(self):
        """Test initialization with all parameters."""
        robot = DashRobot(ip="10.0.0.1", port=29999, timeout=3.0)
        assert robot.name == "DashRobot"
        assert isinstance(robot, threading.Thread)


class TestDashboardCommand:
    """Test the internal Dashboard command method."""

    @patch("socket.create_connection")
    @patch("builtins.input")
    def test_successful_command_response(self, mock_input, mock_create_connection):
        """Test a successful dashboard command response."""

        mock_sock = MagicMock()

        mock_create_connection.return_value.__enter__.return_value = mock_sock
        mock_create_connection.return_value.__exit__.return_value = None

        mock_sock.recv.side_effect = [
            b"ROBOT_OK\n",
            b"PLAYING test_program\n",
        ]

        robot = DashRobot(ip="192.168.1.10", port=29999)

        result = robot._DashRobot__DashBoardCommand("play")

        assert result == "PLAYING test_program"

    @patch('socket.create_connection')
    def test_server_closed_no_greeting(self, mock_socket):
        """Test when server doesn't send greeting."""
        mock_sock = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_sock
        
        # Mock that recv returns empty for greeting
        mock_sock.recv.return_value = b""
        
        robot = DashRobot(ip="192.168.1.10", port=29999)
        
        with patch('socket.socket', return_value=mock_sock):
            with pytest.raises(RuntimeError, match="Dashboard server closed connection"):
                robot._DashRobot__DashBoardCommand("play")

    @patch('socket.create_connection')
    def test_server_closed_no_response(self, mock_socket):
        """Test when server doesn't respond to command."""
        mock_sock = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_sock
        
        # Mock greeting received but no response
        mock_sock.recv.side_effect = [b"ROBOT_OK\n", b""]
        
        robot = DashRobot(ip="192.168.1.10", port=29999)
        
        with patch('socket.socket', return_value=mock_sock):
            with pytest.raises(RuntimeError, match="Dashboard server closed connection"):
                robot._DashRobot__DashBoardCommand("play")


class TestPlay:
    """Test the play method."""

    @patch.object(DashRobot, '_DashRobot__DashBoardCommand')
    def test_play_when_not_playing(self, mock_command):
        """Test play when program is not playing."""
        mock_command.return_value = "STOPPED initial_prog"
        
        robot = DashRobot(ip="192.168.1.10")
        robot._DashRobot__DashBoardCommand = mock_command
        
        result = robot.play()
        
        assert mock_command.called
        assert mock_command.call_args[0][0] == "play"

    @patch.object(DashRobot, '_DashRobot__DashBoardCommand')
    def test_play_when_already_playing(self, mock_command):
        """Test play when program is already playing."""
        mock_command.return_value = "PLAYING test_program"
        
        robot = DashRobot(ip="192.168.1.10")
        robot._DashRobot__DashBoardCommand = mock_command
        
        result = robot.play()
        
        mock_command.assert_called_once_with("programState")


class TestStop:
    """Test the stop method."""

    @patch.object(DashRobot, '_DashRobot__DashBoardCommand')
    def test_stop_when_not_stopped(self, mock_command):
        """Test stop when program is not stopped."""
        mock_command.return_value = "PLAYING test_program"
        
        robot = DashRobot(ip="192.168.1.10")
        robot._DashRobot__DashBoardCommand = mock_command
        
        result = robot.stop()
        
        assert mock_command.called

    @patch.object(DashRobot, '_DashRobot__DashBoardCommand')
    def test_stop_when_already_stopped(self, mock_command):
        """Test stop when program is already stopped."""
        mock_command.return_value = "STOPPED current_program"
        
        robot = DashRobot(ip="192.168.1.10")
        robot._DashRobot__DashBoardCommand = mock_command
        
        result = robot.stop()
        
        mock_command.assert_called_once_with("programState")



class TestPause:
    """Test the pause method."""

    @patch.object(DashRobot, '_DashRobot__DashBoardCommand')
    def test_pause_when_not_paused(self, mock_command):
        """Test pause when program is not paused."""
        mock_command.return_value = "PLAYING test_program"
        
        robot = DashRobot(ip="192.168.1.10")
        robot._DashRobot__DashBoardCommand = mock_command
        
        result = robot.pause()
        
        assert mock_command.called

    @patch.object(DashRobot, '_DashRobot__DashBoardCommand')
    def test_pause_when_already_paused(self, mock_command):
        """Test pause when program is already paused."""
        mock_command.return_value = "PAUSED current_program"
        
        robot = DashRobot(ip="192.168.1.10")
        robot._DashRobot__DashBoardCommand = mock_command
        
        result = robot.pause()
        
        mock_command.assert_called_once_with("programState")



class TestProgramStateProperty:
    """Test the programState property."""

    @patch.object(DashRobot, '_DashRobot__DashBoardCommand')
    def test_program_state_return_format(self, mock_command):
        """Test that program state returns correct format."""
        mock_command.return_value = "PLAYING my_robot_program"
        
        robot = DashRobot(ip="192.168.1.10")
        robot._DashRobot__DashBoardCommand = mock_command
        
        state = robot.programState
        
        assert isinstance(state, str)
        assert "PLAYING" in state
        assert "my_robot_program" in state

    @patch.object(DashRobot, '_DashRobot__DashBoardCommand')
    def test_state_stopped(self, mock_command):
        """Test stopped state."""
        mock_command.return_value = "STOPPED idle"
        
        robot = DashRobot(ip="192.168.1.10")
        robot._DashRobot__DashBoardCommand = mock_command
        
        assert robot.programState == "STOPPED idle"


class TestProgramNameProperty:
    """Test the programName property."""

    @patch.object(DashRobot, '_DashRobot__DashBoardCommand')
    def test_extract_program_name_from_state(self, mock_command):
        """Test that program name is correctly extracted from state."""
        mock_command.return_value = "PLAYING welding_operation"
        
        robot = DashRobot(ip="192.168.1.10")
        robot._DashRobot__DashBoardCommand = mock_command
        
        name = robot.programName
        
        assert name == "welding_operation"

    @patch.object(DashRobot, '_DashRobot__DashBoardCommand')
    def test_extract_program_name_stopped(self, mock_command):
        """Test extracting program name when stopped."""
        mock_command.return_value = "STOPPED calibration"
        
        robot = DashRobot(ip="192.168.1.10")
        robot._DashRobot__DashBoardCommand = mock_command
        
        assert robot.programName == "calibration"