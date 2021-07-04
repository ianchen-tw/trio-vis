import random

import trio

from trio_vis import SC_Monitor, VisConfig

# ref: Nathaniel J. Smith - Trio: Async concurrency for mere mortals - PyCon 2018
# https://www.youtube.com/watch?v=oLkfnc_UMcE

CONN_SUCCESS_RATE = 0.15
BASE_DELAY_TIME = 0
MAX_TIME_TO_NEXT_ISSUE = 1
MAX_RETRY = 20


def main():
    random.seed(3)
    cfg = VisConfig(print_task_tree=True)
    trio.run(fetch_resource, instruments=[SC_Monitor(config=cfg)])


async def fetch_resource():
    async with trio.open_nursery() as nursery:
        nursery.start_soon(open_tcp_socket, nursery, MAX_TIME_TO_NEXT_ISSUE)


async def fake_connect(success_rate):
    delay_time = random.random() / 2 + BASE_DELAY_TIME
    await trio.sleep(delay_time)
    if random.random() < success_rate:
        return True
    else:
        raise OSError("Nooop")


async def open_tcp_socket(program_scope, max_wait_time=0.1):
    targets = [i for i in range(MAX_RETRY)]
    failed_attempts = [trio.Event() for _ in targets]
    winning_socket = None

    async def attempt(target_idx, nursery):
        def log(msg):
            print(" " * target_idx * 5 + f"Attempt{target_idx}: {msg}")

        # wait for previous one to finished, or timeout to expire
        log("start")
        if target_idx > 0:
            with trio.move_on_after(max_wait_time):
                log(f"wait for {target_idx-1} to fail")
                await failed_attempts[target_idx - 1].wait()
            log(f"{max_wait_time} sec passed")

        # start next attempt
        if target_idx + 1 < len(targets):
            log(f"trigger {target_idx+1}")
            nursery.start_soon(attempt, target_idx + 1, nursery)

        # try to connect to our target
        try:
            log("try to connect")
            await fake_connect(CONN_SUCCESS_RATE)
        # if fails, tell next attenpt to go ahead
        except OSError:
            log("connect failed")
            failed_attempts[target_idx].set()
        else:
            # if succeeds, save winning socket
            nonlocal winning_socket
            log("connect succeed")
            #             winning_socket = socket
            winning_socket = target_idx
            # and cancel other attempts
            nursery.cancel_scope.cancel()

    async with trio.open_nursery() as nursery:
        nursery.start_soon(attempt, 0, nursery)

    if winning_socket is None:
        program_scope.cancel_scope.cancel()
        raise OSError("ruh-oh")
    else:
        program_scope.cancel_scope.cancel()
        return winning_socket


if __name__ == "__main__":
    main()
