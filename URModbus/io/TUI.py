"""TUI code to display text with a simple helper.

Functions:
 - tuiPrint: Display a list of strings on fixed lines in the terminal, rewriting the same lines on each call.
 - format_pile: Simple helper function to prettyfly task pile display
 """
from datetime import datetime

def tuiPrint(lines:list) -> None:
    """Display a list of strings on fixed lines in the terminal, rewriting the same lines on each call

    Args:
        lines (list): list of lines to be written to the terminal. EX: ['text on line 1','text on line 2']
    """
    #We always add the current time to have a tracker of thing mooving
    lines = [f"# > {datetime.now().strftime('%H:%M:%S')}"] + lines 
    
    # Keep track of how many lines were printed last time
    if not hasattr(tuiPrint, "line_count"):
        tuiPrint.line_count = 0

    # Move up and clear previous lines
    for _ in range(tuiPrint.line_count):
        print("\033[F\033[K", end="")

    # Print new lines
    for line in lines:
        print(line)

    # Update stored line count
    tuiPrint.line_count = len(lines)

def format_pile(pile:list[int])->list:
    """Function to simplify the current task pile of the bot.
    Tranform [0,1,0,2,0,3,0,4,0,5,0,6,0] into a pretty version

    Args:
        pile (list[int]): raw task pile

    Returns:
        list: formated task pile
    """

    pile = [i for i in pile if i != 0]

    if len(pile)>6: #if more than 6 tasks
        pile = pile[0:3] + ["..."] + pile[-3:]
    
    return pile