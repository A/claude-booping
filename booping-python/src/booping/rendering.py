from pathlib import Path
from typing import Any

import yaml
from jinja2 import Environment, FileSystemLoader, Undefined


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


def _find_plugin_root(template_path: str) -> Path:
    p = Path(template_path).resolve()
    for parent in p.parents:
        if (parent / "src" / "config.yaml").exists():
            return parent
    msg = (
        f"could not find plugin root "
        f"(directory containing src/config.yaml) from {template_path}"
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
    tools: dict[str, Any] | None = None,
) -> str:
    plugin_root = _find_plugin_root(template_path)
    templates_dir = plugin_root / "src" / "templates"

    if config is None:
        config = _load_config(plugin_root)

    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=False,
        keep_trailing_newline=True,
        undefined=LenientUndefined,
    )

    template_rel = Path(template_path).resolve().relative_to(templates_dir)
    tpl = env.get_template(str(template_rel))

    return tpl.render(
        context=context or {},
        config=config,
        tools=tools or {},
    )