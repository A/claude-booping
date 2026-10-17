"""Argument parser base shared by every `booping` parser."""

from __future__ import annotations

import argparse
from typing import Any


class Parser(argparse.ArgumentParser):
    """ArgumentParser whose invalid-choice message is the same on every Python.

    CPython changed how "(choose from …)" renders the choices between releases
    (repr-quoted vs bare); the CLI's error contract keeps the bare form.
    """

    def _check_value(self, action: argparse.Action, value: Any) -> None:
        choices = action.choices
        if choices is None:
            return
        if value not in (iter(choices) if isinstance(choices, str) else choices):
            listed = ", ".join(str(choice) for choice in choices)
            message = f"invalid choice: {str(value)!r} (choose from {listed})"
            raise argparse.ArgumentError(action, message)
