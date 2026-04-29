from __future__ import annotations

from pathlib import Path
from typing import Any



from booping.rendering import render as _render


class Tools:
    """Namespace of callable helpers passed to templates."""

    def __init__(self, plugin_root: Path, context: Any, config: Any):
        self._plugin_root = plugin_root
        self._context = context
        self._config = config

    def render(self, template_path: str | Path, **kw: Any) -> str:
        """
        Render another template with the same context/config/tools globals,
        plus the kwargs namespace.
        """
        return _render(
            template_path=str(template_path),
            context=self._context,
            config=self._config,
            tools=self,
            kwargs=kw,
            plugin_root=self._plugin_root,
        )