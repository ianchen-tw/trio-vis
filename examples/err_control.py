import trio
import random
import attr
from attr import attrs, attrib
from typing import Protocol
from trio import open_memory_channel
from rich.table import Table
from rich.text import Text
from rich.live import Live
from typing import Optional
from trio_vis import SC_Monitor

NM_LOGS_SHOWN = 8


class ConnectionError(BaseException):
    pass


class Scope(Protocol):
    def cancel(self):
        pass


class STATUS:
    OK: int = "Ok"
    ERR: int = "Err"


def get_scope(nursery):
    return (nursery.start_soon, nursery.cancel_scope)


@attrs(auto_attribs=True)
class Logger:
    # 0/1/2
    _child_logs: list = attrib(default=[[] for _ in range(3)])
    _logs: list = attrib(default=["--" for _ in range(NM_LOGS_SHOWN)])

    _CHILD_LOG_HEIGHT: int = 10

    def _log_child(self, _id: int, info: str):
        if _id not in [0, 1, 2]:
            raise RuntimeError
        target = self._child_logs[_id]
        target.append(info)
        if len(target) > 10:
            del target[0]

    def _log_global(self, info: str):
        self._logs.append(info)
        if len(self._logs) > NM_LOGS_SHOWN:
            del self._logs[0]

    def log(self, child_id: Optional[int] = None, info: str = ""):
        if child_id is None:
            self._log_global(info)
        else:
            self._log_child(_id=child_id, info=info)

    def clear_log(self, _id: int):
        self._child_logs[_id] = []
        self.log(child_id=_id, info=f"cancel child {_id}")

    # def show(self):
    #     rich.print(self.generate_table())

    def generate_table(self) -> Table:
        # self.log("--")

        table = Table(expand=True)
        table.add_column("name", max_width=1)
        table.add_column("content")

        def get_log(log_id: int) -> str:
            blank_lines = [
                ""
                for _ in range(self._CHILD_LOG_HEIGHT - len(self._child_logs[log_id]))
            ]
            lines = self._child_logs[log_id] + blank_lines
            return "\n".join(lines)

        log_table = Table(padding=1, show_header=True, expand=True)
        log_table.add_column("child 0", max_width=5, min_width=5)
        log_table.add_column("child 1", max_width=5, min_width=5)
        log_table.add_column("child 2", max_width=5, min_width=5)
        log_table.add_row(Text(get_log(0)), Text(get_log(1)), Text(get_log(2)))

        table.add_row("", log_table)
        table.add_row("info", Text("\n".join(self._logs)))
        return table


logger = Logger()


def log(id=None, info: str = ""):
    logger.log(id, info)


def clear_log(id=None):
    logger.clear_log(id)


@attr.s(auto_attribs=True)
class BehaviorChecker:
    events: list = attr.ib(default=attr.Factory(list))
    mx_nm_history: int = 10

    @property
    def err_rate(self):
        return self.events.count(False) / len(self.events)

    def new_event(self, is_good: bool):
        self.events.append(is_good)
        if len(self.events) > self.mx_nm_history:
            del self.events[0]

    @property
    def is_unstable(self) -> bool:
        if len(self.events) < self.mx_nm_history / 2:
            return False
        else:
            return self.err_rate > 0.7


@attr.s(auto_attribs=True)
class LowerCtrl:
    err_rate: float = 0
    err_rate_add: float = 0.1  # amount of error rate increase per tick
    inc_interval_sec: float = 2  # interval for error rate increase tick

    @classmethod
    def RandQuality(cls):
        base_rate = 0 if random.random() > 0.2 else 0.9
        return cls(err_rate=base_rate)

    async def start(self, report_chan):
        async def communiate(report_chan):
            async with report_chan:
                while True:
                    await trio.sleep(random.uniform(1, 2))
                    msg = STATUS.OK if random.random() > self.err_rate else STATUS.ERR
                    await report_chan.send(msg)

        async def error_rate_tick():
            while True:
                await trio.sleep(self.inc_interval_sec)
                self.err_rate += self.err_rate_add
                self.err_rate = min(1, self.err_rate)

        async with trio.open_nursery() as rate_nursery:
            launch_in_scope, _ = get_scope(rate_nursery)
            launch_in_scope(communiate, report_chan)
            launch_in_scope(error_rate_tick)


@attr.s(auto_attribs=True)
class UpperCtrl:
    nm_conn: int = 2

    async def task_control_child(self, _id: int):
        """Start a service to keep monitoring children"""

        async def job_monitor(recv_chan, parent_scope):
            checker = BehaviorChecker()
            while True:
                status = await recv_chan.receive()
                checker.new_event(status == STATUS.OK)
                log(id=_id, info=f"recv: {status} ({checker.err_rate:.2f})")
                if checker.is_unstable:
                    clear_log(id=_id)
                    parent_scope.cancel()

        async def run_session():
            async with trio.open_nursery() as nursery_ctrl:
                (send_chan, recv_chan) = open_memory_channel(0)
                launch_in_ctrl, scope_ctrl = get_scope(nursery_ctrl)

                lower_ctrl = LowerCtrl.RandQuality()

                launch_in_ctrl(job_monitor, recv_chan, scope_ctrl)
                launch_in_ctrl(lower_ctrl.start, send_chan)

        while True:
            await run_session()

    async def start_control(self):
        log(info="app launched")
        while True:
            async with trio.open_nursery() as main_nursery:
                # print("restart all services")
                (launch_in_main, scope_main) = get_scope(main_nursery)
                for _id in range(self.nm_conn):
                    launch_in_main(self.task_control_child, _id)
                # await trio.sleep(5)
                # scope_main.cancel()


async def CliApp(upper_ctrl):
    async def task_ui():
        with Live(logger.generate_table(), refresh_per_second=4) as live:
            while True:
                await trio.sleep(0.2)
                live.update(logger.generate_table())

    async with trio.open_nursery() as app_nursery:
        app_nursery.start_soon(task_ui)
        app_nursery.start_soon(upper_ctrl.start_control)


def main():
    upper_ctrl = UpperCtrl()
    # trio.run(upper_ctrl.start_control)
    # trio.run(CliApp, upper_ctrl)
    trio.run(upper_ctrl.start_control, instruments=[SC_Monitor()])


if __name__ == "__main__":
    main()
