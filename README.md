# trio-vis

trio-vis is a plugin for visualizing your project Trio's scope history.

![showcase](res/showcase.png)

## How to use

[sc-vis]: sc-vis.ianchen.github.com

1. Install `trio-vis` via `pip install trio-vis`
2. In your source code, register `SC_Monitor()` as an Instrument while running `trio`

    ```python
    from trio_vis import SC_Monitor
    trio.run(my_main_funciton, instruments=[SC_Monitor()])
    ```

3. After your program finished(or exited), the scope history would be stored in `./logs.json`
4. Upload your log file to [sc-visualiver][sc-vis], this is a twin project which focus on visualization work.
5. See your visuailzation result and help us improve.

## What does it do

[ins-api]: https://trio.readthedocs.io/en/stable/reference-lowlevel.html#instrument-api

`trio-vis` utilize the [Instrument API][ins-api] to monitor the lifetime of scopes (`Task`,`Nursery`).
Since the [Instrument API][ins-api] doesn't provide callbacks for `Nursery`, we make inferences on our own.

## Why visualize

[trio]: https://github.com/python-trio/trio
[trio-issue-413]: https://github.com/python-trio/trio/issues/413

[curio]: https://github.com/dabeaz/curio
[curio-monitor]: https://github.com/dabeaz/curio/blob/master/curio/monitor.py

Derived from [curio], [trio] combine the idea of Strucutured Concurrency with existing single-threaded event-driven architecture. Which does make concurent progams more managable.

To make trio comparable with curio, contributors of trio also want to mimic the feature of [curio-monitor] in order to monitor the current system running state. This idea could be trace back to [trio-issue-413].

Since then, projects have been developed (showen below).

However, **trio is not curio**, at least lifetimes of scopes are strucutred by nature. I argue that by utilizing the feature of Structured Concurrency, we could visualize programs better.
Developer could easily conceptualize their program, and bring their developing experience to the next level.

### Previous work

+ [python-trio/trio-monitor]: officail project developed under trio, however it use the old InstruementAPI
+ [syncrypt/trio-inspector]: is a webmonitor to visualize the current state of the program
+ [Tronic/trio-web-monitor] a experiment to unified all previous work, developed by [Tronic](https://github.com/Tronic)

[python-trio/trio-monitor]:https://github.com/python-trio/trio-monitor
[Tronic/trio-web-monitor]:https://github.com/Tronic/trio-web-monitor
[syncrypt/trio-inspector]:https://github.com/syncrypt/trio-inspector

## Future plan

This project is in an early developing stage. Stay tuned for future update.
