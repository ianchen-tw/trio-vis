from trio_monitor.fake import Nursery, Task, gen_tree_from_json
import rich


def test_all():
    root_task = {
        "name": "task1",
        "nurseries": [
            {
                "name": "<nursery>",
                "tasks": [
                    {
                        "name": "task2",
                        "nurseries": [],
                    },
                    {
                        "name": "task2",
                        "nurseries": [],
                    },
                ],
            }
        ],
    }
    tree = gen_tree_from_json(root_task)
    assert len(tree.child_nurseries[0].child_tasks) == 2
    rich.print(tree)
    # print(tree)


if __name__ == "__main__":
    test_all()
