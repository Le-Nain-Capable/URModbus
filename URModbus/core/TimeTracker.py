"""Time tracker to follow robot task execution time. Values are written to a file.

class:
 - TimeTracker: class to track time
"""
from URModbus.core.RobotController import RobotController
from URModbus.core.ProcessTools import Process
from URModbus.config.constants import Settings
from URModbus.io.DataParser import write_task_time
from threading import Thread, Lock
from time import sleep,time

mutex = Lock()

class TimeTracker(Thread):
    """Class for tracking robot task time
    
    Functions:
     - __init__: Initialize the class
     - run: Run the class
     - stop: Stop the class"""
    def __init__(self,controller:RobotController,process:Process):
        """Initialise the tracker.

        Args:
            controller (Robotcontroller): The current robot controller, to track the process of robot tasks
            process (Process): The current process
        """
        Thread.__init__(self,name="TimeTracker")
        self.__running = True #Boolean for the loop iteration
        self.__controller = controller
        self.__process = process
        self.__start_time = 0
        self.__end_time = 0
        self.__pause_time = 0

    def run(self):
        """The program monitor task execution and stores times. It can also detect if the bot is not running
        """
        last_task = 0
        #This simple watcher will keep track of task times

        while self.__running: # Main loop 
            sleep(Settings.ROBOT_SLEEP_TIME/5)
            current_task = self.__controller.get_current_task()

            # IF there is a mismatch, then it means the task as changed.
            # Either we finished one either we started one
            if last_task != current_task:
                if current_task != 0:
                    # IF current task change from 0, it means a new tasks starts
                    with mutex:
                        self.__start_time = time()
                if current_task == 0 and last_task !=0:
                    # A task end

                    with mutex:
                        self.__end_time = time()

                        t = self.__end_time-self.__start_time-self.__pause_time-(2*Settings.ROBOT_SLEEP_TIME)

                        if t > 0 :
                            write_task_time(self.__process.name,
                                            last_task,
                                            self.__end_time,
                                            t) #2 0 task between tasks

                        self.__pause_time = 0
                last_task = current_task
            
            if "PLAYING" not in self.__controller.programState or self.__controller.isEmergencyStopped: 
                #This simple thing will check if the robot is running or not and add sleeping time
                with mutex:
                    self.__pause_time += Settings.ROBOT_SLEEP_TIME/5
 
    def stop(self):
        self.__running = False

    @property
    def time(self):
        with mutex:
            t = round(time()-self.__start_time-self.__pause_time-Settings.ROBOT_SLEEP_TIME,2)
            if t>0:
                return t
            else:
                return 0

    
    