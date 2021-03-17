from collections import defaultdict

import ipdb
import trio
from rich.console import Console

console = Console()


def task_name_colored(task):
    return f"[yellow]{task.name}[reset]"


class TaskLoggingMonitor(trio.abc.Instrument):
    def __init__(self):
        self.tasks = defaultdict(defaultdict)
        self.id_in_name = defaultdict(int)

    def _new_task_by_name(self, task):
        i = self.id_in_name[task.name]
        self.id_in_name[task.name] += 1
        return i

    def before_run(self):
        print("[Logger] run")

    def task_spawned(self, task):
        if "trio/_core" not in task.coro.cr_frame.f_code.co_filename:
            sid = self._new_task_by_name(task)
            t = self.tasks[task]
            t["sid"] = sid
            t["name"] = f"{task.name}-{sid}"
            ipdb.set_trace()
            console.print(
                f"[green]new task spwaned[orange_red1]({sid})[reset]: [yellow]{t['name']}"
            )

    def task_exited(self, task):
        if task in self.tasks:
            t = self.tasks[task]
            sid = t["sid"]
            console.print(
                f"[red]task exited[orange_red1]({sid})[reset]: [yellow]{t['name']}"
            )

    def before_task_step(self, task):
        if task in self.tasks:
            t = self.tasks[task]
            console.print(f"[bright_black]task step: {t['name']}")
