# URModbus Test Summary

**Location:** `URModbus/tests/`  
**Test Coverage:** All modules in `core/`, `config/`, `io/` directories. Directory **app** is yet to be supported

---

## Table of Contents
- App Module Tests
- Core Module Tests
- Config Module Tests
- IO Module Tests

---

## App Module Tests (`tests/app/`)

### 1. `test_main.py`
**Module:** `URModbus/app/main.py`

**Test Classes:**

- **TestAppRunInitialization**
  - `test_run_prints_logo`
  - `test_run_detects_local_vs_remote`

- **TestAppRunWithoutController**
  - `test_run_without_controller_uses_degraded_mode`

- **TestAppRunWithController**
  - `test_run_with_controller_uses_full_mode`

- **TestAppRunProcessLoading**
  - `test_run_autoload_process_from_controller`
  - `test_run_fallback_to_test_file_when_no_controller`

- **TestAppRunTerminalServer**
  - `test_run_starts_terminal_server`

- **TestAppRunSignalHandlers**
  - `test_run_sets_signal_handler_with_controller`
  - `test_run_sets_signal_handler_without_controller`

- **TestAppRunAutoMode**
  - `test_run_auto_mode_prints_start_sequence`
  - `test_run_auto_mode_uses_process_ordering`

- **TestAppRunTaskExecution**
  - `test_run_handles_task_execution`

- **TestAppRunEmergencyStop**
  - `test_run_handles_emergency_stop`

**Key Features:**
- Controller available and degraded-mode startup paths
- Docker/container detection logic
- Automatic process loading behavior
- TerminalServer initialization verification
- Signal handler registration
- AUTO mode execution flow
- Emergency stop handling
- Startup banner and console output validation

---

## Core Module Tests (`tests/core/`)

### 1. `test_ProcessTools.py` (164 lines)
**Module:** `URModbus/core/ProcessTools.py`

**Test Classes:**
- **`TestTask`** - Task class tests
  - `test_task_initialization` - Valid parameters
  - `test_task_initialization_with_empty_requirements` - Empty requirements
  - `test_task_getter_properties` - Property getters
  
- **`TestProcess`** - Process class tests
  - `test_process_initialization_with_data` - Valid data
  - `test_process_initialization_without_name` - Missing name field
  - `test_process_initialization_without_ordering` - Missing ordering
  - `test_process_initialization_without_tasks` - No tasks
  - `test_process_get_task` - Get task by ID
  - `test_process_get_nulltask` - Non-existent task returns null
  - `test_process_is_task_in_process` - Check task existence
  - `test_process_tasks_property` - Tasks property returns list
  - `test_process_change_process_file` - Change to new process
  - `test_process_with_custom_requirements` - Custom requirements

**Key Features:**
- Tests both happy paths and error conditions
- Uses fixtures for process data
- Covers edge cases (missing fields, non-existent tasks)

---

### 2. `test_DashTools.py` (256 lines)
**Module:** `URModbus/core/DashTools.py`

**Test Classes:**
- **`TestDashRobotInitialization`** - Initialization tests
  - `test_init_with_ip_and_default_port`
  - `test_init_with_custom_port`
  - `test_init_with_timeout`
  - `test_init_with_all_parameters`
  
- **`TestDashboardCommand`** - Command method tests
  - `test_successful_command_response` - Successful response
  - `test_server_closed_no_greeting` - Server closed (no greeting)
  - `test_server_closed_no_response` - No response to command
  
- **`TestPlay`** - Play method
  - `test_play_when_not_playing`
  - `test_play_when_already_playing`
  
- **`TestStop`** - Stop method
  - `test_stop_when_not_stopped`
  - `test_stop_when_already_stopped`
  
- **`TestPause`** - Pause method
  - `test_pause_when_not_paused`
  - `test_pause_when_already_paused`
  
- **`TestProgramStateProperty`** - programState property
  - `test_program_state_return_format`
  - `test_state_stopped`
  
- **`TestProgramNameProperty`** - programName property
  - `test_extract_program_name_from_state`
  - `test_extract_program_name_stopped`

**Key Features:**
- Extensive socket mocking with `unittest.mock.patch`
- Tests both success and error scenarios (connection closed, no response)
- All methods tested with happy path and edge cases

---

### 3. `test_ModbusTools.py` (299 lines)
**Module:** `URModbus/core/ModbusTools.py`

**Test Classes:**
- **`TestModbusRobotInitialization`**
  - `test_init_with_ip`
  - `test_thread_name`
  - `test_mapping_addresses_are_set`
  
