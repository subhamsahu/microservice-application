"""
This module contains formatters used in the application
"""
from dataclasses import dataclass
from pyfiglet import Figlet

@dataclass
class Colour:
    """
    Used to print the colours in the Console Prints.
    Contains no Methods
    """
    header = '\033[95m'
    blue = '\033[94m'
    green = '\033[92m'
    yellow = '\033[93m'
    red = '\033[91m'
    end_c = '\033[0m'
    bold = '\033[1m'
    underline = '\033[4m'


def display_dotted_string(string):
    """
    Used to display the string in a dotted format
    :param string: String
    :return: None
    """

    font = Figlet(font='slant')
    print(Colour.blue + font.renderText(string) + Colour.end_c)
