"""Test suite for URModbus app/main module."""

import pytest
from unittest.mock import patch, MagicMock, Mock
import os
from threading import Thread
from time import sleep

from URModbus.app.main import run
from URModbus.core.RobotController import RobotController
from URModbus.core.TimeTracker import TimeTracker
from URModbus.core.ProcessTools import Process
from URModbus.io.CommandServer import TerminalServer
from URModbus.config.constants import Settings

import pytest
import threading

#This fixture will prevent real threads to start.
#Necessary to prevent infinite runs
@pytest.fixture(autouse=True, scope="module")
def prevent_threads():
    with patch("threading.Thread.start"):
        yield

class TestAppRunInitialization:
    """Test app run initialization."""

    @patch("URModbus.app.main.subprocess")
    def test_run_prints_logo(self, mock_subprocess):

        mock_subprocess.Popen.side_effect = SystemExit()

        with patch("builtins.print") as mock_print:
            
            with pytest.raises(SystemExit):
                run()

        assert mock_print.called


    @patch('URModbus.app.main.RobotController')
    @patch('URModbus.app.main.subprocess')
    def test_run_detects_local_vs_remote(self, mock_subprocess, mock_controller):
        """Test that run() correctly detects Docker container presence."""
        # Mock subprocess to indicate running locally (container exists)
        mock_check = MagicMock()
        mock_check.stdout.read.return_value.decode.return_value.strip.return_value = Settings.CONTAINER
        mock_ping = MagicMock()
        mock_ping.stdout.strip.return_value = "ms"
        mock_subprocess.Popen.return_value = mock_check
        mock_subprocess.run.return_value = mock_ping

        mock_controller.side_effect = SystemExit

        with patch('URModbus.app.main.platform') as mock_platform:
            # Mock platform to return Linux (not Windows)
            mock_platform.system.return_value = "Linux"

            with pytest.raises(SystemExit):
                run()

            # Run should set CONTROLLER to True since container exists and not on Windows
            assert Settings.UR5_IP == Settings.CONTAINER #Like this because of the mock before


class TestAppRunWithoutController:
    """Test app run without robot controller (degraded mode)."""

    @patch('URModbus.app.main.sleep')
    @patch('URModbus.app.main.subprocess')
    @patch('URModbus.app.main.platform')
    def test_run_without_controller_uses_degraded_mode(self, mock_platform, mock_subprocess, mock_sleep):
        """Test that run() operates in degraded mode when controller is not available."""
        # Mock subprocess to indicate no container (running on real robot)
        mock_check = MagicMock()
        mock_check.stdout.read.return_value.decode.return_value.strip.return_value = Settings.CONTAINER

        mock_subprocess.Popen.return_value = mock_check

        mock_platform.system.return_value = "Linux"
        
        # Mock ping to fail (no controller)
        mock_ping_result = MagicMock()
        mock_ping_result.stdout.strip.return_value = ""  # No time found
        mock_ping_result.returncode = 1
        mock_subprocess.run.return_value = mock_ping_result

        mock_sleep.side_effect = SystemExit()


        with patch('builtins.print') as mock_print:
            
            with pytest.raises(SystemExit):
                            run()

            # Should print that controller is not reachable
            assert any("not reachable" in str(call.args).lower() for call in mock_print.call_args_list)


class TestAppRunWithController:
    """Test app run with robot controller."""

    @patch('URModbus.app.main.subprocess')
    @patch('URModbus.app.main.platform')
    def test_run_with_controller_uses_full_mode(self, mock_platform, mock_subprocess):
        """Test that run() operates in full mode when controller is available."""
        # Mock subprocess to indicate container exists (running locally)
        mock_check = MagicMock()
        mock_check.stdout.read.return_value.decode.return_value.strip.return_value = "192.168.1.10"
        mock_subprocess.Popen.return_value = mock_check

        mock_platform.system.return_value = "Linux"
        
        # Mock ping to succeed
        mock_ping_result = MagicMock()
        mock_ping_result.stdout.strip.return_value = "64 bytes from 192.168.1.10: time=1.2 ms"
        mock_ping_result.returncode = 0
        mock_subprocess.run.return_value = mock_ping_result

        with patch('URModbus.app.main.RobotController') as mock_ctrl:
            # Mock the controller to return program name
            mock_controller_instance = MagicMock()
            mock_controller_instance.programName = "test"
            mock_ctrl.return_value = mock_controller_instance
            mock_controller_instance.get_current_task.side_effect = SystemExit()

            with patch('URModbus.app.main.TimeTracker'):
                with patch('builtins.print') as mock_print:
                    with pytest.raises(SystemExit):
                        run()

                    # Controller should be created
                    assert mock_ctrl.called
                    # If we end up here, controller attempted to contact emergency stop
                    # And in doing so SysExit
                    assert mock_controller_instance.get_current_task.called

