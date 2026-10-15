from __future__ import annotations

from typing import Any, cast

MODES = ("supervised", "autonomous")

_INVALID = (
    "**STOP — tell the user:** `core.autonomy` is `{value}`; it must be `supervised`"
    " or `autonomous`. Fix it in the config tier that sets it, then retry."
)


def render_gate(config: dict[str, Any]) -> str | None:
    """The notice a render surface must print *instead of* its output, or None.

    Takes the final config — every tier merged and every `--set` applied — so an
    override is validated the same as a tier value.
    """
    core = config.get("core")
    if not isinstance(core, dict):
        return None
    value = cast("dict[str, object]", core).get("autonomy", "supervised")
    if value in MODES:
        return None
    return _INVALID.format(value=value)
