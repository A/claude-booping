"""Run executor — move a file through the playbook state machine it is an artifact of.

The machine is inferred: every `states:` entry whose `artifact:` pattern the file
satisfies (the run workdir is the directory the pattern hangs off), filtered by an edge
from the file's current status; `--playbook`/`--state` narrow the candidates. The
playbook dir stays read-only source. Every artifact mutation happens here — the
printed report is the authoritative record of what changed.
"""

from __future__ import annotations

import argparse
import os
import re
import shlex
import subprocess
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, NoReturn

from booping import logger
from booping.commands.set import parse_pairs, resolve_values
from booping.context import Context
from booping.context._yaml import parse_frontmatter_only, update_frontmatter
from booping.context.lifecycle import resolve_edges, resolve_hooks
from booping.context.playbook import Playbook, StateMachine
from booping.context.project import Project

NOT_STARTED = "not-started"


def dispatch_set(
    hook: str,
    target: Path,
    project: Project | None,
    *,
    file_base: Path,
    instance: str | None = None,
    config: Mapping[str, Any] | None = None,
) -> tuple[str | None, dict[str, str]]:
    """Parse and apply a `set` hook string against *target*.

    E.g. ``set status=ready-for-dev`` or, with a file target,
    ``set _specs/brief.md reviewed="{{ macro('core.macros.date',
    '+%Y-%m-%d') }}"``.

    Returns ``(file-target rel-path or None, applied key → interpolated text)``;
    the written values are typed as the ``set`` CLI types them.
    """
    # shlex, not str.split: a value carrying a macro call has spaces in it and is
    # quoted in the hook string.
    try:
        tokens = shlex.split(hook)
    except ValueError as exc:
        print(f"error: malformed hook {hook!r}: {exc}", file=sys.stderr)
        sys.exit(2)
    # First token is the hook name; rest are key=val pairs, optionally
    # preceded by a file target (the only token carrying no "=").
    pairs = tokens[1:]
    rel: str | None = None
    if pairs and "=" not in pairs[0]:
        rel, pairs = pairs[0], pairs[1:]
        if "{instance}" in rel:
            if instance is None:
                print(
                    f"error: set target {rel} carries {{instance}} but no instance is in scope",
                    file=sys.stderr,
                )
                sys.exit(2)
            rel = rel.replace("{instance}", instance)
        target = file_base / rel

    repo_dir = project.repo_directory if project is not None else None
    resolved, rendered = resolve_values(dict(parse_pairs(pairs)), repo_dir, config)

    try:
        update_frontmatter(target, resolved)
    except Exception as exc:
        print(f"error: set failed: {exc}", file=sys.stderr)
        sys.exit(2)

    return rel, rendered


def format_frontmatter_line(resolved: dict[str, str], target: str | None = None) -> str:
    pairs = [f'{k}="{v}"' if " " in v else f"{k}={v}" for k, v in resolved.items()]
    prefix = "frontmatter: " if target is None else f"frontmatter {target}: "
    return prefix + " ".join(pairs)


def add_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "transition",
        help="Move a run artifact to a new status along the machine it matches, running its hooks",
    )
    p.add_argument("file", help="The run artifact to move")
    p.add_argument("to_status", metavar="to", help="Target status")
    p.add_argument(
        "--playbook",
        type=str,
        default=None,
        metavar="NAME",
        help=(
            "Playbook whose machines are the candidates (required for a machine "
            "declaring no `artifact:`, where the file is the target)"
        ),
    )
    p.add_argument(
        "--state",
        type=str,
        default=None,
        metavar="NAME",
        help="States entry within the candidates to move along",
    )
    p.set_defaults(func=_run)


def _fail(message: str, code: int = 1) -> NoReturn:
    print(f"error: {message}", file=sys.stderr)
    sys.exit(code)


@dataclass(frozen=True)
class Match:
    """A machine whose artifact pattern the file satisfies, with what the pattern implies."""

    playbook: Playbook
    state: str
    machine: StateMachine
    workdir: Path
    instance: str | None
    rel: str

    @property
    def label(self) -> str:
        return f"{self.playbook.name}/{self.state}"


def _segment_regex(segment: str) -> re.Pattern[str]:
    prefix, _, suffix = segment.partition("{instance}")
    return re.compile(f"{re.escape(prefix)}(?P<instance>.+){re.escape(suffix)}")


