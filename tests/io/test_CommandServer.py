"""Test suite for URModbus io/CommandServer module."""

import pytest
from unittest.mock import patch, MagicMock, Mock
from pathlib import Path
import numpy as np
import tempfile



class TestTerminalServerInitialization:
    """Test TerminalServer initialization."""

    def test_init_with_all_parameters(self):
        """Test initialization with all parameters."""
        from URModbus.io.CommandServer import TerminalServer
        
        mock_ctrl = MagicMock()
        mock_trk = MagicMock()
        mock_proc = MagicMock()
        
        server = TerminalServer(
            controller=mock_ctrl,
            tracker=mock_trk,
            process=mock_proc,
            degraded=False,
            host="127.0.0.1",
            port=9999
        )
        
        assert isinstance(server, TerminalServer)  # Thread is mocked

    def test_init_with_degraded_mode(self):
        """Test initialization with degraded mode."""
        from URModbus.io.CommandServer import TerminalServer
        
        mock_ctrl = MagicMock()
        mock_trk = MagicMock()
        mock_proc = MagicMock()
        
        server = TerminalServer(
            controller=mock_ctrl,
            tracker=mock_trk,
            process=mock_proc,
            degraded=True,
            host="10.0.0.1",
            port=8888
        )
        
        assert isinstance(server, TerminalServer)


class TestParseCommand:
    """Test the internal __parse_command method."""

    def test_parse_simple_command(self):
        """Test parsing a simple command without arguments."""
        from URModbus.io.CommandServer import TerminalServer
        
        mock_ctrl = MagicMock()
        mock_trk = MagicMock()
        mock_proc = MagicMock()
        
        server = TerminalServer(mock_ctrl, mock_trk, mock_proc)
        
        cmd_name, args = server._TerminalServer__parse_command("status")
        
        assert cmd_name == "status"
        assert args == []

    def test_parse_command_with_args(self):
        """Test parsing command with arguments."""
        from URModbus.io.CommandServer import TerminalServer
        
        mock_ctrl = MagicMock()
        mock_trk = MagicMock()
        mock_proc = MagicMock()
        
        server = TerminalServer(mock_ctrl, mock_trk, mock_proc)
        
        cmd_name, args = server._TerminalServer__parse_command("add 5 -f")
        
        assert cmd_name == "add"
        assert set(args) == {"5", "-f"}

    def test_parse_empty_command(self):
        """Test parsing an empty command."""
        from URModbus.io.CommandServer import TerminalServer
        
        mock_ctrl = MagicMock()
        mock_trk = MagicMock()
        mock_proc = MagicMock()
        
        server = TerminalServer(mock_ctrl, mock_trk, mock_proc)
        
        cmd_name, args = server._TerminalServer__parse_command("   ")
        
        assert cmd_name is None
        assert args == []

    def test_parse_command_with_multiple_args(self):
        """Test parsing command with multiple arguments."""
        from URModbus.io.CommandServer import TerminalServer
        
        mock_ctrl = MagicMock()
        mock_trk = MagicMock()
        mock_proc = MagicMock()
        
        server = TerminalServer(mock_ctrl, mock_trk, mock_proc)
        
        cmd_name, args = server._TerminalServer__parse_command("gaussian -name Test 1 2")
        
        assert cmd_name == "gaussian"
        assert "-name" in args
        assert "Test" in args
        assert "1" in args
        assert "2" in args


