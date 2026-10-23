"""Test suite for URModbus core/ProcessTools module."""

import pytest
from unittest.mock import patch, MagicMock
from URModbus.core.ProcessTools import Task, Process


class TestTask:
    """Test the Task class."""

    def test_task_initialization(self):
        """Test task initialization with valid parameters."""
        task = Task(taskId=1, name="Test Task", requirements=[0])
        assert task.taskId == 1
        assert task.name == "Test Task"
        assert task.requirements == [0]

    def test_task_initialization_with_empty_requirements(self):
        """Test task initialization with empty requirements."""
        task = Task(taskId=5, name="Task without deps", requirements=[])
        assert task.taskId == 5
        assert task.name == "Task without deps"
        assert task.requirements == []

    def test_task_getter_properties(self):
        """Test that getter properties return correct values."""
        task = Task(taskId=10, name="Property Test", requirements=[0, 1])
        
        assert task.taskId == 10
        assert task.name == "Property Test"
        assert task.requirements == [0, 1]


class TestProcess:
    """Test the Process class."""

    @pytest.fixture
    def simple_process_data(self):
        """Provide a simple process data structure for tests."""
        return {
            "name": "Simple Process",
            "ordering": [1, 2, 3],
            "tasks": {
                0: {"name": "Start", "requires": []},
                1: {"name": "Task 1", "requires": [0]},
                2: {"name": "Task 2", "requires": [1]},
                3: {"name": "End", "requires": [2]}
            }
        }

    def test_process_initialization_with_data(self, simple_process_data):
        """Test process initialization with valid data."""
        process = Process(data=simple_process_data)
        
        assert process.name == "Simple Process"
        assert len(process.tasks) == 4
        assert 0 in process.tasks
        assert 1 in process.tasks
        assert 2 in process.tasks
        assert 3 in process.tasks

    def test_process_initialization_without_name(self):
        """Test process initialization without name field."""
        data = {
            "ordering": [1],
            "tasks": {
                0: {"name": "Task", "requires": []}
            }
        }
        process = Process(data=data)
        assert process.name == "Not specified"

    def test_process_initialization_without_ordering(self):
        """Test process initialization without ordering field."""
        data = {
            "name": "Process with no ordering",
            "tasks": {
                0: {"name": "Task", "requires": []}
            }
        }
        process = Process(data=data)
        assert process.ordering == [0]

    def test_process_initialization_without_tasks(self):
        """Test process initialization without tasks field."""
        data = {
            "name": "Process with no tasks",
            "ordering": []
        }
        process = Process(data=data)
        assert len(process.tasks) == 1

    def test_process_get_task(self, simple_process_data):
        """Test getting a task by its ID."""
        process = Process(data=simple_process_data)
        
        task_1 = process.get_task(1)
        assert task_1.taskId == 1
        assert task_1.name == "Task 1"
        assert task_1.requirements == [0]

    def test_process_get_nulltask(self, simple_process_data):
        """Test getting a non-existent task returns null task."""
        process = Process(data=simple_process_data)
        
        null_task = process.get_task(999)
        assert null_task.taskId == -1
        assert null_task.name == "Task missmatch"
        assert null_task.requirements == [0]

    def test_process_is_task_in_process(self, simple_process_data):
        """Test checking if a task is in the process."""
        process = Process(data=simple_process_data)
        
        assert process.isTaksInProcess(1) is True
        assert process.isTaksInProcess(2) is True
        assert process.isTaksInProcess(999) is False

    def test_process_tasks_property(self, simple_process_data):
        """Test that tasks property returns list of task IDs."""
        process = Process(data=simple_process_data)
        
        task_ids = process.tasks
        assert isinstance(task_ids, list)
        assert len(task_ids) == 4
        assert set(task_ids) == {0, 1, 2, 3}

    def test_process_change_process_file(self, simple_process_data):
        """Test changing the process to another one."""
        new_data = {
            "name": "New Process",
            "ordering": [5, 6],
            "tasks": {
                5: {"name": "Task 5", "requires": []},
                6: {"name": "Task 6", "requires": [5]}
            }
        }
        
        process = Process(data=simple_process_data)
        process.changeProcessFile(new_data)
        
        assert process.name == "New Process"
        assert len(process.tasks) == 2
        assert 5 in process.tasks
        assert 6 in process.tasks

    def test_process_with_custom_requirements(self):
        """Test process with custom task requirements."""
        data = {
            "name": "Complex Process",
            "ordering": [1, 2],
            "tasks": {
                0: {"name": "Start", "requires": []},
                1: {"name": "Task 1", "requires": [0]},
                2: {"name": "Task 2", "requires": [0]}  # Parallel task
            }
        }
        process = Process(data=data)
        
        task_1 = process.get_task(1)
        assert task_1.requirements == [0]
        
        task_2 = process.get_task(2)
        assert task_2.requirements == [0]