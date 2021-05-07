from trio_monitor.fake import Task, gen_tree_from_json, Nursery
from rich.tree import Tree
import rich
from typing import Dict

import pytest


def test_build_tree(tmpl1: Dict):
    tree: Task = gen_tree_from_json(tmpl1)

    t1: Task = tree.nodes["t1"]
    assert len(t1.child_nurseries) == 1

    n1: Nursery = tree.nodes["n1"]
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