def match_artifact(pattern: str, file: Path) -> tuple[Path, str | None, str] | None:
    """Match an absolute *file* against a machine's `artifact:` pattern, anchored at its
    tail. Returns (workdir the pattern hangs off, instance filled from the path, path
    relative to the workdir), or None; every `{instance}` must capture the same slug."""
    parts = PurePosixPath(pattern).parts
    if not parts or len(parts) >= len(file.parts):
        return None
    tail = file.parts[-len(parts) :]
    instance: str | None = None
    for want, got in zip(parts, tail, strict=True):
        if "{instance}" not in want:
            if want != got:
                return None
            continue
        found = _segment_regex(want).fullmatch(got)
        if found is None or (instance is not None and found["instance"] != instance):
            return None
        instance = found["instance"]
    return file.parents[len(parts) - 1], instance, "/".join(tail)


def fallback_workdir(ctx: Context, file: Path) -> Path:
    """Workdir of a machine declaring no artifact: the vault holding the file, else cwd."""
    vault = ctx.project.directory.resolve() if ctx.project is not None else None
    if vault is not None and file.is_relative_to(vault):
        return vault
    return Path.cwd()


def _playbooks(ctx: Context, name: str | None) -> list[Playbook]:
    if name is None:
        return [pb for pb in ctx.playbooks if pb.states]
    pb = next((p for p in ctx.playbooks if p.name == name), None)
    if pb is None:
        known = ", ".join(sorted(p.name for p in ctx.playbooks)) or "(none)"
        _fail(f"playbook not found: {name} (known: {known})")
    if not pb.states:
        _fail(f"playbook '{pb.name}' declares no states")
    return [pb]


def resolve_matches(
    ctx: Context, file: Path, playbook: str | None, state: str | None
) -> list[Match]:
    """Every machine the file is an artifact of — across all playbooks, or only *playbook*
    (where a machine declaring no `artifact:` takes the file as its target) — narrowed
    to *state* when given."""
    matches: list[Match] = []
    for pb in _playbooks(ctx, playbook):
        if state is not None and playbook is not None and state not in pb.states:
            known = ", ".join(sorted(pb.states)) or "(none)"
            _fail(f"unknown state '{state}' in playbook '{pb.name}' (known: {known})")
        for name, machine in pb.states.items():
            if state is not None and name != state:
                continue
            if not machine.artifact:
                if playbook is not None:
                    matches.append(
                        Match(pb, name, machine, fallback_workdir(ctx, file), None, str(file))
                    )
                continue
            found = match_artifact(machine.artifact, file)
            if found is not None:
                matches.append(Match(pb, name, machine, *found))
    return matches


def _assemble_for(file: Path) -> Context:
    start = next(p for p in file.parents if p.is_dir())
    return Context.assemble(start=start)


def read_status(artifact: Path) -> str | None:
    """The artifact's run status, or None when the run has not started — the file is
    missing, carries no frontmatter block, or its frontmatter has no `status:` key."""
    if not artifact.exists():
        return None
    try:
        fm = parse_frontmatter_only(artifact)
    except ValueError:
        fm = {}
    status = fm.get("status")
    if status is None or str(status) == "":
        return None
    return str(status)


def _bootstrap(artifact: Path, initial: str) -> None:
    """Stamp the initial status onto an artifact that carries none. An existing file
    keeps its other frontmatter keys and their order (ruamel round-trip), and one
    without a frontmatter block gets it bootstrapped by the same writer."""
    if artifact.exists():
        try:
            update_frontmatter(artifact, {"status": initial})
        except Exception as exc:
            _fail(f"cannot stamp status onto {artifact}: {exc}", code=2)
        return
    artifact.parent.mkdir(parents=True, exist_ok=True)
    try:
        artifact.write_text(f"---\nstatus: {initial}\n---\n")
    except OSError as exc:
        _fail(f"cannot create artifact {artifact}: {exc}", code=2)


