# trio-vis

`trio-vis` is a plugin for visualizing the scope history of your Trio project.

![showcase](res/showcase.png)

## How to use

[sc-vis]: sc-vis.ianchen-tw.github.com

1. Install `trio-vis` via `pip install trio-vis`
2. In your source code, register `SC_Monitor()` as an Instrument while running `trio`

    ```python
    from trio_vis import SC_Monitor
    trio.run(my_main_funciton, instruments=[SC_Monitor()])
    ```

3. After your program finished(or exited), the scope history would be stored in `./sc-logs.json`
4. Upload your log file to [sc-visualiver][sc-vis], this is a twin project which focuses on visualization work.
5. See your visualization result and help us improve.

## Configuration

Import `VisConfig` from `trio_vis`, and provide it as an argument while making your `SC_Monitor` object.

```python
from trio_vis import SC_Monitor, VisConfig
cfg = VisConfig(print_task_tree=True)
trio.run(my_main_funciton, instruments=[SC_Monitor(config=cfg)])
```

## What does it do

[ins-api]: https://trio.readthedocs.io/en/stable/reference-lowlevel.html#instrument-api

`trio-vis` utilize the [Instrument API][ins-api] to monitor the lifetime of scopes (`Task`,`Nursery`).
Since the [Instrument API][ins-api] doesn't provide callbacks for `Nursery`, we make inferences on our own.

## Why visualize

[trio]: https://github.com/python-trio/trio
[trio-issue-413]: https://github.com/python-trio/trio/issues/413

[curio]: https://github.com/dabeaz/curio
[curio-monitor]: https://github.com/dabeaz/curio/blob/master/curio/monitor.py

Derived from [curio], [trio] combines the idea of Structured Concurrency with existing single-threaded event-driven architecture. Which does make concurrent programs more manageable.

To make trio comparable with curio, contributors of trio also want to mimic the feature of [curio-monitor] to monitor the current system running state. This idea could be traced back to [trio-issue-413].

Since then, projects have been developed (shown below).

However, **trio is not curio**, at least lifetimes of scopes are structured by nature. I argue that by utilizing the feature of Structured Concurrency, we could visualize programs better.
Developers could easily conceptualize their program, and bring their developing experience to the next level.

### Previous work

+ [python-trio/trio-monitor]: officail project developed under trio, however it use the old InstruementAPI
+ [syncrypt/trio-inspector]: is a webmonitor to visualize the current state of the program
+ [Tronic/trio-web-monitor] a experiment to unified all previous work, developed by [Tronic](https://github.com/Tronic)

[python-trio/trio-monitor]:https://github.com/python-trio/trio-monitor
[Tronic/trio-web-monitor]:https://github.com/Tronic/trio-web-monitor
[syncrypt/trio-inspector]:https://github.com/syncrypt/trio-inspector

## Future plan

This project is in an early developing stage. Stay tuned for future update.
