# Light Strip Control Code

import fpstimer
import sys

from colors import *
from lightstrip import LightStrip
from rule import Rule

FRAMERATE = 60


def main():
    print("Python version:", sys.version)

    light_strip = LightStrip(150)
    cool_colors = Rule().stripes([RED, WHITE, BLUE], 10).animate(5)
    light_strip.set_rule(cool_colors)

    # Framerate maintainer
    timer = fpstimer.FPSTimer(FRAMERATE)

    while True:
        light_strip.update()
        timer.sleep()


if __name__ == "__main__":
    main()
