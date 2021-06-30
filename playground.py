def myFunc():
    print("Hello World!")


async def afunc():
    yield "a"
    yield "b"


def handle(func):
    print(f"get funciton: {func}")


def async_runner(async_function):
    next_stage = async_function()
    while True:
        try:
            next_stage = next(next_stage)
        except StopIteration:
            print("finished")
            break


def main():
    # handle(myFunc)
    # handle(afunc())
    async_runner(afunc)


if __name__ == "__main__":
    main()
