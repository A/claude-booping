from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, NoReturn, cast

import yaml

from booping import logger
from booping.context import Context
from booping.context import config as config_mod
from booping.rendering import get_plugin_root
from booping.specs import open_items
from booping.specs.check import CheckError, check_tier, display_path, format_finding
from booping.specs.init import InitError, apply, plan
from booping.specs.open_items import OpenItemError
from booping.specs.records import Record, load_tier
from booping.specs.site.index import ProjectsError, build_index, load_projects
from booping.specs.site.items import OpenItem, load_open_items
from booping.specs.site.labels import load_labels
from booping.specs.site.model import SiteRoot, SiteWarning, load_site
from booping.specs.site.pages import build_site
from booping.specs.site.plans import Work, load_work
from booping.specs.site.write import SiteError, write_site
from booping.specs.tiers import (
    Tier,
    _resolve_path,  # pyright: ignore[reportPrivateUsage]
    resolve_tiers,
    types,
)

TIER_CHOICES = ("core", "global", "project")
ROOT_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")


def add_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "specs",
        help="List, number and check typed spec records (values, rules, ADRs, …) of a tier",
    )
    verbs = p.add_subparsers(dest="specs_verb", metavar="<verb>", required=True)

    ls = verbs.add_parser("ls", help="List a tier's records: {type}/{NNNN}  {status}  {summary}")
    _add_tier(ls)
    ls.add_argument("--type", dest="record_type", metavar="TYPE", help="Only records of this type")
    ls.set_defaults(func=_run_ls)

    nxt = verbs.add_parser("next", help="Print the next free ref of a type in a tier")
    nxt.add_argument("record_type", metavar="type", help="Record type (e.g. adr, rule)")
    _add_tier(nxt)
    nxt.set_defaults(func=_run_next)

    chk = verbs.add_parser(
        "check",
        help="Validate a tier's records: {path}:{line}  {level}  {check}  {message}",
    )
    _add_tier(chk)
    chk.set_defaults(func=_run_check)

    scan = verbs.add_parser(
        "scan",
        help="File one clarify open item per [clarify]/[unknown] mark and per `specs check`"
        " finding in a tier, skipping any already tracked",
    )
    _add_tier(scan, "Tier to scan (default: project)")
    scan.set_defaults(func=_run_scan)

    init = verbs.add_parser(
        "init",
        help="Create a tier's root and README (and the vault symlink); print the tier root",
    )
    _add_tier(init, "Tier to create; core ships with the plugin and is rejected (default: project)")
    init.set_defaults(func=_run_init)

    site = verbs.add_parser(
        "site",
        help="Render specs roots to a static HTML site (default roots: the tiers"
        " plus core.specs.site.roots)",
    )
    site.add_argument(
        "--out",
        default="specs-site",
        metavar="DIR",
        help="Output directory (default: specs-site)",
    )
    site.add_argument(
        "--root",
        dest="roots",
        action="append",
        default=[],
        metavar="NAME=PATH",
        help="A root to render (repeatable); replaces the tier and config roots",
    )
    site.add_argument(
        "--home",
        metavar="NAME",
        help="The root rendered as the project's own registry; the others get their own"
        " blocks (default: the first --root, else the project tier's root)",
    )
    site.add_argument(
        "--title",
        metavar="TEXT",
        help="Site title in the header and every page title"
        " (default: the attached project's name, else Specs)",
    )
    site.add_argument(
        "--site-url",
        metavar="URL",
        help="Public http(s) URL the site is served at; writes a 404.html whose links"
        " resolve against its path",
    )
    site.set_defaults(func=_run_site)

    index = verbs.add_parser(
        "site-index",
        help="Render an index page listing projects' specs sites, in the site's look",
    )
    index.add_argument(
        "--projects",
        default="-",
        metavar="PATH",
        help="Project list of {name, url, description}: `-` reads JSON from stdin,"
        " a path is read as YAML (default: -)",
    )
    index.add_argument(
        "--out",
        default="specs-site-index",
        metavar="DIR",
        help="Output directory (default: specs-site-index)",
    )
    index.add_argument(
        "--title",
        default="Specs",
        metavar="TEXT",
        help="Page title, crumb and heading (default: Specs)",
    )
    index.set_defaults(func=_run_site_index)


def _add_tier(
    p: argparse.ArgumentParser, help_text: str = "Tier to read (default: project)"
) -> None:
    p.add_argument(
        "--tier",
        choices=TIER_CHOICES,
        default="project",
        help=help_text,
    )


def _fail(message: str, code: int = 1) -> NoReturn:
    print(f"error: {message}", file=sys.stderr)
    sys.exit(code)


