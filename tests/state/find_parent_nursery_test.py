from typing import cast

from trio_monitor.fake import Task, gen_tree_from_json
from trio_monitor.state import DescTree


# @pytest.mark.dev
def test_find_parent_nursery(tmpl1):
    internal_tree: Task = cast(Task, gen_tree_from_json(tmpl1))
    tree = DescTree.build(internal_tree)

    t4 = Task(name="t4")
    internal_tree.nodes["n1"]._add_task(t4)

    nursery = tree.find_parent_nursery_from_trio(t4)
    assert nursery is not None
    assert nursery == internal_tree.nodes["n1"]


# @pytest.mark.dev
# def test_find_parent_nursery(tmpl1):
#     internal_tree: Task = cast(Task, gen_tree_from_json(tmpl1))
#     tree = DescTree.build(internal_tree)

#     t3 = internal_tree.nodes["t3"]
#     rich.print(tree)
#     tree.remove_task(t3)
#     rich.print(tree)
# print(tree)


# assert nursery is not None
# assert nursery == internal_tree.nodes["n1"]
