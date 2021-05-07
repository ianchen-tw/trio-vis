from typing import Optional

import rich

from .fake import Nursery, Task, gen_tree_from_json

event_id = 0


def log(msg):
    global event_id
    event_id += 1
    rich.print(f"[red]event-{event_id}[reset] - [blue]{msg}")


def find_parent_nursery(
    tree_root: Task,
    target: Task,
):
    for n in tree_root.child_nurseries:
        if target in n.child_tasks:
            return n
        else:
            for t in n.child_tasks:
                nursery = find_parent_nursery(t, target)
                if nursery:
                    return nursery
    return None


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

    def task_spawned(self, task):
        if not self.root_task:
            self.root_task = task
            log(f"root task added:{task}")
            return
        parent_nursery: Nursery = find_parent_nursery(self.root_task, task)
        if parent_nursery is None:
            log("Error!!!")
            return
        if len(parent_nursery.child_tasks) == 1:
            log(f"nursery started: {parent_nursery}")
        log(f"task started: {task}, parent:{parent_nursery}")

    def task_exited(self, task):
        pass


class TrioScenes:
    def __init__(self, monitor=None):
        self._monitor: Monitor = monitor
        self.tree = None

    def event1(self):
        tmpl = {
            "name": "t1",
            "nurseries": [],
        }
        tree: Task = gen_tree_from_json(tmpl)
        self.tree = tree
        root_task = tree.nodes["t1"]
        print("-- event1")
        rich.print(self.tree)
        self._monitor.task_spawned(root_task)

    def event2(self):
        n1 = Nursery(name="n1")
        t2 = Task(name="t2")
        n1._add_task(t2)
        self.tree._add_nursery(n1)
        print("-- event2")
        rich.print(self.tree)
        self._monitor.task_spawned(t2)

    def event3(self):
        n1: Nursery = self.tree.nodes["n1"]
        t3 = Task(name="t3")
        n1._add_task(t3)
        print("-- event3")
        rich.print(self.tree)
        self._monitor.task_spawned(t3)


def main():
    m = Monitor()
    scene = TrioScenes(monitor=m)
    scene.event1()
    scene.event2()
    scene.event3()


if __name__ == "__main__":
    main()
