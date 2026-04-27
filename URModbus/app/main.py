from URModbus.core.RobotController import RobotController
from URModbus.core.TimeTracker import TimeTracker
from URModbus.core.ProcessTools import Task,Process
from URModbus.io.TUI import tuiPrint
from URModbus.io.DataParser import read_data_file,build_sequence,calculate_mean_time
from URModbus.io.CommandServer import TerminalServer
from URModbus.config.constants import Settings
from subprocess import Popen, PIPE
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
    container_check = Popen(f'docker ps --filter "name={Settings.CONTAINER}"', shell=True, stdout=PIPE)
    container_output = container_check.stdout.read().decode('utf-8').strip()

    if container_output == "":
        locally = False
    else:
        if platform.system().lower().startswith('win'):
            UR5_IP = 'localhost'
        else:
            ip_command = Popen(['docker','inspect','-f','{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}',f'{Settings.CONTAINER}'],stdout=PIPE)
            UR5_IP = ip_command.stdout.read().decode('utf-8').strip()
        locally = True
    
    # Ping the IP address to check if it responds
    ping_check = Popen(f'ping -c 1 {UR5_IP}', shell=True, stdout=PIPE)
    ping_output = ping_check.stdout.read().decode('utf-8').strip()

    if "1 received" in ping_output:
        tuiPrint(['State: UR5 robot IP is reachable', 'IP responded'])
    else:
        tuiPrint(['State: UR5 robot IP is not reachable', 'IP did not respond', 'Aborting boot....'])
        exit()
        
    ############################## Boot Up controller ############################
    tuiPrint([f'State: Connecting to {UR5_IP}','Creating Controller'])

    controller = RobotController(UR5_IP)

    ############################## Process File ############################
    tuiPrint([f'Reading Process File'])

    pName = controller.programName
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



    tuiPrint([f'State: Starting Time Tracker'])
    

    tracker = TimeTracker(controller,process)
    tracker.start()

    tuiPrint([f'State: Starting Terminal'])


    terminal_thread = TerminalServer(controller,tracker,process)
    terminal_thread.start()

    tuiPrint([f'State: Starting up controller to {UR5_IP}'])
    def signal_handler(sig, frame):
        print('Interupting controller')
        controller.stop()
        terminal_thread.stop()
        tracker.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    controller.start()

    if Settings.MODE == "AUTO":
        for i in range(1,4)[::-1]:
            tuiPrint(["Successfully booted up !",f"Using automated sequence: {process.ordering}",f"Starting in {i}"])
            sleep(1)

    while True:    
        
        while controller.hasTask:
            if controller.isEmergencyStopped:
                tuiPrint([f'Emergency Stop Detected - Please Follow safety Rules before Restoring Cycle',f"Current task: {task} - {process.get_task(task).name}",f"TaskPile: {controller.taskPile}"])
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
                          f"TaskPile: {controller.taskPile}"])
        
            sleep(Settings.ROBOT_SLEEP_TIME/2)
        
        tuiPrint([f"Cycle Ended - Robot: {controller.state} - Program: {controller.programState}"])
        sleep(Settings.ROBOT_SLEEP_TIME/2)

        if Settings.MODE == "AUTO":
            tuiPrint([f'Starting Cycle',f"Scheduling the following sequence {process.ordering}"])
            controller.follow_sequence(process.ordering)













    



    

