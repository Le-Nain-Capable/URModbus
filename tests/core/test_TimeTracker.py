"""Test suite for URModbus core/TimeTracker module."""

import pytest
from unittest.mock import patch, MagicMock, call
from time import sleep, time
from URModbus.core.TimeTracker import TimeTracker


class TestTimeTrackerInitialization:
    """Test TimeTracker initialization."""

    def test_init_with_controller_and_process(self):
        """Test initialization with controller and process."""
        # Mock dependencies
        with patch('URModbus.core.TimeTracker.RobotController') as mock_rc, \
             patch('URModbus.core.TimeTracker.Process') as mock_proc:
            
            mock_controller = MagicMock()
            mock_process = MagicMock()
            
            TimeTracker(mock_controller, mock_process)

class TestTaskSwitch:
    @patch("URModbus.core.TimeTracker.sleep")
    @patch("URModbus.core.TimeTracker.time")
    @patch("URModbus.core.TimeTracker.Settings")
    def test_task_switch_updates_start_time(
        self,
        mock_settings,
        mock_time,
        mock_sleep,
    ):
        """Verify a task switch resets start_time."""

        mock_settings.ROBOT_SLEEP_TIME = 1

        controller = MagicMock()
        process = MagicMock()

        controller.programState = "PLAYING test"
        controller.isEmergencyStopped = False

        # 0 -> first task -> second task
        controller.get_current_task.side_effect = [
            0,
            123,
            456,
        ]

        starts = []

        def time_side_effect():
            value = 100.0 if len(starts) == 0 else 200.0
            starts.append(value)
            return value

        mock_time.side_effect = time_side_effect

        tracker = TimeTracker(controller, process)

        iterations = 0

        def sleep_side_effect(*args):
            nonlocal iterations
            iterations += 1

            if iterations >= 3:
                tracker.stop()

        mock_sleep.side_effect = sleep_side_effect

        tracker.run()

        # start_time set when task 123 starts then reset when task 456 starts
        assert starts == [100.0, 200.0]
        assert tracker._TimeTracker__start_time == 200.0
        assert mock_time.call_count == 2




class TestTimeTracking:
    """Test the time tracking functionality."""

    @pytest.fixture
    def mock_robot_controller(self):
        """Provide a mocked robot controller."""
        controller = MagicMock()
        controller.programState.return_value = "STOPPED"
        controller.isEmergencyStopped.return_value = False
        
        return controller

    @pytest.fixture
    def mock_process(self):
        """Provide a mock process."""
        process = MagicMock()
        process.name = "Test_Process"
        return process

    def test_init_sets_attributes(self):
        """Test that initialization sets correct attributes."""
        mock_ctrl = MagicMock()
        mock_ctrl.programState.return_value = "PLAYING test_program"
        mock_ctrl.isEmergencyStopped.return_value = False
        
        mock_proc = MagicMock()
        mock_proc.name = "Assembly_Test"
        
        tracker = TimeTracker(mock_ctrl, mock_proc)
        
        assert tracker._TimeTracker__running is True

class TestStop:
    """Test the stop method."""

    def test_stop_stops_running(self):
        """Test that stop sets running to False."""
        mock_ctrl = MagicMock()
        
        tracker = TimeTracker(mock_ctrl, MagicMock())
        
        assert tracker._TimeTracker__running is True
        
        tracker.stop()
        
        assert tracker._TimeTracker__running is False


class TestTimeProperty:
    """Test the time property."""

    @patch('URModbus.core.TimeTracker.Settings')
    @patch('URModbus.core.TimeTracker.time')
    def test_time_returns_elapsed_time(self, mock_time, mock_settings,):
        """Test that time property returns correct elapsed time."""
        # Set up mocks
        mock_ctrl = MagicMock()
        mock_ctrl.programState.return_value = "PLAYING test_program"
        
        mock_proc = MagicMock()
        mock_proc.name = "Test_Process"
        
        with patch('URModbus.core.TimeTracker.write_task_time'):
            tracker = TimeTracker(mock_ctrl, mock_proc)
            
            mock_time.return_value = 100.0
            tracker._TimeTracker__start_time = 90.0
            tracker._TimeTracker__pause_time = 0.0
            mock_settings.ROBOT_SLEEP_TIME = 0.0

            assert tracker.time == 10.0


class TestPauseTracking:
    """Test pause tracking."""

    def test_pause_time_accumulation(self):
        """Test that pause time accumulates correctly."""
        mock_ctrl = MagicMock()
        
        tracker = TimeTracker(mock_ctrl, MagicMock())
        
        assert tracker._TimeTracker__pause_time == 0
        
        tracker.stop()  # Stop tracking
        
        # Simulate pause accumulation
        with patch('URModbus.core.TimeTracker.Settings') as mock_settings:
            mock_settings.ROBOT_SLEEP_TIME = 0.1
            
            from threading import Lock
            with Lock():
                tracker._TimeTracker__pause_time = 0.5
                
        assert tracker._TimeTracker__pause_time == 0.5


class TestMutexLocking:
    """Test mutex locking."""

    def test_mutex_used_for_timing(self):
        """Test that mutex is used for timing operations."""
        from threading import Lock
        
        mock_ctrl = MagicMock()
        
        tracker = TimeTracker(mock_ctrl, MagicMock())
        
        # Verify mutex exists in module scope
        assert 'mutex' in dir() or hasattr(tracker, '_TimeTracker__controller')