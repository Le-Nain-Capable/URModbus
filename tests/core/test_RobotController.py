"""Test suite for URModbus core/RobotController module."""

import pytest
from unittest.mock import patch, MagicMock, Mock
from threading import Thread, Lock
from URModbus.core.RobotController import RobotController


class TestRobotControllerInitialization:
    """Test RobotController initialization."""

    @patch('URModbus.core.RobotController.ModbusRobot')
    @patch('URModbus.core.RobotController.DashRobot')
    def test_init_creates_interfaces(self, mock_dash_robot, mock_modbus_robot):
        """Test that initialization creates Modbus and Dash interfaces."""
        mock_modbus_instance = MagicMock()
        mock_dash_instance = MagicMock()
        
        mock_modbus_robot.return_value = mock_modbus_instance
        mock_dash_robot.return_value = mock_dash_instance
        
        controller = RobotController(ip="192.168.1.10")
        
        assert isinstance(controller, Thread)
        assert controller.name == "RobotController"


class TestTaskPileProperties:
    """Test task pile related properties."""

    @patch('URModbus.core.RobotController.ModbusRobot')
    @patch('URModbus.core.RobotController.DashRobot')
    def test_task_pile_property(self, mock_dash_robot, mock_modbus_robot):
        """Test taskPile property returns list."""
        mock_modbus_instance = MagicMock()
        mock_dash_instance = MagicMock()
        
        mock_modbus_robot.return_value = mock_modbus_instance
        mock_dash_robot.return_value = mock_dash_instance
        
        controller = RobotController(ip="192.168.1.10")
        
        result = controller.taskPile
        assert isinstance(result, list)

    @patch('URModbus.core.RobotController.ModbusRobot')
    @patch('URModbus.core.RobotController.DashRobot')
    def test_next_task_property(self, mock_dash_robot, mock_modbus_robot):
        """Test nextTask property returns None when empty."""
        mock_modbus_instance = MagicMock()
        mock_dash_instance = MagicMock()
        
        mock_modbus_robot.return_value = mock_modbus_instance
        mock_dash_robot.return_value = mock_dash_instance
        
        controller = RobotController(ip="192.168.1.10")
        
        # Set up task pile with tasks
        controller._RobotController__taskPile = [5, 3, 1]
        
        result = controller.nextTask
        assert result == 5

    @patch('URModbus.core.RobotController.ModbusRobot')
    @patch('URModbus.core.RobotController.DashRobot')
    def test_last_task_property(self, mock_dash_robot, mock_modbus_robot):
        """Test lastTask property returns last in pile."""
        mock_modbus_instance = MagicMock()
        mock_dash_instance = MagicMock()
        
        mock_modbus_robot.return_value = mock_modbus_instance
        mock_dash_robot.return_value = mock_dash_instance
        
        controller = RobotController(ip="192.168.1.10")
        
        # Set up task pile with tasks
        controller._RobotController__taskPile = [5, 3, 1]
        
        result = controller.lastTask
        assert result == 1

    @patch('URModbus.core.RobotController.ModbusRobot')
    @patch('URModbus.core.RobotController.DashRobot')
    def test_has_task_property_empty(self, mock_dash_robot, mock_modbus_robot):
        """Test hasTask property returns False when empty."""
        mock_modbus_instance = MagicMock()
        mock_dash_instance = MagicMock()
        
        mock_modbus_robot.return_value = mock_modbus_instance
        mock_dash_robot.return_value = mock_dash_instance
        
        controller = RobotController(ip="192.168.1.10")
        
        result = controller.hasTask
        assert result is False

    @patch('URModbus.core.RobotController.ModbusRobot')
    @patch('URModbus.core.RobotController.DashRobot')
    def test_has_task_property_with_tasks(self, mock_dash_robot, mock_modbus_robot):
        """Test hasTask property returns True when tasks exist."""
        mock_modbus_instance = MagicMock()
        mock_dash_instance = MagicMock()
        
        mock_modbus_robot.return_value = mock_modbus_instance
        mock_dash_robot.return_value = mock_dash_instance
        
        controller = RobotController(ip="192.168.1.10")
        
        # Add tasks to pile
        controller._RobotController__taskPile = [5, 3, 1]
        
        result = controller.hasTask
        assert result is True


