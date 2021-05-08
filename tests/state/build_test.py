from typing import Dict, cast

import pytest

from trio_monitor.fake import Task, gen_tree_from_json
from trio_monitor.state import DescTree


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


def test_build_state_tree(tmpl1):
    internal_tree: Task = cast(Task, gen_tree_from_json(tmpl1))
    tree = DescTree.build(internal_tree)
    print(tree)


@pytest.mark.dev
def test_find_parent_nursery(tmpl1):
    internal_tree: Task = cast(Task, gen_tree_from_json(tmpl1))
    tree = DescTree.build(internal_tree)

    t2 = internal_tree.nodes["t2"]
    parent_nursery = tree.parent_nursery(t2)
    assert parent_nursery == internal_tree.nodes["n1"]

    assert tree.parent_nursery(internal_tree) is None