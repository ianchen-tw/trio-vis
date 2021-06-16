# Logger for structure-concurrent events
import json
from typing import Dict, Optional

import attr

from .desc_tree import TrioNode
from .registry import SCRegistry


@attr.s(auto_attribs=True, slots=True, frozen=True)
class SCEvent:
    time: int
    desc: str
    id: str
    parent: str

    def as_dict(self) -> Dict:
        return attr.asdict(self)


def get_name(target: Optional[TrioNode], registry: SCRegistry) -> str:
    if target == None:
        return "null"
    return registry.get_info(target).name


class SCLogger:
    def __init__(self, registry: SCRegistry):
        self.event_id: int = 0
        self.registry: SCRegistry = registry

    def gen_event(self, desc: str, child: TrioNode, parent: Optional[TrioNode]):
        child_id = get_name(child, self.registry)
        parent_id = get_name(parent, self.registry)
        event = SCEvent(time=self.time, id=child_id, desc=desc, parent=parent_id)
        print(json.dumps(event.as_dict()))

    @property
    def time(self) -> int:
        ret = self.event_id
        self.event_id += 1
        return ret


def log():
    event = SCEvent(2, "t0", "start", "n0")
    print(json.dumps(event.as_dict()))


def main():
    print("good")
    log()


if __name__ == "__main__":
    main()
