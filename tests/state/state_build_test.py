from typing import cast

from trio_monitor.fake import Task, gen_tree_from_json
from trio_monitor.state import DescTree


def test_build_state_tree(tmpl1):
    internal_tree: Task = cast(Task, gen_tree_from_json(tmpl1))
    tree = DescTree.build(internal_tree)
    print(tree)


def test_get_parent_nursery(tmpl1):
    internal_tree: Task = cast(Task, gen_tree_from_json(tmpl1))
    tree = DescTree.build(internal_tree)

    t2 = internal_tree.nodes["t2"]
    parent_nursery = tree.get_parent_nursery(t2)
    assert parent_nursery == internal_tree.nodes["n1"]

    assert tree.get_parent_nursery(internal_tree) is None
