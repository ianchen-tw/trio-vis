from trio_monitor.fake import Task, gen_tree_from_json, Nursery
from rich.tree import Tree
import rich

from typing import Dict

import pytest


@pytest.mark.dev
def test_add_task_to_nursery(tmpl1: Dict):
    tree1 = gen_tree_from_json(tmpl1)
    n1: Nursery = tree1.nodes["n1"]
    print("")
    rich.print(tree1)
    t4 = Task(name="t4")
    n1._add_task(t4)
    rich.print(tree1)

    assert "t4" in tree1.nodes
    assert len(n1.child_tasks) == 3
