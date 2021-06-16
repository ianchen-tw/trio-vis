from typing import cast

from trio_monitor.desc_tree import DescTree
from trio_monitor.trio_fake import FakeTrioTask, gen_tree_from_json


def test_build_state_tree(tmpl1):
    internal_tree: FakeTrioTask = cast(FakeTrioTask, gen_tree_from_json(tmpl1))
    tree = DescTree.build(internal_tree)
    print(tree)


def test_get_parent_nursery(tmpl1):
    internal_tree: FakeTrioTask = cast(FakeTrioTask, gen_tree_from_json(tmpl1))
    tree = DescTree.build(internal_tree)

    t2 = internal_tree.nodes["t2"]
    parent_nursery = tree.get_parent_ref(t2)
    assert parent_nursery == internal_tree.nodes["n1"]

    assert tree.get_parent_ref(internal_tree) is None
