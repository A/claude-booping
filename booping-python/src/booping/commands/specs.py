from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import NoReturn

from booping import logger
from booping.context import Context
from booping.context import config as config_mod
from booping.rendering import get_plugin_root
from booping.specs.check import CheckError, check_tier, format_finding
from booping.specs.records import Record, load_tier
from booping.specs.tiers import Tier, resolve_tiers, types

TIER_CHOICES = ("core", "global", "project")


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


def _add_tier(p: argparse.ArgumentParser) -> None:
    p.add_argument(
        "--tier",
        choices=TIER_CHOICES,
        default="project",
        help="Tier to read (default: project)",
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


def _select_tier(ctx: Context, root: Path, home_dir: Path, name: str) -> Tier:
    tiers = resolve_tiers(
        ctx.config,
        plugin_root=root,
        home_dir=home_dir,
        repo=ctx.project.repo_directory if ctx.project is not None else None,
        vault=ctx.vault,
    )
    tier = next((t for t in tiers if t.name == name), None)
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
        findings, checked = check_tier(tier, _format_dir(ctx, root), known)
    except CheckError as exc:
        _fail(str(exc), 2)
    for f in findings:
        print(format_finding(f))
    errors = sum(1 for f in findings if f.level == "error")
    warnings = len(findings) - errors
    print(f"{checked} record(s) checked: {errors} error(s), {warnings} warning(s)", file=sys.stderr)
    if errors:
        sys.exit(1)
