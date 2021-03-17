from trio_monitor import TaskLoggingMonitor
from user_programs.happyeyeball import main as happyeyeball

import trio
import random


def main():
    random.seed(3)
    trio.run(happyeyeball, instruments=[TaskLoggingMonitor()])


if __name__ == "__main__":
    main()
