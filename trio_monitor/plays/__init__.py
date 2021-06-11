""" Play
This package is used for mocking the real interaction between
our library objects with the Trio Instrument API.

Simply are some pre-coded plays in the trio mainline

Basically testing for the Instrument API of Trio
"""
from script_1 import Script1

from ..protocol import TrioInstrument


def start_play(script, instrument: TrioInstrument):
    for _ in script(ins=instrument):
        pass


__all__ = ["start_play", "Script1"]