class TestTaskOperations:
    """Test task operations."""

    @patch('URModbus.core.RobotController.ModbusRobot')
    @patch('URModbus.core.RobotController.DashRobot')
    def test_clear_task_pile(self, mock_dash_robot, mock_modbus_robot):
        """Test clear_task_pile clears the pile."""
        mock_modbus_instance = MagicMock()
        mock_dash_instance = MagicMock()
        
        mock_modbus_robot.return_value = mock_modbus_instance
        mock_dash_robot.return_value = mock_dash_instance
        
        controller = RobotController(ip="192.168.1.10")
        
        # Set up with tasks
        controller._RobotController__taskPile = [5, 3, 1]
        
        controller.clear_task_pile()
        
        assert controller.taskPile == [0]

    @patch('URModbus.core.RobotController.ModbusRobot')
    @patch('URModbus.core.RobotController.DashRobot')
    def test_perform_task(self, mock_dash_robot, mock_modbus_robot):
        """Test perform_task adds task to pile."""
        mock_modbus_instance = MagicMock()
        mock_dash_instance = MagicMock()
        
        mock_modbus_robot.return_value = mock_modbus_instance
        mock_dash_robot.return_value = mock_dash_instance
        
        controller = RobotController(ip="192.168.1.10")
        
        result = controller.perform_task(5)
        
        assert controller.taskPile == [0,5,0]

    @patch('URModbus.core.RobotController.ModbusRobot')
    @patch('URModbus.core.RobotController.DashRobot')
    def test_follow_sequence(self, mock_dash_robot, mock_modbus_robot):
        """Test follow_sequence adds sequence to pile."""
        mock_modbus_instance = MagicMock()
        mock_dash_instance = MagicMock()
        
        mock_modbus_robot.return_value = mock_modbus_instance
        mock_dash_robot.return_value = mock_dash_instance
        
        controller = RobotController(ip="192.168.1.10")
        
        result = controller.follow_sequence([5, 3, 1])
        
        assert controller.taskPile == [0,5,0,3,0,1,0]

    @patch('URModbus.core.RobotController.ModbusRobot')
    @patch('URModbus.core.RobotController.DashRobot')
    def test_follow_sequence_with_0(self, mock_dash_robot, mock_modbus_robot):
        """Test follow_sequence adds sequence to pile."""
        mock_modbus_instance = MagicMock()
        mock_dash_instance = MagicMock()
        
        mock_modbus_robot.return_value = mock_modbus_instance
        mock_dash_robot.return_value = mock_dash_instance
        
        controller = RobotController(ip="192.168.1.10")
        
        result = controller.follow_sequence([0, 3, 0, 1])
        
        assert controller.taskPile == [0,0,0,3,0,0,0,1,0]

    @patch('URModbus.core.RobotController.ModbusRobot')
    @patch('URModbus.core.RobotController.DashRobot')
    def test_follow_sequence_invalid_type(self, mock_dash_robot, mock_modbus_robot):
        """Test follow_sequence with invalid sequence type."""
        mock_modbus_instance = MagicMock()
        mock_dash_instance = MagicMock()
        
        mock_modbus_robot.return_value = mock_modbus_instance
        mock_dash_robot.return_value = mock_dash_instance
        
        controller = RobotController(ip="192.168.1.10")
        
        with pytest.raises(TypeError, match="Sequence must be a list"):
            controller.follow_sequence("invalid")