class TestAppRunProcessLoading:
    """Test app run process loading logic."""

    @patch('URModbus.app.main.subprocess')
    @patch('URModbus.app.main.platform')
    def test_run_autoload_process_from_controller(self, mock_platform, mock_subprocess):
        """Test that run() autoloads process from controller when available."""
        # Mock subprocess to indicate container exists
        mock_check = MagicMock()
        mock_check.stdout.read.return_value.decode.return_value.strip.return_value = "192.168.1.10"
        mock_subprocess.Popen.return_value = mock_check

        mock_platform.system.return_value = "Linux"
        
        # Mock ping to succeed
        mock_ping_result = MagicMock()
        mock_ping_result.stdout.strip.return_value = "64 bytes from 192.168.1.10: time=1.2 ms"
        mock_ping_result.returncode = 0
        mock_subprocess.run.return_value = mock_ping_result

        with patch('URModbus.app.main.RobotController') as mock_ctrl:
            # Mock controller with a loaded program
            mock_controller_instance = MagicMock()
            mock_controller_instance.programName = "auto_test.urp"
            mock_ctrl.return_value = mock_controller_instance
            
            with patch('URModbus.app.main.Settings') as mock_settings:
                mock_settings.AUTO_LOAD = True
                mock_settings.CONTAINER = "ursim"
                mock_settings.DATA_DIR = "test_dir"

                with patch('os.path.exists') as mock_read:
                    mock_read.side_effect = SystemExit()
                    with pytest.raises(SystemExit):
                        run()

                    mock_read.assert_called_once_with(
                        f"{mock_settings.DATA_DIR}/auto_test.yaml"
                    )

    @patch('URModbus.app.main.subprocess')
    @patch('URModbus.app.main.platform')
    def test_run_fallback_to_test_file_when_no_controller(self, mock_platform, mock_subprocess):
        """Test that run() falls back to test file when controller is not available."""
        # Mock subprocess to indicate no container (running on real robot)
        mock_check = MagicMock()
        mock_check.stdout.read.return_value.decode.return_value.strip.return_value = ""
        mock_subprocess.Popen.return_value = mock_check

        mock_platform.system.return_value = "Linux"
        
        # Mock ping to fail (no controller)
        mock_ping_result = MagicMock()
        mock_ping_result.stdout.strip.return_value = ""  # No time found, bot is dead
        mock_ping_result.returncode = 1
        mock_subprocess.run.return_value = mock_ping_result

        with patch('URModbus.app.main.RobotController'):
            with patch('URModbus.app.main.Settings') as mock_settings:
                mock_settings.AUTO_LOAD = True
                mock_settings.CONTAINER = "ursim"
                mock_settings.TEST_FILE = "test.yaml"
                mock_settings.PROCESS_FILE = "data.yaml"
                mock_settings.DATA_DIR = "./data"

                with patch('URModbus.app.main.read_data_file') as mock_read:
                    mock_read.side_effect = SystemExit()
                    with pytest.raises(SystemExit):
                        run()

                    mock_read.assert_called_once_with(
                        f"{mock_settings.PROCESS_FILE}"
                    )

class TestAppRunTerminalServer:
    """Test app run terminal server initialization."""

    @patch('URModbus.app.main.subprocess')
    @patch('URModbus.app.main.platform')
    def test_run_starts_terminal_server(self, mock_platform, mock_subprocess):
        """Test that run() starts TerminalServer with proper parameters."""
        # Mock subprocess to indicate container exists
        mock_check = MagicMock()
        mock_check.stdout.read.return_value.decode.return_value.strip.return_value = "192.168.1.10"
        mock_subprocess.Popen.return_value = mock_check

        mock_platform.system.return_value = "Linux"
        
        # Mock ping to succeed
        mock_ping_result = MagicMock()
        mock_ping_result.stdout.strip.return_value = "64 bytes from 192.168.1.10: time=1.2 ms"
        mock_ping_result.returncode = 0
        mock_subprocess.run.return_value = mock_ping_result

        with patch('URModbus.app.main.RobotController') as mock_ctrl:
            # Mock the controller
            mock_controller_instance = MagicMock()
            mock_controller_instance.programName = "test"
            mock_ctrl.return_value = mock_controller_instance
            mock_controller_instance.get_current_task.side_effect = SystemExit()


            with patch('URModbus.app.main.TimeTracker') as mock_tracker:
                # Mock tracker
                mock_tracker_instance = MagicMock()
                mock_tracker.return_value = mock_tracker_instance

                with patch('URModbus.app.main.TerminalServer') as mock_terminal:
                    # Terminal server should be created with degraded=False (controller available)
                    mock_terminal_instance = MagicMock()
                    mock_terminal.return_value = mock_terminal_instance

                    with patch('signal.signal'):
                        with patch('builtins.print'):
                            with pytest.raises(SystemExit):
                                run()

                            # Verify terminal was called with correct parameters
                            assert mock_terminal.called


