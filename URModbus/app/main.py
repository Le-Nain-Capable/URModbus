from URModbus.core.RobotController import RobotController
from URModbus.core.TimeTracker import TimeTracker
from URModbus.core.ProcessTools import Task,Process
from URModbus.io.TUI import tuiPrint,format_pile
from URModbus.io.DataParser import read_data_file,calculate_mean_time
from URModbus.io.CommandServer import TerminalServer
from URModbus.config.constants import Settings

import subprocess
from time import sleep
import platform
import signal
import sys
import os

def run():

    global UR5_IP

    print(Settings.LOGO)

    ############################## Pick UR5 IP Address ############################

    tuiPrint(['State: Locating UR5 robot IP ',"Do: looking for ip"])
    container_check = subprocess.Popen(f'docker ps --filter "name={Settings.CONTAINER}"',
                                        shell=True,
                                        stdout=subprocess.PIPE)
    container_output = container_check.stdout.read().decode('utf-8').strip()

    if container_output == "":
        locally = False
    else:
        if platform.system().lower().startswith('win'):
            UR5_IP = 'localhost'
        else:
            ip_command = subprocess.Popen(['docker',
                                           'inspect',
                                           '-f',
                                           '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}',
                                           f'{Settings.CONTAINER}'],
                                           stdout=subprocess.PIPE)
            UR5_IP = ip_command.stdout.read().decode('utf-8').strip()
        locally = True

    # Determine the correct ping command based on OS
    if platform.system() == "Windows":
        ping_command = f'ping -n 1 {UR5_IP}'
    else:
        ping_command = f'ping -c 1 {UR5_IP}'

    try:
        # Use subprocess.run which handles encoding and returns a Result object
        result = subprocess.run(
            ping_command,
            shell=True,
            capture_output=True, # Captures stdout and stderr
            text=True,            # Important: Tells Python to decode output using default OS encoding
            check=True            # Raises CalledProcessError if the command fails
        )
        ping_output = result.stdout.strip()

    except subprocess.CalledProcessError as e:
        tuiPrint([f"Ping failed: {e}"])
        ping_output = "" # Handle failure case gracefully

    if "ms" in ping_output: #We check for a time to be present, indicating a success
        tuiPrint(['State: UR5 robot IP is reachable', 'IP responded'])
        CONTROLLER = True
    else:
        tuiPrint(['State: UR5 robot IP is not reachable', 'Booting without the controller'])
        CONTROLLER = False
        
        
    ############################## Boot Up controller ############################
    # IF controller we attempt to communicate to the bot
    if CONTROLLER:    
        tuiPrint([f'State: Connecting to {UR5_IP}','Creating Controller'])
        controller = RobotController(UR5_IP)
    else :
        tuiPrint([f'State: Bypassing Controller'])
        controller = None

    ############################## Process File ############################
    #IF controller we attempt to autoload the program name
    tuiPrint([f'Reading Process File'])
    if CONTROLLER:
        pName = controller.programName
    else:
        pName = "null"

    if pName != "null" and Settings.AUTO_LOAD: #A File is loaded on the bot if it is not null here
        pName = pName[:-4] #Removes the .urp
        tuiPrint(['Attempting to load a process file',f'file: {pName}'])
        if os.path.exists(f"./{Settings.DATA_DIR}/{pName}.yaml"):
            tuiPrint(['Reading Process File'])
            file = pName + ".yaml"
        else:
            file = Settings.TEST_FILE if locally else Settings.PROCESS_FILE
    else:
        file = Settings.TEST_FILE if locally else Settings.PROCESS_FILE

    tuiPrint([f'Building Process',f'File: {file}'])
    process = Process(read_data_file(file))


    ############################## Time tracker ############################
    if CONTROLLER:
        tuiPrint([f'State: Starting Time Tracker'])
        tracker = TimeTracker(controller,process)
        tracker.start()
    else: 
        tuiPrint([f'State: Bypassing Time Tracker'])
        tracker = None


    ############################## TerminalServer ############################
    tuiPrint([f'State: Starting Terminal'])
    terminal_thread = TerminalServer(controller,tracker,process,degraded=not CONTROLLER) #if no controller then we must enable degraded mode
    terminal_thread.start()

    if CONTROLLER:
        tuiPrint([f'State: Starting up controller to {UR5_IP}'])
        def signal_handler(sig, frame):
            print('Interupting controller')
            controller.stop()
            terminal_thread.stop()
            tracker.stop()
            sys.exit(0)
        controller.start()
    else:
        tuiPrint([f'State: Starting up terminal in minimal mode'])
        def signal_handler(sig, frame):
            print('Interupting controller')
            terminal_thread.stop()
            sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    if not CONTROLLER:
        while True: 
            tuiPrint(["Robot was not reachable", "Booted in minimal mode", f'TUI can be accessed at {Settings.TERMINAL_HOST} - {Settings.TERMINAL_PORT}'])
            sleep(1)

    if Settings.MODE == "AUTO":
        for i in range(1,4)[::-1]:
            tuiPrint(["Successfully booted up !",f"Using automated sequence: {process.ordering}",f"Starting in {i}"])
            sleep(1)

    while True:    
        
        while controller.hasTask:
            if controller.isEmergencyStopped:
                tuiPrint([f'Emergency Stop Detected - Please Follow safety Rules before Restoring Cycle',f"Current task: {task} - {process.get_task(task).name}",f"TaskPile: {format_pile(controller.taskPile)}"])
                controller.clear_task_pile()
            else:

                task = controller.get_current_task()

                if task == 0:
                    time_data = f"Mean: N/A - Time: N/A"
                else :
                    process_data = calculate_mean_time(process.name,task)
                    time_data = f"Mean: {process_data[0]}s - Time: {tracker.time}s"

                tuiPrint([f'Running Cycle - Robot: {controller.state} - Program: {controller.programState}',
                          f"Current task: {task} - {process.get_task(task).name}",
                          time_data,
                          f"TaskPile: {format_pile(controller.taskPile)}"])
        
            sleep(Settings.ROBOT_SLEEP_TIME/2)
        
        tuiPrint([f"Cycle Ended - Robot: {controller.state} - Program: {controller.programState}"])
        sleep(Settings.ROBOT_SLEEP_TIME/2)

        if Settings.MODE == "AUTO":
            tuiPrint([f'Starting Cycle',f"Scheduling the following sequence {process.ordering}"])
            controller.follow_sequence(process.ordering)













    



    

