from trio_monitor.desc_tree import DescTree
from trio_monitor.trio_fake import FakeTrioTask


def test_build_state_tree(fake_tree: FakeTrioTask):
    desc_tree = DescTree.build(fake_tree)
    print(desc_tree)


def test_get_parent_nursery(fake_tree: FakeTrioTask):
    tree = DescTree.build(fake_tree)

    t2 = fake_tree.get_task_node("t2")
    parent_nursery = tree.get_parent_ref(t2)
    assert parent_nursery == fake_tree.get_nursery_node("n1")

    assert tree.get_parent_ref(fake_tree) is None


def test_remove_nursery(fake_tree: FakeTrioTask):
    desc_tree = DescTree.build(fake_tree)

    n1 = fake_tree.get_nursery_node("n1")
    n1_node = desc_tree.ref_2node[n1]

    desc_tree.remove_node(n1_node)

    assert desc_tree._nodes.get("n1", None) is None
    assert desc_tree.ref_2node.get(n1, None) is None

    # child should be removed
    assert desc_tree._nodes.get("t2", None) is None


def test_remove_task(fake_tree: FakeTrioTask):
    desc_tree = DescTree.build(fake_tree)

    t2 = fake_tree.get_task_node("t2")
    t2_node = desc_tree.ref_2node[t2]

    desc_tree.remove_node(t2_node)

    assert desc_tree._nodes.get("t2", None) is None
    assert desc_tree.ref_2node.get(t2, None) is None


# @pytest.mark.dev
# def test_add_task(tmpl1):
#     internal_tree: FakeTrioTask = cast(FakeTrioTask, gen_tree_from_json(tmpl1))
#     tree = DescTree.build(internal_tree)

#     t4 = FakeTrioTask(name="t4")

#     internal_tree.nodes["n1"]._add_task(t4)
#     t4_node = DescNode(t4)

#     tree.add_node(t4_node, tree._nodes["n1"])

#     assert tree._nodes.get("t4", None) == t4_node
#     assert tree.ref_2node.get(t4, None) == t4_node