class TestAppRunSignalHandlers:
    """Test app run signal handlers."""

    @patch('URModbus.app.main.subprocess')
    @patch('URModbus.app.main.platform')
    def test_run_sets_signal_handler_with_controller(self, mock_platform, mock_subprocess):
        """Test that run() sets correct signal handler when controller is available."""
        # Mock subprocess to indicate container exists
        mock_check = MagicMock()
        mock_check.stdout.read.return_value.decode.return_value.strip.return_value = ""
        mock_subprocess.Popen.return_value = mock_check

        mock_platform.system.return_value = "Linux"
        
        # Mock ping to succeed
        mock_ping_result = MagicMock()
        mock_ping_result.stdout.strip.return_value = "64 bytes from 192.168.1.10: time=1.2 ms"
        mock_ping_result.returncode = 0
        mock_subprocess.run.return_value = mock_ping_result

        with patch('URModbus.app.main.RobotController') as mock_ctrl:
            # Mock the controller
            mock_controller_instance = MagicMock()
            mock_controller_instance.get_current_task.side_effect = SystemExit()

            mock_ctrl.return_value = mock_controller_instance

            with patch('builtins.print') as mock_print:
                with pytest.raises(SystemExit):
                    run()

                # Should print controller startup message
                assert any('successfully booted up !' in str(call.args).lower() for call in mock_print.call_args_list)

    @patch('URModbus.app.main.sleep')
    @patch('URModbus.app.main.subprocess')
    @patch('URModbus.app.main.platform')
    def test_run_sets_signal_handler_without_controller(self, mock_platform, mock_subprocess, mock_sleep):
        """Test that run() sets minimal signal handler when controller is not available."""
        # Mock subprocess to indicate no container (running on real robot)
        mock_check = MagicMock()
        mock_check.stdout.read.return_value.decode.return_value.strip.return_value = ""
        mock_subprocess.Popen.return_value = mock_check

        mock_platform.system.return_value = "Linux"
        
        # Mock ping to fail (no controller)
        mock_ping_result = MagicMock()
        mock_ping_result.stdout.strip.return_value = ""  # No time found
        mock_ping_result.returncode = 1
        mock_subprocess.run.return_value = mock_ping_result

        mock_sleep.side_effect = SystemExit()

        with patch('URModbus.app.main.TerminalServer') as mock_terminal:
            # Mock terminal server
            mock_terminal_instance = MagicMock()
            mock_terminal.return_value = mock_terminal_instance

            with patch('builtins.print') as mock_print:
                with pytest.raises(SystemExit):
                    run()

                # Should print minimal mode message
                assert any("booted in minimal mode" in str(call.args).lower() for call in mock_print.call_args_list)


class TestAppRunAutoMode:
    """Test app run auto mode behavior."""

    @patch('URModbus.app.main.subprocess')
    @patch('URModbus.app.main.platform')
    def test_run_auto_mode_prints_start_sequence(self, mock_platform, mock_subprocess):
        """Test that run() prints auto mode startup sequence."""
        # Bypass container
        mock_check = MagicMock()
        mock_check.stdout.read.return_value.decode.return_value.strip.return_value = "192.168.1.10"
        mock_subprocess.Popen.return_value = mock_check

        mock_platform.system.return_value = "Linux"
        
        # Mock ping to succeed
        mock_ping_result = MagicMock()
        mock_ping_result.stdout.strip.return_value = "64 bytes from 192.168.1.10: time=1.2 ms"
        mock_ping_result.returncode = 0
        mock_subprocess.run.return_value = mock_ping_result

        with patch('URModbus.app.main.RobotController') as mock_ctrl:
            # Mock the controller to return program name
            mock_controller_instance = MagicMock()
            mock_controller_instance.programName = "test"
            mock_ctrl.return_value = mock_controller_instance
            mock_controller_instance.get_current_task.side_effect = SystemExit()

            with patch('URModbus.app.main.TimeTracker'):
                with patch('builtins.print') as mock_print:
                    with pytest.raises(SystemExit):
                        run()
                    assert any("automated sequence" in str(call.args).lower() for call in mock_print.call_args_list)


    @patch('URModbus.app.main.subprocess')
    @patch('URModbus.app.main.platform')
    def test_run_auto_mode_uses_process_ordering(self, mock_platform, mock_subprocess):
        """Test that run() uses process ordering when running in AUTO mode."""
        # Mock subprocess to indicate container exists
        mock_check = MagicMock()
        mock_check.stdout.read.return_value.decode.return_value.strip.return_value = "192.168.1.10"
        mock_subprocess.Popen.return_value = mock_check

        mock_platform.system.return_value = "Linux"
        
        # Mock ping to succeed
        mock_ping_result = MagicMock()
        mock_ping_result.stdout.strip.return_value = "64 bytes from 192.168.1.10: time=1.2 ms"
        mock_ping_result.returncode = 0
        mock_subprocess.run.return_value = mock_ping_result

        with patch('URModbus.app.main.RobotController') as mock_ctrl:
            # Mock the controller to return program name
            mock_controller_instance = MagicMock()
            mock_controller_instance.programName = "test"
            mock_ctrl.return_value = mock_controller_instance
            mock_controller_instance.get_current_task.side_effect = SystemExit()

            with patch('URModbus.app.main.TimeTracker'):
                with patch('builtins.print') as mock_print:
                    with pytest.raises(SystemExit):
                        run()
                    assert any("sequence" in str(call.args).lower() for call in mock_print.call_args_list)


