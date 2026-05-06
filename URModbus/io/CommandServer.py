"""This script hold the TUI input server for the robot self.__controller

class:
 - Terminal Server: TUI input server
"""
from URModbus.config.constants import Settings
from URModbus.core.RobotController import RobotController
from URModbus.core.ProcessTools import Process
from URModbus.core.TimeTracker import TimeTracker
from URModbus.io.DataParser import read_data_file,calculate_mean_time,plot_gantt,cli_gantt
import os
import socket
import threading
from datetime import datetime


class TerminalServer(threading.Thread):
    """Terminal server used to respond to user input. You can connect to it via nc TERMINAL_HOST TERMINAL_PORT

    Functions:
     - run: Start the server
     - stop: stop the server
     - __parse_command: Parse the command and call the callback function
     - __handle_command: Handle the command
    """
    def __init__(self, 
                 controller:RobotController, 
                 tracker:TimeTracker,
                 process:Process,
                 host:str=Settings.TERMINAL_HOST, 
                 port:int=Settings.TERMINAL_PORT):
        """Innstatiate the Terminal Server

        Args:
            controller (RobotController): Controller of the robot
            tracker (TimeTracker): Time Tracker
            process (Process): Process data
            host (str, optional): ip of the terminal. Defaults to TERMINAL_HOST.
            port (int, optional): port. Defaults to TERMINAL_PORT.
        """
        super().__init__(daemon=True)
        self.__host = host
        self.__port = port
        self.running = True
        self.__controller = controller
        self.__process = process
        self.__tracker = tracker


        self.__welcome = (
                    f"Welcome to UR Robot controller\n"
                    "Use <help> to get help\n"
                )



        self.__logo = Settings.LOGO

    
    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((self.__host, self.__port))
            server.listen(1)


            while self.running:
                conn, addr = server.accept()


                with conn:
                    # 1. Send logo
                    conn.sendall(self.__logo.encode("utf-8") + b"\n")

                    # 2. Send welcome/help
                    conn.sendall(self.__welcome.encode("utf-8") + b"\n")

                    # 3. Auto status command
                    status = self.__handle_command("status",[])
                    if status:
                        conn.sendall(status.encode("utf-8") + b"\n")

                    # 4. Prompt
                    conn.sendall(b"\n> ")

                    while self.running:
                        data = conn.recv(1024)
                        if not data:
                            break

                        cmd = data.decode().strip()
                        if cmd:
                            try:
                                cmd_name, args = self.__parse_command(cmd)
                                response = self.__handle_command(cmd_name, args)
                            except Exception as e:
                                response = f"ERROR: {e}"


                            if response:
                                conn.sendall(response.encode() + b"\n")
                        conn.sendall(b"> ")

    def stop(self):
        self.running = False
    

    def __parse_command(self,raw: str)->tuple[str, list[str]]:
        """Simple parser to exctract data from the recieved command

        Args:
            raw (str): command like <verb> <arg*>

        Returns:
            tuple[str, list[str]]: return both the command and the list or args for it
        """
        parts = raw.strip().split()
        if not parts:
            return None, []

        cmd = parts[0].lower()
        args = parts[1:]
        return cmd, args

    def __handle_command(self, cmd:str, args:list[str])->str:

        
        if cmd == "add":
            if "-h" in args:
                text = ["This command allows you to add tasks to the task list",
                        "Usage: add <task_id>",
                        "Special Parameters",
                        " -f: force adding a task to the pile"]
                return '\n'.join(text)
            
            f_flag = False
            if "-f" in args:
                f_flag = True
                args.remove("-f")
            
            if len(args) < 1:
                return "You need to specify a task"
            
            if len(args) > 1:
                return "You can only add one task. For sequence use sequence"

            try:
                task_id = int(args[0])
            except ValueError:
                return "Task id must be an integer"
            
            if task_id < 0 :
                return "Task id must be a positive integer"
            
            elif self.__process.isTaksInProcess(task_id) is False and f_flag is False:
                return "This task is not in the process file"

            else : 
                self.__controller.perform_task(task_id)
                return f"Task {task_id} added to pile, new pile: {self.__controller.taskPile}"

        
        elif cmd == "clear":
            if "-h" in args:
                text = ["This command allows you to clear the task pile",
                        "Usage: clear"]
                return '\n'.join(text)
                           
            self.__controller.clear_task_pile()
            return "Cleared Tasks"

        elif cmd== "gantt":
            if "-h" in args:
                text = ["This command allows you to draw a gantt",
                        "Usage: gantt <parameters>",
                        "Special Parameters",
                        " <tasks_ids>: plot only requested tasks. ex 1 2 3 4",
                        " -cli: render the graph in the CLI",
                        " -name <name>: change the graph name"]
                return '\n'.join(text)
            if "-cli" in args:
                cli_flag = True
                args.remove('-cli')
            else:
                cli_flag = False
            if "-name" in args:
                name_pos = args.index("-name")
                name = args[name_pos + 1]
                args.pop(name_pos + 1)
                args.remove("-name")
            else:
                name = ""
            
            if len(args) > 0: #If tasks are passed, we must look fo task validity
                try:
                    tasks = [int(task.strip()) for task in args]
                except ValueError:
                    return "Task id must be an integer"
            
                if any(task < 0 for task in tasks):
                    return "Task id must be a positive integer"
            
                if not all(self.__process.isTaksInProcess(task) is True for task in tasks):
                    return "One or more tasks are not in the process file"
            else:
                tasks = []

            if not cli_flag:
                text = plot_gantt(self.__process, tasks, name)
                return text
            else:
                text = cli_gantt(self.__process, tasks, name)
                return '\n'.join(text)
 
        elif cmd == "help":
            text = ["add        -     add a task to pile",
                    "clear      -     clear task pile",
                    "gantt      -     generate a process gantt"
                    "help       -     display help",
                    "info       -     display info on a task",
                    "load       -     load a new process file",
                    "pause      -     pause the bot",
                    "play       -     resume the bot",
                    "process    -     get info on the running process",
                    "program    -     get program name",
                    "sequence   -     add a sequence to pile",
                    "stats      -     displays statistics values"
                    "status     -     display bot status informations",
                    "stop       -     stop current task",
                    "Pro tip: use <command> -h to obtain specific help"]
            return '\n'.join(text)
        
        elif cmd == "info":
            if "-h" in args:
                text = ["This command allows you to display information on a specific task",
                        "Usage: info <task_id>"]
                return '\n'.join(text)
            
            if len(args) < 1:
                return "You need to specify a task"
           
            try:
                task_id = int(args[0])
            except ValueError:
                return "Task id must be an integer"
            
            if task_id < 0 :
                return "Task id must be a positive integer"
            
            elif self.__process.isTaksInProcess(task_id) is False:
                return "This task is not in the process file"

            else : 
                task = self.__process.get_task(task_id)
                text = [f"Id: {task.taskId}",
                        f"Name: {task.name}",
                        f"Requirements: {task.requirements}"]
                return '\n'.join(text)

        elif cmd == "load":
            if "-h" in args:
                text = ["This command allows you to load a new process file.",
                        "WARNING: This will erase the current task pile",
                        "Usage: load <process_file_name>",
                        "Hint: '.yaml' is not required for the file name. Do not input a path"]
                return '\n'.join(text)
            
            if len(args) < 1:
                return "You need to specify a process file"
            #Probably spaces in the file name like "load Assembly 1" -> cmd = 'load' & args = ['Assembly','1']
            if len(args) >1: 
                file_name = ' '.join(args[1:])
            else:
                file_name = args[0]
            
            if ".yaml" not in file_name:
                file_name = file_name + ".yaml"
            
            if os.path.exists(f"./{Settings.DATA_DIR}/{file_name}"):
                data = read_data_file(file_name)
                self.__controller.clear_task_pile()
                self.__process.changeProcessFile(data)
                return f"Process {file_name} loaded"
            else:
                return f"Process file {file_name} doesnt exist"

            

        elif cmd == "pause":
            if "-h" in args:
                text = ["This command allows you to clear the pause the program execution",
                        "Usage: pause"]
                return '\n'.join(text)
                

            self.__controller.pause_program()
            return "Bot paused"
        
        elif cmd == "play":
            if "-h" in args:
                text = ["This command allows you to clear the play the program execution",
                        "Usage: play"]
                return '\n'.join(text)
            self.__controller.play_program()
            return "Bot started"
        
        elif cmd == "sequence":
            if "-h" in args:
                text = ["This command allows you to add a sequence of tasks to the task list",
                        "Usage: sequence id1 id2.....",
                        "Special Parameters",
                        " -f: force adding a sequence to the pile"]
                return '\n'.join(text)
            
            f_flag = False
            if "-f" in args:
                f_flag = True
                args.remove("-f")
            

            try:
                sequence = [int(task.strip()) for task in args]
            except ValueError:
                return "Task id must be an integer"
            
            if any(task < 0 for task in sequence):
                return "Task id must be a positive integer"
            
            if not all(self.__process.isTaksInProcess(task) is True for task in sequence) and f_flag is False:
                return "One or more tasks are not in the process file"

            self.__controller.follow_sequence(sequence)
            return f"Sequence added to pile, new pile: {self.__controller.taskPile}"

        elif cmd == "process":
            if "-h" in args:
                text = ["This command allows you to display information of the current process",
                        "Usage: process"]
                return '\n'.join(text)
           
            text = [f"Name: {self.__process.name}",
                    f"Tasks: {set(self.__process.ordering)}",
                    f"Ordering: {self.__process.ordering}"]
            return '\n'.join(text)
        
        elif cmd == "program":
            if "-h" in args:
                text = ["This command allows you to display information of the current program",
                        "Usage: program"]
                return '\n'.join(text)
           
            text = [f"Name: {self.__controller.programName}"]
            return '\n'.join(text)
        
        elif cmd == "stop":
            if "-h" in args:
                text = ["This command allows you to clear the stop the program execution",
                        "Usage: stop"]
                return '\n'.join(text)
            self.__controller.stop_program()
            return "Bot stopped"
        
        elif cmd == "stats":
            if "-h" in args:
                text = ["This command allows you to obtain a stats report",
                        "Usage: stats [options] [<task1> <task2> ...]",
                        "Optional Parameters:",
                        " <task>: if provided, outputs data for requested tasks; otherwise outputs for the current task",
                        "Special Parameters:",
                        " -full: display stats for the whole process",
                        " -p:    display only general process info"]

                return '\n'.join(text)

            
            f_flag = False
            if "-full" in args:
                f_flag = True
                args.remove("-full")
            
            p_flag = False
            if "-p" in args:
                p_flag = True
                args.remove("-p")

            if p_flag and f_flag:
                return "Can only use -p or -full but not both"
        
            if f_flag or p_flag: #Either the user want the full process or the process summary. So we need to fecth process data

                tasks = self.__process.tasks
            
            elif len(args)>0: # Elswise we look if user request a specific task
            
                try:
                    tasks = [int(task.strip()) for task in args]
                except ValueError:
                    return "Task id must be an integer"
            
                if not all(self.__process.isTaksInProcess(task) is True for task in tasks):
                    return "One or more tasks are not in the process file"
            else: #The user just want the current task
                tasks = [self.__controller.get_current_task()] 
            
            L = [calculate_mean_time(self.__process.name,task) for task in tasks] #We get statistical data

            text = []

            if not p_flag: # If user didnt explicitly requested the process, we create task data

                for i,task in enumerate(tasks):
                    text += [f"Task {tasks[i]} - {self.__process.get_task(task).name}:",
                            f"Mean: {L[i][0]}s",
                            f"Deviation: {L[i][1]}s",
                            f"Mean +/- Deviation: {L[i][2]}s",
                            f"Last 100 Mean: {L[i][3]}s",
                            "---------------------------"]
                
            if f_flag or p_flag: #If the user want a full report or a process one
                sum_mean = sum([L[i][0] for i in range(len(L))])
                sum_dev = sum([L[i][1] for i in range(len(L))])
                text += [f"General Process data for {self.__process.name}",
                         f"Mean process time: {round(sum_mean,2)}s",
                         f"Best possible time: {round(sum_mean-sum_dev,2)}s",
                         f"Worst possible time: {round(sum_mean+sum_dev,2)}s"]
            
            return '\n'.join(text)

        
        
        elif cmd == "status":
            if "-h" in args:
                text = ["This command allows you to obtain a status report",
                        "Usage: status"]
                return '\n'.join(text)    

                
            
            lenght = 69
            l1 = f"Status obtained at: {datetime.now().strftime('%H:%M:%S')}"
            l2 = f"Robot IP: {self.__controller.ip}"
            l3 = f"Emergency stop: {self.__controller.isEmergencyStopped} - False=0 True=1"
            l4 = f"Robot status: {self.__controller.state} - Disconnected=0, Confirm_safety=1, Booting=2, Power_off=3, Power_on=4, Idle=5, Backdrive=6, Running=7"
            l5 = f"Program status: {self.__controller.programState}"
            text_list = [
                f"# {'-'*lenght} #",
                f"| {l1}",
                f"| {l2}",
                f"| {l3}",
                f"| {l4}",
                f"| {l5}",
                f"# {'-'*lenght} #"
            ]
            return '\n'.join(text_list)
            return text

        else:
            return "Unknown command"
