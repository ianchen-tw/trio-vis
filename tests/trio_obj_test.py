from trio_monitor.fake import Task, gen_tree_from_json, Nursery
from rich.tree import Tree
import rich
from typing import Dict

import pytest


@pytest.fixture
def tmpl1() -> Dict:
    return {
        "name": "t1",
        "nurseries": [
            {
                "name": "n1",
                "tasks": [
                    {
                        "name": "t2",
                        "nurseries": [],
                    },
                    {
                        "name": "t3",
                        "nurseries": [],
                    },
                ],
            }
        ],
    }


@pytest.fixture
def tree1(tmpl1) -> Task:
    return gen_tree_from_json(tmpl1)


def test_build_tree(tmpl1: Dict):
    tree: Task = gen_tree_from_json(tmpl1)

    t1: Task = tree.nodes["t1"]
    assert len(t1.child_nurseries) == 1

    n1: Nursery = tree.nodes["n1"]
    assert len(n1.child_tasks) == 2


@pytest.mark.dev
def test_add_task_to_nursery(tree1: Task):
    n1: Nursery = tree1.nodes["n1"]
    print("")
    rich.print(tree1)
    t4 = Task(name="t4")
    n1._add_task(t4)
    rich.print(tree1)

    assert "t4" in tree1.nodes
    assert len(n1.child_tasks) == 3


def test_rich_print_tree(tmpl1: Dict):
    print("")
    print("print tree with rich")
    tree = gen_tree_from_json(tmpl1)
    rich.print(tree)
