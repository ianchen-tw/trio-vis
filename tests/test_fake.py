import rich

from trio_monitor.trio_fake import (FakeTrioNursery, FakeTrioTask,
                                    build_tree_from_json)


def test_build_child_root_tree():
    tree: FakeTrioTask = build_tree_from_json(
        {
            "name": "t1",
            "nurseries": [],
        }
    )
    assert tree.get_task_node("t1").name == "t1"
    assert len(tree.get_task_node("t1").child_nurseries) == 0


def test_build_tree(fake_tree: FakeTrioTask):
    t1: FakeTrioTask = fake_tree.get_task_node("t1")
    assert len(t1.child_nurseries) == 1

    n1: FakeTrioNursery = fake_tree.get_nursery_node("n1")
    assert len(n1.child_tasks) == 2


def test_rich_print_tree(fake_tree: FakeTrioTask):
    print("")
    print("print tree with rich")
    rich.print(fake_tree)


def test_add_task_to_nursery(fake_tree: FakeTrioTask):
    n1: FakeTrioNursery = fake_tree.get_nursery_node("n1")
    print("")
    rich.print(fake_tree)
    t4 = FakeTrioTask(name="t4")
    n1._add_task(t4)
    rich.print(fake_tree)

    assert "t4" in fake_tree
    assert len(n1.child_tasks) == 3
