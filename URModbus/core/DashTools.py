"""
Dashboard implementation similar to the ur-rtde lib https://pypi.org/project/ur-rtde/

Class:
 - DashRobot: Implementation of the dashBoard
"""

import socket
from threading import Thread, Lock

mutex = Lock()

class DashRobot(Thread):
    """Dash Robot class to interact with a Dashboard server. 
        Simple TCP communication with the dashboard to interact with the bot

        init:
        - ip: IP address of the Dashboard server (your robot ip)
        - port: Port of the Dashboard server (default 29999)
        - timeout: Timeout Value (default 2.0)

        Functions:
        - play: Play the program
        - stop: Stop the current program
        - pause: Pause the current program

        Property:
        - programState: Get the current state of the robot
        - programNAme: Get the current program name
        """
    def __init__(self, ip, port=29999, timeout: float = 2.0):
        """Dash Robot class to interact with a Dashboard server. 
        It's a simple implentation to match my needs.

        init:
        - ip: IP address of the Dashboard server (your robot ip)
        - port: Port of the Dashboard server (default 29999)
        - timeout: Timeout Value (default 2.0)

        Functions:
        - play: Play the program
        - stop: Stop the current program
        - pause: Pause the current program

        Property:
        - programState: Get the current state of the robot
        - programName: Get the current program name
        """
        Thread.__init__(self,name="DashRobot") #On his own thread
        self.__ip = ip
        self.__port = port
        self.__timeout = timeout
    
    def __DashBoardCommand(self, command:str)-> str:
        """Simple tcp comunication with the bot

        Args:
            command (str): command to send

        Raises:
            RuntimeError: Server refused to greet us
            RuntimeError: Server didnt respond

        Returns:
            str: returned str
        """
        with mutex:
            with socket.create_connection((self.__ip, self.__port), timeout=self.__timeout) as sock:
                sock.settimeout(self.__timeout)

                # Read mandatory greeting
                greeting = sock.recv(1024)
                if not greeting:
                    raise RuntimeError("Dashboard server closed connection (no greeting)")

                # Send command
                sock.sendall((command + "\n").encode("ascii"))

                # Read response
                response = sock.recv(1024)
                if not response:
                    raise RuntimeError("Dashboard server closed connection (no response)")

                return response.decode("ascii", errors="ignore").strip()


    def play(self):
        """Play the program
        """
        state = self.programState
        if "PLAYING" not in state:
            self.__DashBoardCommand("play")
    
    def stop(self):
        """Stop the current program
        """
        state = self.programState
        if "STOPPED" not in state:
            self.__DashBoardCommand("stop")

    def pause(self):
        """Pause the program
        """
        state = self.programState
        if "PAUSED" not in state:
            self.__DashBoardCommand("pause")

    
    @property
    def programState(self) -> str:
        """Get the current state of the robot and loaded program

        STATE:
        - STOPPED <program name>
        - PLAYING <program name>
        - PAUSED  <program name>

        Returns:
            str: state at format <STATE> <program name>.
        """
        return self.__DashBoardCommand("programState")
        
    @property
    def programName(self) -> str:
        """Return the program name

        Returns:
            str: name of the program loaded
        """
        name = self.programState.split(" ")[-1]
        return name