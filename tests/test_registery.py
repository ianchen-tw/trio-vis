import pytest

from trio_vis.registry import *
from trio_vis.trio_fake import FakeTrioNursery, FakeTrioTask


@pytest.fixture
def drawer() -> SerialNumberGen:
    return SerialNumberGen()


@pytest.fixture
def registry() -> SCRegistry:
    return SCRegistry()


def test_drawer(drawer: SerialNumberGen):
    assert drawer.draw("a") == 0
    assert drawer.draw("b") == 0
    assert drawer.draw("a") == 1
    assert drawer.draw("c") == 0
    assert drawer.draw("c") == 1


def test_parser():
    assert parse_obj_type(FakeTrioTask(name="t1")) == TYPE_TRIO_TASK
    assert parse_obj_type(FakeTrioNursery(name="n1")) == TYPE_TRIO_NURSERY


def test_registry_add(registry: SCRegistry):
    t0 = FakeTrioTask(name="func1")
    t1 = FakeTrioTask(name="func1")
    assert "func1-0" == registry.get_name(t0)
    assert "func1-1" == registry.get_name(t1)
    assert "func1-0" == registry.get_name(t0)


def test_registry_remove(registry: SCRegistry):
    t0 = FakeTrioTask(name="func1")
    t1 = FakeTrioTask(name="func1")
    assert "func1-0" == registry.get_name(t0)
    assert "func1-1" == registry.get_name(t1)
    assert True == registry.remove(t0)
    with pytest.raises(RuntimeError):
        registry.remove(t0)
