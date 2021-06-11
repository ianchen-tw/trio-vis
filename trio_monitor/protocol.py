import typing

""" Use Protocol for better type checking
"""


class TrioNursery(typing.Protocol):
    """Represent trio's internal `Nursery` type"""

    # a nursery does not have name
    name: str
    child_tasks: typing.List["TrioTask"]


class TrioTask(typing.Protocol):
    """Represent trio's internal `Task` type"""

    name: str
    child_nurseries: typing.List["TrioNursery"]


class TrioInstrument(typing.Protocol):
    """Trio's instrument class to used the instrument API

    Refer to:
        https://trio.readthedocs.io/en/stable/reference-lowlevel.html#trio.abc.Instrument
    """

    def task_exited(self, task: TrioTask):
        pass

    def task_spawned(self, task: TrioTask):
        pass
