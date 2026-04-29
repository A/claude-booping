from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import ChainableUndefined, Environment, FileSystemLoader


class RenderCycleError(Exception):
    pass


class RenderDepthExceededError(Exception):
    pass


class ToolsNS:
    """Wrapper so tools.render() is callable as an attribute, not bare function."""
    def __init__(self, render_fn: Any):
        self._render = render_fn
    def render(self, path: str | Path, **kw: Any) -> str:
        return self._render(path, **kw)


def render(
    template_path: str | Path,
    context: Any,
    config: Any,
    tools: Any,
    kwargs: Any,
    plugin_root: Path | None = None,
    undefined: type | None = None,
) -> str:
    """
    Render a Jinja2 template with four namespaces:
    - context: assembled data (project, plans, lessons, etc.)
    - config: alias of context.config for ergonomic access
    - tools: callable helpers (tools.render for nested templates)
    - kwargs: dict-like access to call-site kwargs
    """
    if plugin_root is None:
        plugin_root = Path(__file__).parent.parent.parent
    templates_dir = plugin_root / "src" / "templates"

    jinja_env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        undefined=undefined if undefined is not None else ChainableUndefined,
    )

    # Thread a render stack through globals for cycle/depth checks
    _render_stack: list[str] = []

    def _make_render(stack: list[str]):
        def _render(path: str | Path, **kw: Any) -> str:
            path_str = str(path)
            # Cycle detection
            if path_str in stack:
                raise RenderCycleError(f"cycle detected: {' → '.join(stack)} → {path_str}")
            # Depth check (default max 10)
            if len(stack) >= 10:
                raise RenderDepthExceededError(f"render depth {len(stack)} exceeds limit of 10")
            new_stack = stack + [path_str]
            nested_tools = ToolsNS(_make_render(new_stack))
            nested_kwargs = dict(kw)
            tmpl = jinja_env.get_template(str(path))
            return tmpl.render(
                context=context,
                config=config if hasattr(config, '__dict__') else config,
                tools=nested_tools,
                kwargs=nested_kwargs,
            )
        return _render

    tools_ns = ToolsNS(_make_render(_render_stack))

    # Top-level kwargs is empty dict seeded by caller
    tmpl = jinja_env.get_template(str(template_path))
    return tmpl.render(
        context=context,
        config=config if hasattr(config, '__dict__') else config,
        tools=tools_ns,
        kwargs={},
    )