class TestProgramControl:
    """Test program control methods."""

    @patch('URModbus.core.RobotController.ModbusRobot')
    @patch('URModbus.core.RobotController.DashRobot')
    def test_play_program(self, mock_dash_robot, mock_modbus_robot):
        """Test play_program calls dash interface play."""
        mock_modbus_instance = MagicMock()
        mock_dash_instance = MagicMock()
        
        mock_modbus_robot.return_value = mock_modbus_instance
        mock_dash_robot.return_value = mock_dash_instance
        
        controller = RobotController(ip="192.168.1.10")
        
        controller.play_program()
        
        mock_dash_instance.play.assert_called_once()

    @patch('URModbus.core.RobotController.ModbusRobot')
    @patch('URModbus.core.RobotController.DashRobot')
    def test_stop_program(self, mock_dash_robot, mock_modbus_robot):
        """Test stop_program calls dash interface stop."""
        mock_modbus_instance = MagicMock()
        mock_dash_instance = MagicMock()
        
        mock_modbus_robot.return_value = mock_modbus_instance
        mock_dash_robot.return_value = mock_dash_instance
        
        controller = RobotController(ip="192.168.1.10")
        
        controller.stop_program()
        
        mock_dash_instance.stop.assert_called_once()

    @patch('URModbus.core.RobotController.ModbusRobot')
    @patch('URModbus.core.RobotController.DashRobot')
    def test_pause_program(self, mock_dash_robot, mock_modbus_robot):
        """Test pause_program calls dash interface pause."""
        mock_modbus_instance = MagicMock()
        mock_dash_instance = MagicMock()
        
        mock_modbus_robot.return_value = mock_modbus_instance
        mock_dash_robot.return_value = mock_dash_instance
        
        controller = RobotController(ip="192.168.1.10")
        
        controller.pause_program()
        
        mock_dash_instance.pause.assert_called_once()


class TestStop:
    """Test stop method."""

    @patch('URModbus.core.RobotController.ModbusRobot')
    @patch('URModbus.core.RobotController.DashRobot')
    def test_stop_sets_running_false(self, mock_dash_robot, mock_modbus_robot):
        """Test that stop sets running to False."""
        mock_modbus_instance = MagicMock()
        mock_dash_instance = MagicMock()
        
        mock_modbus_robot.return_value = mock_modbus_instance
        mock_dash_robot.return_value = mock_dash_instance
        
        controller = RobotController(ip="192.168.1.10")
        
        assert controller._RobotController__running is True
        
        controller.stop()
        
        assert controller._RobotController__running is False


class TestModbusInterface:
    """Test ModBusInterface property."""

    @patch('URModbus.core.RobotController.ModbusRobot')
    @patch('URModbus.core.RobotController.DashRobot')
    def test_modbus_interface_property(self, mock_dash_robot, mock_modbus_robot):
        """Test that ModBusInterface property returns the modbus instance."""
        mock_modbus_instance = MagicMock()
        mock_dash_instance = MagicMock()
        
        mock_modbus_robot.return_value = mock_modbus_instance
        mock_dash_robot.return_value = mock_dash_instance
        
        controller = RobotController(ip="192.168.1.10")
        
        result = controller.ModBusInterface
        
        assert isinstance(result, Mock)


class TestStateProperties:
    """Test state properties."""

    @patch('URModbus.core.RobotController.ModbusRobot')
    @patch('URModbus.core.RobotController.DashRobot')
    def test_state_property(self, mock_dash_robot, mock_modbus_robot):
        """Test state property returns robot state."""
        mock_modbus_instance = MagicMock()
        mock_modbus_instance.read.return_value = 5  # Idle state
        
        mock_dash_instance = MagicMock()
        
        mock_modbus_robot.return_value = mock_modbus_instance
        mock_dash_robot.return_value = mock_dash_instance
        
        controller = RobotController(ip="192.168.1.10")
        
        result = controller.state
        assert result == 5

    @patch('URModbus.core.RobotController.ModbusRobot')
    @patch('URModbus.core.RobotController.DashRobot')
    def test_program_state_property(self, mock_dash_robot, mock_modbus_robot):
        """Test programState property returns state string."""
        mock_modbus_instance = MagicMock()
        
        mock_dash_instance = MagicMock()
        mock_dash_instance.programState.return_value = "PLAYING welding_task"
        
        mock_modbus_robot.return_value = mock_modbus_instance
        mock_dash_robot.return_value = mock_dash_instance
        
        controller = RobotController(ip="192.168.1.10")
        
        result = controller.programState
        assert "PLAYING" in result.return_value

    @patch('URModbus.core.RobotController.ModbusRobot')
    @patch('URModbus.core.RobotController.DashRobot')
    def test_program_name_property(self, mock_dash_robot, mock_modbus_robot):
        """Test programName property extracts name from state."""
        mock_modbus_instance = MagicMock()
        
        mock_dash_instance = MagicMock()
        mock_dash_instance.programName = "welding_task"
        
        mock_modbus_robot.return_value = mock_modbus_instance
        mock_dash_robot.return_value = mock_dash_instance
        
        controller = RobotController(ip="192.168.1.10")
        
        assert controller.programName == "welding_task"


