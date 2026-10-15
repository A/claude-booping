from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any, NoReturn, cast

from booping import logger
from booping.context import Context
from booping.context import config as config_mod
from booping.rendering import get_plugin_root
from booping.specs import open_items
from booping.specs.check import CheckError, check_tier, display_path, format_finding
from booping.specs.init import InitError, apply, plan
from booping.specs.open_items import OpenItemError
from booping.specs.records import Record, load_tier
from booping.specs.site.model import SiteRoot, load_site
from booping.specs.site.pages import build_site
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
    site.set_defaults(func=_run_site)

    oi = verbs.add_parser(
        "open-items",
        help="List, file and move open items — the specs-to-code gaps under {vault}/open-items",
    )
    oi_verbs = oi.add_subparsers(dest="open_items_verb", metavar="<verb>", required=True)

    add = oi_verbs.add_parser(
        "add",
        help="File the next open item and print its vault-relative path",
    )
    add.add_argument("--title", default=None, metavar="TEXT", help="Item title")
    add.add_argument(
        "--direction",
        default=None,
        metavar="D",
        help=f"One of: {', '.join(open_items.DIRECTIONS)} (default with --record adr/NNNN:"
        " spec-to-code)",
    )
    add.add_argument(
        "--record",
        default=None,
        metavar="REF",
        help="Record the item is about, e.g. adr/0025#consequences; adr/NNNN without"
        " --title takes the title from the ADR's Confirmation: line",
    )
    add.add_argument(
        "--source",
        default=None,
        metavar="S",
        help=f"One of: {', '.join(open_items.SOURCES)} (default: manual; adr with"
        " --record adr/NNNN)",
    )
    add.add_argument("--body", default=None, metavar="TEXT", help="Optional body paragraph")
    add.set_defaults(func=_run_oi_add)

    scan = oi_verbs.add_parser(
        "scan",
        help="File one clarify item per [clarify]/[unknown] mark and per `specs check`"
        " finding in a tier, skipping any already tracked",
    )
    _add_tier(scan, "Tier to scan (default: project)")
    scan.set_defaults(func=_run_oi_scan)

    lst = oi_verbs.add_parser(
        "list",
        help="Print the open-items index as a markdown table (open and planned items)",
    )
    lst.add_argument("--all", action="store_true", help="Include closed items too")
    lst.set_defaults(func=_run_oi_list)

    pln = oi_verbs.add_parser("plan", help="Link open items to a plan and move them to planned")
    pln.add_argument("ids", nargs="+", metavar="ID", help="Open item id, e.g. OI-0001")
    pln.add_argument(
        "--plan",
        required=True,
        metavar="PATH",
        help="The plan's index.md, vault-relative (plans/{dir}/index.md); must exist",
    )
    pln.set_defaults(func=_run_oi_plan)

    close = oi_verbs.add_parser(
        "close",
        help="Close planned items as done (or open/planned ones as dropped with --dropped)",
    )
    close.add_argument("ids", nargs="*", metavar="ID", help="Open item id, e.g. OI-0001")
    close.add_argument(
        "--plan",
        default=None,
        metavar="PATH",
        help="Instead of ids: every planned item linked to this plan",
    )
    close.add_argument(
        "--dropped", action="store_true", help="Close as dropped (no work done); accepts open items"
    )
    close.add_argument("--reason", default=None, metavar="TEXT", help="Why the item closed")
    close.set_defaults(func=_run_oi_close)

    reopen = oi_verbs.add_parser("reopen", help="Return planned items to open, clearing their plan")
    reopen.add_argument("ids", nargs="*", metavar="ID", help="Open item id, e.g. OI-0001")
    reopen.add_argument(
        "--plan",
        default=None,
        metavar="PATH",
        help="Instead of ids: every planned item linked to this plan",
    )
    reopen.set_defaults(func=_run_oi_reopen)


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


def _known_types(ctx: Context, root: Path) -> list[str]:
    return types(_format_dir(ctx, root))


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


def _select_tier(ctx: Context, root: Path, home_dir: Path, name: str) -> Tier:
    tier = next((t for t in _resolve(ctx, root, home_dir) if t.name == name), None)
    if tier is None:
        _fail(f"tier `{name}` is not available here")
    if not tier.root.is_dir():
        _fail(f"no specs for tier `{name}` at {tier.root}")
    return tier


def _numbered(records: list[Record], known: list[str]) -> list[Record]:
    """Records `ls`/`next` can address: a known type and a `NNNN-slug.md` name;
    the rest are `check`'s to report."""
    return [r for r in records if r.type in known and r.number is not None]


def _run_ls(args: argparse.Namespace) -> None:
    ctx, root, home_dir = _assemble()
    logger.log(vault=ctx.vault, subcommand="specs", message=f"ls --tier {args.tier}")
    known = _known_types(ctx, root)
    if args.record_type is not None:
        _check_type(args.record_type, known)
    tier = _select_tier(ctx, root, home_dir, args.tier)

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
    known = _known_types(ctx, root)
    _check_type(args.record_type, known)
    tier = _select_tier(ctx, root, home_dir, args.tier)

    numbers = [
        r.number
        for r in _numbered(load_tier(tier, known), known)
        if r.type == args.record_type and r.number is not None
    ]
    print(f"{args.record_type}/{max(numbers, default=0) + 1:04d}")


