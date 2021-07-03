# Logger for structure-concurrent events
import atexit
import json
from typing import Dict, List, Optional, cast

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
    target = cast(TrioNode, target)
    return registry.get_info(target).name


class SCLogger:
    def __init__(self, registry: SCRegistry, log_filename: str):
        self.event_id: int = 0
        self.registry: SCRegistry = registry
        self.events: List[Dict] = []
        self.log_filename: str = log_filename
        atexit.register(self._write_log)

    def _get_id(self, child, parent):
        if child is None:
            raise RuntimeError("target should not be none")
        child_id = get_name(child, self.registry)
        parent_id = get_name(parent, self.registry)
        return (child_id, parent_id)

    def log_start(self, child: TrioNode, parent: Optional[TrioNode]):
        child_id, parent_id = self._get_id(child, parent)
        event = SCEvent(time=self.time, id=child_id, desc="created", parent=parent_id)
        self.events.append(event.as_dict())

    def log_exit(self, child: TrioNode, parent: Optional[TrioNode]):
        child_id, parent_id = self._get_id(child, parent)
        event = SCEvent(time=self.time, id=child_id, desc="exited", parent=parent_id)
        self.events.append(event.as_dict())

    def _write_log(self):
        with open(self.log_filename, "w") as log_file:
            json.dump(self.events, log_file, indent=4)

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