def _assemble() -> tuple[Context, Path, Path]:
    """Context, plugin root and the core+global `home_dir` — the same merge
    `Context.assemble()` resolves the global roots from, which it does not carry."""
    try:
        ctx = Context.assemble()
        root = get_plugin_root()
        base_cfg = config_mod.load(root, [config_mod.global_config_path()])
    except Exception as exc:  # noqa: BLE001 — surface any loader failure as internal error
        _fail(f"could not load config: {exc}", 2)
    home_dir = Path(str(base_cfg.get("home_dir", "~/Claude"))).expanduser()
    return ctx, root, home_dir


def _format_dir(ctx: Context, root: Path) -> Path:
    specs = ctx.config.get("core", {}).get("specs", {})
    return root / str(specs.get("format"))


def _check_type(type_: str, known: list[str]) -> None:
    if type_ not in known:
        _fail(f"unknown type `{type_}`; known: {', '.join(known)}")


def _resolve(ctx: Context, root: Path, home_dir: Path) -> list[Tier]:
    return resolve_tiers(
        ctx.config,
        plugin_root=root,
        home_dir=home_dir,
        repo=ctx.project.repo_directory if ctx.project is not None else None,
        vault=ctx.vault,
    )


def _find_tier(ctx: Context, root: Path, home_dir: Path, name: str) -> Tier:
    tier = next((t for t in _resolve(ctx, root, home_dir) if t.name == name), None)
    if tier is None:
        _fail(f"tier `{name}` is not available here")
    return tier


def _require_dir(tier: Tier) -> Tier:
    if not tier.root.is_dir():
        _fail(f"no specs for tier `{tier.name}` at {tier.root}")
    return tier


def _select_tier(ctx: Context, root: Path, home_dir: Path, name: str) -> Tier:
    return _require_dir(_find_tier(ctx, root, home_dir, name))


def _numbered(records: list[Record], known: list[str]) -> list[Record]:
    """Records `ls`/`next` can address: a known type and a `NNNN-slug.md` name;
    the rest are `check`'s to report."""
    return [r for r in records if r.type in known and r.number is not None]


def _run_ls(args: argparse.Namespace) -> None:
    ctx, root, home_dir = _assemble()
    logger.log(vault=ctx.vault, subcommand="specs", message=f"ls --tier {args.tier}")
    tier = _find_tier(ctx, root, home_dir, args.tier)
    known = tier.types
    if args.record_type is not None:
        _check_type(args.record_type, known)
    _require_dir(tier)

    records = _numbered(load_tier(tier, known), known)
    if args.record_type is not None:
        records = [r for r in records if r.type == args.record_type]
    records.sort(key=lambda r: (r.type, r.number))
    for r in records:
        status = r.frontmatter.get("status")
        summary = r.frontmatter.get("summary")
        print(
            f"{r.type}/{r.number:04d}  {status if status is not None else '-'}"
            f"  {summary if summary is not None else ''}"
        )


def _run_next(args: argparse.Namespace) -> None:
    ctx, root, home_dir = _assemble()
    logger.log(
        vault=ctx.vault,
        subcommand="specs",
        message=f"next {args.record_type} --tier {args.tier}",
    )
    tier = _find_tier(ctx, root, home_dir, args.tier)
    known = tier.types
    _check_type(args.record_type, known)
    _require_dir(tier)

    numbers = [
        r.number
        for r in _numbered(load_tier(tier, known), known)
        if r.type == args.record_type and r.number is not None
    ]
    print(f"{args.record_type}/{max(numbers, default=0) + 1:04d}")


def _run_check(args: argparse.Namespace) -> None:
    ctx, root, home_dir = _assemble()
    logger.log(vault=ctx.vault, subcommand="specs", message=f"check --tier {args.tier}")
    tier = _select_tier(ctx, root, home_dir, args.tier)

    try:
        findings, checked = check_tier(tier, _resolve(ctx, root, home_dir))
    except CheckError as exc:
        _fail(str(exc), 2)
    for f in findings:
        print(format_finding(f))
    errors = sum(1 for f in findings if f.level == "error")
    warnings = len(findings) - errors
    print(f"{checked} record(s) checked: {errors} error(s), {warnings} warning(s)", file=sys.stderr)
    if errors:
        sys.exit(1)


def _run_scan(args: argparse.Namespace) -> None:
    ctx, root, home_dir = _assemble()
    try:
        open_items.require_vault(ctx)
    except OpenItemError as exc:
        _fail(str(exc))
    tier = _select_tier(ctx, root, home_dir, args.tier)
    known = tier.types
    records = load_tier(tier, known)
    try:
        findings, _ = check_tier(tier, _resolve(ctx, root, home_dir))
    except CheckError as exc:
        _fail(str(exc), 2)
    candidates = open_items.mark_candidates(
        [r for r in records if r.type in known], tier.root
    ) + open_items.finding_candidates(findings, tier.root)
    try:
        created, skipped = open_items.scan(ctx, candidates)
    except OpenItemError as exc:
        _fail(str(exc))
    for path in created:
        print(open_items.vault_relative(ctx, path))
    logger.log(vault=ctx.vault, subcommand="specs", message=f"scan --tier {args.tier}")
    print(f"{len(created)} created, {skipped} already tracked")


