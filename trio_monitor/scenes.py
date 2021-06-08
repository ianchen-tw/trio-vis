from typing import Optional

import rich

from .fake import Nursery, Task, gen_tree_from_json
from .state import DescNode, DescTree

event_id = 0


def log(msg):
    global event_id
    event_id += 1
    rich.print(f"[red]event-{event_id}[reset] - [blue]{msg}")


class Monitor:
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

    def __init__(self):
        self.root_task: Optional[Task] = None
        self.desc_tree: Optional[DescTree] = None

    def task_spawned(self, task):
        if not self.root_task:
            self.root_task = task
            self.desc_tree = DescTree.build(task)
            log(f"root task added:{task}")
            return
        parent_nursery: Nursery = self.desc_tree.find_parent_nursery_from_trio(task)
        if parent_nursery is None:
            log("Error!!!")
            return
        if len(parent_nursery.child_tasks) == 1:
            log(f"nursery started: {parent_nursery}")
        log(f"task started: {task}, parent:{parent_nursery}")
        # TODO: optimize
        self.desc_tree = DescTree.build(self.root_task)

    def task_exited(self, task):
        desc_task: DescNode = self.desc_tree.ref_2node[task]
        if len(desc_task.children) > 0:
            for desc_child_nursery in desc_task.children:
                log(f"nursery exited: {desc_child_nursery.ref}, parent: {task}")
        if task == self.root_task:
            log(f"root task exited: {task}")
            return
        parent_nursery: Nursery = self.desc_tree.get_parent_nursery(task)
        log(f"task exited: {task}, parent:{parent_nursery}")
        self.desc_tree = DescTree.build(self.root_task)


class TrioScenes:
    def __init__(self, monitor=None):
        self._monitor: Monitor = monitor
        self.tree = None

    def scene0(self):
        tmpl = {
            "name": "t0",
            "nurseries": [],
        }
        tree: Task = gen_tree_from_json(tmpl)
        self.tree = tree
        root_task = tree.nodes["t0"]
        print("-- scene0")
        rich.print(self.tree)
        self._monitor.task_spawned(root_task)

    def scene1(self):
        n0 = Nursery(name="n0")
        t1 = Task(name="t1")
        n0._add_task(t1)
        self.tree._add_nursery(n0)
        print("-- scene1 spawn task")
        rich.print(self.tree)
        self._monitor.task_spawned(t1)

    def scene2(self):
        t1: Task = self.tree.nodes["t1"]
        n1 = Nursery(name="n1")
        t2 = Task(name="t2")
        n1._add_task(t2)
        t1._add_nursery(n1)
        print("-- scene2 spawn task")
        rich.print(self.tree)
        self._monitor.task_spawned(t2)

    def scene3(self):
        n1: Nursery = self.tree.nodes["n1"]
        t3: Task = Task(name="t3")
        n1._add_task(t3)
        print("-- scene3 spawn task")
        rich.print(self.tree)
        self._monitor.task_spawned(t3)

    def scene4(self):
        n1: Nursery = self.tree.nodes["n1"]
        t3 = self.tree.nodes["t3"]
        n1._remove_task(t3)
        print("-- scene4 exit task")
        rich.print(self.tree)
        self._monitor.task_exited(t3)

    def scene5(self):
        n1: Nursery = self.tree.nodes["n1"]
        t2 = self.tree.nodes["t2"]
        n1._remove_task(t2)
        print("-- scene5 exit task")
        rich.print(self.tree)
        self._monitor.task_exited(t2)

    def scene6(self):
        n0: Nursery = self.tree.nodes["n0"]
        t1 = self.tree.nodes["t1"]
        n0._remove_task(t1)
        print("-- scene6 exit task/nursery")
        rich.print(self.tree)
        self._monitor.task_exited(t1)

    def scene7(self):
        t0: Task = self.tree.nodes["t0"]
        print("-- scene7 exit root task")
        self._monitor.task_exited(t0)


def main():
    m = Monitor()
    scene = TrioScenes(monitor=m)
    scene.scene0()
    scene.scene1()
    scene.scene2()
    scene.scene3()
    scene.scene4()
    scene.scene5()
    scene.scene6()
    scene.scene7()


if __name__ == "__main__":
    main()
