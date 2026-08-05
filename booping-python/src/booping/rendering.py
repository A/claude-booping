from __future__ import annotations

from collections.abc import Callable, Iterator
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

from jinja2 import BaseLoader, ChainableUndefined, Environment, FileSystemLoader, pass_context

from booping.macros import make_macro

if TYPE_CHECKING:
    from jinja2.runtime import Context as JinjaContext

    from booping.query import Row


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


def _vault_of(context: object) -> Path | None:
    """The vault a query runs against: the render's resolved vault, else the project's."""
    vault = getattr(context, "vault", None)
    if isinstance(vault, Path):
        return vault
    project = getattr(context, "project", None)
    directory = getattr(project, "directory", None)
    return directory if isinstance(directory, Path) else None


def make_query_filter(config: object) -> Callable[..., list[Row]]:
    """The `query` filter: `{{ 'a.b.c' | query(where={...}) }}`.

    The left-hand side is a dotted config path whose value is the spec; keyword
    arguments deep-merge over it for this call only. An unresolvable path raises
    rather than rendering empty.
    """
    # Local import: booping.query pulls in booping.context, which imports this module.
    from booping.query import QueryError, build_spec, resolve_spec, run

    @pass_context
    def query_filter(
        jinja_ctx: JinjaContext, spec_path: object, **overrides: Any
    ) -> list[Row]:
        cfg = cast("dict[str, Any]", config) if isinstance(config, dict) else {}
        dotted = str(spec_path)
        base = resolve_spec(cfg, dotted)
        try:
            spec = build_spec(cfg, base, overrides)
        except Exception as exc:
            raise QueryError(f"invalid query spec at config path {dotted}: {exc}") from exc
        vault = _vault_of(jinja_ctx.get("context"))
        # A `root: core` spec globs the plugin root, so it needs no vault at all.
        if vault is None and spec.root is None:
            raise QueryError(
                f"cannot run query {dotted}: no vault resolved for this render"
            )
        return run(spec, vault)

    return query_filter


def _build_env(
    loader_root: Path,
    *,
    loader: BaseLoader | None = None,
    env_class: type[Environment] = Environment,
    config: object = None,
) -> Environment:
    from booping.query import as_table  # local import: see make_query_filter

    env = env_class(
        loader=loader if loader is not None else FileSystemLoader(str(loader_root)),
        undefined=LenientUndefined,
        keep_trailing_newline=True,
    )
    globals_: dict[str, Any] = env.globals  # type: ignore[assignment]
    globals_["macro"] = make_macro(config)
    filters: dict[str, Any] = env.filters  # type: ignore[assignment]
    filters["query"] = make_query_filter(config)
    filters["as_table"] = as_table
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
