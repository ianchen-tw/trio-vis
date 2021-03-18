import json
from collections import defaultdict
from pathlib import Path
from typing import Optional

import trio
from rich.console import Console
from trio.lowlevel import Task
from trio_typing import Nursery

console = Console()


class TaskRegistry:
    def __init__(self):
        self.serial_num_from_name = defaultdict(int)
        self.registered_tasks = defaultdict(defaultdict)

    def get_task_name(self, task: Task):
        if task not in self.registered_tasks:
            serial_num = self.serial_num_from_name[task.name]
            self.serial_num_from_name[task.name] += 1
            self.registered_tasks[task]["serial_num"] = serial_num
        else:
            serial_num = self.registered_tasks[task]["serial_num"]
        return f"{task.name}-{serial_num}"


class TrioStatusLogger:
    def __init__(self):
        self.registry = TaskRegistry()

    def get_system_status_json(self, root_task: Task):
        result = self.task_to_json(root_task)
        return result

    def nursery_to_json(self, nursery: Nursery):
        return {
            "id": id(nursery),
            "name": "<nursery>",
            "tasks": [self.task_to_json(child) for child in nursery.child_tasks],
        }

    def task_to_json(self, task: Task):
        return {
            "id": id(task),
            "name": self.registry.get_task_name(task),
            "nurseries": [
                self.nursery_to_json(nursery) for nursery in task.child_nurseries
            ],
        }


class TaskLoggingMonitor(trio.abc.Instrument):
    def __init__(self):
        self.event_id = 0
        self.logger = TrioStatusLogger()
        self.client_root_task: Optional[Task] = None

    def log_status(self, suffix: str = ""):
        eid = self.event_id
        self.event_id += 1
        dic = self.logger.get_system_status_json(root_task=self.client_root_task)
        actual_suffix = f"-{suffix}" if suffix != "" else ""
        Path("./status").mkdir(exist_ok=True)
        with open(f"./status/event-{eid}{actual_suffix}.json", "w") as outfile:
            json.dump(dic, outfile, indent=4)

    def task_spawned(self, task):
        if "trio/_core" not in task.coro.cr_frame.f_code.co_filename:
            if not self.client_root_task:
                self.client_root_task = task
            self.log_status(suffix="spawned")

    def task_exited(self, task):
        # if "trio/_core" not in task.coro.cr_frame.f_code.co_filename:
        self.log_status(suffix="exited")
