from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any, NoReturn, cast

from booping import logger
from booping.argparser import Parser
from booping.commands.scaffold import _plan  # pyright: ignore[reportPrivateUsage]
from booping.context import Context
from booping.context._yaml import parse_frontmatter_only
from booping.context.scaffold import ScaffoldError, load
from booping.plan.check import CHECKS, check_milestone
from booping.plan.split import SECTION_KEYS, Cut, Milestone, block, cut_draft, demote, split_lines
from booping.query import QuerySpec, as_dict, cell, expand
from booping.query import run as run_query
from booping.rendering import build_source_env
from booping.utils import PathError, resolve_path

USAGE_EXIT = 1
REFUSED_EXIT = 2
NO_MILESTONES_EXIT = 3
FLAGGED_EXIT = 4

MILESTONE_SCAFFOLD = "core.groom_playbook.milestone_scaffold"
SECTIONS_PATH = "core.groom_playbook.split.sections"
MILESTONES_PATH = "core.plans.milestones"
MAX_SP_PATH = "core.sprint.max_sp"
THRESHOLD_PATH = "core.sprint.redecompose_threshold"

CLEAN_EXIT = 0
FINDINGS_EXIT = 1
NOTHING_TO_CHECK_EXIT = 2

FRONTMATTER = re.compile(r"\A(---\n)(.*?)(\n---\n)", re.DOTALL)
SP_LINE = re.compile(r"^sp:.*$", re.MULTILINE)

SPLIT_EPILOG = f"""\
stdout: one `M{{nn}}-{{kebab}} sp={{n|null}} sections=tasks:N,dod:N,references:N,verify:N`
line per milestone, one `group G{{k}}: M{{nn}}, … ({{sum}} SP)` line per group, then
`demoted: N` when headings were demoted. stderr: one `flag: …` line per flag.

exit codes:
  0  written, no flags
  {USAGE_EXIT}  usage or config error
  {REFUSED_EXIT}  refused (milestone files exist without --replace) or a write failed
  {NO_MILESTONES_EXIT}  no milestone heading found; nothing written
  {FLAGGED_EXIT}  written, with flags
"""


CHECK_EPILOG = f"""\
checks:
  verify  Verify holds exactly one command: one fenced block with one non-blank line,
          or one line that is a single inline code span
  files   Tasks names at least one path: a backticked token holding `/` or a `.ext`
  dod     DoD checkboxes are at least as many as the tasks (rows of the first table
          with a `Task` column, else top-level list items); no task at all is a finding
  sp      frontmatter `sp` is set and below core.sprint.redecompose_threshold

stdout: one `{{milestone dir}}: {{check}}: {{finding}}` line per finding, in milestone id
order; nothing when clean.

exit codes:
  {CLEAN_EXIT}  clean
  {FINDINGS_EXIT}  findings
  {NOTHING_TO_CHECK_EXIT}  PLAN_DIR missing or holding no milestone file
"""


class _UsageParser(Parser):
    """Argument errors exit with the plan verbs' usage code rather than argparse's 2,
    which the verbs reserve for a refused write."""

    def error(self, message: str) -> NoReturn:
        self.print_usage(sys.stderr)
        self.exit(USAGE_EXIT, f"{self.prog}: error: {message}\n")


