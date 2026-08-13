from __future__ import annotations

from collections.abc import Callable, Mapping

from booping_tracker.facade import TrackerProvider
from booping_tracker.providers.cli import CliProvider

PROVIDERS: Mapping[str, Callable[[], TrackerProvider]] = {
    "cli": CliProvider,
}
