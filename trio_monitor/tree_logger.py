import json
import time
from pathlib import Path
from typing import Optional

import trio
from rich.console import Console
from rich.tree import Tree
from trio.lowlevel import Task
from trio_typing import Nursery

from trio_monitor.task import TaskRegistry

console = Console()


class TrioJsonLogger:
    def __init__(self):
        self.registry = TaskRegistry()

    def dump_state_from_task(self, root_task: Task, name: str):
        data = self.task_to_json(root_task)
        Path("./status").mkdir(exist_ok=True)
        with open(f"./status/{name}.json", "w") as outfile:
            json.dump(data, outfile, indent=4)

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


class TrioTerminalLogger:
    def __init__(self):
        self.console = Console()
        self.registry = TaskRegistry()

    def dump_state_from_task(self, root_task: Task, name):
        root_node = Tree(f"[b green]{name}")
        self.append_task_to_node(root_task, parent_node=root_node)
        console.print(root_node)

    def append_nursery_to_node(self, nursery: Nursery, parent_node):
        nursery_node = parent_node.add("[bold yellow]Nursery")
        for t in nursery.child_tasks:
            self.append_task_to_node(task=t, parent_node=nursery_node)

    def append_task_to_node(self, task: Task, parent_node):
        task_node = parent_node.add(
            "[bold magenta]" + self.registry.get_task_name(task)
        )
        for n in task.child_nurseries:
            self.append_nursery_to_node(nursery=n, parent_node=task_node)


class TaskLoggingMonitor(trio.abc.Instrument):
    def __init__(self, logger):
        self.event_id = 0
        self.logger = logger
        self.client_root_task: Optional[Task] = None

    def get_new_event_id(self) -> int:
        eid = self.event_id
        self.event_id += 1
        return eid

    def dump(self, name):
        self.logger.dump_state_from_task(
            self.client_root_task,
            name=name,
        )

    def task_spawned(self, task):
        # log from user root
        if "trio/_core" not in task.coro.cr_frame.f_code.co_filename:
            if not self.client_root_task:
                self.client_root_task = task
            name = f"event-{self.get_new_event_id()}-spawned"
            self.dump(name)
            time.sleep(0.5)

    def task_exited(self, task):
        # if "trio/_core" not in task.coro.cr_frame.f_code.co_filename:
        name = f"event-{self.get_new_event_id()}-exited"
        self.dump(name)