- **`TestReadReg`** - Register read tests
  - `test_successful_read_register`
  - `test_read_register_value_zero`
  - `test_read_register_empty_registers`
  
- **`TestWriteReg`** - Register write tests
  - `test_successful_write_register`
  - `test_write_register_connection_failure`
  
- **`TestRead`** - Public read method
  - `test_read_int_register_readable`
  - `test_read_int_register_not_readable`
  - `test_read_str_register_readable`
  - `test_read_invalid_type`
  
- **`TestWrite`** - Public write method
  - `test_write_int_register`
  - `test_write_string_register`
  - `test_write_invalid_register_type`
  
- **`TestMapping`** - Mapping dictionaries
  - `test_mots_mapping_exists`
  - `test_mapping_addresses_mot_structure`
  
- **`TestErrorHandling`**
  - `test_read_on_connection_failure`

**Key Features:**
- Uses `pymodbus` library with proper mocking
- Tests both read/write operations
- Covers error scenarios (connection failures, invalid types)
- Verifies mapping dictionaries structure

---

### 4. `test_TimeTracker.py` (217 lines)
**Module:** `URModbus/core/TimeTracker.py`

**Test Classes:**
- **`TestTimeTrackerInitialization`**
  - `test_init_with_controller_and_process`
  
- **`TestTaskSwitch`**
  - `test_task_switch_updates_start_time` - Resets start time on task switch
  
- **`TestTimeTracking`**
  - Tests with fixtures (mock_robot_controller, mock_process)
  
- **`TestStop`**
  - `test_stop_with_running_true`
  - `test_stop_with_running_false`

**Key Features:**
- Extensive time tracking simulation
- Uses real `time` and `sleep` modules (patched in tests)
- Tests task switching scenarios
- Edge cases: empty task pile, emergency stop

---

### 5. `test_RobotController.py` (465 lines)
**Module:** `URModbus/core/RobotController.py`

**Test Classes:**
- **`TestRobotControllerInitialization`**
  - `test_init_creates_interfaces`
  
- **`TestTaskPileProperties`**
  - `test_task_pile_property`
  - `test_next_task_property`
  - `test_last_task_property`
  - `test_has_task_property_empty`
  - `test_has_task_property_with_tasks`
  
- **`TestTaskOperations`**
  - `test_clear_task_pile`
  - `test_perform_task`
  - `test_follow_sequence`
  - `test_follow_sequence_with_0`
  - `test_follow_sequence_invalid_type`
  
- **`TestProgramControl`**
  - `test_play_program`
  - `test_stop_program`
  - `test_pause_program`
  
- **`TestStop`**
  - `test_stop_sets_running_false`
  
- **`TestModbusInterface`**
  - `test_modbus_interface_property`
  
- **`TestStateProperties`**
  - `test_state_property`
  - `test_program_state_property`
  - `test_program_name_property`
  
- **`TestEmergencyStop`**
  - `test_is_emergency_stopped_property`
  
- **`TestIpAddress`**
  - `test_ip_property`
  
- **`TestGetCurrentTask`**
  - `test_get_current_task`
  
- **`TestAssignNewTask`**
  - `test_assign_new_task_valid_int`
  
- **`TestRemoveTask`**
  - `test_remove_task`

**Key Features:**
- Most comprehensive test file (465 lines)
- Tests both Modbus and Dash interfaces
- Extensive task pile management scenarios
- Program state tracking (play/stop/pause)
- Emergency stop handling
- All property tests with proper mocking

---

## Config Module Tests (`tests/config/`)

### 1. `test_constants.py` (115 lines)
**Module:** `URModbus/config/constants.py`

**Test Class:** **`TestSettings`**
- `test_default_values` - All default settings
- `test_update_setting_string` - String setting update
- `test_update_setting_integer` - Integer setting update
- `test_update_setting_invalid_integer` - Invalid type handling
- `test_update_setting_float` - Float setting update

**Key Features:**
- Tests Settings class and `updateSetting()` method
- Verifies all default values match constants.py
- Tests both successful and failed updates

---

### 2. `parser_test.py` (already existed)
**Module:** Config parser tests

**Features:**
- YAML parsing tests
- Configuration file reading
- Validation tests

---

## IO Module Tests (`tests/io/`)

### 3. `test_TUI.py` (134 lines)
**Module:** `URModbus/io/TUI.py`

**Test Classes:**
- **`TestTuiPrint`**
  - `test_tui_print_adds_timestamp` - First line has timestamp
  - `test_tui_print_updates_line_count` - Line counter state
  - `test_tui_print_empty_lines` - Empty lines handling
  - `test_tui_print_single_line` - Single line input
  