def _run_init(args: argparse.Namespace) -> None:
    ctx, root, home_dir = _assemble()
    repo = ctx.project.repo_directory if ctx.project is not None else None
    tier = next((t for t in _resolve(ctx, root, home_dir) if t.name == args.tier), None)
    try:
        if tier is None:
            raise InitError(f"tier `{args.tier}` is not available here")
        actions = plan(tier, repo=repo, vault=ctx.vault)
    except InitError as exc:
        print(f"specs init: {exc}", file=sys.stderr)
        sys.exit(1)
    for line in apply(actions):
        print(line)
    logger.log(vault=ctx.vault, subcommand="specs", message=f"init --tier {args.tier}")
    print(tier.root.absolute())


def _flag_roots(values: list[str]) -> list[SiteRoot]:
    roots: list[SiteRoot] = []
    for value in values:
        name, sep, path = value.partition("=")
        if not sep:
            _fail(f"--root `{value}` is not NAME=PATH")
        if ROOT_NAME.fullmatch(name) is None:
            _fail(f"--root name `{name}` must match {ROOT_NAME.pattern}")
        root_path = Path(path).expanduser()
        if not root_path.is_dir():
            _fail(f"--root `{name}`: {path} is not a directory")
        roots.append(SiteRoot(name=name, path=root_path))
    return roots


def _default_roots(
    ctx: Context, root: Path, home_dir: Path
) -> tuple[list[SiteRoot], list[tuple[Path, str]]]:
    """Tier roots then configured roots, deduplicated by resolved path; the second
    item is the configured roots skipped for a missing directory, as `(path, name)`."""
    roots: list[SiteRoot] = []
    seen: set[Path] = set()
    skipped: list[tuple[Path, str]] = []
    for tier in _resolve(ctx, root, home_dir):
        if not tier.root.is_dir() or tier.root.resolve() in seen:
            continue
        if tier.namespace is not None:
            name, source = tier.namespace, f"core.specs.tiers.{tier.name}.namespace"
        elif ctx.project is not None:
            name, source = ctx.project.name, "project name"
        else:
            name, source = tier.name, "tier name"
        if ROOT_NAME.fullmatch(name) is None:
            _fail(f"{source} `{name}` must match {ROOT_NAME.pattern} to name a site root")
        roots.append(SiteRoot(name=name, path=tier.root))
        seen.add(tier.root.resolve())

    site_cfg: dict[str, Any] = ctx.config.get("core", {}).get("specs", {}).get("site") or {}
    entries: list[Any] = site_cfg.get("roots") or []
    for entry in entries:
        fields: dict[str, Any] = cast("dict[str, Any]", entry) if isinstance(entry, dict) else {}
        name = fields.get("name")
        path = fields.get("path")
        if not isinstance(name, str) or ROOT_NAME.fullmatch(name) is None:
            _fail(
                f"core.specs.site.roots: bad entry {entry!r}; name must match {ROOT_NAME.pattern}"
            )
        if path is None:
            _fail(f"core.specs.site.roots: entry `{name}` has no path")
        root_path = _resolve_path(home_dir, str(path))
        if root_path.resolve() in seen:
            continue
        if not root_path.is_dir():
            skipped.append((root_path, name))
            continue
        roots.append(SiteRoot(name=name, path=root_path))
        seen.add(root_path.resolve())
    return roots, skipped


def _project_root_name(
    ctx: Context, root: Path, home_dir: Path, roots: list[SiteRoot]
) -> str | None:
    """The rendered root holding the project tier's directory, or None."""
    tier = next((t for t in _resolve(ctx, root, home_dir) if t.name == "project"), None)
    if tier is None or not tier.root.is_dir():
        return None
    path = tier.root.resolve()
    return next((r.name for r in roots if r.path.resolve() == path), None)


