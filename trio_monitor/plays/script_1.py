from contextlib import contextmanager

import rich

from trio_monitor.protocol import TrioInstrument
from trio_monitor.trio_fake import FakeTrioNursery, FakeTrioTask


class MyIns(TrioInstrument):
    def __init__(self) -> None:
        super().__init__()

    def task_exited(self, task):
        print("exited")

    def task_spawned(self, task):
        print("spawned")


def Script1(ins: TrioInstrument):
    tree: FakeTrioTask
    cur_step = 0

    @contextmanager
    def step(info=""):
        nonlocal cur_step
        print(f"--- Step{cur_step}: {info}")
        yield
        rich.print(tree)
        print("-======")
        cur_step += 1

    with step("Gen root task"):
        t0 = FakeTrioTask(name="t0")
        tree = t0
        ins.task_spawned(t0)
        yield

    # step1
    with step("add t1, n0 under t0"):
        n0 = FakeTrioNursery(name="n0")
        t1 = FakeTrioTask(name="t1")
        n0._add_task(t1)
        t0._add_nursery(n0)
        ins.task_spawned(t1)
        yield

    # step2
    with step("add n1/t2 under t1"):
        n1 = FakeTrioNursery(name="n1")
        t2 = FakeTrioTask(name="t2")
        n1._add_task(t2)
        t1._add_nursery(n1)
        ins.task_spawned(t2)
        yield

    # step3
    with step("spwan task under n1"):
        t3: FakeTrioTask = FakeTrioTask(name="t3")
        n1._add_task(t3)
        ins.task_spawned(t3)

    # step4
    with step("remove t3"):
        n1._remove_task(t3)
        ins.task_exited(t3)
        del t3

    # step5
    with step("remove t2"):
        n1._remove_task(t2)
        ins.task_exited(t2)
        del t2

    # step6
    with step("remove t1 and all of it's child"):
        n0._remove_task(t1)
        ins.task_exited(t1)
        del t1

    # step7
    with step("root task exited"):
        ins.task_exited(t0)
        del t0
