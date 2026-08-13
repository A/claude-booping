from __future__ import annotations

from collections.abc import Callable, Mapping

from booping_tracker.config import TrackerConfig
from booping_tracker.facade import TrackerProvider
from booping_tracker.providers.cli import CliProvider
from booping_tracker.providers.linear import LinearProvider

PROVIDERS: Mapping[str, Callable[[TrackerConfig], TrackerProvider]] = {
    "cli": lambda _config: CliProvider(),
    "linear": LinearProvider.from_config,
}