class TestHandleCommand:
    """Test the internal __handle_command method."""
    
    def test_handle_status_command(self):
        """Test handling status command."""
        from URModbus.io.CommandServer import TerminalServer
        
        mock_ctrl = MagicMock()
        mock_ctrl.ip = "192.168.1.10"
        mock_ctrl.state = 5
        mock_ctrl.programState = "PLAYING test_program"
        mock_ctrl.isEmergencyStopped = False
        
        mock_proc = MagicMock()
        
        server = TerminalServer(mock_ctrl, MagicMock(), mock_proc)
        
        result = server._TerminalServer__handle_command("status", [])
        
        assert "Robot IP:" in result

    
    
    def test_handle_help_command(self):
        """Test handling help command."""
        from URModbus.io.CommandServer import TerminalServer
        
        mock_ctrl = MagicMock()
        mock_proc = MagicMock()
        
        server = TerminalServer(mock_ctrl, MagicMock(), mock_proc)
        
        result = server._TerminalServer__handle_command("help", [])
        
        assert "add" in result
        assert "clear" in result

    
    
    def test_handle_unknown_command(self):
        """Test handling unknown command."""
        from URModbus.io.CommandServer import TerminalServer
        
        mock_ctrl = MagicMock()
        mock_proc = MagicMock()
        
        server = TerminalServer(mock_ctrl, MagicMock(), mock_proc)
        
        result = server._TerminalServer__handle_command("unknown", [])
        
        assert "Unknown command" in result

    
    
    def test_handle_add_command_help(self):
        """Test add command with -h flag."""
        from URModbus.io.CommandServer import TerminalServer
        
        mock_ctrl = MagicMock()
        mock_proc = MagicMock()
        
        server = TerminalServer(mock_ctrl, MagicMock(), mock_proc)
        
        result = server._TerminalServer__handle_command("add", ["-h"])
        
        assert "This command allows you to add tasks" in result

    
    
    def test_handle_add_command_invalid_task(self):
        """Test add command with non-existent task."""
        from URModbus.io.CommandServer import TerminalServer
        
        mock_ctrl = MagicMock()
        mock_proc = MagicMock()
        mock_proc.isTaksInProcess.return_value = False
        
        server = TerminalServer(mock_ctrl, MagicMock(), mock_proc)
        
        result = server._TerminalServer__handle_command("add", ["5"])
        
        assert "not in the process file" in result

    
    
    def test_handle_add_command_with_force(self):
        """Test add command with -f flag."""
        from URModbus.io.CommandServer import TerminalServer
        
        mock_ctrl = MagicMock()
        mock_proc = MagicMock()
        mock_proc.isTaksInProcess.return_value = False
        
        server = TerminalServer(mock_ctrl, MagicMock(), mock_proc)
        
        result = server._TerminalServer__handle_command("add", ["5", "-f"])
        
        assert "added to pile" in result

    
    
    def test_handle_add_negative_task_id(self):
        """Test add command with negative task ID."""
        from URModbus.io.CommandServer import TerminalServer
        
        mock_ctrl = MagicMock()
        mock_proc = MagicMock()
        
        server = TerminalServer(mock_ctrl, MagicMock(), mock_proc)
        
        result = server._TerminalServer__handle_command("add", ["-5"])
        
        assert "positive integer" in result

    
    
    def test_handle_add_multiple_args(self):
        """Test add command with multiple task IDs."""
        from URModbus.io.CommandServer import TerminalServer
        
        mock_ctrl = MagicMock()
        mock_proc = MagicMock()
        
        server = TerminalServer(mock_ctrl, MagicMock(), mock_proc)
        
        result = server._TerminalServer__handle_command("add", ["1", "2"])
        
        assert "only add one task" in result

    
    
    def test_handle_clear_command(self):
        """Test clear command."""
        from URModbus.io.CommandServer import TerminalServer
        
        mock_ctrl = MagicMock()
        mock_proc = MagicMock()
        
        server = TerminalServer(mock_ctrl, MagicMock(), mock_proc)
        
        result = server._TerminalServer__handle_command("clear", [])
        
        assert "Cleared Tasks" in result

    
    
    def test_handle_clear_help(self):
        """Test clear command with -h flag."""
        from URModbus.io.CommandServer import TerminalServer
        
        mock_ctrl = MagicMock()
        mock_proc = MagicMock()
        
        server = TerminalServer(mock_ctrl, MagicMock(), mock_proc)
        
        result = server._TerminalServer__handle_command("clear", ["-h"])
        
        assert "This command allows you to clear" in result

