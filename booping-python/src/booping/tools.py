from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Environment

from booping.rendering import RenderCycleError, RenderDepthExceededError


class Tools:
    def __init__(
        self,
        env: Environment,
        context: object,
        config: object,
        plugin_root: Path,
        render_stack: list[str],
        max_depth: int = 10,
    ) -> None:
        self._env = env
        self._context = context
        self._config = config
        self._plugin_root = plugin_root
        self._render_stack = render_stack
        self._max_depth = max_depth

    def render(self, template_path: str, **kwargs: Any) -> str:
        resolved = str(Path(self._plugin_root / template_path).resolve())

        if resolved in self._render_stack:
            chain = " -> ".join(self._render_stack + [resolved])
            raise RenderCycleError(f"cycle detected: {chain}")

        if len(self._render_stack) >= self._max_depth:
            raise RenderDepthExceededError(
                f"render depth exceeded {self._max_depth}: {self._render_stack}"
            )

        self._render_stack.append(resolved)
        try:
            templates_dir = self._plugin_root / "src" / "templates"
            p = Path(resolved)
            if p.is_relative_to(templates_dir):
                template_name = str(p.relative_to(templates_dir))
                template = self._env.get_template(template_name)
            elif p.is_relative_to(self._plugin_root):
                # Re-use the env's loader if path is under plugin root
                template_name = str(p.relative_to(self._plugin_root))
                template = self._env.get_template(template_name)
            else:
                template = self._env.from_string(p.read_text())

            return template.render(
                context=self._context,
                config=self._config,
                tools=self,
                kwargs=kwargs,
            )
        finally:
            self._render_stack.pop()
