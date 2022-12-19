# Definitions for colors and sets of colors

import random

# Colors
DARK_RED = (80, 0, 0)
RED = (255, 0, 0)
ORANGE = (255, 40, 0)
YELLOW = (255, 255, 0)
DARK_GREEN = (0, 80, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
DARK_BLUE = (0, 0, 80)
BLUE = (0, 0, 255)
PURPLE = (150, 0, 255)
MAGENTA = (255, 0, 255)
PINK = (255, 0, 80)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
BLACK = (0, 0, 0)
OFF = (0, 0, 0)

RAINBOW = (RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE)

# Schools
VT = ((50, 10, 0), (255, 80, 0))

# Countries
USA = (RED, WHITE, BLUE)
GERMANY = (OFF, RED, YELLOW)
MEXICO = (DARK_GREEN, WHITE, RED)  # Also Italy
SPAIN = (RED, (100, 100, 0), RED)
INDIA = (ORANGE, WHITE, DARK_GREEN)
CHINA = (RED, YELLOW)

# Mario characters
MARIO = (RED, BLUE)
LUIGI = (GREEN, BLACK, GREEN, WHITE)
BOWSER = (RED, YELLOW, ORANGE)
WARIO = (YELLOW, BLACK)
WALUIGI = (PURPLE, GRAY)
PEACH = (PINK, WHITE)
BOO = (WHITE, BLACK)


def random_color():
    """
    :return: A random color.
    """
    return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