class TestEmergencyStop:
    """Test emergency stop property."""

    @patch('URModbus.core.RobotController.ModbusRobot')
    @patch('URModbus.core.RobotController.DashRobot')
    def test_is_emergency_stopped_property(self, mock_dash_robot, mock_modbus_robot):
        """Test isEmergencyStopped property returns boolean value."""
        mock_modbus_instance = MagicMock()
        mock_modbus_instance.read.return_value = 0  # False
        
        mock_dash_instance = MagicMock()
        
        mock_modbus_robot.return_value = mock_modbus_instance
        mock_dash_robot.return_value = mock_dash_instance
        
        controller = RobotController(ip="192.168.1.10")
        
        result = controller.isEmergencyStopped
        assert result == 0


class TestIpAddress:
    """Test ip property."""

    @patch('URModbus.core.RobotController.ModbusRobot')
    @patch('URModbus.core.RobotController.DashRobot')
    def test_ip_property(self, mock_dash_robot, mock_modbus_robot):
        """Test ip property returns the IP address."""
        mock_modbus_instance = MagicMock()
        
        mock_dash_instance = MagicMock()
        
        mock_modbus_robot.return_value = mock_modbus_instance
        mock_dash_robot.return_value = mock_dash_instance
        
        controller = RobotController(ip="192.168.1.10")
        
        result = controller.ip
        assert result == "192.168.1.10"


class TestGetCurrentTask:
    """Test get_current_task method."""

    @patch('URModbus.core.RobotController.ModbusRobot')
    @patch('URModbus.core.RobotController.DashRobot')
    def test_get_current_task(self, mock_dash_robot, mock_modbus_robot):
        """Test get_current_task returns current task from robot."""
        mock_modbus_instance = MagicMock()
        mock_modbus_instance.read.return_value = 5
        
        mock_dash_instance = MagicMock()
        
        mock_modbus_robot.return_value = mock_modbus_instance
        mock_dash_robot.return_value = mock_dash_instance
        
        controller = RobotController(ip="192.168.1.10")
        
        result = controller.get_current_task()
        assert result == 5


class TestAssignNewTask:
    """Test internal task assignment."""

    @patch('URModbus.core.RobotController.ModbusRobot')
    @patch('URModbus.core.RobotController.DashRobot')
    def test_assign_new_task_valid_int(self, mock_dash_robot, mock_modbus_robot):
        """Test assigning a valid int task."""
        mock_modbus_instance = MagicMock()
        
        mock_dash_instance = MagicMock()
        
        mock_modbus_robot.return_value = mock_modbus_instance
        mock_dash_robot.return_value = mock_dash_instance
        
        controller = RobotController(ip="192.168.1.10")
        
        controller._RobotController__assign_new_task(5)


class TestRemoveTask:
    """Test internal task removal."""

    @patch('URModbus.core.RobotController.ModbusRobot')
    @patch('URModbus.core.RobotController.DashRobot')
    def test_remove_task(self, mock_dash_robot, mock_modbus_robot):
        """Test removing first task from pile."""
        mock_modbus_instance = MagicMock()
        
        mock_dash_instance = MagicMock()
        
        mock_modbus_robot.return_value = mock_modbus_instance
        mock_dash_robot.return_value = mock_dash_instance
        
        controller = RobotController(ip="192.168.1.10")
        
        # Set up with tasks
        controller._RobotController__taskPile = [5, 3, 1]
        
        controller._RobotController__remove_task()
        
        assert controller.taskPile == [3, 1]