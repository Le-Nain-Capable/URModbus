"""Settings parser
"""
#      ____                          
#     |  _ \ __ _ _ __ ___  ___ _ __ 
#     | |_) / _` | '__/ __|/ _ \ '__|
#     |  __/ (_| | |  \__ \  __/ |   
#     |_|   \__,_|_|  |___/\___|_|   
#                                    
from typing import Dict, List, Tuple, Callable, Optional, Set
from pathlib import Path
import logging
import re



SCRIPT_DIR = Path(__file__).resolve().parent
LOGGER = logging.getLogger(__name__)

def __read_Settings_raw() -> List:
    """Simple function to read the setting file

    Returns:
        List: content of the file
    """
    with open(SCRIPT_DIR / 'constants.py', 'r') as f:
        return f.readlines()

def parse_Settings()->Dict:
    """Simple parser to read data frome the settings file

    Returns:
        Dict: A dictionnary with setting: {"type": setting_type,"default": default,"description":comment}
    """

    text = __read_Settings_raw()

    section:str = ''
    setting:str = ''
    comment:str = ''
    default:str = ''
    type_dict = {'str':str,'float':float,'list':list,'int':int,'bool':bool,'dict':dict}
    setting_type:type
    relevant_text:List[str] = []

    parsed_results:Dict ={}



    for line in text:

        content = line.strip()

        
        #Parse section of the setting
        if content.startswith(("# -", "#-")) and content.endswith(("- #", "-#")):
            section = content.replace('#',"").replace("-","").strip()

            relevant_text = []
            continue

        #Parse settings values
        if re.search(r":\s*(bool|str|float|int|list(?:\[.*?\])?|dict(?:\[.*?\])?)\s*=", content):
            setting = content.split(":")[0].strip()
            setting_type = type_dict[content.split(':')[1].split('=')[0].split('[')[0].strip()]
            


            if setting != '':
                comment = '. '.join(relevant_text[:-1])
                default = relevant_text[-1]

                if 'Current_Action' in default: defval = {"Current_Action":(130,"R"), "Next_Action":(131,"W"), "isEmergencyStopped":(262,"R"), "state":(258,"R")}
                else: defval = setting_type(default)
                parsed_results[setting] = {"type": setting_type,
                                           "default": defval,
                                           "description":comment}

            relevant_text = []
            continue

        #End of content
        if "@staticmethod" in content:
            break
        #used to store data
        if content.strip()!= '':
            relevant_text += [content.strip('#').strip()]

    return parsed_results