import trio
from trio_typing import Nursery
import random
from trio_vis import SC_Monitor, VisConfig


async def do_job(name: str, log_nursery: Nursery):
    async def wait_and_submit(nursery: Nursery):
        for i in range(10):
            if random.random() > 0.9:
                nursery.cancel_scope.cancel()
            await trio.sleep(1)
            await submit_log(f"job{name}: count {i}", log_nursery)
            # await submit_log(f"job{name}: count {i}", nursery)

    async with trio.open_nursery() as n:
        n.start_soon(wait_and_submit, n)


async def submit_log(msg, nursery: Nursery):
    async def do_log():
        await trio.sleep(1)
        print(f"Log info: {msg}")

    nursery.start_soon(do_log)


async def main():
    nm = 5
    async with trio.open_nursery() as n:
        for i in range(nm):
            n.start_soon(do_job, f"{i}", n)


if __name__ == "__main__":
    cfg = VisConfig(log_filename="./sc-logs-global-logger.json")
    trio.run(main, instruments=[SC_Monitor(config=cfg)])

    pass
