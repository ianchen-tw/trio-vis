from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Dict, Optional, Union, cast

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


def parseObjectType(object):
    if getattr(object, "child_tasks", None) != None:
        return TYPE_TRIO_NURSERY
    elif getattr(object, "child_nurseries", None) != None:
        return TYPE_TRIO_TASK
    return TYPE_UNKOWN


# TODO: slotted? freezed?
@dataclass
class RegisteredSCInfo:
    name: str
    serial_num: Optional[int]

    @classmethod
    def from_task(cls, task: TrioTask, serial_num: SerialNumberGen):
        num = serial_num.draw(task.name)
        name = f"{task.name}-{num}"
        return cls(name=name, serial_num=num)

    @classmethod
    def from_nursery(cls, _nursery: TrioNursery, serial_num: SerialNumberGen):
        # TODO: parse from more specific info
        num = serial_num.draw("nursery")
        name = f"nursery-{num}"
        return cls(name=name, serial_num=num)


class SCRegistry:
    def __init__(self):
        self.serial_drawer = SerialNumberGen()
        self.registered: Dict[Any, RegisteredSCInfo] = {}

    def get_name(self, obj: Union[TrioTask, TrioNursery]):
        if obj in self.registered:
            return self.registered[obj].name

        objType = parseObjectType(obj)

        if objType is TYPE_TRIO_TASK:
            info = RegisteredSCInfo.from_task(cast(TrioTask, obj), self.serial_drawer)
        elif objType is TYPE_TRIO_NURSERY:
            info = RegisteredSCInfo.from_nursery(
                cast(TrioNursery, obj), self.serial_drawer
            )
        else:
            raise RuntimeError("[registry] Unkown type")
        self.registered[obj] = info
        return info.name

    def remove(self, obj) -> bool:
        if obj in self.registered:
            del self.registered[obj]
            return True
        else:
            raise RuntimeError("Bug remove item not in registry")
