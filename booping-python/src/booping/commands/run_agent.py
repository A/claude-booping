"""`booping run-agent <id>` — exec a cli-typed agent from `skills.*.agents.<id>`.

Resolution: walk `context.config["skills"]` in iteration order; the first skill
whose `agents` mapping contains `<id>` wins. Uniqueness across skills is not
enforced.

Hard-errors (exit 2, one-line stderr) on:
- unknown id
- entry with `internal: true`
- entry with `type` missing or `type: agent` (native agents are dispatched via
  Claude Code's `Agent` tool, not this CLI)

Briefing source: `--briefing-file PATH` if given, else stdin. Refuses to read a
TTY stdin (prevents indefinite hang in interactive shells).

Extension: `<context.project.directory>/_booping/agent_<id>.md`, prepended to
the briefing with `\n\n---\n\n` as separator. Missing or empty file → briefing
alone.

Command rendering: the entry's `command` is a Jinja2 template with one variable
`prompt = shlex.quote(final_prompt)`. When the template body has no
`{{ prompt }}` placeholder, the quoted prompt is appended as the last positional
arg. Executed via `subprocess.run(shlex.split(rendered), shell=False)` —
stdout/stderr inherit the parent's, exit code propagates.
"""

from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, cast

from jinja2 import Environment

from booping import logging as booping_logging
from booping.context import Context


def add_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "run-agent",
        help="Exec a cli-typed agent from skills.*.agents.<id>",
        description=(
            "Resolve <id> across all skills.*.agents (first match wins), compose the "
            "extension at <vault>/_booping/agent_<id>.md with the briefing read from "
            "stdin or --briefing-file, and exec the configured command."
        ),
    )
    p.add_argument("id", help="agent id declared under skills.*.agents.<id>")
    p.add_argument(
        "--briefing-file",
        type=Path,
        default=None,
        help="Read briefing from this file instead of stdin",
    )
    p.set_defaults(func=_run)


def die(msg: str) -> None:
    sys.stderr.write(msg.rstrip() + "\n")
    sys.exit(2)


def resolve_agent(
    cfg: dict[str, Any], agent_id: str
) -> tuple[str, dict[str, Any]] | None:
    """Return (skill_name, entry_dict) for the first skill whose `agents` contains agent_id."""
    skills_any: Any = cfg.get("skills", {})
    if not isinstance(skills_any, dict):
        return None
    skills = cast(dict[str, Any], skills_any)
    for skill_name, block in skills.items():
        if not isinstance(block, dict):
            continue
        block_d = cast(dict[str, Any], block)
        agents_any: Any = block_d.get("agents", {})
        if not isinstance(agents_any, dict):
            continue
        agents = cast(dict[str, Any], agents_any)
        if agent_id in agents:
            entry = agents[agent_id]
            if isinstance(entry, dict):
                return (str(skill_name), cast(dict[str, Any], entry))
    return None


def stdin_is_tty() -> bool:
    """Indirection so tests can monkeypatch."""
    return sys.stdin.isatty()


def read_briefing(briefing_file: Path | None) -> str:
    if briefing_file is not None:
        return briefing_file.read_text()
    if stdin_is_tty():
        die("stdin is a TTY; pipe briefing or pass --briefing-file PATH")
    return sys.stdin.read()


def read_extension(vault_dir: Path | None, agent_id: str) -> str:
    if vault_dir is None:
        return ""
    ext_path = vault_dir / "_booping" / f"agent_{agent_id}.md"
    if not ext_path.is_file():
        return ""
    return ext_path.read_text()


OUTPUT_GUIDE = (
    "# Output contract (booping)\n"
    "Your final reply MUST contain ONLY the list of files you changed, one per "
    "line, paths relative to the repo root. No prose, no preamble, no markdown, "
    "no fenced code blocks, no commentary. If you changed nothing, reply with an "
    "empty string.\n"
)


def compose_prompt(extension: str, briefing: str) -> str:
    body = briefing if extension.strip() == "" else extension + "\n\n---\n\n" + briefing
    return OUTPUT_GUIDE + "\n---\n\n" + body


def render_command(command_template: str, final_prompt: str) -> list[str]:
    quoted = shlex.quote(final_prompt)
    env = Environment(autoescape=False, keep_trailing_newline=True)
    rendered = env.from_string(command_template).render(prompt=quoted)
    argv = shlex.split(rendered)
    if "{{ prompt }}" not in command_template and "{{prompt}}" not in command_template:
        argv.append(final_prompt)
    return argv


def _run(args: argparse.Namespace) -> None:
    run_with_context(args, Context.assemble())


def run_with_context(args: argparse.Namespace, ctx: Context) -> None:
    agent_id: str = args.id

    resolved = resolve_agent(ctx.config, agent_id)
    if resolved is None:
        die(f"agent '{agent_id}' not found in any skill's agents block")
        return

    _skill_name, entry = resolved

    if entry.get("internal") is True:
        die(f"agent '{agent_id}' is internal; use the Agent tool, not booping run-agent")
        return

    entry_type = entry.get("type", "agent")
    if entry_type != "cli":
        die(f"agent '{agent_id}' has type '{entry_type}'; only cli agents are runnable here")
        return

    command_template = entry.get("command")
    if not isinstance(command_template, str) or not command_template:
        die(f"agent '{agent_id}' has no `command`")
        return

    briefing = read_briefing(args.briefing_file)
    vault_dir = ctx.project.directory if ctx.project is not None else None
    extension = read_extension(vault_dir, agent_id)
    final_prompt = compose_prompt(extension, briefing)

    booping_logging.log_invocation(
        vault_dir, "run-agent", f"{agent_id}: `{command_template}`"
    )

    argv = render_command(command_template, final_prompt)
    repo_dir = ctx.project.repo_directory if ctx.project is not None else None
    before = {(p, _git_porcelain_code(line)) for line, p in _porcelain_pairs(repo_dir)}
    start = time.monotonic()
    child = subprocess.run(  # noqa: S603
        argv, check=False, shell=False, capture_output=True, text=True
    )
    elapsed = time.monotonic() - start

    sys.stdout.write(child.stdout)
    sys.stderr.write(child.stderr)

    after = {(p, _git_porcelain_code(line)) for line, p in _porcelain_pairs(repo_dir)}
    delta_paths = sorted({p for p, _ in (before ^ after)})
    if delta_paths:
        sys.stdout.write("\n--- changed files ---\n")
        for p in delta_paths:
            sys.stdout.write(p + "\n")

    out_snip = repr(child.stdout[:100])
    err_full = repr(child.stderr)
    booping_logging.log_invocation(
        vault_dir,
        "run-agent",
        (
            f"{agent_id}: exit={child.returncode} elapsed={elapsed:.2f}s "
            f"stdout[0:100]={out_snip} stderr={err_full}"
        ),
    )
    sys.exit(child.returncode)


def _git_porcelain_code(line: str) -> str:
    return line[:2]


def _porcelain_pairs(repo_dir: Path | None) -> list[tuple[str, str]]:
    """Return list of (raw_line, path) tuples from `git status --porcelain`."""
    if repo_dir is None:
        return []
    try:
        r = subprocess.run(  # noqa: S603
            ["git", "status", "--porcelain"],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return []
    if r.returncode != 0:
        return []
    pairs: list[tuple[str, str]] = []
    for line in r.stdout.splitlines():
        if len(line) < 4:
            continue
        path = line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        pairs.append((line, path))
    return pairs