class TestAppRunTaskExecution:
    """Test app run task execution loop."""

    @patch('URModbus.app.main.subprocess')
    @patch('URModbus.app.main.platform')
    def test_run_handles_task_execution(self, mock_platform, mock_subprocess):
        """Test that run() handles task execution correctly."""
        # Mock subprocess to indicate container exists
        mock_check = MagicMock()
        mock_check.stdout.read.return_value.decode.return_value.strip.return_value = "192.168.1.10"
        mock_subprocess.Popen.return_value = mock_check

        mock_platform.system.return_value = "Linux"
        
        # Mock ping to succeed
        mock_ping_result = MagicMock()
        mock_ping_result.stdout.strip.return_value = "64 bytes from 192.168.1.10: time=1.2 ms"
        mock_ping_result.returncode = 0
        mock_subprocess.run.return_value = mock_ping_result

        with patch('URModbus.app.main.RobotController') as mock_ctrl:
            # Mock the controller
            mock_controller_instance = MagicMock()
            
            # Configure controller to have no tasks initially (idle)
            mock_controller_instance.hasTask = False
            mock_controller_instance.state = "IDLE"
            mock_controller_instance.programState = "STOPPED"
            mock_ctrl.return_value = mock_controller_instance
            mock_controller_instance.follow_sequence.side_effect = SystemExit()

            with patch('URModbus.app.main.Settings') as mock_settings:
                mock_settings.MODE = "AUTO"
                mock_settings.ROBOT_SLEEP_TIME = 0.1
                mock_settings.CONTAINER = "ursim"
                mock_settings.PROCESS_FILE="data.yaml"

                # Mock subprocess.Popen for sleep to return immediately
                with patch('time.sleep', side_effect=lambda x: None):
                    with patch('builtins.print') as mock_print:
                        with pytest.raises(SystemExit):
                            run()

                        # Should handle task execution loop
                        assert mock_controller_instance.follow_sequence.called


class TestAppRunEmergencyStop:
    """Test app run emergency stop handling."""

    @patch('URModbus.app.main.subprocess')
    @patch('URModbus.app.main.platform')
    def test_run_handles_emergency_stop(self, mock_platform, mock_subprocess):
        """Test that run() handles emergency stop correctly."""
        # Mock subprocess to indicate container exists
        mock_check = MagicMock()
        mock_check.stdout.read.return_value.decode.return_value.strip.return_value = "192.168.1.10"
        mock_subprocess.Popen.return_value = mock_check


        mock_platform.system.return_value = "Linux"
        
        # Mock ping to succeed
        mock_ping_result = MagicMock()
        mock_ping_result.stdout.strip.return_value = "64 bytes from 192.168.1.10: time=1.2 ms"
        mock_ping_result.returncode = 0
        mock_subprocess.run.return_value = mock_ping_result

        with patch('URModbus.app.main.RobotController') as mock_ctrl:
            # Mock the controller
            mock_controller_instance = MagicMock()
            
            # Configure controller to have no tasks initially (idle)
            mock_controller_instance.hasTask = True
            mock_controller_instance.isEmergencyStopped = True
            mock_ctrl.return_value = mock_controller_instance
            mock_controller_instance.get_current_task.return_value = 0
            mock_controller_instance.clear_task_pile.side_effect = SystemExit()

            with patch('URModbus.app.main.Settings') as mock_settings:
                mock_settings.MODE = "AUTO"
                mock_settings.ROBOT_SLEEP_TIME = 0.1
                mock_settings.CONTAINER = "ursim"
                mock_settings.PROCESS_FILE="data.yaml"

                # Mock subprocess.Popen for sleep to return immediately
                with patch('time.sleep', side_effect=lambda x: None):
                    with patch('builtins.print') as mock_print:
                        with pytest.raises(SystemExit):
                            run()

                        # Should handle emergency stop gracefully
                        assert any("Emergency" in str(call.args) for call in mock_print.call_args_list)