def add_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("plan", help="Cut a one-file plan draft into milestone files")
    verbs = p.add_subparsers(
        dest="plan_verb", metavar="<verb>", required=True, parser_class=_UsageParser
    )

    split = verbs.add_parser(
        "split",
        help="Write index.md and one milestone file per milestone from a one-file draft",
        epilog=SPLIT_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    split.add_argument("draft", metavar="DRAFT", type=Path, help="The one-file plan draft")
    split.add_argument(
        "--out",
        type=Path,
        default=None,
        metavar="DIR",
        help="Plan directory to write (default: DRAFT's directory)",
    )
    split.add_argument(
        "--replace",
        action="store_true",
        help="Remove the existing milestone directories (core.plans.milestones.glob) first",
    )
    split.set_defaults(func=_run_split)

    check = verbs.add_parser(
        "check",
        help=f"Check every milestone file of a plan against the milestone contract"
        f" ({', '.join(CHECKS)})",
        epilog=CHECK_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    check.add_argument("plan_dir", metavar="PLAN_DIR", type=Path, help="The plan directory")
    check.set_defaults(func=_run_check)


def _fail(message: str, code: int = USAGE_EXIT) -> NoReturn:
    print(f"error: {message}", file=sys.stderr)
    sys.exit(code)


def _config(config: dict[str, Any], dotted: str) -> Any:
    try:
        return resolve_path(config, dotted)
    except PathError:
        _fail(f"config key {dotted} is missing")


def _globs(spec: Any) -> list[str]:
    value: Any = cast("dict[str, Any]", spec).get("glob") if isinstance(spec, dict) else None
    if isinstance(value, str):
        return [value]
    if isinstance(value, list) and value:
        return [str(item) for item in cast("list[Any]", value)]
    _fail(f"{MILESTONES_PATH}.glob must be a string or a non-empty list")


def _milestone_files(plan_dir: Path, globs: Sequence[str]) -> list[Path]:
    return sorted({path for pattern in globs for path in expand(plan_dir, pattern)})


def _plan_ref(ctx: Context, index: Path) -> str:
    """The plan's index.md as the milestone frontmatter names it: vault-relative, else
    relative to the working directory when the plan sits outside the vault."""
    target = index.resolve()
    if ctx.project is not None:
        vault = ctx.project.directory.resolve()
        if target.is_relative_to(vault):
            return target.relative_to(vault).as_posix()
    return Path(os.path.relpath(target, Path.cwd().resolve())).as_posix()


def _section_body(lines: Sequence[str]) -> str:
    body = list(lines)
    while body and not body[0].strip():
        body.pop(0)
    return block(demote(body)[0])


def _fill(content: str, names: Sequence[str], m: Milestone) -> str:
    """The scaffolded milestone file with each section's lines under its `## {name}`."""
    keys = {f"## {name}": key for name, key in zip(names, SECTION_KEYS, strict=True)}
    lines = split_lines(content)
    out: list[str] = []
    placed: set[str] = set()
    i = 0
    while i < len(lines):
        line = lines[i]
        out.append(line)
        i += 1
        key = keys.get(line.rstrip("\r\n"))
        if key is None or key in placed:
            continue
        placed.add(key)
        body = _section_body(m.sections[key])
        if not body:
            continue
        if i < len(lines) and not lines[i].strip():
            out.append(lines[i])
            i += 1
        else:
            out.append("\n")
        out.append(body)
    text = "".join(out)
    for name, key in zip(names, SECTION_KEYS, strict=True):
        if key in placed:
            continue
        if not text.endswith("\n\n"):
            text += "\n" if text.endswith("\n") else "\n\n"
        text += f"## {name}\n\n" + _section_body(m.sections[key])
    return text.rstrip("\n") + "\n"


def _table(rows: Sequence[dict[str, Any]], columns: Sequence[str]) -> str:
    """`refresh-milestone-table`'s format, so develop's first refresh is a no-op."""

    def render(row: dict[str, Any], col: str) -> str:
        if col == "title" and row.get("path"):
            return f"[{cell(row.get(col))}]({row['path']})"
        return cell(row.get(col))

    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    lines += ["| " + " | ".join(render(row, col) for col in columns) + " |" for row in rows]
    return "\n".join(lines) + "\n"


def _group_sp(cut: Cut, group: Sequence[str]) -> int:
    sp = {m.id: m.sp for m in cut.milestones}
    return sum(value for mid in group if (value := sp[mid]) is not None)


def _groups_table(cut: Cut) -> str:
    lines = ["| group | milestones | sp |", "| --- | --- | --- |"]
    for k, group in enumerate(cut.groups, 1):
        ids = ", ".join(f"M{mid}" for mid in group)
        lines.append(f"| G{k} | {ids} | {_group_sp(cut, group)} |")
    return "\n".join(lines) + "\n"


def _index(head: str, cut: Cut, skip: int, generated: str) -> str:
    plan = list(cut.plan_lines[skip:])
    at = max(cut.generated_at - skip, 0)
    before, after = plan[:at], plan[at:]
    # Blank lines around the generated block collapse to one on each side.
    while before and not before[-1].strip():
        before.pop()
    while after and not after[0].strip():
        after.pop(0)
    text = "".join(before)
    if text:
        text += "\n" if text.endswith("\n") else "\n\n"
    text += generated
    if after:
        text += "\n" + "".join(after)
    if head and text and text[0].strip():
        text = "\n" + text
    return head + text


def _restamp(frontmatter: re.Match[str], total: int) -> str:
    inner = frontmatter.group(2)
    if SP_LINE.search(inner):
        inner = SP_LINE.sub(f"sp: {total}", inner, count=1)
    return frontmatter.group(1) + inner + frontmatter.group(3)


def _run_split(args: argparse.Namespace) -> None:
    draft: Path = args.draft
    try:
        text = draft.read_text(encoding="utf-8")
    except OSError as exc:
        _fail(f"cannot read {draft}: {exc}")
    out: Path = args.out if args.out is not None else draft.parent

    ctx = Context.assemble()
    config = ctx.config
    logger.log(
        vault=ctx.project.directory if ctx.project is not None else None,
        subcommand="plan split",
        message=f"{draft} → {out}",
    )
    max_sp: Any = _config(config, MAX_SP_PATH)
    if max_sp is not None and (not isinstance(max_sp, int) or isinstance(max_sp, bool)):
        _fail(f"{MAX_SP_PATH} must be an integer or null")
    names: Any = _config(config, SECTIONS_PATH)
    if not (
        isinstance(names, list)
        and len(cast("list[Any]", names)) == len(SECTION_KEYS)
        and all(isinstance(n, str) for n in cast("list[Any]", names))
    ):
        _fail(f"{SECTIONS_PATH} must list {len(SECTION_KEYS)} heading names")
    section_names = cast("list[str]", names)
    spec: Any = _config(config, MILESTONES_PATH)
    globs = _globs(spec)
    columns = [str(c) for c in cast("list[Any]", spec.get("table_columns") or [])]

    cut = cut_draft(text, max_sp)
    if not cut.milestones:
        _fail(f"no milestone heading found in {draft}", NO_MILESTONES_EXIT)

    existing = _milestone_files(out, globs)
    if existing and not args.replace:
        _fail(
            f"{len(existing)} milestone file(s) already exist under {out}; pass --replace",
            REFUSED_EXIT,
        )

    index_path = out / "index.md"
    env = build_source_env(context=ctx, config=config)
    globals_: dict[str, Any] = env.globals  # type: ignore[assignment]
    plan_ref = _plan_ref(ctx, index_path)
    writes: list[tuple[Path, str | None]] = []
    try:
        root = load(config, MILESTONE_SCAFFOLD)
        for m in cut.milestones:
            globals_.update(
                id=m.id,
                slug=m.slug,
                title=m.title,
                sp="null" if m.sp is None else str(m.sp),
                plan=plan_ref,
            )
            for write in _plan(root, out / "milestones", env):
                content = write.content
                relative = write.path.relative_to(out)
                if content is not None and any(relative.match(g) for g in globs):
                    content = _fill(content, section_names, m)
                writes.append((write.path, content))
    except ScaffoldError as exc:
        _fail(str(exc))

    if index_path.is_file():
        source = index_path.read_text(encoding="utf-8")
        own = FRONTMATTER.match(source)
    else:
        own = FRONTMATTER.match(text)
    in_draft = FRONTMATTER.match(text)
    skip = len(split_lines(in_draft.group(0))) if in_draft else 0
    total = sum(m.sp for m in cut.milestones if m.sp is not None)
    head = _restamp(own, total) if own else ""

    try:
        for path in {p.parent for p in existing}:
            shutil.rmtree(path)
        for path, content in writes:
            if content is None:
                path.mkdir(parents=True, exist_ok=True)
            else:
                path.write_bytes(content.encode("utf-8"))
        rows = [as_dict(row) for row in run_query(QuerySpec(glob=globs, columns=columns), out)]
        generated = (
            "## Milestones\n\n" + _table(rows, columns) + "\n## Groups\n\n" + _groups_table(cut)
        )
        index_path.write_bytes(_index(head, cut, skip, generated).encode("utf-8"))
    except OSError as exc:
        _fail(f"failed to write the plan into {out}: {exc}", REFUSED_EXIT)

    for m in cut.milestones:
        counts = ",".join(f"{key}:{len(m.sections[key])}" for key in SECTION_KEYS)
        sp = "null" if m.sp is None else m.sp
        print(f"M{m.id}-{m.slug} sp={sp} sections={counts}")
    for k, group in enumerate(cut.groups, 1):
        ids = ", ".join(f"M{mid}" for mid in group)
        print(f"group G{k}: {ids} ({_group_sp(cut, group)} SP)")
    if cut.demoted:
        print(f"demoted: {cut.demoted}")
    for flag in cut.flags:
        print(f"flag: {flag}", file=sys.stderr)
    sys.exit(FLAGGED_EXIT if cut.flags else 0)


def _run_check(args: argparse.Namespace) -> None:
    plan_dir: Path = args.plan_dir
    if not plan_dir.is_dir():
        _fail(f"no plan directory at {plan_dir}", NOTHING_TO_CHECK_EXIT)
    ctx = Context.assemble()
    config = ctx.config
    globs = _globs(_config(config, MILESTONES_PATH))
    threshold: Any = _config(config, THRESHOLD_PATH)
    if not isinstance(threshold, int) or isinstance(threshold, bool):
        _fail(f"{THRESHOLD_PATH} must be an integer")
    names: Any = _config(config, SECTIONS_PATH)
    if not (
        isinstance(names, list)
        and len(cast("list[Any]", names)) == len(SECTION_KEYS)
        and all(isinstance(n, str) for n in cast("list[Any]", names))
    ):
        _fail(f"{SECTIONS_PATH} must list {len(SECTION_KEYS)} heading names")
    section_names = cast("list[str]", names)

    files = _milestone_files(plan_dir, globs)
    if not files:
        _fail(f"no milestone file under {plan_dir}", NOTHING_TO_CHECK_EXIT)
    ordered = sorted(files, key=lambda f: (str(parse_frontmatter_only(f).get("id", "")), f))
    found = False
    for path in ordered:
        for finding in check_milestone(path.read_text(encoding="utf-8"), section_names, threshold):
            found = True
            print(f"{path.parent.name}: {finding.check}: {finding.message}")
    sys.exit(FINDINGS_EXIT if found else CLEAN_EXIT)
