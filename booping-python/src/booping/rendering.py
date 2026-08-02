from __future__ import annotations

from collections.abc import Callable, Iterator
from datetime import datetime
from pathlib import Path
from typing import Any, cast

from jinja2 import BaseLoader, ChainableUndefined, Environment, FileSystemLoader


class RenderCycleError(Exception):
    pass


class RenderDepthExceededError(Exception):
    pass


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


def now(fmt: str = "%Y%m%d-%H-%M") -> str:
    """Local wall-clock stamp, evaluated at render time."""
    return datetime.now().strftime(fmt)


def make_now(config: object = None) -> Callable[..., str]:
    """The `now` global a rendering env gets. A `now` key in config pins it: every
    call returns that value verbatim, whatever format is asked for — which makes a
    render byte-reproducible. Absent → the live wall-clock stamp.
    """
    pinned: object = (
        cast("dict[str, Any]", config).get("now") if isinstance(config, dict) else None
    )
    if pinned is None:
        return now
    value = str(pinned)

    def pinned_now(fmt: str = "%Y%m%d-%H-%M") -> str:  # noqa: ARG001
        return value

    return pinned_now


def _build_env(
    loader_root: Path,
    *,
    loader: BaseLoader | None = None,
    env_class: type[Environment] = Environment,
    config: object = None,
) -> Environment:
    env = env_class(
        loader=loader if loader is not None else FileSystemLoader(str(loader_root)),
        undefined=LenientUndefined,
        keep_trailing_newline=True,
    )
    globals_: dict[str, Any] = env.globals  # type: ignore[assignment]
    globals_["now"] = make_now(config)
    return env


def build_source_env(
    context: object,
    config: object,
    plugin_root: Path | None = None,
    *,
    loader: BaseLoader | None = None,
    env_class: type[Environment] = Environment,
) -> Environment:
    """Environment for rendering ad-hoc sources (not files under the plugin root).

    Same loader root and globals `render` gives a template under `src/templates/`, but
    bound as env globals so `env.from_string(...).render()` sees them — and so do the
    `{% include %}` / `{% import %}` targets the source pulls in.
    """
    from booping.tools import Tools  # local import to avoid circular at module level

    root = plugin_root if plugin_root is not None else get_plugin_root()
    env = _build_env(
        root / "src" / "templates",
        loader=loader,
        env_class=env_class,
        config=config,
    )
    globals_: dict[str, Any] = env.globals  # type: ignore[assignment]
    globals_["context"] = context
    globals_["config"] = config
    globals_["tools"] = Tools(
        env=env,
        context=context,
        config=config,
        plugin_root=root,
        render_stack=[],
    )
    return env


def render(
    template_path: Path | str,
    context: object,
    config: object,
    tools: object,
    kwargs: dict[str, Any],
    plugin_root: Path | None = None,
) -> str:
    from booping.tools import Tools  # local import to avoid circular at module level

    root = plugin_root if plugin_root is not None else get_plugin_root()
    templates_dir = root / "src" / "templates"
    path = Path(template_path).resolve()

    if templates_dir.exists() and path.is_relative_to(templates_dir):
        loader_root = templates_dir
        template_name = str(path.relative_to(templates_dir))
    elif path.is_relative_to(root):
        loader_root = root
        template_name = str(path.relative_to(root))
    else:
        loader_root = root
        template_name = None

    env = _build_env(loader_root, config=config)

    # Top-level render seeds an empty stack and constructs a real Tools instance.
    real_tools: Tools
    if isinstance(tools, Tools):
        real_tools = tools
    else:
        real_tools = Tools(
            env=env,
            context=context,
            config=config,
            plugin_root=root,
            render_stack=[],
        )

    if template_name is not None:
        template = env.get_template(template_name)
    else:
        source = path.read_text()
        template = env.from_string(source)

    return template.render(
        context=context,
        config=config,
        tools=real_tools,
        kwargs=kwargs,
    )
