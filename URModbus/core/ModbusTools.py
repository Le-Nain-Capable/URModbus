"""Modbus tools to interact with the root modbus

class:
 - ModbusRobot: Class to interact with the robot modbus server.
"""
from URModbus.config.constants import Settings
from pymodbus.client import ModbusTcpClient
from threading import Thread, Lock

mutex = Lock()

class ModbusRobot(Thread):
    """Modbus Robot class to interact with a Modbus server. 

    Functions:
     - __read_reg: Read wrapper, add connection and disconection to the robot
     - __write_reg: Write wrapper, add connection and disconnection to the robot
     - read: This function is used to read robot register, it uses mapping dictionnary to verify if it can read the register.
     - write: This function is used to write a value to a robot register, it uses mapping dictionnary to verify if it can write the register.
    """
    __MAPPING_MOT_ADRESSES = Settings.MOTS.copy() #Private shared property
    __MAPPING_ADRESSES_MOT = {value[0]:(key,value[1]) for key,value in __MAPPING_MOT_ADRESSES.items()} #private shared property
    def __init__(self,ip:str):
        """Modbus Robot class to interact with a Modbus server. 

        Functions:
        - __read_reg: Read wrapper, add connection and disconection to the robot
        - __write_reg: Write wrapper, add connection and disconnection to the robot
        - read: This function is used to read robot register, it uses mapping dictionnary to verify if it can read the register.
        - write: This function is used to write a value to a robot register, it uses mapping dictionnary to verify if it can write the register.
        """
        Thread.__init__(self,name="ModbusRobot")
        self.__client = ModbusTcpClient(ip) 

    def __read_reg(self,address:int,count:int) -> int:
        """Read wrapper, add connection and disconection to the robot

        Args:
            address (int): address to be written
            count (int): count

        Returns:
            int: value read
        """
        mutex.acquire()
        self.__client.connect()
        value = self.__client.read_holding_registers(address=address, count=count).registers[0]
        self.__client.close()
        mutex.release()
        return value
    
    def __write_reg(self,address:int,value:int) -> bool:
        """Write wrapper, add connection and disconection to the robot

        Args:
            address (int): address to be written
            value (int): value to be written

        Returns:
            bool: True if the write was successful, False otherwise.
        """
        mutex.acquire()
        self.__client.connect()
        self.__client.write_register(address=address,value=value)
        self.__client.close()
        mutex.release()
        return True

    def read(self,register:int | str) -> int:
        """This function is used to read robot register, it uses mapping dictionnary to verify if it can read the register.

        Args:
            register (int | str): read modbus address, can be int or str

        Raises:
            ValueError: Address not readable
            TypeError: Adress is neither int or str

        Returns:
            int: read value
        """
        if isinstance(register, int):
            mot, access_type = ModbusRobot.__MAPPING_ADRESSES_MOT[register]
            if access_type == "R":
                return self.__read_reg(address=register, count=1)
            else:
                raise ValueError(f"Register {register},{mot} is not readable")
            
        elif isinstance(register, str):
            register_address, access_type = ModbusRobot.__MAPPING_MOT_ADRESSES[register]
            if access_type == "R":
                return self.__read_reg(address=register_address, count=1)
            else:
                raise ValueError(f"Register {register_address},{register} is not readable")
        else:
            raise TypeError("Invalid type for register. Expected int or str.")
        
    def write(self,register:int | str,value:int) -> bool:
        """This function is used to write a value to a robot register, it uses mapping dictionnary to verify if it can write the register.

        Args:
            register (int | str): written modbus address, can be int or str
            value (int): written modbus value

        Raises:
            ValueError: Address not writeable
            TypeError: Adress is neither int or str

        Returns:
            bool: write success
        """
        if isinstance(value, int) == False:
            raise ValueError("Value must be an integer")

        if isinstance(register, int):
            mot, access_type = ModbusRobot.__MAPPING_ADRESSES_MOT[register]
            if access_type == "W":
                return self.__write_reg(address=register, value=value)
            else:
                raise ValueError(f"Register {register},{mot} is not writable")
            
        elif isinstance(register, str):
            register_address, access_type = ModbusRobot.__MAPPING_MOT_ADRESSES[register]
            if access_type == "W":
                return self.__write_reg(address=register_address, value=value)
            else:
                raise ValueError(f"Register {register_address},{register} is not writable")
        else:
            raise TypeError("Invalid type for register. Expected int or str.")