- **`TestFormatPile`**
  - `test_format_pile_empty_pile`
  - `test_format_pile_with_single_task`
  - `test_format_pile_multiple_tasks`
  - `test_format_pile_exactly_seven_tasks`
  - `test_format_pile_truncation_at_six_plus`
  - `test_format_pile_truncation_three_plus`
  - `test_format_pile_mixed_zero_and_positive`
  - `test_format_pile_all_zeros`

**Key Features:**
- Tests internal state (line_count)
- Proper fixture setup for isolated tests
- Edge cases: empty piles, exactly 6 tasks, truncation at 7+

---

### 4. `test_DataParser.py` (296 lines)
**Module:** `URModbus/io/DataParser.py`

**Test Classes:**
- **`TestReadDataFile`**
  - `test_read_valid_yaml_file`
  - `test_read_yaml_with_single_key`
  - `test_read_yaml_with_error`
  
- **`TestBuildSequence`**
  - `test_build_sequence_from_dict`
  - `test_build_sequence_empty_ordering`
  - `test_build_sequence_missing_ordering`
  
- **`TestWriteTaskTime`**
  - `test_write_creates_directory`
  - `test_write_creates_file`
  - `test_write_skips_directory_creation`
  - `test_write_appends_to_existing_file`
  
- **`TestCalculateMeanTime`**
  - `test_calculate_with_valid_data`
  - `test_calculate_with_no_file`
  - `test_calculate_with_empty_file`
  
- **`TestCreateGanttData`**
  - `test_create_with_empty_tasks`
  - `test_create_with_default_tasks`
  
- **`TestPlotGantt`**
  - `test_plot_gantt_creates_file`
  - `test_plot_gantt_with_name`
  
- **`TestCliGantt`**
  - `test_cli_gantt_creates_output`

**Key Features:**
- Uses `mock_open` for file reading tests
- NumPy array mocking for statistical functions
- Matplotlib operations properly mocked
- File I/O edge cases (missing files, empty files)

---

### 5. `test_CommandServer.py` (667 lines )
**Module:** `URModbus/io/CommandServer.py`

**Test Classes:**
- **`TestTerminalServerInitialization`**
  - `test_init_with_all_parameters`
  - `test_init_with_degraded_mode`
  
- **`TestParseCommand`**
  - `test_parse_simple_command`
  - `test_parse_command_with_args`
  - `test_parse_empty_command`
  - `test_parse_command_with_multiple_args`
  
- **`TestHandleCommand`** (All 17+ commands)
  - `test_handle_status_command`
  - `test_handle_help_command`
  - `test_handle_unknown_command`
  - `test_handle_add_command_help`
  - `test_handle_add_command_invalid_task`
  - `test_handle_add_command_with_force`
  - `test_handle_add_negative_task_id`
  - `test_handle_add_multiple_args`
  - `test_handle_clear_command`
  - `test_handle_clear_help`
  - `test_gaussian_help`
  - `test_gaussian_with_name_flag`
  - `test_gaussian_with_tasks`
  - `test_gaussian_invalid_task`
  - `test_gaussian_negative_task`
  - `test_sequence_help`
  - `test_sequence_with_tasks`
  - `test_sequence_with_force`
  - `test_play_command`
  - `test_pause_command`
  - `test_stop_command`
  - `test_process_command`
  - `test_load_command`
  - `test_info_command`
  - `test_stats_command`
  
- **`TestGaussianCommand`** (with fixtures)
  - `test_gaussian_help`
  - `test_gaussian_with_name_flag`
  - `test_gaussian_with_tasks`
  
- **`TestSequenceCommand`**
  - `test_sequence_help`
  - `test_sequence_with_tasks`
  - `test_sequence_with_force`
  
- **`TestProgramControlCommands`**
  - `test_play_command`
  - `test_pause_command`
  - `test_stop_command`
  
- **`TestProcessControlCommands`**
  - `test_process_help`
  - `test_process_add_task`
  - `test_process_remove_task`
  
- **`TestLoadCommand`**
  - `test_load_help`
  - `test_load_with_filename`
  
- **`TestInfoCommand`**
  - `test_info_command`
  
- **`TestStatsCommand`**
  - `test_stats_command`

**Key Features:**
- Comprehensive command coverage (17+ commands)
- Argument parsing tests
- Degraded mode restrictions
- Error message verification
- Extensive mocking of dependencies

---
