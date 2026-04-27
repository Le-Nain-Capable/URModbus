"""This code implements a process into the code

Class:
 - Process: Manages a process with multiple tasks
 - Task: Manages a task within the process
"""
class Task():
    """Implementation of a Task
    """
    def __init__(self,taskId:int,name:str,requirements:list):
        """Implementation of a Task

        Args:
            taskId (int): id of the task
            name (str): description f the task
            requirements (list): task requirements
        """
        self.__taskId = taskId
        self.__name = name
        self.__requirements = requirements

    @property
    def taskId(self)->int:
        """Allow to get the task id

        Returns:
            int: task id
        """
        return self.__taskId
    
    @property
    def name(self)->str:
        """Allow to get the task name

        Returns:
            str: name
        """
        return self.__name
    
    @property
    def requirements(self)->list:
        """Allows to get the task requirements

        Returns:
            list: requirements
        """
        return self.__requirements

class Process():
    """Representation of the process file
    """
    def __init__(self,data:dict):
        """Implementation of a Process
        Args:
            data (dict): data.yaml read by the appropriate extract

        """
        self.__data = data

        self.__name = self.__data.get("name", "Not specified")
        self.__ordering = self.__data.get("ordering", [0])

        self.__tasks = []

        for task_id, task_data in self.__data.get("tasks", {0:{}}).items(): #Tasks for the process
            name = task_data.get('name', '')
            requires = task_data.get("requires", [0])
            self.__tasks.append(Task(task_id,name,requires))

        self._nulltask = Task(-1,"Task missmatch",[0]) #This is to handle accessing garbage tasks
        
    @property
    def name(self)->str:
        """Name of the process

        Returns:
            str: name
        """
        return self.__name
    
    @property
    def ordering(self)->list:
        """Ordering of the process

        Returns:
            list: ordering
        """
        return self.__ordering
    
    def get_task(self,task_id:int)->Task:
        """Allow to obtain a task

        Args:
            task_id (int): id of the task to obtain. Ex 0, 1 ,....

        Returns:
            Task: Task Object
        """
        if task_id < len(self.__tasks):
            
            return self.__tasks[task_id]
        else:
            return self._nulltask
        
    def isTaksInProcess(self,task_id:int)->bool:
        """Check if a task is in the process

        Args:
            task_id (int): task id

        Returns:
            bool: is task in process ?
        """
        task = self.get_task(task_id)
        return task != self._nulltask

    def changeProcessFile(self,data:dict)->None:
        """Change the current process to another one.

        Call this function with a new data dictionary to change the current process.

        Args:
            data (dict): data of the process file.
        """
        self.__data = data

        self.__name = self.__data.get("name", "Not specified")
        self.__ordering = self.__data.get("ordering", [0])

        self.__tasks = []

        for task_id, task_data in self.__data.get("tasks", {0:{}}).items(): #Tasks for the process
            name = task_data.get('name', '')
            requires = task_data.get("requires", [0])
            self.__tasks.append(Task(task_id,name,requires))



