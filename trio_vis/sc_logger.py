# Logger for structure-concurrent events
import atexit
import json
from abc import abstractmethod
from typing import Dict, List, Optional, cast

import attr
from typing_extensions import Protocol

from .desc_tree import TrioNode
from .registry import RegisteredSCInfo, SCRegistry


class Logger(Protocol):
    @abstractmethod
    def log_start(self, child: TrioNode, parent: Optional[TrioNode]):
        raise NotImplementedError

    @abstractmethod
    def log_exit(self, child: TrioNode, parent: Optional[TrioNode]):
        raise NotImplementedError


@attr.s(auto_attribs=True, slots=True, frozen=True)
class SCEvent:
    time: int
    desc: str
    name: str
    type: str
    parent: Optional[str]

    def as_dict(self) -> Dict:
        # Parent need to be undefined if not specified
        return {k: v for k, v in attr.asdict(self).items() if v is not None}


def get_info(
    target: Optional[TrioNode], registry: SCRegistry
) -> Optional[RegisteredSCInfo]:
    if target == None:
        return None
    target = cast(TrioNode, target)
    return registry.get_info(target)


def scope_name(task_info: RegisteredSCInfo):
    if task_info.type != "task":
        raise RuntimeError("Can only call this method with task object")
    return f"{task_info.name}__TRIO_VIS_Tscope"


class SCLogger(Logger):
    def __init__(self, registry: SCRegistry, log_filename: str):
        self.event_id: int = 0
        self.registry: SCRegistry = registry
        self.events: List[Dict] = []
        self.log_filename: str = log_filename
        atexit.register(self._write_log)

    def _get_info(self, child, parent):
        if child is None:
            raise RuntimeError("target should not be none")
        child_info = get_info(child, self.registry)
        parent_info = get_info(parent, self.registry)
        return (child_info, parent_info)

    def log_start(self, child: TrioNode, parent: Optional[TrioNode]):
        child_info, parent_info = self._get_info(child, parent)
        if parent_info is None:
            # Root Scope
            self.events.append(
                SCEvent(
                    time=self.time,
                    name=scope_name(child_info),
                    desc="created",
                    parent=None,
                    type="scope",
                ).as_dict()
            )
            # Root task
            self.events.append(
                SCEvent(
                    time=self.time,
                    name=child_info.name,
                    desc="created",
                    parent=scope_name(child_info),
                    type="task",
                ).as_dict()
            )

            # print(f"Create root scope: {scope_name(child_info)}")
            # print(
            #     f"Create root task: {child_info.name} under scope:{scope_name(child_info)}"
            # )
        elif child_info.type == "task" and parent_info.type == "nursery":
            # Scope for child task
            self.events.append(
                SCEvent(
                    type="scope",
                    time=self.time,
                    name=scope_name(child_info),
                    desc="created",
                    parent=parent_info.name,
                ).as_dict()
            )
            # Child task
            self.events.append(
                SCEvent(
                    type="task",
                    time=self.time,
                    name=child_info.name,
                    desc="created",
                    parent=scope_name(child_info),
                ).as_dict()
            )
            # print(
            #     f"Create scope: {scope_name(child_info)} under scope:{parent_info.name}"
            # )
            # print(
            #     f"Create task: {child_info.name} under scope:{scope_name(child_info)}"
            # )
        elif child_info.type == "nursery" and parent_info.type == "task":
            self.events.append(
                SCEvent(
                    type="scope",
                    time=self.time,
                    name=child_info.name,
                    desc="created",
                    parent=scope_name(parent_info),
                ).as_dict()
            )
            # print(
            #     f"Create scope: {child_info.name} under scope: {scope_name(parent_info)}"
            # )
        else:
            print("spawn unknown")

    def log_exit(self, child: TrioNode, parent: Optional[TrioNode]):
        child_info, parent_info = self._get_info(child, parent)
        if parent_info is None:
            # root exit
            # print(f"Exit task: {child_info.name} under scope:{scope_name(child_info)}")
            # print(f"Exit scope: {scope_name(child_info)}")
            # Root task
            self.events.append(
                SCEvent(
                    time=self.time,
                    name=child_info.name,
                    desc="exited",
                    parent=scope_name(child_info),
                    type="task",
                ).as_dict()
            )
            # Root scope
            self.events.append(
                SCEvent(
                    time=self.time,
                    name=scope_name(child_info),
                    desc="exited",
                    parent=None,
                    type="task",
                ).as_dict()
            )
        elif child_info.type == "task" and parent_info.type == "nursery":
            # print(f"Exit task:{child_info.name} under scope:{scope_name(child_info)}")
            # print(f"Exit scope:{scope_name(child_info)} under scope:{parent_info.name}")
            self.events.append(
                SCEvent(
                    time=self.time,
                    name=child_info.name,
                    desc="exited",
                    parent=scope_name(child_info),
                    type="task",
                ).as_dict()
            )
            self.events.append(
                SCEvent(
                    time=self.time,
                    name=scope_name(child_info),
                    desc="exited",
                    parent=parent_info.name,
                    type="scope",
                ).as_dict()
            )

        elif child_info.type == "nursery" and parent_info.type == "task":
            # print(f"Exit scope:{child_info.name} under scope:{scope_name(parent_info)}")
            self.events.append(
                SCEvent(
                    time=self.time,
                    name=child_info.name,
                    desc="exited",
                    parent=scope_name(parent_info),
                    type="scope",
                ).as_dict()
            )
        else:
            print("exit unknown")

    def _write_log(self):
        sc_logs = {
            "config": {"makeDirectScopeTransparent": True},
            "runRecords": self.events,
        }
        with open(self.log_filename, "w") as log_file:
            json.dump(sc_logs, log_file, indent=4)

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
