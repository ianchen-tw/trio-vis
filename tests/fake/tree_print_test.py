from typing import Dict

import rich

from trio_monitor.trio_fake import gen_tree_from_json


def test_rich_print_tree(tmpl1: Dict):
    print("")
    print("print tree with rich")
    tree = gen_tree_from_json(tmpl1)
    rich.print(tree)
