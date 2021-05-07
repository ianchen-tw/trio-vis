from trio_monitor.fake import Task, gen_tree_from_json, Nursery
from rich.tree import Tree
import rich
from typing import Dict

import pytest


def test_rich_print_tree(tmpl1: Dict):
    print("")
    print("print tree with rich")
    tree = gen_tree_from_json(tmpl1)
    rich.print(tree)