def _run_check(args: argparse.Namespace) -> None:
    ctx, root, home_dir = _assemble()
    logger.log(vault=ctx.vault, subcommand="specs", message=f"check --tier {args.tier}")
    known = _known_types(ctx, root)
    tier = _select_tier(ctx, root, home_dir, args.tier)

    try:
        findings, checked = check_tier(
            tier, _format_dir(ctx, root), known, _resolve(ctx, root, home_dir)
        )
    except CheckError as exc:
        _fail(str(exc), 2)
    for f in findings:
        print(format_finding(f))
    errors = sum(1 for f in findings if f.level == "error")
    warnings = len(findings) - errors
    print(f"{checked} record(s) checked: {errors} error(s), {warnings} warning(s)", file=sys.stderr)
    if errors:
        sys.exit(1)


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


def _run_site(args: argparse.Namespace) -> None:
    ctx, root, home_dir = _assemble()
    logger.log(vault=ctx.vault, subcommand="specs", message=f"site --out {args.out}")
    known = _known_types(ctx, root)

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

    site = load_site(roots, known)
    files, warnings = build_site(site, known)
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
    print(
        f"specs site: {len(roots)} roots, {len(site.records)} records, {pages} pages,"
        f" {len(lines)} warnings -> {args.out}"
    )


def _run_oi_add(args: argparse.Namespace) -> None:
    ctx, root, home_dir = _assemble()
    title: str | None = args.title
    direction: str | None = args.direction
    record: str | None = args.record
    source: str | None = args.source
    try:
        open_items.require_vault(ctx)
        if record is not None and open_items.is_adr_ref(record):
            known = _known_types(ctx, root)
            tier = _select_tier(ctx, root, home_dir, "project")
            adr = open_items.find_adr(load_tier(tier, known), record)
            if title is None:
                title = open_items.confirmation_title(adr)
                if title is None:
                    raise OpenItemError(
                        f"{record} has no `Confirmation:` line under ## Consequences"
                    )
            direction = direction or "spec-to-code"
            source = source or "adr"
            record = f"{record}#consequences"
        if title is None:
            raise OpenItemError("--title is required unless --record names an ADR")
        if direction is None:
            raise OpenItemError("--direction is required unless --record names an ADR")
        source = source or "manual"
        open_items.check_choice("--direction", direction, open_items.DIRECTIONS)
        open_items.check_choice("--source", source, open_items.SOURCES)
        path = open_items.write_item(
            ctx, title=title, direction=direction, record=record, source=source, body=args.body
        )
    except OpenItemError as exc:
        _fail(str(exc))
    rel = open_items.vault_relative(ctx, path)
    logger.log(vault=ctx.vault, subcommand="specs", message=f"open-items add {rel}")
    print(rel)


def _run_oi_scan(args: argparse.Namespace) -> None:
    ctx, root, home_dir = _assemble()
    try:
        open_items.require_vault(ctx)
    except OpenItemError as exc:
        _fail(str(exc))
    known = _known_types(ctx, root)
    tier = _select_tier(ctx, root, home_dir, args.tier)
    records = load_tier(tier, known)
    try:
        findings, _ = check_tier(tier, _format_dir(ctx, root), known, _resolve(ctx, root, home_dir))
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
    logger.log(vault=ctx.vault, subcommand="specs", message=f"open-items scan --tier {args.tier}")
    print(f"{len(created)} created, {skipped} already tracked")


def _run_oi_list(args: argparse.Namespace) -> None:
    ctx = _assemble()[0]
    try:
        where: dict[str, Any] = (
            {} if args.all else {"status:in": open_items.open_statuses(open_items.machine(ctx))}
        )
        rows, columns = open_items.index_rows(ctx, where)
    except OpenItemError as exc:
        _fail(str(exc))
    logger.log(vault=ctx.vault, subcommand="specs", message="open-items list")
    print(open_items.index_table(rows, columns) if rows else "no open items")


def _selected(ctx: Context, ids: list[str], plan: str | None) -> list[str]:
    """The ids a close/reopen acts on: given outright, or every planned item of a plan."""
    if bool(ids) == (plan is not None):
        raise OpenItemError("pass item ids or --plan PATH, not both")
    if plan is None:
        return ids
    selected = open_items.planned_for(ctx, open_items.vault_path(ctx, plan))
    if not selected:
        print(f"no planned items for {plan}")
    return selected


def _run_oi_move(
    verb: str, ids: list[str], plan: str | None, to: str, fields: dict[str, str]
) -> None:
    ctx = _assemble()[0]
    try:
        for item_id in _selected(ctx, ids, plan):
            print("\n".join(open_items.move(ctx, item_id, to, fields)))
            logger.log(vault=ctx.vault, subcommand="specs", message=f"open-items {verb} {item_id}")
    except OpenItemError as exc:
        _fail(str(exc))


def _run_oi_plan(args: argparse.Namespace) -> None:
    ctx = _assemble()[0]
    try:
        plan = open_items.vault_path(ctx, args.plan)
        if not (open_items.require_vault(ctx) / plan).is_file():
            raise OpenItemError(f"plan not found: {plan}")
    except OpenItemError as exc:
        _fail(str(exc))
    _run_oi_move("plan", args.ids, None, "planned", {"plan": plan})


def _run_oi_close(args: argparse.Namespace) -> None:
    fields = {"reason": args.reason} if args.reason is not None else {}
    to = "dropped" if args.dropped else "done"
    _run_oi_move("close", args.ids, args.plan, to, fields)


def _run_oi_reopen(args: argparse.Namespace) -> None:
    _run_oi_move("reopen", args.ids, args.plan, "open", {})
