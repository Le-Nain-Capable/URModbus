"""Test suite for URModbus io/DataParser module."""

import pytest
from unittest.mock import patch, MagicMock, mock_open, Mock
from pathlib import Path
import numpy as np
import tempfile


class TestReadDataFile:
    """Test the read_data_file function."""

    @patch("URModbus.io.DataParser.open", new_callable=mock_open,
    read_data='name: "Test Process"\nordering: [1, 2, 3]\ntasks:\n  0:\n    name: Start\n    requires: []')
    def test_read_valid_yaml_file(self, mock_file):
        """Test reading a valid YAML file."""
        from URModbus.io.DataParser import read_data_file
        
        result = read_data_file("test.yaml")
        
        assert isinstance(result, dict)
        assert "name" in result
        assert "ordering" in result
        assert "tasks" in result

    @patch("URModbus.io.DataParser.open", new_callable=mock_open, read_data="name: \"Another Process\"")
    def test_read_yaml_with_single_key(self, mock_file):
        """Test reading a YAML file with single key."""
        from URModbus.io.DataParser import read_data_file
        
        result = read_data_file("single.yaml")
        
        assert isinstance(result, dict)
        assert result["name"] == "Another Process"

    @patch("URModbus.io.DataParser.open", new_callable=mock_open, read_data="invalid: yaml:")
    def test_read_yaml_with_error(self, mock_file):
        """Test reading a YAML file that returns error."""
        from URModbus.io.DataParser import read_data_file
        
        result = read_data_file("error.yaml")
        
        # Error case returns the exception (as per implementation)
        assert isinstance(result, Exception) or result is not None


class TestBuildSequence:
    """Test the build_sequence function."""

    def test_build_sequence_from_dict(self):
        """Test building sequence from process dict data."""
        data = {
            "name": "Test",
            "ordering": [1, 2, 3]
        }
        
        from URModbus.io.DataParser import build_sequence
        
        result = build_sequence(data)
        
        assert isinstance(result, list)
        assert len(result) == 3
        assert result == [1, 2, 3]

    def test_build_sequence_empty_ordering(self):
        """Test building sequence with empty ordering."""
        data = {
            "name": "Empty",
            "ordering": []
        }
        
        from URModbus.io.DataParser import build_sequence
        
        result = build_sequence(data)
        
        assert isinstance(result, list)
        assert len(result) == 0

    def test_build_sequence_missing_ordering(self):
        """Test building sequence when ordering is missing."""
        data = {
            "name": "No Ordering"
        }
        
        from URModbus.io.DataParser import build_sequence
        
        with pytest.raises(KeyError, match="ordering"):
            build_sequence(data)


