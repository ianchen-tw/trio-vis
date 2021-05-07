from typing import Dict, cast

from trio_monitor.fake import Nursery, Task, gen_tree_from_json


def test_build_tree(tmpl1: Dict):
    tree: Task = cast(Task, gen_tree_from_json(tmpl1))

    t1: Task = cast(Task, tree.nodes["t1"])
    assert len(t1.child_nurseries) == 1

    n1: Nursery = cast(Nursery, tree.nodes["n1"])
    assert len(n1.child_tasks) == 2


def test_build_child_root_tree():
    tree: Task = gen_tree_from_json(
        {
            "name": "t1",
            "nurseries": [],
        }
    )
    assert tree.nodes["t1"].name == "t1"
    assert len(tree.nodes["t1"].child_nurseries) == 0