def _run_site(args: argparse.Namespace) -> None:
    ctx, root, home_dir = _assemble()
    logger.log(vault=ctx.vault, subcommand="specs", message=f"site --out {args.out}")
    if args.site_url is not None and not args.site_url.startswith(("http://", "https://")):
        _fail("--site-url must be an http:// or https:// URL")
    known = types(_format_dir(ctx, root))

    skipped: list[tuple[Path, str]] = []
    if args.roots:
        roots = _flag_roots(args.roots)
    else:
        roots, skipped = _default_roots(ctx, root, home_dir)
    if not roots:
        _fail("no specs roots to render")
    names = [r.name for r in roots]
    duplicates = sorted({n for n in names if names.count(n) > 1})
    if duplicates:
        _fail(f"duplicate root name(s): {', '.join(duplicates)}")

    site_cfg: dict[str, Any] = ctx.config.get("core", {}).get("specs", {}).get("site") or {}
    labels, lang, label_warnings = load_labels(site_cfg)
    for text in label_warnings:
        print(f"warning: {text}", file=sys.stderr)
    title = args.title or (ctx.project.name if ctx.project is not None else "Specs")

    open_items: list[OpenItem] = []
    item_warnings: list[SiteWarning] = []
    if args.home is not None:
        if args.home not in names:
            _fail(f"--home `{args.home}` names no rendered root (roots: {', '.join(names)})", 2)
        home: str | None = args.home
    elif args.roots:
        home = roots[0].name
    else:
        home = _project_root_name(ctx, root, home_dir, roots)
    items_root: str | None = None
    if not args.roots and ctx.vault is not None:
        items_root = home
        specs_cfg: dict[str, Any] = ctx.config.get("core", {}).get("specs", {})
        settings: dict[str, Any] = specs_cfg.get("open_items") or {}
        open_items, item_warnings = load_open_items(ctx.vault / str(settings.get("dir")))

    work = Work()
    if not args.roots and ctx.vault is not None and home is not None:
        work = _load_work(ctx, ctx.vault, home)

    site = load_site(roots, known)
    files, warnings = build_site(
        site,
        known,
        labels,
        lang,
        title,
        args.site_url,
        open_items=open_items,
        items_root=items_root,
        home=home,
        work=work,
    )
    warnings = sorted([*warnings, *item_warnings])
    try:
        write_site(files, Path(args.out), roots)
    except SiteError as exc:
        _fail(str(exc))

    lines = [
        (display_path(w.path), w.line, f":{w.line}  warning  site  {w.message}") for w in warnings
    ]
    lines += [
        (display_path(path), 0, f"  warning  site  root {name} not found, skipped")
        for path, name in skipped
    ]
    for path, _, rest in sorted(lines):
        print(f"{path}{rest}", file=sys.stderr)
    pages = sum(1 for path in files if path.endswith(".html"))
    plans = f" {len(work.plans)} plans, {len(work.retros)} retrospectives," if work else ""
    print(
        f"specs site: {len(roots)} roots, {len(site.records)} records,{plans} {pages} pages,"
        f" {len(lines)} warnings -> {args.out}"
    )


def _str_list(value: Any) -> list[str]:
    return [str(v) for v in cast("list[Any]", value)] if isinstance(value, list) else []


def _load_work(ctx: Context, vault: Path, home: str) -> Work:
    """The vault's plans (`core.plans.glob`, milestones by `core.plans.milestones.glob`)
    and retrospectives (`core.learn_playbook.queries.candidates.glob`)."""
    core: dict[str, Any] = ctx.config.get("core", {})
    plans_cfg: dict[str, Any] = core.get("plans") or {}
    milestones: dict[str, Any] = plans_cfg.get("milestones") or {}
    learn: dict[str, Any] = core.get("learn_playbook") or {}
    queries: dict[str, Any] = learn.get("queries") or {}
    retros: dict[str, Any] = queries.get("candidates") or {}
    glob = milestones.get("glob")
    return load_work(
        vault,
        home,
        _str_list(plans_cfg.get("glob")),
        None if glob is None else str(glob),
        _str_list(retros.get("glob")),
    )


def _read_projects(source: str) -> Any:
    try:
        if source == "-":
            return json.loads(sys.stdin.read())
        return yaml.safe_load(Path(source).read_text())
    except FileNotFoundError:
        _fail(f"--projects {source}: no such file")
    except (json.JSONDecodeError, yaml.YAMLError) as exc:
        _fail(f"--projects {source}: {str(exc).splitlines()[0]}")


def _run_site_index(args: argparse.Namespace) -> None:
    ctx, _, _ = _assemble()
    logger.log(vault=ctx.vault, subcommand="specs", message=f"site-index --out {args.out}")
    try:
        projects = load_projects(_read_projects(args.projects))
    except ProjectsError as exc:
        _fail(str(exc))
    site_cfg: dict[str, Any] = ctx.config.get("core", {}).get("specs", {}).get("site") or {}
    labels, lang, label_warnings = load_labels(site_cfg)
    for text in label_warnings:
        print(f"warning: {text}", file=sys.stderr)
    try:
        write_site(build_index(projects, args.title, labels, lang), Path(args.out), [])
    except SiteError as exc:
        _fail(str(exc))
    print(f"specs site-index: {len(projects)} projects -> {args.out}")
