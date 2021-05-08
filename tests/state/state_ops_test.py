from typing import cast

import pytest

from trio_monitor.fake import Task, gen_tree_from_json
from trio_monitor.state import DescNode, DescTree


# @pytest.mark.dev
def test_find_parent_nursery(tmpl1):
    internal_tree: Task = cast(Task, gen_tree_from_json(tmpl1))
    tree = DescTree.build(internal_tree)

    t4 = Task(name="t4")
    internal_tree.nodes["n1"]._add_task(t4)

    nursery = tree.find_parent_nursery_from_trio(t4)
    assert nursery is not None
    assert nursery == internal_tree.nodes["n1"]


def test_remove_nursery(tmpl1):
    internal_tree: Task = cast(Task, gen_tree_from_json(tmpl1))
    tree = DescTree.build(internal_tree)

    n1 = internal_tree.nodes["n1"]
    n1_node = tree.ref_2node[n1]

    tree.remove_node(n1_node)

    assert tree.nodes.get("n1", None) is None
    assert tree.ref_2node.get(n1, None) is None

    # child should be removed
    assert tree.nodes.get("t2", None) is None


def test_remove_task(tmpl1):
    internal_tree: Task = cast(Task, gen_tree_from_json(tmpl1))
    tree = DescTree.build(internal_tree)

    t2 = internal_tree.nodes["t2"]
    t2_node = tree.ref_2node[t2]

    tree.remove_node(t2_node)

    assert tree.nodes.get("t2", None) is None
    assert tree.ref_2node.get(t2, None) is None


@pytest.mark.dev
def test_add_task(tmpl1):
    internal_tree: Task = cast(Task, gen_tree_from_json(tmpl1))
    tree = DescTree.build(internal_tree)

    t4 = Task(name="t4")

    internal_tree.nodes["n1"]._add_task(t4)
    t4_node = DescNode(t4)

    tree.add_node(t4_node, tree.nodes["n1"])

    assert tree.nodes.get("t4", None) == t4_node
    assert tree.ref_2node.get(t4, None) == t4_node
