# ⚠️ Disclaimers

## Using this project
This repository is part of a research project **[ANR MITCH](https://anr.fr/Projet-ANR-24-CE10-3545)**.  
The provided code is **research-grade** and **not intended for industrial or safety‑critical deployment**.

## GitHub vs GitLab
This repository is **primarily hosted on GitHub**.
For the moment, **pushes are mirrored to GitLab** because the project is linked to my lab environment. However, I’m not certain I’ll retain access to the lab’s GitLab after my PhD, so GitHub is the long‑term home of the project.

If you need access to my laboratory GitLab instance, you can find it [here](https://gitlab.ensam.eu/explore/projects/active)

### Where to contribute


- ✅ GitHub: This is the main platform for the project. Please use it to open Pull Requests, report issues and discuss features and bugs.
- ⚠️ GitLab: The repository is mirrored. Please do not open issues or merge requests there — [use GitHub instead](https://github.com/Le-Nain-Capable/URModbus/tree/main)

---

# 🤖 URModbus

**URModbus** enables external control of **Universal Robots (UR)** via the **Modbus** and **Dashboard** interfaces while keeping task logic on the robot itself.

The core idea is simple:

> ✨ _Program tasks directly on the teach pendant but manage execution and scheduling externally._

## Quick Demo
Quick demo of the capabilities
![QuickDemo](pictures/QuickDemo.gif)
> The script is running in `AUTO`, therefore it is currently following the associated process file.
---

## ✅ Tested Configurations

**Offline**:
- UR CB3 Offline Simulator  
     [ursim cb3 docker](https://hub.docker.com/r/universalrobots/ursim_cb3) - Used for developing

**Online**:
- UR5 CB3.15 & OnRobot equipments - Used for validating:
    - [EYES](https://onrobot.com/fr/produits/onrobot-eyes) - [RG6](https://onrobot.com/fr/produits/prehenseur-rg6) - [HEX](https://onrobot.com/fr/produits/capteur-force-couple-6-axes-hex)

---

## ✨ Features

### Robot-side

- Tasks are implemented **directly on the teach pendant**
- A Modbus-based switch controls execution
- Robot publishes its current state continuously

### Controller-side

- External task scheduling and monitoring
- Execution timing and logging
- Interactive terminal-based control interface (TUI)

### Project Structure

|File|Description|
|---|---|
|**RobotController.py**|Main controller; manages task execution using a task queue|
|**TimeTracker.py**|Measures and logs task execution times|
|**ModbusTools.py**|Modbus communication layer|
|**DashTools.py**|Dashboard server interface|
|**ProcessTool.py**|Loads and manages task process files|
|**CommandServer.py**|Interactive terminal (TUI)|
|**Constants.py**|Settings for the code|

---

## 🚀 Quick Setup — Real Robot

### A) Robot Configuration

1. **Enable Modbus** on the robot
2. Create an **input word**
    - Address: `131`
    - Name: `Next_Action`
3. Create an **output word**
    - Address: `130`
    - Name: `Current_Action`
4. Create a program named **`test_modbus.urp`** containing a switch based on `Next_Action`
![example_process](pictures/test_modbus.png)
> ⚠️ Ensure:
> 
> - A **default case**
> - Proper **initial variable values**
> - Task `0` is reserved for _idle_

---

### B) Code Setup

1. Clone the repository

```
git clone https://github.com/Le-Nain-Capable/URModbus.git
```

2. Navigate to it
```
cd URModbus
```
3. Install dependencies
```
pip install -r requirements.txt
```
4. Configure `constants.py`

- Robot IP (real robot)
- OR container name (simulation)

5. Run the controller
```
python3 main.py
```
or
```
python3 -m URModbus
```
✅ The controller is now running.

---

### 🖥️ Command-Line Interface (TUI)

Open another terminal:
```
nc localhost 9999
```
You should see the interactive TUI.
![TUI](pictures/TUI.png)
- Type `play` **or**
- Start the UR program manually

---

## 🧠 How It Works

The system relies on **Modbus word exchange**:

- **`Next_Action`** → what the robot should do next
- **`Current_Action`** → what the robot is currently executing


```mermaid
sequenceDiagram
    participant Robot

    participant Controller

    Robot -->> Controller: Current_Action

    Controller -->> Robot: Next_Action
```
### Task Model

- Each task is identified by a **unique integer**
- The integer corresponds to a `switch` case on the robot
- Example:
    - `1` → Pick part
    - `2` → Place part

### Mandatory Rules

- ✅ Set `Current_Action` at task start
- ✅ Always implement a **default case**
- ✅ Initialize all variables
- ⚠️ **Task `0` is strictly reserved for “Do Nothing”**

---

## ⚙️ Advanced Setup

### Configuration Constants (`constants.py`)

|Variable|Description|Default|
|---|---|---|
|MODE|`AUTO` or `MANUAL`|`AUTO`|
|AUTO_LOAD|Auto-load YAML based on UR program|`True`|
|TERMINAL_PORT|TUI port|`9999`|
|TERMINAL_HOST|TUI host|`127.0.0.1`|
|ROBOT_SLEEP_TIME|Loop sleep time (must match UR sleep!)|`0.1`|
|UR5_IP|Robot IP address|`192.168.1.10`|
|CONTAINER|URSim container name|`ursim`|
|DATA_DIR|Data folder|`data`|
|AUTOGEN_DIR|Time logs directory|`data/autogenerated`|
|TEST_FILE|Simulator YAML file|`test.yaml`|
|PROCESS_FILE|Real robot YAML file|`data.yaml`|
|MOTS|Modbus word mapping|see file|

---

### ⚙️ Changing Settings

Settings can be configured in **3 ways**:

1. **Edit defaults**  
Modify values directly in `URModbus/config/constants.py`

2. **Script arguments**  
Override settings at runtime  
`python3 main.py --<argument> <value>`  
Example:  
`python3 main.py --MODE MANUAL`

3. **Module arguments**  
Run URModbus as a module  
`python3 -m URModbus --<argument> <value>`  
Example:  
`python3 -m URModbus --MODE MANUAL`

> ⚠️ Command-line arguments (2 and 3) are temporary and will not be saved.

---

### CB3 Docker Simulator

Ensure the container exposes:

- `502` (Modbus)
- `29999` (Dashboard)

Set the container name in `CONTAINER`.

---

## 📄 YAML Process Files

YAML files define task sequencing and dependencies.

**Example – `test_modbus.yaml`:**
```YAML
version: 0
name: Test
tasks:
    0:
        name: Intermediate
        requires: 
    1:
        name: Task 1
        requires: 0
    2: 
        name: Task 2
        requires: 1
ordering: [1,2]
```

> ⚠️ Task `0` is mandatory and acts as a safe idle state between tasks.

---

## 🔄 A note on execution modes: MODE

### AUTO

- Executes tasks sequentially using `ordering`

### MANUAL

- Tasks must be injected dynamically by the user

---

## ⏳ A note on program loading mode: AUTO_LOAD

- If enabled:
    - Reads the active UR program name
    - Attempts to auto-load the matching YAML file
- Falls back to `TEST_FILE` or `PROCESS_FILE` if unavailable

---

## ⚙️ A note on the TUI:

### General stuff
By default:
- The TUI should be available at localhost:9999. **It is a pure TCP connection and not a true TUI**
- You can establish a TCP connection to it with any tool like `nc` or any `socket` library.
- You have to send it `str` of requested functions call with arguments. 


**`help`** is a good way to start, as it should display all available commands. Then running `<command> -h` will get you information on how to use such command.

### TCP socket connection breakdown
The TCP will accept **only 1 connection**. 

The greetings' interaction is as follows:
```mermaid
sequenceDiagram
    participant TUI

    participant TCP

    TCP -->> TUI: Establish connection

    TUI -->> TCP: Send Logo

    TUI -->> TCP: Send Greetings message

    TUI -->> TCP: Send Status results
```

Keep the socket open and send commands to it. Per command, you will receive a response.

### Available commands.
Here is a breakdown of commands, usage and parameters.

|Command|Details|Usage|Special Parameters|Example|
|---|---|---|---|---|
|**add**|Add tasks to the task pile|`add <task_id>`|`-f`: force adding a task to the pile|`add 1`<br>`add -f 500`|
|**clear**|Clear the task pile|`clear`|None|`clear`|
|**gantt**|Draw a gantt|`gantt`|`<task(s)_id(s)>`: plot only requested tasks.<br> `-cli`: render the graph in the CLI <br> `-car <caracter>` caracter used for a full cell in cli chart mode <br> `-name <name>`: change the graph name |`gantt`<br>`gantt -cli 8 7 9`<br>`gantt -name MyGantt`| 
|**gaussian**|Draw a gaussian|`gaussian`|`<task(s)_id(s)>`: plot only requested tasks. <br> `-name <name>`: change the graph name |`gaussian`<br>`gaussian 8 7 9`<br>`gaussian -name MyGaussian`|                       
|**help**|Display help|`help`|None |`help`|
|**info**|Display information on a specific task|`info <task_id>`|None |`info 1`|         
|**load**|Load a new process file|`load <process_file_name>`|None |`load myfile`<br> `load myfile.yaml`|  
|**pause**|Pause the program execution|`pause`|None |`pause`|           
|**play**|Play the program execution|`play`|None |`play`| 
|**sequence**|Add a sequence to the task pile|`sequence <tasks_ids>`|`-f`: force adding a task to the pile|`sequence 1 2 3 4 5`<br>`sequence -f 500`|           
|**process**|Display information of the current process|`process`|None|`process`|             
|**program**|Display information of the current program|`program`|None|`program`|
|**stop**|Stop the program execution|`stop`|None |`stop`| 
|**stats**|Obtain a stats report|`stats`|`<task(s)>`: request data for selected tasks<br>`-full`:whole process report<br>`-p`:only general process info |`stats`<br>`stats 1 2 3`<br>`stats -full`<br>`stats -p`|   
|**status**|Status report|`status`|None |`status`|   
