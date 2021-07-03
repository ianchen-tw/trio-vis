import pytest

from trio_vis.trio_fake import FakeNode


@pytest.fixture
def tree_line() -> FakeNode:
    """ n0 -> n1 -> n2 """
    n0 = FakeNode(name="n0")
    n1 = FakeNode(name="n1")
    n2 = FakeNode(name="n2")
    n0.tree_add(n1, parent_name="n0")
    n0.tree_add(n2, parent_name="n1")
    return n0


def test_node_add(tree_line: FakeNode):
    assert tree_line._nodes.get("n2", None) is not None


def test_node_change_root(tree_line: FakeNode):
    n3 = FakeNode(name="n3")
    n1 = tree_line._nodes["n1"]
    n2 = tree_line._nodes["n2"]
    n1.tree_root = n3
    assert tree_line._nodes.get("n2", None) is None
    assert n3._nodes.get("n1", None) is n1
    assert n3._nodes.get("n2", None) is n2


def test_node_assign_self_root(tree_line: FakeNode):
    n1 = tree_line._nodes["n1"]
    n1.tree_root = n1
    assert tree_line._nodes.get("n1", None) is None
    assert tree_line._nodes.get("n2", None) is None
    assert n1._tree_root is n1
    assert n1._nodes.get("n2") is not None


def test_tree_node_remove(tree_line: FakeNode):
    tree_line.tree_remove("n1")
    assert tree_line._nodes.get("n1", None) is None
    assert tree_line._nodes.get("n2", None) is None


def test_tree_node_should_not_assign_none(tree_line: FakeNode):
    n1 = tree_line._nodes["n1"]
    with pytest.raises(RuntimeError):
        n1.tree_root = None
