from trio_monitor import tree_logger
from user_programs.happyeyeball import main as happyeyeball

import trio
import random


def main():
    random.seed(3)
    monitor = tree_logger.TaskLoggingMonitor(logger=tree_logger.TrioJsonLogger())
    # monitor = tree_logger.TaskLoggingMonitor(logger=tree_logger.TrioTerminalLogger())

    trio.run(happyeyeball, instruments=[monitor])


if __name__ == "__main__":
    main()
