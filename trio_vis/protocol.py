from typing import Coroutine, List

from typing_extensions import Protocol

""" Use Protocol for better type checking
"""


class TrioNursery(Protocol):
    """Represent trio's internal `Nursery` type"""

    child_tasks: List["TrioTask"]


class TrioTask(Protocol):
    """Represent trio's internal `Task` type"""

    name: str
    child_nurseries: List["TrioNursery"]

    # Internal object link to the coroutine
    coro: Coroutine


class TrioInstrument(Protocol):
    """Trio's instrument class to used the instrument API

    Refer to:
        https://trio.readthedocs.io/en/stable/reference-lowlevel.html#trio.abc.Instrument
    """

    def task_exited(self, task: TrioTask):
        pass

    def task_spawned(self, task: TrioTask):
        pass
