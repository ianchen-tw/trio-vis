from typing import Optional

import rich

from trio_monitor.desc_tree import DescNode, DescTree
from trio_monitor.protocol import TrioInstrument, TrioNursery, TrioTask
from trio_monitor.registry import SCRegistry
from trio_monitor.sc_logger import SCLogger

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


def parent_from_registry(target, registry: SCRegistry):
    pass


class SC_Monitor(TrioInstrument):
    """SC Monitor
    Monitoring key structured-concurreny events happend in Trio
    """

    def __init__(self):
        self.registry = SCRegistry()
        self.root_task: Optional[TrioTask] = None
        self.desc_tree: Optional[DescTree] = None
        self.root_exited = False
        self.sc_logger = SCLogger(self.registry)

    def _name(self, obj) -> str:
        """Get parsed info from trio's task/nursery"""
        return self.registry.get_info(obj).name

    def rebuild_tree(self):
        self.desc_tree = DescTree.build(
            root_task=self.root_task, registry=self.registry
        )

    def task_spawned(self, task):
        # if not is_user_task(task):
        #     return
        api_called()
        if not self.root_task:
            self.root_task = task
            self.desc_tree = DescTree.build(task, registry=self.registry)
            log(f"root task added:{self._name(task)}")
            self.sc_logger.gen_event(desc="start", child=task, parent=None)
            return

        # Rebuild: becuase parent nursery might be added without notify our monitor
        # in that case we might need to detect these changes ourself
        # However, to keep it simple, we simply rebuild the whole tree here
        self.rebuild_tree()
        rich.print(self.desc_tree)

        parent_nursery: TrioNursery = self.desc_tree.get_parent_ref(task)
        if parent_nursery is None:
            log("Error!!!")
            return

        if len(parent_nursery.child_tasks) == 1:
            grand_parent = self.desc_tree.get_parent_ref(parent_nursery)
            log(f"nursery started: {self._name(parent_nursery)}")
            self.sc_logger.gen_event(
                desc="start", child=parent_nursery, parent=grand_parent
            )

        log(f"task started: {self._name(task)}, parent:{self._name(parent_nursery)}")
        self.sc_logger.gen_event(desc="start", child=task, parent=parent_nursery)

    def task_exited(self, task):
        # we only trace user task
        if self.root_exited:
            return

        api_called()
        task_name = self._name(task)

        desc_task: DescNode = self.desc_tree.ref_2node[task]
        if len(desc_task.children) > 0:
            for desc_child_nursery in desc_task.children:
                nursery_name = self._name(desc_child_nursery.ref)
                log(f"nursery exited: {nursery_name}, parent: {task_name}")
                self.sc_logger.gen_event(
                    desc="exited", child=desc_child_nursery.ref, parent=task
                )
                self.desc_tree.remove_ref(desc_child_nursery.ref)

        if task == self.root_task:
            log(f"root task exited: {task_name}")
            self.root_exited = True
            self.desc_tree.remove_ref(task)
            self.sc_logger.gen_event(desc="exited", child=task, parent=None)
            return

        parent_nursery: TrioNursery = self.desc_tree.get_parent_ref(task)
        log(f"task exited: {task_name}, parent:{self._name(parent_nursery)}")
        self.sc_logger.gen_event(desc="exited", child=task, parent=parent_nursery)
        self.desc_tree.remove_ref(task)

        # Bug
        # self.desc_tree.remove_node(desc_task)
        self.rebuild_tree()
        rich.print(self.desc_tree)
