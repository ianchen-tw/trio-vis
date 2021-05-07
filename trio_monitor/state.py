import typing
from typing import Any, TypeVar, cast

""" Description Node/Tree

    We trace the current system state by keeping our own task tree

    This tree must support:
    1. Build up a state tree based on the trio node given
    2. Given a task, find it's parent
    3. Given another tree, find the first node which is different
    4. Operations for adding/removing a single node to/from tree
"""


class TrioNursery(typing.Protocol):
    """Represent trio's internal `Nursery` type"""

    name: str
    child_tasks: typing.List["TrioTask"]


class TrioTask(typing.Protocol):
    """Represent trio's internal `Task` type"""

    name: str
    child_nurseries: typing.List["TrioNursery"]


TrioNode = TypeVar("TrioNode", TrioNursery, TrioTask)


class DescNode:
    def __init__(self, node: TrioNode):
        self.name: str = node.name

        self.parent: Any = None
        self.childs: typing.List[DescNode] = []

        # ref to the actual node
        self.ref: typing.Union[TrioTask, TrioNursery] = node

    def __repr__(self):
        return f"<DescNode:{self.name}: {self.childs}>"


class DescTree:
    def __init__(self, root):
        self.root: DescNode = root

    def __repr__(self):
        return f"{self.root}"

    @classmethod
    def build(cls, root_task: TrioTask) -> "DescTree":
        """Build a tree of from source"""

        def build_task(desc_task: DescNode):
            task = cast(TrioTask, desc_task.ref)
            for n in task.child_nurseries:
                desc_n = DescNode(n)
                desc_n.parent = desc_task
                desc_task.childs.append(desc_n)
                build_nursery(desc_n)

        def build_nursery(desc_nursery: DescNode):
            nursery = cast(TrioNursery, desc_nursery.ref)
            for t in nursery.child_tasks:
                desc_t = DescNode(t)
                desc_t.parent = desc_nursery
                desc_nursery.childs.append(desc_t)
                build_task(desc_t)

        desc_root = DescNode(root_task)
        build_task(desc_root)
        instance = cls(root=desc_root)
        return instance
