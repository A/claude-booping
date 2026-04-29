from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Any

from jinja2 import ChainableUndefined, Environment, FileSystemLoader


class LenientUndefined(ChainableUndefined):
    """Undefined that silently absorbs attribute access, subscript, iteration, and .get()."""

    def get(self, key: object = None, default: object = None) -> object:
        return default if default is not None else LenientUndefined()

    def __call__(self, *args: object, **kwargs: object) -> LenientUndefined:
        return LenientUndefined()

    def __iter__(self) -> Iterator[Any]:
        return iter([])

    def __len__(self) -> int:
        return 0

    def __bool__(self) -> bool:
        return False

    def items(self) -> Any:
        _empty: dict[str, object] = {}
        return _empty.items()

    def values(self) -> Any:
        _empty: dict[str, object] = {}
        return _empty.values()

    def keys(self) -> Any:
        _empty: dict[str, object] = {}
        return _empty.keys()


def _find_plugin_root(start: Path) -> Path:
    """Walk up from start until a directory contains both src/ and bin/booping."""
    candidate = start.resolve()
    for _ in range(20):
        if (candidate / "src").is_dir() and (candidate / "bin" / "booping").exists():
            return candidate
        parent = candidate.parent
        if parent == candidate:
            break
        candidate = parent
    raise RuntimeError(
        f"Could not locate plugin root (needs src/ and bin/booping) starting from {start}"
    )


_plugin_root: Path | None = None


def get_plugin_root() -> Path:
    global _plugin_root
    if _plugin_root is None:
        _plugin_root = _find_plugin_root(Path(__file__).parent)
    return _plugin_root


def render(
    template_path: Path | str,
    context: dict[str, object],
    config: dict[str, object],
    tools: dict[str, object],
    kwargs: dict[str, object],
    plugin_root: Path | None = None,
) -> str:
    root = plugin_root if plugin_root is not None else get_plugin_root()
    # Templates use includes relative to src/templates/ (mirrors booping-build loader root).
    templates_dir = root / "src" / "templates"
    path = Path(template_path).resolve()

    if templates_dir.exists() and path.is_relative_to(templates_dir):
        loader_root = templates_dir
        template_name = str(path.relative_to(templates_dir))
    elif path.is_relative_to(root):
        loader_root = root
        template_name = str(path.relative_to(root))
    else:
        # Template lives outside plugin root — read as string (no include support).
        loader_root = root
        template_name = None

    env = Environment(
        loader=FileSystemLoader(str(loader_root)),
        undefined=LenientUndefined,
        keep_trailing_newline=True,
    )

    if template_name is not None:
        template = env.get_template(template_name)
    else:
        source = path.read_text()
        template = env.from_string(source)

    return template.render(
        context=context,
        config=config,
        tools=tools,
        kwargs=kwargs,
    )
