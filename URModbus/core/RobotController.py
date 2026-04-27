""" Robot task controller

Class:
 - RobotController: controls robot tasks via modbus
"""
from URModbus.core.ModbusTools import ModbusRobot
from URModbus.core.DashTools import DashRobot
from URModbus.config.constants import ROBOT_SLEEP_TIME
from threading import Thread, Lock
from time import sleep

mutex = Lock()

class RobotController(Thread):
    """Controller For Robot task execution. It uses a pile to schedule task and execute the task when avaliable.

    Functions:
     - run: Main loop of the controller and task pile executer
     - stop: Stops controller
     - clear_task_pile: empty the task pile
     - __remove_task: Remove the first task of the pile
     - __assign_new_task: Assign a new task via modbus to the robot, task will be put in task register to be executed by the robot when avaliable
     - get_current_task: Get the current task from the robot
     - perform_task: Add a single task to the pile
     - follow_sequence: add a sequence of tasks to the pile
     - play_program: Start the program
     - stop_program: Stop the program
     - pause_program: Pause the program
    
    Property :
     - taskPile: Returns the current task pile
     - nextTask: Return the next task in the pile to be done
     - lastTask: Return the last task in the pile to be done
     - hasTask: Check for task in the taskpile
     - isEmergencyStopped: Returns if the bot is emergency stopped
     - ModBusInterface: Robot Modbus interface
     - state: Robot state
     - programState: Program state and name
    """
    def __init__(self,ip:str):
        """Controller For Robot task execution. It uses a pile to schedule task and execute the task when avaliable.

        Functions:
        - run: Main loop of the controller and task pile executer
        - stop: Stops controller
        - clear_task_pile: empty the task pile
        - __remove_task: Remove the first task of the pile
        - __assign_new_task: Assign a new task via modbus to the robot, task will be put in task register to be executed by the robot when avaliable
        - get_current_task: Get the current task from the robot
        - perform_task: Add a single task to the pile
        - follow_sequence: add a sequence of tasks to the pile
        - play_program: Start the program
        - stop_program: Stop the program
        - pause_program: Pause the program
        
        Property :
        - taskPile: Returns the current task pile
        - nextTask: Return the next task in the pile to be done
        - lastTask: Return the last task in the pile to be done
        - hasTask: Check for task in the taskpile
        - isEmergencyStopped: Returns if the bot is emergency stopped
        - ModBusInterface: Robot Modbus interface
        - state: Robot state
        - programState: Program state and name
        """
        Thread.__init__(self,name="RobotController")
        self.__ip = ip # IP of the bot

        self.__ModBusInterface = ModbusRobot(ip) #To interact with the bot
        self.__ModBusInterface.start()
        self.__DashInterface = DashRobot(ip) #To obtain program state
        self.__DashInterface.start()
        self.__taskPile = [] #This taks pile is used by the running loop to execute tasks
        self.__running = True #Boolean for the loop iteration

    def run(self):
        """Main Loop of the controller.
        Execute task from the pile and then remove it
        """
        while self.__running: # Main loop of the bot controller

            if self.hasTask: #Only if task are scheduled
                task = self.nextTask # Get next task from the pile

                self.__assign_new_task(task) # here we assign the task to the bot. It will be put in the register as the next action to be donne

                # Wait until bot finish previous task and start the new one put inside the register
                while self.get_current_task() != task and self.__running:
                    sleep(ROBOT_SLEEP_TIME/2)
                self.__remove_task() #Remove the scheduled task
            else :
                sleep(ROBOT_SLEEP_TIME)

    def stop(self):
        self.__running = False
    
    def clear_task_pile(self):
        """Clear all tasks in the pile"""
        with mutex:
            self.__taskPile = [0] #0 to ensure it goes back to idle state

    def __remove_task(self):
        """Remove the first task to the pile
        """
        mutex.acquire()
        if len(self.__taskPile) > 0:
            self.__taskPile.pop(0)
        mutex.release()
   


    def __assign_new_task(self,task:int):
        """Assign a new task via modbus to the robot, task will be put in task register to be executed by the robot when avaliable

        Args:
            task (int): number of the task

        Raises:
            TypeError: Task must be a int
        """
        if isinstance(task,int):
            self.__ModBusInterface.write("Next_Action",task)
        else:
            raise TypeError('Task must be a int')
    
        
    def get_current_task(self)->int:
        """Return the current task on the robot
        NOTE: It is fetched on the bot, not in the pile

        Returns:
            int: number of the currently executing task
        """
        return self.__ModBusInterface.read("Current_Action")
    
    def perform_task(self,task:int):
        """Method to perform a single task, create a sequence of 1 task

        Args:
            task (int): number of the task

        Raises:
            TypeError: Task must be a int
        """
        if isinstance(task,int):
            self.follow_sequence([task]) 
        else:
            raise TypeError('Task must be a int')
 
    
    
    def follow_sequence(self,sequence:list[int]):
        """Function to follow a sequence. Will add 0 before and after each task, to allow reapeating tasks

        Args:
            sequence (list[int]): sequence to follow

        Raises:
            TypeError: Sequence must be a list of ints
            Exception: Emergency stop
        """
        if not isinstance(sequence, list) or not all(isinstance(x, int) for x in sequence):
            raise TypeError("Sequence must be a list of ints")
        

              

        # Add 0 between each task in the sequence
        new_sequence = [item for task in sequence for item in (0, task)]

        # We must add a 0 to start the sequence only if last task is not 0
        if new_sequence[0] == 0 and self.lastTask == 0:
            new_sequence.pop(0)
        elif new_sequence[0] !=0 and self.lastTask != 0:
            new_sequence.insert(0, 0)
        
        if new_sequence[-1] != 0: #add 0 at the end
            new_sequence.append(0)

        mutex.acquire() #We need to lock to ensure we donet asign two different sequence at the same time
        for task in new_sequence:     
            self.__taskPile.append(task)
        mutex.release()


    def play_program(self):
        """Play the program
        """
        self.__DashInterface.play()
    
    def stop_program(self):
        """Stop the program
        """
        self.__DashInterface.stop()

    def pause_program(self):
        """Pause the program
        """
        self.__DashInterface.pause()

    @property
    def taskPile(self) -> list:
        """Returns the current task pile

        Returns:
            List: Task Pile
        """
        mutex.acquire()
        task_pile = self.__taskPile
        mutex.release()
        return task_pile

    @property
    def nextTask(self)->int:
        """Return the next task in the pile to be done
        NOTE: It is fetched on the pile, not in the bot

        Returns:
            int: Following task
        """
        task = None
        mutex.acquire()
        if len(self.__taskPile) > 0:
            task = self.__taskPile[0]
        
        mutex.release()
        return task 
    
    @property
    def lastTask(self)->int:
        """Return the last task in the pile to be done

        Returns:
            int: Following task
        """
        task = None
        mutex.acquire()
        if len(self.__taskPile) > 0:
            task = self.__taskPile[-1]
        
        mutex.release()
        return task 


    @property
    def hasTask(self) -> bool:
        """Check for task in the taskpile

        Returns:
            bool: True if task in taskpile, false otherwise
        """
        mutex.acquire()
        l = len(self.__taskPile)
        mutex.release()
        return l > 0

    @property
    def isEmergencyStopped(self)->int:
        """Check if the bot is emergency stopped

        Returns:
            int: 0 False and 1 True
        """
        return self.__ModBusInterface.read("isEmergencyStopped")

    @property
    def ModBusInterface(self)->ModbusRobot:
        """Returns the modbus interface. This allows to talk to the robot without requesting it via the controller.
        NOTE: DO NOT USE IT TO SCHEDULE TASKS

        Returns:
            ModbusRobot: Modbus interface
        """
        return self.__ModBusInterface
    
    @property
    def state(self)->int:
        """State of the robot.

        States:
        - Disconnected=0
        - Confirm_safety=1
        - Booting=2
        - Power_off=3
        - Power_on=4
        - Idle=5
        - Backdrive=6
        - Running=7

        Returns:
            int: State of the bot
        """
        return self.__ModBusInterface.read("state")
    
    @property
    def programState(self) -> str:
        """Returns the program state and the associated name
        
        STATE:
        - STOPPED <program name>
        - PLAYING <program name>
        - PAUSED  <program name>

        Returns:
            str: state at format <STATE> <program name>.
        """
        return self.__DashInterface.programState
    
    @property
    def programName(self) -> str:
        """Return the program name

        Returns:
            str: name of the program loaded
        """
        return self.__DashInterface.programName

    @property
    def ip(self) -> str:
        """Ip address of the robot

        Returns:
            str: ip address
        """
        return self.__ip
    

        
