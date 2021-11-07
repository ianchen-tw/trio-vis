from typing import Any, Dict, List, Optional, Union, cast

from rich.console import Console, ConsoleOptions, RenderResult
from rich.tree import Tree as RichTree

from .protocol import TrioNursery, TrioTask

""" Generate Identical Fake data for developing & test
Provide a simpler interface for constructing trio task tree & specifying nodes by their name
"""


class FakeNode:
    """The underlying node for fake objects"""

    def __init__(self, name: str):
        self._children: List = []
        self._parent: Optional["FakeNode"] = None
        self._name: str = name

        # FakeTrioTask is able to reference node by it's name without using registry

        # Each node would register itself with to root node's dict, so we could referece
        # node by it's name
        self._tree_root: Optional["FakeNode"] = self
        self._nodes: Dict[str, "FakeNode"] = {}  # only used by the tree root node
        self.register(self, name=name)

    def __contains__(self, key: Union[str]) -> bool:
        if type(key) is str:
            return key in self._nodes
        else:
            NotImplementedError
        return False

    def get_task_node(self, node_name: str) -> "FakeTrioTask":
        return cast("FakeTrioTask", self._nodes[node_name])

    def get_nursery_node(self, node_name: str) -> "FakeTrioNursery":
        return cast("FakeTrioNursery", self._nodes[node_name])

    @property
    def is_root(self) -> bool:
        return self == self.tree_root

    def tree_add(self, node: "FakeNode", parent_name: str):
        parent: "FakeNode" = self.tree_root._nodes[parent_name]
        if node in parent._children:
            raise RuntimeError(f"Children alreay exists: {node._name}")
        parent._children.append(node)
        node._parent = parent
        # child would register itself to the root node while new root node is assigned
        node.tree_root = self.tree_root

    def tree_remove(self, node_name: str):
        node = self.tree_root._nodes[node_name]
        if node == self.tree_root:
            raise RuntimeError("Should not remove root from tree")
        # except the root node, every node must have parent
        if node._parent is None:
            raise RuntimeError("Bug: orphan node")
        parent = node._parent
        if node not in node._parent._children:
            raise RuntimeError("Bug: children node not recorded in parent")
        parent._children.remove(node)
        node._parent = None
        # Modify root
        node.tree_root = node

    @property
    def tree_root(self):
        return self._tree_root

    @tree_root.setter
    def tree_root(self, new_root: "FakeNode"):
        """side effect: would register itself to the root node"""
        if new_root is None:
            raise RuntimeError("Should not assign root to none")
        if new_root == self._tree_root:
            return

        # parent management
        if new_root is self and self._parent is not None:
            parent = self._parent
            if self not in parent._children:
                raise RuntimeError("Bug: children node not recorded in parent")
            parent._children.remove(self)
            self._parent = None

        # only used for type checking...
        assert self._tree_root is not None

        # unregister from old root
        # clear self from the origianl tree root
        del self._tree_root._nodes[self._name]

        # register to the new root
        self._tree_root = new_root
        self._tree_root.register(node=self, name=self._name)

        # propagate to all of it's children
        for child in self._children:
            child.tree_root = self.tree_root

    def register(self, node: "FakeNode", name: str):
        """Register a node to this root node"""
        if not self.is_root:
            raise RuntimeError("Could only call register on a root task")
        if name in self._nodes:
            raise ValueError(f"Registered name already exists: {name}")
        self._nodes[name] = node


def generate_fake_attr(nested_list: List[str], val: Any):
    """Generate a nested attribute"""

    class FakeObject:
        def __init__(self):
            pass

    obj = None

    target = val
    for attr in nested_list[::-1]:
        obj = FakeObject()
        setattr(obj, attr, target)
        target = obj
    return target


class FakeTrioNursery(FakeNode, TrioNursery):
    """Represent the trio internal type."""

    def __init__(self, name: str):
        super().__init__(name)

    @property
    def child_tasks(self):
        return self._children

    @property
    def _trio_vis_name(self):
        return self._name

    def _add_task(self, task: "FakeTrioTask"):
        self.tree_root.tree_add(task, self._name)

    def _remove_task(self, task_name: str):
        self.tree_root.tree_remove(task_name)

    def __repr__(self):
        if len(self.child_tasks) > 0:
            return f"<Nursery({self._name}) {self.child_tasks}>"
        return f"<Nursery({self._name})>"

    @property
    def rich_tag(self):
        ret = "[bold magenta]Nursery"
        if self._name is not None:
            ret += f": [white]{self._name}"
        return ret

    def _rich_node(self, parent: RichTree):
        cur_node = parent.add(self.rich_tag)
        for t in self.child_tasks:
            t._rich_node(parent=cur_node)


class FakeTrioTask(FakeNode, TrioTask):
    """Represent the trio internal type
    The only usable attributes are `self.child_nurseries` & `name`
    """

    def __init__(self, name: str):
        super().__init__(name)
        self.coro = generate_fake_attr(["cr_code", "co_name"], name)
        print(f"get root-> {super().tree_root}")

    @property
    def name(self):
        return self._name

    @property
    def child_nurseries(self):
        return self._children

    def _add_nursery(self, nursery: "FakeTrioNursery"):
        self.tree_root.tree_add(nursery, parent_name=self._name)

    def _remove_nursery(self, nursery_name: str):
        self.tree_root.tree_remove(nursery_name)

    def __repr__(self):
        if len(self.child_nurseries) > 0:
            return f"<Task:{self.name} {self.child_nurseries}>"
        return f"<Task: {self.name}>"

    @property
    def rich_tag(self):
        ret = "[bold yellow]Task"
        if self.name is not None:
            ret += f": [white]{self.name}"
        return ret

    def _rich_node(self, parent: RichTree):
        cur_node = parent.add(self.rich_tag)
        [n._rich_node(parent=cur_node) for n in self.child_nurseries]

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        """Support Python `rich` lib"""
        root = RichTree(self.rich_tag)
        [n._rich_node(parent=root) for n in self.child_nurseries]
        yield root


def build_tree_from_json(dic: Dict) -> FakeTrioTask:
    """Generate a trio task tree based on dict provided"""

    def build_task(task: Dict) -> FakeTrioTask:
        t = FakeTrioTask(name=task.get("name", None))
        for n in task["nurseries"]:
            t._add_nursery(build_nursery(n))
        return t

    def build_nursery(nursery: Dict) -> FakeTrioNursery:
        n = FakeTrioNursery(name=nursery.get("name", None))
        for t in nursery["tasks"]:
            n._add_task(build_task(t))
        return n

    return build_task(dic)
