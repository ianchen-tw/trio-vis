import random

import trio

# from trio_monitor import tree_logger
from trio_monitor.monitors import SC_Monitor
from user_programs.happyeyeball import main as happyeyeball


def main():
    random.seed(3)
    # monitor = tree_logger.TaskLoggingMonitor(logger=tree_logger.TrioJsonLogger())
    # monitor = tree_logger.TaskLoggingMonitor(logger=tree_logger.TrioTerminalLogger())

    trio.run(happyeyeball, instruments=[SC_Monitor()])


if __name__ == "__main__":
    main()
