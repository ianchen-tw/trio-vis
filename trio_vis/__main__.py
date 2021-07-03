if __name__ == "__main__":
    import rich

    from trio_vis.dry_run import Script1
    from trio_vis.protocol import TrioInstrument
    from trio_vis.sc_monitor import SC_Monitor

    def start_play(script, instrument: TrioInstrument):
        for _ in script(ins=instrument):
            pass

    rich.print("[bold red] start running with fake data")

    start_play(Script1, SC_Monitor(ignore_trio=False))
