"""TUI code to display text with a simple helper.

Functions:
 - tuiPrint: Display a list of strings on fixed lines in the terminal, rewriting the same lines on each call.
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