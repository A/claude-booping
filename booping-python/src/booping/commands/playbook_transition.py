"""Playbook run executor — move a run artifact through a playbook state machine.

The artifact path of a `states:` entry is relative to the run workdir (default cwd);
the playbook dir stays read-only source. Every artifact mutation happens here — the
printed report is the authoritative record of what changed.
"""
from __future__ import annotations

import argparse
import os
import shlex
import subprocess
import sys
from collections.abc import Mapping
from pathlib import Path, PurePosixPath
from typing import Any, NoReturn

from booping import logger
from booping.commands.frontmatter_update import interpolate, parse_pairs
from booping.context import Context
from booping.context._yaml import parse_frontmatter_only, update_frontmatter
from booping.context.lifecycle import resolve_edges, resolve_hooks
from booping.context.playbook import Playbook, StateMachine
from booping.context.project import Project

NOT_STARTED = "not-started"


def dispatch_frontmatter_update(
    hook: str,
    target: Path,
    project: Project | None,
    *,
    file_base: Path,
    instance: str | None = None,
    config: Mapping[str, Any] | None = None,
) -> tuple[str | None, dict[str, str]]:
    """Parse and apply a frontmatter-update hook string against *target*.

    E.g. ``frontmatter-update status=ready-for-dev`` or, with a file target,
    ``frontmatter-update _specs/brief.md reviewed="{{ macro('core.macros.date',
    '+%Y-%m-%d') }}"``.

    Returns ``(file-target rel-path or None, applied key → resolved-value)``.
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
                    f"error: frontmatter-update target {rel} carries "
                    "{instance} but no instance is in scope",
                    file=sys.stderr,
                )
                sys.exit(2)
            rel = rel.replace("{instance}", instance)
        target = file_base / rel

    repo_dir = project.repo_directory if project is not None else None
    resolved = {
        key: interpolate(value, repo_dir, config)
        for key, value in parse_pairs(pairs).items()
    }

    try:
        update_frontmatter(target, dict(resolved))
    except Exception as exc:
        print(f"error: frontmatter-update failed: {exc}", file=sys.stderr)
        sys.exit(2)

    return rel, resolved


def format_frontmatter_line(
    resolved: dict[str, str], target: str | None = None
) -> str:
    pairs = [
        f'{k}="{v}"' if " " in v else f"{k}={v}" for k, v in resolved.items()
    ]
    prefix = "frontmatter: " if target is None else f"frontmatter {target}: "
    return prefix + " ".join(pairs)


def add_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "playbook-transition",
        help="Move a playbook run artifact to a new status, running its hooks",
    )
    p.add_argument("playbook", help="Playbook name")
    p.add_argument("to_status", metavar="to", help="Target status")
    p.add_argument(
        "--state",
        type=str,
        default=None,
        metavar="NAME",
        help="States entry to move (default: the outer graph's state ref)",
    )
    p.add_argument(
        "--instance",
        type=str,
        default=None,
        metavar="SLUG",
        help="Instance slug, required iff the artifact path carries {instance}",
    )
    p.add_argument(
        "--target",
        type=str,
        default=None,
        metavar="PATH",
        help=(
            "Artifact to move instead of the machine's declared `artifact:` "
            "(relative paths resolve against the workdir; an absolute path ending "
            "in the declared `artifact:` implies the workdir)"
        ),
    )
    p.add_argument(
        "--workdir",
        type=str,
        default=None,
        metavar="PATH",
        help=(
            "Run workspace the artifact path resolves against "
            "(default: the workdir an absolute --target implies, else cwd)"
        ),
    )
    p.set_defaults(func=_run)


def _fail(message: str, code: int = 1) -> NoReturn:
    print(f"error: {message}", file=sys.stderr)
    sys.exit(code)


def _resolve_playbook(ctx: Context, name: str) -> Playbook:
    pb = next((p for p in ctx.playbooks if p.name == name), None)
    if pb is None:
        known = ", ".join(sorted(p.name for p in ctx.playbooks)) or "(none)"
        _fail(f"playbook not found: {name} (known: {known})")
    return pb


def _resolve_state(pb: Playbook, requested: str | None) -> tuple[str, StateMachine]:
    if not pb.states:
        _fail(f"playbook '{pb.name}' declares no states")
    name = requested if requested is not None else pb.state_refs.get("")
    if name is None:
        _fail(f"playbook '{pb.name}' declares no state for its outer graph; pass --state")
    if name not in pb.states:
        known = ", ".join(sorted(pb.states)) or "(none)"
        _fail(f"unknown state '{name}' in playbook '{pb.name}' (known: {known})")
    return name, pb.states[name]


def resolve_target(target: str, workdir: Path) -> Path:
    """Anchor an explicit `--target` at the workdir; an absolute path is honoured."""
    path = Path(target).expanduser()
    return path if path.is_absolute() else workdir / path


def implied_workdir(artifact: Path, rel: str | None) -> Path | None:
    """The workdir an explicit `--target` implies — the directory the machine's declared
    `artifact:` hangs off, so `--target {vault}/plans/x/index.md` runs hooks in
    `{vault}/plans/x` the way `--workdir` would. None when the machine declares no
    artifact, its path is per-instance, or the target does not end with it."""
    if not rel or "{instance}" in rel:
        return None
    parts = PurePosixPath(rel).parts
    if len(parts) >= len(artifact.parts) or artifact.parts[-len(parts):] != parts:
        return None
    return artifact.parents[len(parts) - 1]


def _resolve_artifact(
    machine: StateMachine, workdir: Path, instance: str | None, target: str | None
) -> tuple[Path, str]:
    """Interpolate `{instance}` into the artifact path and anchor it at the workdir.
    Returns (absolute path, path as written relative to the workdir)."""
    if target is not None:
        resolved = resolve_target(target, workdir)
        return resolved, str(resolved)
    if not machine.artifact:
        _fail(
            f"state '{machine.name}' declares no `artifact:`; pass --target PATH"
        )
    rel = machine.artifact
    if "{instance}" in rel:
        if instance is None:
            _fail(
                f"state '{machine.name}' is per-instance "
                f"(artifact {machine.artifact}); pass --instance SLUG"
            )
        rel = rel.replace("{instance}", instance)
    elif instance is not None:
        _fail(
            f"state '{machine.name}' has no {{instance}} in its artifact path "
            f"({machine.artifact}); --instance is not accepted"
        )
    return workdir / rel, rel


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
    to_status: str = args.to_status
    instance: str | None = args.instance
    target: str | None = args.target
    if target is not None and instance is not None:
        _fail("--target and --instance are mutually exclusive")

    workdir_arg: str | None = args.workdir
    workdir = (
        Path(workdir_arg).expanduser().resolve()
        if workdir_arg is not None
        else Path.cwd()
    )
    if not workdir.is_dir():
        _fail(f"workdir not found: {workdir}")

    ctx = Context.assemble(start=workdir)
    pb = _resolve_playbook(ctx, args.playbook)
    state_name, machine = _resolve_state(pb, args.state)

    # Only an absolute target implies a workdir — a relative one is *defined* against
    # the workdir, so deriving one from it would re-anchor the path under itself.
    if workdir_arg is None and target is not None and Path(target).expanduser().is_absolute():
        implied = implied_workdir(Path(target).expanduser(), machine.artifact)
        if implied is not None and implied != workdir:
            if not implied.is_dir():
                _fail(f"workdir implied by --target not found: {implied}")
            # Re-assemble: the implied workdir may resolve a different project and a
            # different playbook root than cwd did.
            workdir = implied
            ctx = Context.assemble(start=workdir)
            pb = _resolve_playbook(ctx, args.playbook)
            state_name, machine = _resolve_state(pb, args.state)

    artifact, artifact_rel = _resolve_artifact(machine, workdir, instance, target)

    report: list[str] = []
    existing = artifact.exists()
    current = read_status(artifact)
    if current is None:
        if to_status != machine.initial:
            missing = (
                f"{artifact}: no frontmatter `status:` key"
                if existing
                else f"artifact {artifact_rel} does not exist"
            )
            _fail(
                f"{missing}; the only legal target is "
                f"the initial status {machine.initial!r}"
            )
        _bootstrap(artifact, machine.initial)
        from_status = NOT_STARTED
        report.append(
            f"bootstrapped {artifact_rel}" if existing else f"created {artifact_rel}"
        )
        report.append(f"{from_status} → {to_status}")
        report.append(format_frontmatter_line({"status": to_status}))
        hooks = [str(h) for h in machine.raw.get("hooks", {}).get("post", [])]
    else:
        from_status = current
        if from_status == to_status:
            report.append(f"{to_status} → {to_status} (idempotent)")
            hooks = [str(h) for h in machine.raw.get("hooks", {}).get("post", [])]
        else:
            edges = resolve_edges(from_status, machine.raw)
            allowed = {e.to for e in edges}
            if to_status not in allowed:
                allowed_list = ", ".join(sorted(allowed)) or "(none)"
                _fail(
                    f"cannot transition from {from_status!r} to {to_status!r} in state "
                    f"'{state_name}'; allowed targets: {allowed_list}"
                )
            report.append(f"{from_status} → {to_status}")
            hooks = resolve_hooks(from_status, to_status, machine.raw)

    project: Project | None = ctx.project
    # A `~/Claude` workdir carries no `.booping`, so the workdir-resolved context knows no
    # repo; a `cwd: repo` macro in a hook resolves it from the process cwd instead.
    hook_project = project if project is not None else Project.load_cwd_configured()
    playbook_dir = pb.path.parent.resolve()

    for hook in hooks:
        hook_name = hook.split()[0] if hook.split() else ""
        if hook_name == "frontmatter-update":
            rel, resolved = dispatch_frontmatter_update(
                hook,
                artifact,
                hook_project,
                file_base=workdir,
                instance=instance,
                config=ctx.config,
            )
            report.append(format_frontmatter_line(resolved, rel))
        elif hook_name == "script":
            name = _dispatch_script(
                hook, playbook_dir, pb.search_roots, workdir, artifact, instance
            )
            report.append(f"script {name}: ok")
        else:
            _fail(f"unknown hook: {hook_name!r}", code=2)

    scope = f"{state_name}/{instance}" if instance else state_name
    logger.log(
        vault=project.directory if project is not None else None,
        subcommand="playbook-transition",
        message=f"{pb.name} {scope} {from_status}→{to_status}",
    )

    print("\n".join(report))
