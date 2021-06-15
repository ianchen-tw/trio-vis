import typing
from typing import Dict, Optional, TypeVar, cast

from rich.console import Console, ConsoleOptions, RenderResult
from rich.tree import Tree

from .protocol import TrioNursery, TrioTask

""" Description Tree

    We trace the current system state by keeping our own task tree

    This tree must support:
    1. Build up a state tree based on the trio node given
    2. Given a task, find it's parent
    3. Given another tree, find the first node which is different
    4. Operations for adding/removing a single node to/from tree
"""


TrioNode = TypeVar("TrioNode", TrioNursery, TrioTask)


class DescNode:
    def __init__(self, node: TrioNode):
        if getattr(node, "name", None) is None:
            self.name = "unknown"
        else:
            self.name = node.name

        self.parent: Optional[DescNode] = None
        self.children: typing.List[DescNode] = []

        # ref to the actual node
        self.ref: typing.Union[TrioTask, TrioNursery] = node

    def __repr__(self):
        return f"<DescNode:{self.name}: {self.children}>"

    def _rich_node(self, parent: Tree):
        cur_node = parent.add(f"[yellow] name: {self.name}")
        [n._rich_node(parent=cur_node) for n in self.children]


class DescTree:
    def __init__(self, root):
        self.root: DescNode = root

        self.ref_2node: Dict[TrioNode, DescNode] = {}
        self.nodes: Dict[str, DescNode] = {}

    def __repr__(self):
        return f"{self.root}"

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        """Support Python `rich` lib"""
        root = Tree("DescTree")
        self.root._rich_node(parent=root)
        yield root

    def get_parent_nursery(self, task: TrioTask) -> Optional[TrioNursery]:
        """Directly retrieve the parent nursery of a task"""
        node = self.ref_2node.get(task, None)
        if node is not None:
            if node.parent is not None:
                nursery = cast(TrioNursery, node.parent.ref)
                return nursery
        return None

    def find_parent_nursery_from_trio(self, target: TrioTask) -> Optional[TrioNursery]:
        """Return the parent nursery of the target task from trio"""

        def find_parent_nursery(
            tree_root: TrioTask,
            target: TrioTask,
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

        # root.ref point to the root of a trio task tree
        nursery = find_parent_nursery(cast(TrioTask, self.root.ref), target)
        return nursery

    def ensure_node_in_tree(self, node: DescNode):
        if node != self.nodes[node.name]:
            raise RuntimeError(f"bug: node not exists in tree: {node}")
        if self.ref_2node.get(node.ref, None) is None:
            raise RuntimeError(f"bug: ref not exists in tree: {node.ref}")

    def ensure_node_not_in_tree(self, node: DescNode):
        if node in self.nodes:
            raise RuntimeError(f"bug: node already exists in tree: {node}")
        if self.ref_2node.get(node.ref, None) is not None:
            raise RuntimeError(f"bug: ref already exists in tree: {node.ref}")

    def remove_node(self, node: DescNode):
        """Remove node from tree, also break the link to it's parent"""
        self.ensure_node_in_tree(node)
        self.ref_2node.pop(node.ref)
        self.nodes.pop(node.name)

        # unregister all children in the tree
        for child in node.children:
            self.remove_node(child)

        if node.parent:
            node.parent.children.remove(node)

            # if we remove the only task from parent nursery,
            # the parent nursery would also be removed
            # trio only notify us the creation/removement of tasks, but not nurseries
            if len(node.parent.children) == 0:
                self.remove_node(node.parent)
            node.parent = None

    def add_node(self, node: DescNode, parent: DescNode):
        self.ensure_node_in_tree(parent)
        self.ensure_node_not_in_tree(node)

        if node in parent.children:
            raise RuntimeError(f"bug add same child({node}) to parent{parent}")
        node.parent = parent
        parent.children.append(node)

        self.ref_2node[node.ref] = node
        self.nodes[node.name] = node

    @classmethod
    def build(cls, root_task: TrioTask) -> "DescTree":
        """Build a tree of from source"""
        desc_root = DescNode(root_task)
        tree = cls(root=desc_root)

        def add_cache(node: DescNode):
            tree.nodes[node.name] = node
            tree.ref_2node[node.ref] = node

        def build_task(desc_task: DescNode):
            task = cast(TrioTask, desc_task.ref)
            for n in task.child_nurseries:
                desc_n = DescNode(n)
                desc_n.parent = desc_task
                desc_task.children.append(desc_n)
                add_cache(desc_n)
                build_nursery(desc_n)

        def build_nursery(desc_nursery: DescNode):
            nursery = cast(TrioNursery, desc_nursery.ref)
            for t in nursery.child_tasks:
                desc_t = DescNode(t)
                desc_t.parent = desc_nursery
                desc_nursery.children.append(desc_t)
                add_cache(desc_t)
                build_task(desc_t)

        add_cache(desc_root)
        build_task(desc_root)
        return tree