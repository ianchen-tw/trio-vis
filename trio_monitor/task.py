from collections import defaultdict

from trio.lowlevel import Task


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
