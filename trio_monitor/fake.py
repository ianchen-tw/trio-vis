from typing import Dict, List, Optional

from rich.console import Console, ConsoleOptions, RenderResult
from rich.tree import Tree


class Nursery:
    """Represent the trio internal type
    the only usable attribute is `self.child_tasks`
    """

    def __init__(self, name: Optional[str] = None):
        self.child_tasks: List[Task] = []
        self._name = name

    def _add_task(self, task):
        if task not in self.child_tasks:
            self.child_tasks.append(task)

    def __repr__(self):
        if len(self.child_tasks) > 0:
            return f"<Nursery {self.child_tasks}>"
        return f"Nursery"

    @property
    def rich_tag(self):
        ret = "[bold magenta]Nursery"
        if self._name is not None:
            ret += f": [white]{self._name}"
        return ret

    def _rich_node(self, parent: Tree):
        cur_node = parent.add(self.rich_tag)
        for t in self.child_tasks:
            t._rich_node(parent=cur_node)


class Task:
    """Represent the trio internal type
    the only usable attribute is `self.child_nurseries`
    """

    def __init__(self, name: Optional[str] = None):
        self.child_nurseries: List[Nursery] = []
        self._name = name

    def _add_nursery(self, nursery):
        if nursery not in self.child_nurseries:
            self.child_nurseries.append(nursery)

    def __repr__(self):
        if len(self.child_nurseries) > 0:
            return f"<Task {self.child_nurseries}>"
        return "<Task>"

    @property
    def rich_tag(self):
        ret = "[bold yellow]Task"
        if self._name is not None:
            ret += f": [white]{self._name}"
        return ret

    def _rich_node(self, parent: Tree):
        cur_node = parent.add(self.rich_tag)
        [n._rich_node(parent=cur_node) for n in self.child_nurseries]

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        """Support Python `rich` lib"""
        root = Tree(self.rich_tag)
        [n._rich_node(parent=root) for n in self.child_nurseries]
        yield root


class BadInputFormat(BaseException):
    pass


def gen_tree_from_json(dic: Dict) -> Task:
    """Generate a trio task tree based on dict provided"""

    def build_task(task: Dict) -> Task:
        t = Task(name=task.get("name", None))
        for n in task["nurseries"]:
            t._add_nursery(build_nursery(n))
        return t

    def build_nursery(nursery: Dict) -> Nursery:
        n = Nursery(name=nursery.get("name", None))
        for t in nursery["tasks"]:
            n._add_task(build_task(t))
        return n

    return build_task(dic)
