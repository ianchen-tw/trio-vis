from unittest.mock import Mock, call

from trio_vis.config import VisConfig
from trio_vis.sc_monitor import SC_Monitor
from trio_vis.trio_fake import (FakeTrioNursery, FakeTrioTask,
                                build_tree_from_json)

# TODO: refactor the test flow


class fake_logger:
    def __init__(self):
        self.log_start = Mock()
        self.log_exit = Mock()

    def clear_cache(self):
        self.log_start.reset_mock()
        self.log_exit.reset_mock()


def test_root_spawned():
    logger = fake_logger()
    sc_mon = SC_Monitor(
        config=VisConfig(only_vis_user_scope=False), sc_logger=Mock(return_value=logger)
    )

    t0 = FakeTrioTask(name="t0")
    sc_mon.task_spawned(t0)
    logger.log_start.assert_called_once_with(child=t0, parent=None)


def test_first_task_spawned_under_nursery():
    start_state = {
        "name": "t1",
        "nurseries": [],
    }
    logger = fake_logger()
    task_tree = build_tree_from_json(start_state)
    sc_mon = SC_Monitor.from_tree(
        root_task=task_tree,
        sc_logger=Mock(return_value=logger),
    )
    logger.clear_cache()

    n1 = FakeTrioNursery(name="n1")
    t2 = FakeTrioTask(name="t2")
    n1._add_task(t2)
    task_tree._add_nursery(n1)

    sc_mon.task_spawned(t2)

    required_logs = [call(child=n1, parent=task_tree), call(child=t2, parent=n1)]
    logger.log_start.assert_has_calls(required_logs)


def test_normal_task_spawned_under_nursery():
    start_state = {
        "name": "t1",
        "nurseries": [
            {
                "name": "n1",
                "tasks": [
                    {
                        "name": "t2",
                        "nurseries": [],
                    },
                ],
            }
        ],
    }
    logger = fake_logger()
    task_tree = build_tree_from_json(start_state)
    sc_mon = SC_Monitor.from_tree(
        root_task=task_tree,
        sc_logger=Mock(return_value=logger),
    )
    logger.clear_cache()

    n1 = task_tree.get_nursery_node("n1")
    t3 = FakeTrioTask(name="t3")
    n1._add_task(t3)

    sc_mon.task_spawned(t3)

    logger.log_start.assert_called_once_with(child=t3, parent=n1)


def test_task_exit():
    start_state = {
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
    logger = fake_logger()
    task_tree = build_tree_from_json(start_state)
    sc_mon = SC_Monitor.from_tree(
        root_task=task_tree,
        sc_logger=Mock(return_value=logger),
    )
    logger.clear_cache()

    t3 = task_tree.get_task_node("t3")
    n1 = task_tree.get_nursery_node("n1")

    task_tree.tree_remove("t3")
    sc_mon.task_exited(t3)
    logger.log_exit.assert_called_once_with(child=t3, parent=n1)


def test_task_exit_with_nursery():
    start_state = {
        "name": "t1",
        "nurseries": [
            {
                "name": "n1",
                "tasks": [
                    {
                        "name": "t2",
                        "nurseries": [
                            {
                                "name": "n2",
                                "tasks": [],
                            }
                        ],
                    },
                ],
            }
        ],
    }
    logger = fake_logger()
    task_tree = build_tree_from_json(start_state)
    sc_mon = SC_Monitor.from_tree(
        root_task=task_tree,
        sc_logger=Mock(return_value=logger),
    )
    logger.clear_cache()

    t2 = task_tree.get_task_node("t2")
    n2 = task_tree.get_nursery_node("n2")
    n1 = task_tree.get_nursery_node("n1")

    task_tree.tree_remove("t2")
    sc_mon.task_exited(t2)

    required_logs = [call(child=n2, parent=t2), call(child=t2, parent=n1)]
    logger.log_exit.assert_has_calls(required_logs)


def test_root_task_exit():
    start_state = {
        "name": "t1",
        "nurseries": [],
    }
    logger = fake_logger()
    task_tree = build_tree_from_json(start_state)
    sc_mon = SC_Monitor.from_tree(
        root_task=task_tree,
        sc_logger=Mock(return_value=logger),
    )
    logger.clear_cache()
    t1 = task_tree.get_task_node("t1")
    sc_mon.task_exited(t1)

    logger.log_exit.assert_called_once_with(child=t1, parent=None)
    assert sc_mon.root_exited == True
