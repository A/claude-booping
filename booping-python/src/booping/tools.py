from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


class Tools:
    _render_fn: Callable[..., str]
    _plugin_root: str
    _vault: str | None
    _render_stack: list[str]
    _max_depth: int

    def __init__(
        self,
        render_fn: Callable[..., str],
        plugin_root: str,
        vault: str | None,
        render_stack: list[str] | None = None,
        max_depth: int = 10,
    ) -> None:
        self._render_fn = render_fn
        self._plugin_root = plugin_root
        self._vault = vault
        self._render_stack = render_stack or []
        self._max_depth = max_depth

    def render(self, template_path: str, **kwargs: Any) -> str:
        if template_path in self._render_stack:
            raise RuntimeError(
                "Cycle detected: template "
                f"'{template_path}' is already being rendered. "
                f"Stack: {' -> '.join(self._render_stack)}"
            )
        if len(self._render_stack) >= self._max_depth:
            raise RuntimeError(
                f"Max render depth ({self._max_depth}) exceeded. "
                f"Stack: {' -> '.join(self._render_stack)}"
            )
        new_stack = [*self._render_stack, template_path]
        new_tools = Tools(
            render_fn=self._render_fn,
            plugin_root=self._plugin_root,
            vault=self._vault,
            render_stack=new_stack,
            max_depth=self._max_depth,
        )
        return self._render_fn(
            template_path,
            vault=self._vault,
            tools=new_tools,
            kwargs=kwargs,
        )