"""This script contains tools to manipulate data

Functions:
    read_data_file: Reads a YAML file and returns its contents as a dictionary.
    build_sequence: Builds a sequence of integers based on the data provided.
    write_task_time: Writes task time to a file.
    calculate_mean_time: Calculates statistical values for a process task file.
    
"""
from URModbus.config.constants import Settings
import yaml
import os
import numpy as np

def read_data_file(file:str)->dict:
    """This function read the data contained in the yaml process file

    Args:
        file (str): name of the file in the DATA_DIR

    Returns:
        dict: the file data
    """
    # Open the YAML file for reading
    with open(f"./{Settings.DATA_DIR}/{file}", 'r') as stream:
        try:
            # Load the data from the YAML file into a Python dictionary
            data = yaml.safe_load(stream)
            return data
        except yaml.YAMLError as exc:
            return exc
        
def build_sequence(data:dict)->list[int]:
    """This function load the sequence from the extracted process file data

    Args:
        data (dict): data extracted with read_data_file

    Returns:
        list[int]: sequence like [1,2,3,4]
    """
    # Extract the ordering list

    sequence = data['ordering']

    # print("Sequence")

    # for task in sequence:
    #     print(f"{(task,data['tasks'][task]['name'])},")


    return sequence
        
def write_task_time(process:str,task:int,dataID:float,time:float):
    """Function to write process times to a file

    Args:
        process (str): the name of the current process, used for directory
        task (int): int of the task
        dataID (float): identifier for the data
        time (float): time of the task
    """
    # Check if the directory exists
    dir_path = f"./{Settings.AUTOGEN_DIR}/{process}"
    if not os.path.exists(dir_path):
        # Create the directory
        os.makedirs(dir_path)

    file_path = dir_path + f"/{task}.txt"
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            pass
    
    with open(file_path, "a") as f:
        f.write(f"{dataID};{time}\n")

def calculate_mean_time(process:str,task:int)->list[float]:
    """Calculates statistical values for a process task file.
    
    Calculates:
     - Mean
     - Standard Deviation
     - Mean +/- Standard Deviation
     - Last 100 values mean

    Args:
        process (str): name of the process
        task (int): number of the file

    Returns:
        list[float]: returns a list of floats [Means, Std Dev, Mean +/- Std dev, Last 100 values mean]
    """
  

    # Read the file
    try:
        data = np.loadtxt(f"./{Settings.AUTOGEN_DIR}/{process}/{task}.txt", delimiter=';')
    except FileNotFoundError:
        return [0]*4
    
    try:
        values = data[:,1]
    except:
        return [0]*4
    
    # Get the last 100 values
    last_100 = data[-100:, 1]

    # Calculate mean, standard deviation, and mean with values in +/- std dev compared to mean
    mean = np.mean(values)
    std_dev = np.std(values)
    within_std_dev = values[(values >= (mean - std_dev)) & (values <= (mean + std_dev))]
    mean_within_std_dev = np.mean(within_std_dev)
    last_100_mean = np.mean(last_100)

    # Return the calculated values
    return [np.round(mean, 2), np.round(std_dev, 2), np.round(mean_within_std_dev, 2), np.round(last_100_mean, 2)]