import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def autogen_dir(monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.setattr(
            "URModbus.io.DataParser.Settings.AUTOGEN_DIR",
            tmpdir,
        )

        yield Path(tmpdir)
class TestGaussianCommand:

        
    """Test the gaussian command."""

    @patch("URModbus.io.DataParser.np.loadtxt")
    def test_gaussian_help(self, mock_loadtxt, autogen_dir):
        """Test gaussian help."""
        from URModbus.io.CommandServer import TerminalServer
        
        mock_loadtxt.return_value = np.array([
                                                    [1, 5.5],
                                                    [2, 6.0],
                                                    [3, 6.5],
                                                ])
        mock_ctrl = MagicMock()
        mock_proc = MagicMock()
        mock_proc.name = "Test_Process"
        mock_proc.ordering = [1]

        task = MagicMock()
        task.name = "Task 1"
        mock_proc.get_task.return_value = task
        
        server = TerminalServer(mock_ctrl, MagicMock(), mock_proc)
        
        result = server._TerminalServer__handle_command("gaussian", ["-h"])
        
        assert "This command allows you to draw" in result

    @patch("URModbus.io.DataParser.np.loadtxt")
    def test_gaussian_with_name_flag(self,mock_loadtxt, autogen_dir):
        """Test gaussian with -name flag."""
        from URModbus.io.CommandServer import TerminalServer
        
        mock_loadtxt.return_value = np.array([
                                                    [1, 5.5],
                                                    [2, 6.0],
                                                    [3, 6.5],
                                                ])
        mock_ctrl = MagicMock()
        mock_proc = MagicMock()
        mock_proc.name = "Test_Process"
        mock_proc.ordering = [1]
        mock_proc.tasks = [0,1]

        task = MagicMock()
        task.name = "Task 1"
        mock_proc.get_task.return_value = task
        
        server = TerminalServer(mock_ctrl, MagicMock(), mock_proc)
        result = server._TerminalServer__handle_command("gaussian", ["-name", "Test Plot"])
        
        assert "Saved as gaussian" in result


    @patch("URModbus.io.DataParser.np.loadtxt")
    def test_gaussian_with_tasks(self, mock_loadtxt, autogen_dir):
        """Test gaussian with task IDs."""
        from URModbus.io.CommandServer import TerminalServer
        
        mock_loadtxt.return_value = np.array([
                                                            [1, 5.5],
                                                            [2, 6.0],
                                                            [3, 6.5],
                                                        ])
        mock_ctrl = MagicMock()
        mock_proc = MagicMock()
        mock_proc.name = "Test_Process"
        mock_proc.ordering = [1,2]
        mock_proc.tasks = [0,1,2]
        mock_proc.isTaksInProcess.return_value = True

        task = MagicMock()
        task.name = "Task 1"
        mock_proc.get_task.return_value = task
        
        server = TerminalServer(mock_ctrl, MagicMock(), mock_proc)
        
        result = server._TerminalServer__handle_command("gaussian", ["1", "2"])
        
        assert "Saved as gaussian" in result

    
    
    def test_gaussian_invalid_task(self):
        """Test gaussian with invalid task ID."""
        from URModbus.io.CommandServer import TerminalServer
        
        mock_ctrl = MagicMock()
        mock_proc = MagicMock()
        mock_proc.isTaksInProcess.return_value = False
        
        server = TerminalServer(mock_ctrl, MagicMock(), mock_proc)
        
        result = server._TerminalServer__handle_command("gaussian", ["5"])
        
        assert "not in the process file" in result

    
    
    def test_gaussian_negative_task(self):
        """Test gaussian with negative task ID."""
        from URModbus.io.CommandServer import TerminalServer
        
        mock_ctrl = MagicMock()
        mock_proc = MagicMock()
        
        server = TerminalServer(mock_ctrl, MagicMock(), mock_proc)
        
        result = server._TerminalServer__handle_command("gaussian", ["-1"])
        
        assert "positive integer" in result


class TestSequenceCommand:
    """Test the sequence command."""

    
    
    def test_sequence_help(self):
        """Test sequence help."""
        from URModbus.io.CommandServer import TerminalServer
        
        mock_ctrl = MagicMock()
        mock_proc = MagicMock()
        
        server = TerminalServer(mock_ctrl, MagicMock(), mock_proc)
        
        result = server._TerminalServer__handle_command("sequence", ["-h"])
        
        assert "This command allows you to add" in result

    
    
    def test_sequence_with_tasks(self):
        """Test sequence with valid tasks."""
        from URModbus.io.CommandServer import TerminalServer
        
        mock_ctrl = MagicMock()
        mock_proc = MagicMock()
        mock_proc.name = "Test_Process"
        mock_proc.ordering = [1,2]
        mock_proc.tasks = [0,1,2]
        mock_proc.isTaksInProcess.return_value = True

        task = MagicMock()
        task.name = "Task 1"
        mock_proc.get_task.return_value = task
        
        server = TerminalServer(mock_ctrl, MagicMock(), mock_proc)
        
        result = server._TerminalServer__handle_command("sequence", ["1", "2"])
        
        assert "added to pile" in result

    
    
    def test_sequence_with_force(self):
        """Test sequence with -f flag."""
        from URModbus.io.CommandServer import TerminalServer
        
        mock_ctrl = MagicMock()
        mock_proc = MagicMock()
        mock_proc.isTaksInProcess.return_value = False
        
        server = TerminalServer(mock_ctrl, MagicMock(), mock_proc)
        
        result = server._TerminalServer__handle_command("sequence", ["1", "-f"])
        
        assert "added to pile" in result


class TestProgramControlCommands:
    """Test program control commands (play, pause, stop)."""

    
    
    def test_play_command(self):
        """Test play command."""
        from URModbus.io.CommandServer import TerminalServer
        
        mock_ctrl = MagicMock()
        mock_proc = MagicMock()
        
        server = TerminalServer(mock_ctrl, MagicMock(), mock_proc)
        
        result = server._TerminalServer__handle_command("play", [])
        
        assert "Bot started" in result

    
    
    def test_pause_command(self):
        """Test pause command."""
        from URModbus.io.CommandServer import TerminalServer
        
        mock_ctrl = MagicMock()
        mock_proc = MagicMock()
        
        server = TerminalServer(mock_ctrl, MagicMock(), mock_proc)
        
        result = server._TerminalServer__handle_command("pause", [])
        
        assert "Bot paused" in result

    
    
    def test_stop_command(self):
        """Test stop command."""
        from URModbus.io.CommandServer import TerminalServer
        
        mock_ctrl = MagicMock()
        mock_proc = MagicMock()
        
        server = TerminalServer(mock_ctrl, MagicMock(), mock_proc)
        
        result = server._TerminalServer__handle_command("stop", [])
        
        assert "Bot stopped" in result


class TestLoadCommand:
    """Test the load command."""

    
    
    def test_load_help(self):
        """Test load help."""
        from URModbus.io.CommandServer import TerminalServer
        
        mock_ctrl = MagicMock()
        mock_proc = MagicMock()
        
        server = TerminalServer(mock_ctrl, MagicMock(), mock_proc)
        
        result = server._TerminalServer__handle_command("load", ["-h"])
        
        assert "This command allows you to load" in result

    
    
    def test_load_help(self):
        """Test process help."""
        from URModbus.io.CommandServer import TerminalServer
        
        mock_ctrl = MagicMock()
        mock_proc = MagicMock()
        
        server = TerminalServer(mock_ctrl, MagicMock(), mock_proc)
        
        result = server._TerminalServer__handle_command("process", ["-h"])
        
        assert "This command allows you to display" in result

    
    
    def test_process_command(self):
        """Test process command."""
        from URModbus.io.CommandServer import TerminalServer
        
        mock_ctrl = MagicMock()
        mock_proc = MagicMock()
        mock_proc.name = "Assembly Process"
        
        server = TerminalServer(mock_ctrl, MagicMock(), mock_proc)
        
        result = server._TerminalServer__handle_command("process", [])
        
        assert "Assembly Process" in result


class TestInfoCommand:
    """Test the info command."""

    
    
    def test_info_help(self):
        """Test info help."""
        from URModbus.io.CommandServer import TerminalServer
        
        mock_ctrl = MagicMock()
        mock_proc = MagicMock()
        
        server = TerminalServer(mock_ctrl, MagicMock(), mock_proc)
        
        result = server._TerminalServer__handle_command("info", ["-h"])
        
        assert "This command allows you to display" in result

    
    
    def test_info_with_task(self):
        """Test info with valid task."""
        from URModbus.io.CommandServer import TerminalServer
        
        mock_ctrl = MagicMock()
        mock_proc = MagicMock()
        
        server = TerminalServer(mock_ctrl, MagicMock(), mock_proc)
        
        result = server._TerminalServer__handle_command("info", ["5"])
        
        assert result


class TestStatsCommand:
    """Test the stats command."""

    
    
    def test_stats_help(self):
        """Test stats help."""
        from URModbus.io.CommandServer import TerminalServer
        
        mock_ctrl = MagicMock()
        mock_proc = MagicMock()
        
        server = TerminalServer(mock_ctrl, MagicMock(), mock_proc)
        
        result = server._TerminalServer__handle_command("stats", ["-h"])
        
        assert "This command allows you to obtain" in result

    
    
    def test_stats_full(self):
        """Test stats with -full flag."""
        from URModbus.io.CommandServer import TerminalServer
        
        mock_ctrl = MagicMock()
        mock_proc = MagicMock()
        
        server = TerminalServer(mock_ctrl, MagicMock(), mock_proc)
        
        result = server._TerminalServer__handle_command("stats", ["-full"])
        
        assert "General Process data" in result

    
    
    def test_stats_both_flags_invalid(self):
        """Test stats with both flags (invalid)."""
        from URModbus.io.CommandServer import TerminalServer
        
        mock_ctrl = MagicMock()
        mock_proc = MagicMock()
        
        server = TerminalServer(mock_ctrl, MagicMock(), mock_proc)
        
        result = server._TerminalServer__handle_command("stats", ["-full", "-p"])
        
        assert "Can only use -p or -full" in result


class TestDegradedMode:
    """Test degraded mode behavior."""

    
    
    def test_degraded_add_command_unavailable(self):
        """Test that add command is unavailable in degraded mode."""
        from URModbus.io.CommandServer import TerminalServer
        
        mock_ctrl = MagicMock()
        mock_proc = MagicMock()
        
        server = TerminalServer(mock_ctrl, MagicMock(), mock_proc, degraded=True)
        
        result = server._TerminalServer__handle_command("add", ["5"])
        
        assert "not avaliable in degraded mode" in result

    
    
    def test_degraded_clear_command_unavailable(self):
        """Test that clear command is unavailable in degraded mode."""
        from URModbus.io.CommandServer import TerminalServer
        
        mock_ctrl = MagicMock()
        mock_proc = MagicMock()
        
        server = TerminalServer(mock_ctrl, MagicMock(), mock_proc, degraded=True)
        
        result = server._TerminalServer__handle_command("clear", [])
        
        assert "not avaliable in degraded mode" in result


class TestWelcomeMessage:
    """Test welcome message display."""

    
    
    def test_welcome_message_structure(self):
        """Test that welcome message is properly structured."""
        from URModbus.io.CommandServer import TerminalServer
        
        mock_ctrl = MagicMock()
        mock_proc = MagicMock()
        
        server = TerminalServer(mock_ctrl, MagicMock(), mock_proc)
        
        assert hasattr(server, '_TerminalServer__welcome')

    
    
    def test_degraded_welcome_message(self):
        """Test that degraded mode adds note to welcome."""
        from URModbus.io.CommandServer import TerminalServer
        
        mock_ctrl = MagicMock()
        mock_proc = MagicMock()
        
        server = TerminalServer(mock_ctrl, MagicMock(), mock_proc, degraded=True)
        
        assert hasattr(server, '_TerminalServer__welcome')
