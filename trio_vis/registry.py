from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Dict, Optional, Union, cast

from typing_extensions import Literal

from .protocol import TrioNursery, TrioTask

"""
Name Trio objects
"""


class SerialNumberGen:
    """Give serial number to given names"""

    def __init__(self):
        self.numbers: Dict[str, int] = defaultdict(int)

    def draw(self, name: str) -> int:
        serial_num = self.numbers[name]
        self.numbers[name] += 1
        return serial_num


TYPE_TRIO_TASK = 1
TYPE_TRIO_NURSERY = 2
TYPE_UNKOWN = -1


def parse_obj_type(object):
    if getattr(object, "child_tasks", None) != None:
        return TYPE_TRIO_NURSERY
    elif getattr(object, "child_nurseries", None) != None:
        return TYPE_TRIO_TASK
    return TYPE_UNKOWN


# TODO: slotted? freezed?
@dataclass
class RegisteredSCInfo:
    """Store Information about a scope-like object (Task, Nursery)"""

    name: str
    serial_num: Optional[int]
    type: Literal["nursery", "task"]

    @classmethod
    def from_task(cls, task: TrioTask, serial_num: SerialNumberGen):
        task_name: str = task.coro.cr_code.co_name
        num = serial_num.draw(task_name)
        name = f"{task_name}-{num}"
        return cls(name=name, serial_num=num, type="task")

    @classmethod
    def from_nursery(cls, _nursery: TrioNursery, serial_num: SerialNumberGen):
        # TODO: parse from more specific info
        num = serial_num.draw("nursery")

        self_defined_name = getattr(_nursery, "_trio_vis_name", None)
        if self_defined_name is not None:
            name = self_defined_name
        else:
            name = f"nursery-{num}"
        return cls(name=name, serial_num=num, type="nursery")


class SCRegistry:
    """Help to register Structured-Concurrency-related objects

    Also store some meaningful information about those objects
    inside the registry

    here we would register Trio's Task/Nursery object
    """

    def __init__(self):
        self.serial_drawer = SerialNumberGen()
        self.registered: Dict[Any, RegisteredSCInfo] = {}

    def get_name(self, obj: Union[TrioTask, TrioNursery]):
        if obj in self.registered:
            return self.registered[obj].name
        return self.get_info(obj).name

    def get_info(self, obj: Union[TrioTask, TrioNursery]) -> RegisteredSCInfo:
        """Get object information
        would register if not yet stored
        """
        if obj in self.registered:
            return self.registered[obj]

        obj_type = parse_obj_type(obj)
        info: RegisteredSCInfo
        if obj_type is TYPE_TRIO_TASK:
            info = RegisteredSCInfo.from_task(cast(TrioTask, obj), self.serial_drawer)
        elif obj_type is TYPE_TRIO_NURSERY:
            info = RegisteredSCInfo.from_nursery(
                cast(TrioNursery, obj), self.serial_drawer
            )
        else:
            raise RuntimeError("[registry] Unkown type")
        self.registered[obj] = info
        return info

    def remove(self, obj) -> bool:
        if obj in self.registered:
            del self.registered[obj]
            return True
        else:
            raise RuntimeError("Bug remove item not in registry")
