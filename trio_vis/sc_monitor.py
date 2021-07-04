from typing import Optional

import rich

from trio_vis.config import VisConfig
from trio_vis.desc_tree import DescNode, DescTree
from trio_vis.protocol import TrioInstrument, TrioNursery, TrioTask
from trio_vis.registry import SCRegistry
from trio_vis.sc_logger import Logger, SCLogger


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
    5. Task exited with it's child nursery ended
    6. root task exited
"""


def parent_from_registry(target, registry: SCRegistry):
    pass


class SC_Monitor(TrioInstrument):
    """SC Monitor
    Monitoring key structured-concurreny events happend in Trio
    """

    def __init__(self, config: VisConfig = VisConfig(), sc_logger=SCLogger):
        self.registry = SCRegistry()
        self.root_task: Optional[TrioTask] = None
        self.desc_tree: Optional[DescTree] = None
        self.root_exited = False

        self.cfg: VisConfig = config

        self.event_id: int = 0
        self.called_id: int = 0

        # the logger would write the entire file right before the program exit
        self.sc_logger: Logger = sc_logger(
            self.registry, log_filename=self.cfg.log_filename
        )

    def log(self, msg):
        self.event_id += 1
        if self.cfg.print_task_tree is True:
            rich.print(f"[red]event-{self.event_id}[reset] - [blue]{msg}")

    def api_called(self):
        if self.cfg.print_task_tree is True:
            rich.print(f"[yellow]api called-{self.called_id}[reset]")
        self.called_id += 1

    @classmethod
    def from_tree(cls, root_task: TrioTask, *args, **kwargs):
        """Build the Monitor with a given state, used for testing"""
        instance = cls(*args, **kwargs)
        instance.cfg.only_vis_user_scope = False
        instance.root_task = root_task
        instance.rebuild_tree()
        return instance

    def _name(self, obj) -> str:
        """Get parsed info from trio's task/nursery"""
        return self.registry.get_info(obj).name

    def rebuild_tree(self):
        self.desc_tree = DescTree.build(
            root_task=self.root_task, registry=self.registry
        )

    def task_spawned(self, task):
        if self.cfg.only_vis_user_scope is True and not is_user_task(task):
            return
        self.api_called()
        if not self.root_task:
            self.root_task = task
            self.desc_tree = DescTree.build(task, registry=self.registry)
            self.log(f"root task added:{self._name(task)}")
            self.sc_logger.log_start(child=task, parent=None)
            return

        # Rebuild: becuase parent nursery might be added without notify our monitor
        # in that case we might need to detect these changes ourself
        # However, to keep it simple, we simply rebuild the whole tree here
        self.rebuild_tree()
        if self.cfg.print_task_tree:
            rich.print(self.desc_tree)

        parent_nursery: TrioNursery = self.desc_tree.get_parent_ref(task)
        if parent_nursery is None:
            self.log("Error!!!")
            return

        if len(parent_nursery.child_tasks) == 1:
            grand_parent = self.desc_tree.get_parent_ref(parent_nursery)
            self.log(f"nursery started: {self._name(parent_nursery)}")
            self.sc_logger.log_start(child=parent_nursery, parent=grand_parent)

        self.log(
            f"task started: {self._name(task)}, parent:{self._name(parent_nursery)}"
        )
        self.sc_logger.log_start(child=task, parent=parent_nursery)

    def task_exited(self, task):
        # we only trace user task
        if self.root_exited:
            return

        self.api_called()
        task_name = self._name(task)

        desc_task: DescNode = self.desc_tree.ref_2node[task]
        if len(desc_task.children) > 0:
            for desc_child_nursery in desc_task.children:
                nursery_name = self._name(desc_child_nursery.ref)
                self.log(f"nursery exited: {nursery_name}, parent: {task_name}")
                self.sc_logger.log_exit(child=desc_child_nursery.ref, parent=task)
                self.desc_tree.remove_ref(desc_child_nursery.ref)

        if task == self.root_task:
            self.log(f"root task exited: {task_name}")
            self.root_exited = True
            self.sc_logger.log_exit(child=task, parent=None)
            # Notice: we shouldn't remove root task from registry
            # since we need to retrieve it's name from registry in the logger
            return

        parent_nursery: TrioNursery = self.desc_tree.get_parent_ref(task)
        self.log(f"task exited: {task_name}, parent:{self._name(parent_nursery)}")
        self.sc_logger.log_exit(child=task, parent=parent_nursery)
        self.desc_tree.remove_ref(task)

        self.rebuild_tree()
        if self.cfg.print_task_tree:
            rich.print(self.desc_tree)
