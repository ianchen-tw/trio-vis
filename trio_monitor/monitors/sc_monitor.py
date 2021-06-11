from typing import Optional

import rich

from trio_monitor.desc_tree import DescNode, DescTree
from trio_monitor.protocol import TrioInstrument, TrioNursery, TrioTask

event_id = 0


def log(msg):
    global event_id
    event_id += 1
    rich.print(f"[red]event-{event_id}[reset] - [blue]{msg}")


called_id = 0


def api_called():
    global called_id
    rich.print(f"[yellow]api called-{called_id}[reset]")
    called_id += 1


def is_user_task(task):
    filename = None
    filename = task.coro.cr_frame.f_code.co_filename
    if "trio/_core" in filename:
        return False
    return True


"""Capture cases
+ -- task spawned
    1. Child root task spawned
    2. A new nursery started
    3. Task spawnd under a nursery
+ -- task exited
    4. Task exited but it's parent nursery still exists
    5. Task exited with ended it's child nursery
    6. child root exited
"""


class SC_Monitor(TrioInstrument):
    """SC Monitor
    Monitoring key structured-concurreny events happend in Trio
    """

    def __init__(self):
        self.root_task: Optional[TrioTask] = None
        self.desc_tree: Optional[DescTree] = None
        self.root_exited = False

    def task_spawned(self, task):
        # if not is_user_task(task):
        # return
        api_called()
        if not self.root_task:
            self.root_task = task
            self.desc_tree = DescTree.build(task)
            log(f"root task added:{task}")
            return
        parent_nursery: TrioNursery = self.desc_tree.find_parent_nursery_from_trio(task)
        if parent_nursery is None:
            log("Error!!!")
            return
        if len(parent_nursery.child_tasks) == 1:
            log(f"nursery started: {parent_nursery}")
        log(f"task started: {task}, parent:{parent_nursery}")
        # TODO: optimize
        self.desc_tree = DescTree.build(self.root_task)

    def task_exited(self, task):
        if self.root_exited:
            return
        api_called()
        desc_task: DescNode = self.desc_tree.ref_2node[task]
        if len(desc_task.children) > 0:
            for desc_child_nursery in desc_task.children:
                log(f"nursery exited: {desc_child_nursery.ref}, parent: {task}")
        if task == self.root_task:
            log(f"root task exited: {task}")
            self.root_exited = True
            return
        parent_nursery: TrioNursery = self.desc_tree.get_parent_nursery(task)
        log(f"task exited: {task}, parent:{parent_nursery}")
        self.desc_tree = DescTree.build(self.root_task)
