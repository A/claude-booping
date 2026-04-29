from pathlib import Path
from typing import Any

import yaml
from jinja2 import Environment, FileSystemLoader, Undefined
from jinja2.ext import LoopControlExtension

from booping.context import Context
from booping.tools import Tools


class LenientUndefined(Undefined):
    def __str__(self) -> str:
        return ""

    def __iter__(self):  # type: ignore[override]
        return iter([])

    def __bool__(self) -> bool:
        return False

    def __getattr__(self, name: str) -> "LenientUndefined":
        return LenientUndefined(
            hint=self._undefined_hint,
            obj=self._undefined_obj,
            name=name,
            exc=self._undefined_exception,
        )

    def __getitem__(self, name: str) -> "LenientUndefined":
        return LenientUndefined(
            hint=self._undefined_hint,
            obj=self._undefined_obj,
            name=name,
            exc=self._undefined_exception,
        )


def find_plugin_root(start_path: str) -> Path:
    p = Path(start_path).resolve()
    if p.is_file():
        candidates = p.parents
    else:
        candidates = [p, *p.parents]
    for candidate in candidates:
        if (candidate / "src" / "config.yaml").exists():
            return candidate
    msg = (
        f"could not find plugin root "
        f"(directory containing src/config.yaml) from {start_path}"
    )
    raise FileNotFoundError(msg)


def _load_config(plugin_root: Path) -> dict[str, Any]:
    config_path = plugin_root / "src" / "config.yaml"
    if not config_path.exists():
        return {}
    return yaml.safe_load(config_path.read_text()) or {}


def render(
    template_path: str,
    context: dict[str, Any] | None = None,
    config: dict[str, Any] | None = None,
    tools: dict[str, Any] | Any | None = None,
    vault: Path | str | None = None,
    kwargs: dict[str, Any] | None = None,
) -> str:
    plugin_root = find_plugin_root(template_path)
    templates_dir = plugin_root / "src" / "templates"

    if isinstance(vault, str):
        vault = Path(vault)

    if context is not None or config is not None or tools is not None:
        # Legacy call mode: use provided globals directly
        if config is None:
            config = _load_config(plugin_root)
    else:
        # Full context assembly mode
        ctx = Context.assemble(plugin_root, vault)
        context = ctx.model_dump(mode="python")
        config = ctx.config
        if tools is None:
            tools = Tools(
                render_fn=render,
                plugin_root=str(plugin_root),
                vault=str(vault) if vault else None,
            )

    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=False,
        keep_trailing_newline=True,
        undefined=LenientUndefined,
        extensions=[LoopControlExtension],
    )

    template_rel = Path(template_path).resolve().relative_to(templates_dir)
    tpl = env.get_template(str(template_rel))

    render_globals: dict[str, Any] = {
        "context": context or {},
        "config": config,
        "tools": tools or {},
    }
    if kwargs is not None:
        render_globals["kwargs"] = kwargs

    return tpl.render(**render_globals)