def _dispatch_script(
    hook: str,
    playbook_dir: Path,
    search_roots: list[Path],
    workdir: Path,
    artifact: Path,
    instance: str | None,
) -> str:
    """Run a `script <name> [args...]` hook. The script is looked up in the playbook's
    own `_scripts/` first, then in each discovery root's `_scripts/` (most specific
    first); trailing hook tokens are passed through as argv."""
    try:
        parts = shlex.split(hook)
    except ValueError as exc:
        _fail(f"malformed script hook {hook!r}: {exc}", code=2)
    if len(parts) < 2:
        _fail(f"malformed script hook: {hook!r}", code=2)
    name, script_args = parts[1], parts[2:]
    probed = [playbook_dir / "_scripts" / name]
    probed += [root / "_scripts" / name for root in search_roots]
    script = next((p for p in probed if p.is_file()), None)
    if script is None:
        paths = ", ".join(str(p) for p in probed)
        _fail(f"script hook {name!r} not found; probed: {paths}", code=2)
    if not os.access(script, os.X_OK):
        _fail(f"script hook {name!r} is not executable: {script}", code=2)

    env = dict(os.environ)
    env["BOOPING_ARTIFACT"] = str(artifact)
    env["BOOPING_INSTANCE"] = instance or ""
    env["BOOPING_WORKDIR"] = str(workdir)

    result = subprocess.run(
        [str(script), *script_args],
        cwd=str(workdir),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        if result.stderr:
            sys.stderr.write(result.stderr)
        _fail(f"script hook {name!r} exited {result.returncode}", code=2)
    return name


def _run(args: argparse.Namespace) -> None:
    report = transition(args.file, args.to_status, playbook=args.playbook, state=args.state)
    print("\n".join(report))


def _accepts(machine: StateMachine, current: str | None, to_status: str) -> bool:
    if current is None:
        return to_status == machine.initial
    if current == to_status:
        return to_status in machine.statuses
    return any(edge.to == to_status for edge in resolve_edges(current, machine.raw))


def _legal(machine: StateMachine, current: str | None) -> set[str]:
    if current is None:
        return {machine.initial}
    return {edge.to for edge in resolve_edges(current, machine.raw)}


def _pick(file: Path, matches: list[Match], to_status: str, playbook: str | None) -> Match:
    if not matches:
        if playbook is not None:
            _fail(f"{file} matches no machine artifact of playbook '{playbook}'")
        _fail(f"{file} matches no machine artifact; pass --playbook")
    current = read_status(file)
    shown = current if current is not None else NOT_STARTED
    accepted = [m for m in matches if _accepts(m.machine, current, to_status)]
    if not accepted:
        legal: set[str] = set()
        for m in matches:
            legal |= _legal(m.machine, current)
        listed = ", ".join(sorted(legal)) or "(none)"
        _fail(f"{file} ({shown}) has no edge to {to_status}; legal: {listed}")
    if len(accepted) > 1:
        labels = ", ".join(sorted(m.label for m in accepted))
        _fail(
            f"{file} matches more than one machine with an edge {shown} → {to_status}: "
            f"{labels}; pass --playbook"
        )
    return accepted[0]


def transition(
    file: str,
    to_status: str,
    *,
    playbook: str | None = None,
    state: str | None = None,
) -> list[str]:
    """Move *file* to *to_status* along the one machine it matches and run the edge's
    hooks; returns the mutation report lines. The in-process entry other commands share
    with `transition`; a refused move prints `error: …` to stderr and exits like the
    command does."""
    artifact = Path(file).expanduser().resolve()
    ctx = _assemble_for(artifact)
    match = _pick(artifact, resolve_matches(ctx, artifact, playbook, state), to_status, playbook)
    pb, state_name, machine = match.playbook, match.state, match.machine
    run_dir, instance, artifact_rel = match.workdir, match.instance, match.rel
    if not run_dir.is_dir():
        _fail(f"workdir not found: {run_dir}")

    report: list[str] = []
    existing = artifact.exists()
    current = read_status(artifact)
    if current is None:
        _bootstrap(artifact, machine.initial)
        from_status = NOT_STARTED
        report.append(f"bootstrapped {artifact_rel}" if existing else f"created {artifact_rel}")
        report.append(f"{from_status} → {to_status}")
        report.append(format_frontmatter_line({"status": to_status}))
        hooks = [str(h) for h in machine.raw.get("hooks", {}).get("post", [])]
    else:
        from_status = current
        if from_status == to_status:
            report.append(f"{to_status} → {to_status} (idempotent)")
            hooks = [str(h) for h in machine.raw.get("hooks", {}).get("post", [])]
        else:
            report.append(f"{from_status} → {to_status}")
            hooks = resolve_hooks(from_status, to_status, machine.raw)

    project: Project | None = ctx.project
    # A vault workdir resolves its project by containment but knows no repo; a
    # `cwd: repo` macro in a hook resolves it from the process cwd instead.
    hook_project = (
        project
        if project is not None and project.repo_directory is not None
        else Project.load_cwd_configured()
    )
    playbook_dir = pb.path.parent.resolve()

    for hook in hooks:
        hook_name = hook.split()[0] if hook.split() else ""
        if hook_name == "set":
            rel, resolved = dispatch_set(
                hook,
                artifact,
                hook_project,
                file_base=run_dir,
                instance=instance,
                config=ctx.config,
            )
            report.append(format_frontmatter_line(resolved, rel))
        elif hook_name == "script":
            name = _dispatch_script(
                hook, playbook_dir, pb.search_roots, run_dir, artifact, instance
            )
            report.append(f"script {name}: ok")
        else:
            _fail(f"unknown hook: {hook_name!r}", code=2)

    scope = f"{state_name}/{instance}" if instance else state_name
    logger.log(
        vault=project.directory if project is not None else None,
        subcommand="transition",
        message=f"{pb.name} {scope} {from_status}→{to_status}",
    )

    return report