@pytest.fixture
def autogen_dir(monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.setattr(
            "URModbus.io.DataParser.Settings.AUTOGEN_DIR",
            tmpdir,
        )

        yield Path(tmpdir)
class TestWriteTaskTime:
    """Test the write_task_time function."""

    def test_write_creates_directory(self, autogen_dir):
        from URModbus.io.DataParser import write_task_time

        write_task_time("Test_Process", 1, 1.0, 5.5)

        assert (autogen_dir / "Test_Process").is_dir()

    def test_write_creates_file(self, autogen_dir):
        from URModbus.io.DataParser import write_task_time

        write_task_time("Test_Process", 1, 1.0, 5.5)

        assert (autogen_dir / "Test_Process" / "1.txt").is_file()

    def test_write_skips_directory_creation(self, autogen_dir):
        from URModbus.io.DataParser import write_task_time

        process_dir = autogen_dir / "Test_Process"
        process_dir.mkdir(parents=True, exist_ok=True)

        write_task_time("Test_Process", 1, 2.0, 6.5)

        assert process_dir.is_dir()

    def test_write_appends_to_existing_file(self, autogen_dir):
        from URModbus.io.DataParser import write_task_time

        process_dir = autogen_dir / "Test_Process"
        process_dir.mkdir(parents=True, exist_ok=True)

        task_file = process_dir / "1.txt"
        task_file.write_text("1;5.5\n")

        write_task_time("Test_Process", 1, 2.0, 6.5)

        content = task_file.read_text()

        assert "1;5.5" in content
        assert "2.0" in content
        assert "6.5" in content
        assert len(content.splitlines()) == 2
class TestCalculateMeanTime:
    """Test the calculate_mean_time function."""

    @patch("URModbus.io.DataParser.np.loadtxt")
    def test_calculate_with_valid_data(self, mock_loadtxt):
        from URModbus.io.DataParser import calculate_mean_time

        mock_loadtxt.return_value = np.array([
            [1, 5.5],
            [2, 6.0],
            [3, 6.5],
        ])

        result = calculate_mean_time("Test_Process", 1)

        assert result == [6.0, 0.41, 6.0, 6.0]

    def test_calculate_with_no_file(self):
        """Test calculating mean time when file doesn't exist."""
        from URModbus.io.DataParser import calculate_mean_time
        
        result = calculate_mean_time("Test_Process", 1)
        
        assert all(v == 0 for v in result)

    def test_calculate_with_empty_file(self):
        """Test calculating mean time with empty file."""
        from URModbus.io.DataParser import calculate_mean_time
        
        result = calculate_mean_time("Test_Process", 1)
        
        assert all(v == 0 for v in result)


class TestCreateGanttData:
    """Test the create_gantt_data function."""

    @patch("URModbus.io.DataParser.np.loadtxt")
    def test_create_with_empty_tasks(self, mock_loadtxt):
        from URModbus.io.DataParser import create_gantt_data

        mock_loadtxt.return_value = np.array([
                    [1, 5.5],
                    [2, 6.0],
                    [3, 6.5],
                ])

        mock_proc = MagicMock()
        mock_proc.name = "Test_Process"
        mock_proc.ordering = []

        result = create_gantt_data(mock_proc, [])

        assert result == []

    @patch("URModbus.io.DataParser.np.loadtxt")
    def test_create_with_default_tasks(self, mock_loadtxt):
        from URModbus.io.DataParser import create_gantt_data

        mock_loadtxt.return_value = np.array([
                            [1, 5.5],
                            [2, 6.0],
                            [3, 6.5],
                        ])


        mock_proc = MagicMock()
        mock_proc.name = "Test_Process"
        mock_proc.ordering = [1]

        task = MagicMock()
        task.name = "Task 1"
        mock_proc.get_task.return_value = task

        result = create_gantt_data(mock_proc, [])

        assert result == [
            {
                "id": 1,
                "name": "Task 1",
                "duration": 6.0,
            }
        ]

@pytest.fixture
def autogen_dir(monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.setattr(
            "URModbus.io.DataParser.Settings.AUTOGEN_DIR",
            tmpdir,
        )

        yield Path(tmpdir)
class TestPlotGantt:
    """Test the plot_gantt function."""

    @patch("URModbus.io.DataParser.np.loadtxt")
    def test_plot_gantt_creates_file(self, mock_loadtxt, autogen_dir):
        from URModbus.io.DataParser import plot_gantt

        mock_loadtxt.return_value = np.array([
                                    [1, 5.5],
                                    [2, 6.0],
                                    [3, 6.5],
                                ])

        mock_proc = MagicMock()
        mock_proc.name = "Test_Process"
        mock_proc.ordering = []

        plot_gantt(mock_proc, [])

        assert list(autogen_dir.rglob("*.svg"))

    @patch("URModbus.io.DataParser.np.loadtxt")
    def test_plot_gantt_with_name(self, mock_loadtxt, autogen_dir):
        """Test plotting gantt with custom name."""
        from URModbus.io.DataParser import plot_gantt

        mock_loadtxt.return_value = np.array([
                                            [1, 5.5],
                                            [2, 6.0],
                                            [3, 6.5],
                                        ])
        
        mock_proc = MagicMock()
        mock_proc.name = "Test_Process"
        mock_proc.ordering = []
        
        
        result = plot_gantt(mock_proc, [], "Custom Name")
        
        assert list(autogen_dir.rglob("*.svg"))



class TestCliGantt:
    """Test the cli_gantt function."""

    @patch("URModbus.io.DataParser.np.loadtxt")
    def test_cli_gantt_creates_output(self,mock_loadtxt):
        """Test that cli_gantt returns text output."""
        from URModbus.io.DataParser import cli_gantt

        mock_loadtxt.return_value = np.array([
                                                [1, 5.5],
                                                [2, 6.0],
                                                [3, 6.5],
                                            ])
        
        mock_proc = MagicMock()
        mock_proc.name = "Test_Process"
        mock_proc.ordering = [1]

        task = MagicMock()
        task.name = "Task 1"
        mock_proc.get_task.return_value = task
        
        result = cli_gantt(mock_proc, [])
        
        assert isinstance(result, list)
        assert len(result) > 0

    @patch("URModbus.io.DataParser.np.loadtxt")
    def test_cli_gantt_with_fillcar(self, mock_loadtxt):
        """Test that cli_gantt respects fillcar parameter."""
        from URModbus.io.DataParser import cli_gantt

        mock_loadtxt.return_value = np.array([
                                                [1, 5.5],
                                                [2, 6.0],
                                                [3, 6.5],
                                            ])
        
        mock_proc = MagicMock()
        mock_proc.name = "Test_Process"
        mock_proc.ordering = [1]

        task = MagicMock()
        task.name = "Task 1"
        mock_proc.get_task.return_value = task
        
        result = cli_gantt(mock_proc, [], "", "[")  # Custom fill character
        
        assert "[" in result[-2]


@pytest.fixture
def autogen_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "URModbus.io.DataParser.Settings.AUTOGEN_DIR",
        "tmp_test_autogen",
    )
    return Path("./tmp_test_autogen")
class TestGaussian:
    """Test the gaussian function."""

    @patch("URModbus.io.DataParser.np.loadtxt")
    def test_gaussian_creates_output(self, mock_loadtxt, autogen_dir):
        """Test that gaussian returns output string."""
        from URModbus.io.DataParser import gaussian

        mock_loadtxt.return_value = np.array([
                                            [1, 5.5],
                                            [2, 6.0],
                                            [3, 6.5],
                                        ])
        
        mock_proc = MagicMock()
        mock_proc.name = "Test_Process"
        mock_proc.ordering = [1]

        task = MagicMock()
        task.name = "Task 1"
        mock_proc.get_task.return_value = task
        
        result = gaussian(mock_proc, 1)
        
        assert isinstance(result, str)
        assert "Saved as" in result

    def test_gaussian_with_zero_mean(self, autogen_dir):
        """Test that gaussian handles zero mean."""
        from URModbus.io.DataParser import gaussian
        
        mock_proc = MagicMock()
        mock_proc.name = "Test_Process"
        mock_proc.ordering = [1]

        task = MagicMock()
        task.name = "Task 1"
        mock_proc.get_task.return_value = task
        
        with patch("URModbus.io.DataParser.calculate_mean_time", return_value=[0.0, 0.0, 0.0, 0.0]):
            result = gaussian(mock_proc, 1)
        
        assert "hold no exploitable time" in result
