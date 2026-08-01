# Input — booping (Claude Code plugin)

Intake is confirmed: the framing below is the one the user signed off on, scope questions
answered and boundaries agreed. Map the blast radius of this work in the attached repository.

The repository sits on disk in the current working directory, together with the run workdir —
the plan directory `plans/{slug}/`, holding the run's `index.md` and its `plan.md`. None of it
is inlined here and none of it is summarised: read what the work touches before writing
anything, and follow the references out of the files you are pointed at first.

## Context files

<file path="plans/20260731-sprints-report-script/index.md">
---
status: researching
---
# Sprints report as a playbook script

## Framing

### Request

> The sprints.md snapshot is booping's job today, but it is not framework behaviour — it is one
> particular workflow's report. I want it to become a playbook-local script under the groom
> playbook's `_scripts/`, fired as a `script` hook, and the built-in render-sprints to go away
> from the core. Playbook-specific behaviour should live in playbooks; the core stays a pure
> playbook framework.

### Restated problem

`render-sprints` is wired into the core three times over: as a public CLI subcommand, as a
dispatch branch in the plan-transition hook runner, and as a name in the plan lifecycle's
automatic post-hook list. That makes a report about one workflow's plans a fixed cost of the
framework, and every consumer of the framework inherits it whether or not that workflow is the
one they run. The work is to move the behaviour to where it belongs — a playbook-owned script —
and take the core's copy out, without leaving the snapshot unrendered for anyone who relies on
it today.

### Task type

`refactoring` — the behaviour the user sees (a refreshed snapshot after a status move) is meant
to survive unchanged; what moves is who owns it and where it is invoked from. Not a feature (no
new capability is asked for) and not a bug (nothing is misbehaving).

### Scope boundaries

**In scope**

- the core's ownership of the snapshot: the CLI subcommand, the hook-runner dispatch, and the
  post-hook declaration in the lifecycle config
- the playbook-side replacement: a script under the groom playbook's `_scripts/`, wired as a
  `script` hook on the machine's edges
- every place in the plugin that tells a reader or an agent to call the core command
- keeping the snapshot rendered for a run that goes through the playbook

**Out of scope**

- `/develop` — its briefing flow, its milestone loop and the moves it makes stay exactly as they
  are; nothing in this work is allowed to change that skill

### Web research

Requested — the user asked for current practice on how other tools render and refresh a report like this before the design is settled.

### Scope challenge

- [x] Does the snapshot have to keep working for plans moved outside the groom playbook? —
      answered: no guarantee is owed to a run that never enters the playbook; the report is the
      playbook's from this point on.
- [x] Does the template itself move with the behaviour, or stay where it is? — answered: it moves
      with the behaviour; a report and its template belong to the same owner.
- [x] Any surface you already know this must not pull in? — answered: `/develop`, see above.
</file>

<file path="CLAUDE.md">
# booping plugin — project guide

Claude Code plugin that grooms and executes plans across user projects. Plans live in the
per-project vault — `~/Claude/{project}/` by default, or a repo-local directory via the
`.booping` marker's `vault_path:` key; skills, agents, templates and config live in this repo.

## Layout

- `booping-python/` — uv Python project containing the `booping` CLI. Source under
  `booping-python/src/booping/`; tests under `booping-python/tests/`.
- `bin/booping` — shell wrapper; exec's `uv run --project booping-python booping "$@"`.
- `bin/booping-create-project` — standalone uv inline script; scaffolds the vault directories and
  the `.booping` marker. Out of scope for the runtime rendering pipeline.
- `src/config.yaml` — single source of truth for structured data rendered into skills at runtime
  (plan statuses and transitions, task types, per-skill agents). Project-overridable.
- `src/files/{rel}.j2` — build-time templates for every committed `skills/{name}/SKILL.md` and
  `agents/{name}.md`. Rendered by `just build`.
- `src/templates/skills/{name}.md.j2` — runtime skill templates, rendered at skill-load time.
- `src/templates/_partials/_*.j2` — reusable fragments included by skills and agents.
- `skills/{name}/SKILL.md`, `agents/{name}.md` — build artefacts.
- `playbooks/{name}/` — core playbooks shipped with the plugin.

## Config override tiers

Three tiers deep-merge over `src/config.yaml` in order **core → global → project**: the file in
this repo, then `${XDG_CONFIG_HOME:-~/.config}/booping/config.yaml`, then
`{vault}/config.yaml`. Later tiers win; missing keys fall through; lists replace wholesale. A
project that sets a list key therefore replaces the core's list rather than extending it.

## Principles

- **Minimum useful context**: show only information the skill needs to do its job.
- **Schema over prose**: structured data lives in `src/config.yaml`. If a value is there, the
  skill body must not also describe it in prose — render from config.
- **Less prose, less drift**: every extra sentence in a skill adds tension between what is
  written and what the model does.

## Editing conventions

- Edits to `src/templates/skills/*.md.j2`, `src/templates/agents/*.md.j2` and
  `src/templates/_partials/*.j2` are **live** — rendered at skill-load time, no rebuild needed.
- Edits to `src/files/**/*.j2` require `just build` to materialize into the on-disk
  `skills/{name}/SKILL.md` and `agents/{name}.md`. `git diff -- skills/ agents/` after
  `just build` is the drift signal.
- `skills/{name}/SKILL.md` and `agents/{name}.md` are **build artefacts** — never hand-edit.
  Edit `src/files/{rel}.j2` and run `just build`.
- The plugin code itself stays stack-agnostic — no Python/Django/JS specifics inside skills.
- Conventional commits with scope: `feat(booping): ...`, `fix(install): ...`.

## Playbooks

A playbook's `playbook.yaml` carries `graph:` plus optional `states:` — named state machines
whose transitions declare `gates` and `hooks`. Hook vocabulary: `frontmatter-update {key}={val}`
and `script {name}` → `{playbook-dir}/_scripts/{name}`, run with cwd set to the run workdir and
`BOOPING_ARTIFACT` / `BOOPING_WORKDIR` / `BOOPING_INSTANCE` in the environment; a non-zero exit
aborts the transition. `booping playbook-transition` is the only writer of playbook run state.

## Commands

- `just build` — render every `src/files/**/*.j2` to its plugin-root destination.
- `just lint`, `just typecheck`, `just test` — ruff, basedpyright, pytest against
  `booping-python/`.
</file>

<file path="src/config.yaml">
tasks:
  - type: feature
    description: A new user-facing capability with a business goal.
    doc_uri: docs/task_feature.md
  - type: bug
    description: Behaviour diverges from what is expected.
    doc_uri: docs/task_bug.md
  - type: refactoring
    description: Structure changes, behaviour does not.
    doc_uri: docs/task_refactoring.md

sprint:
  default_threshold_sp: 21
  redecompose_threshold: 8
  group_threshold: 2

plan:
  statuses:
    in-spec:
      desc: Being groomed.
      owner: groom
      terminal: false
      transitions:
        - to: awaiting-plan-review
          skill: groom
          when: the draft is finished and verified against the template checklist
          hooks:
            - frontmatter-update commit=@head
    awaiting-plan-review:
      desc: Waiting for the user to approve the plan.
      owner: groom
      terminal: false
      transitions:
        - to: ready-for-dev
          skill: groom
          when: the user approves the plan
          gates:
            - every milestone carries a Definition of Done
          hooks:
            - frontmatter-update planned=@now
        - to: in-spec
          skill: groom
          when: the user asks for changes
    ready-for-dev:
      desc: Queued for implementation.
      owner: develop
      terminal: false
      transitions:
        - to: in-progress
          skill: develop
          when: the first milestone group is briefed
          hooks:
            - frontmatter-update started=@now commit=@head
    in-progress:
      desc: Being implemented.
      owner: develop
      terminal: false
      transitions:
        - to: awaiting-retro
          skill: develop
          when: every milestone is verified
          hooks:
            - frontmatter-update completed=@now

  # Run after every edge's own hooks, on every move, for every status.
  hooks:
    post:
      - render-sprints
      - vault-commit
</file>

<file path="booping-python/src/booping/cli.py">
from __future__ import annotations

import argparse

from booping.commands import build as build_cmd
from booping.commands import config_get as config_get_cmd
from booping.commands import frontmatter_update as frontmatter_update_cmd
from booping.commands import playbook_state as playbook_state_cmd
from booping.commands import playbook_transition as playbook_transition_cmd
from booping.commands import render as render_cmd
from booping.commands import render_playbook as render_playbook_cmd
from booping.commands import render_sprints as render_sprints_cmd
from booping.commands import transition as transition_cmd
from booping.commands import vault_commit as vault_commit_cmd


def main() -> None:
    parser = argparse.ArgumentParser(prog="booping")
    sub = parser.add_subparsers(dest="command", required=True)

    render_cmd.add_parser(sub)
    render_sprints_cmd.add_parser(sub)
    render_playbook_cmd.add_parser(sub)
    playbook_state_cmd.add_parser(sub)
    playbook_transition_cmd.add_parser(sub)
    transition_cmd.add_parser(sub)
    frontmatter_update_cmd.add_parser(sub)
    vault_commit_cmd.add_parser(sub)
    config_get_cmd.add_parser(sub)
    build_cmd.add_parser(sub)

    args = parser.parse_args()
    args.func(args)
</file>

<file path="booping-python/src/booping/commands/render_sprints.py">
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from booping import logger
from booping.context import Context
from booping.rendering import get_plugin_root, render

TEMPLATE = "src/templates/sprints.md.j2"


def add_parser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "render-sprints", help="Render sprints.md from vault plans"
    )
    p.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output path; '-' writes to stdout. Defaults to the vault's sprints.md.",
    )
    p.set_defaults(func=_run)


def do_render_sprints(ctx: Context, output: Path | None) -> tuple[int, Path]:
    """Render the snapshot. Shared with the transition hook runner."""
    template = get_plugin_root() / TEMPLATE
    text = render(template, ctx)
    if ctx.project is None:
        print("error: no booping project attached", file=sys.stderr)
        sys.exit(1)
    target = output if output is not None else ctx.project.vault / "sprints.md"
    target.write_text(text, encoding="utf-8")
    return len(ctx.plans), target


def _run(args: argparse.Namespace) -> None:
    ctx = Context.assemble(start=Path.cwd())
    if args.output == "-":
        sys.stdout.write(render(get_plugin_root() / TEMPLATE, ctx))
        return
    count, target = do_render_sprints(
        ctx, Path(args.output) if args.output else None
    )
    logger.log(ctx, subcommand="render-sprints", detail=f"{count} plans -> {target}")
</file>

<file path="booping-python/src/booping/commands/transition.py">
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from booping.commands.render_sprints import do_render_sprints
from booping.commands.vault_commit import do_vault_commit
from booping.context import Context
from booping.context._yaml import update_frontmatter
from booping.context.lifecycle import resolve_edges, resolve_hooks


def add_parser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "transition", help="Transition a plan to a new status, running all resolved hooks"
    )
    p.add_argument("to_status", metavar="to")
    p.add_argument("plan", type=Path)
    p.add_argument("--also", action="append", type=Path, default=None)
    p.set_defaults(func=_run)


def _run_hooks(ctx: Context, hooks: list[str], plan: Path, to_status: str) -> list[str]:
    report: list[str] = []
    for hook in hooks:
        tokens = hook.split()
        name = tokens[0]
        if name == "frontmatter-update":
            resolved = update_frontmatter(plan, tokens[1:])
            report.append("frontmatter: " + " ".join(resolved))
        elif name == "render-sprints":
            count, path = do_render_sprints(ctx, None)
            report.append(f"render-sprints: {count} plans → {path}")
        elif name == "vault-commit":
            sha = do_vault_commit(ctx, to_status, plan)
            report.append(f"vault-commit: {sha}")
        else:
            print(f"error: unknown hook: {name}", file=sys.stderr)
            sys.exit(2)
    return report


def _run(args: argparse.Namespace) -> None:
    ctx = Context.assemble(start=args.plan.parent)
    edges = resolve_edges(ctx.config["plan"], _current_status(args.plan))
    edge = _pick(edges, args.to_status)
    hooks = resolve_hooks(ctx.config["plan"], edge)
    # every move ends with the automatic post hooks, whatever the edge declared
    hooks += ctx.config["plan"]["hooks"]["post"]
    report = _run_hooks(ctx, hooks, args.plan, args.to_status)
    print("\n".join(report))
</file>

<file path="booping-python/src/booping/commands/playbook_transition.py">
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def _run_script_hook(
    playbook_dir: Path, name: str, workdir: Path, artifact: Path, instance: str | None
) -> str:
    script = playbook_dir / "_scripts" / name
    if not script.is_file():
        _fail(f"script hook {name!r} not found: {script}", code=2)
    if not os.access(script, os.X_OK):
        _fail(f"script hook {name!r} is not executable: {script}", code=2)

    env = dict(os.environ)
    env["BOOPING_ARTIFACT"] = str(artifact)
    env["BOOPING_INSTANCE"] = instance or ""
    env["BOOPING_WORKDIR"] = str(workdir)

    result = subprocess.run(
        [str(script)], cwd=str(workdir), env=env, capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        if result.stderr:
            sys.stderr.write(result.stderr)
        _fail(f"script hook {name!r} exited {result.returncode}", code=2)
    return name
</file>

<file path="src/templates/sprints.md.j2">
<!-- Snapshot generated by booping render-sprints; regenerated by /chat on each orient. Do not hand-edit. -->
| status | sp | title | summary | created | planned | completed | retro | path |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
{% set with_date = context.plans | selectattr('created') | sort(attribute='created', reverse=True) | list -%}
{% set without_date = context.plans | rejectattr('created') | list -%}
{% for plan in with_date + without_date -%}
| {{ plan.status }} | {{ plan.sp if plan.sp is not none else "" }} | {{ plan.title }} | {{ plan.summary }} | {{ plan.created if plan.created is not none else "" }} | {{ plan.planned if plan.planned is not none else "" }} | {{ plan.completed if plan.completed is not none else "" }} | {{ plan.retro if plan.retro is not none else "" }} | plans/{{ plan.path.name }} |
{% endfor -%}
</file>

<file path="src/templates/skills/chat.md.j2">
# Chat

{% include "_partials/_project_context.j2" %}

## Preflight

1. Refresh the plan snapshot so the summary you open with is current:

   ```
   booping render-sprints
   ```

2. Read the refreshed `sprints.md` and open the session with a one-paragraph vault status.

## Chores

Frontmatter tweaks, status flips and inline edits are yours as long as they do not need a
heavier skill. A status flip goes through `booping transition`, never a hand edit — the command
owns the snapshot refresh and the vault commit that follow it.
</file>

<file path="src/templates/skills/develop.md.j2">
# Develop

{% include "_partials/_project_context.j2" %}

{{ available_agents.render("develop") }}

## Phase 1 — Intake

Claim a plan from the queue, re-read it end to end with the user, and confirm it is still valid
against the current HEAD before briefing anything.

## Phase 3 — Milestone loop

Brief one milestone group per agent. When the group's Definition of Done is verified, move the
plan on with `booping transition`. The command carries every mechanical mutation the edge
declares, and the plan snapshot the vault shows (`sprints.md`) refreshes on that move — you
never render it yourself and never hand-edit it.

## Phase 4 — Final verification

Run the project's own lint / typecheck / test tooling once, alongside the plan's own Verify
commands, before the final move.
</file>

<file path="src/templates/_partials/_plan_transitions.j2">
{% macro render(skill) -%}
| From | To | When | Gates | On exit (auto) |
| --- | --- | --- | --- | --- |
{% for status, spec in config.plan.statuses.items() -%}
{% for edge in spec.transitions if edge.skill == skill -%}
| {{ status }} | {{ edge.to }} | {{ edge.when }} | {{ edge.gates | join("; ") }} | {{ summarise(edge.hooks) }} |
{% endfor -%}
{% endfor -%}
{%- endmacro %}

{% macro summarise(hooks) -%}
{%- for hook in hooks or [] -%}
{%- set tokens = hook.split() -%}
{%- if tokens[0] == "frontmatter-update" -%}
sets {{ tokens[1:] | join(", ") }}
{%- elif tokens[0] in ("render-sprints", "vault-commit") -%}
{# automatic post hooks — never shown, they fire on every move #}
{%- endif -%}
{%- endfor -%}
{%- endmacro %}
</file>

<file path="playbooks/groom/playbook.yaml">
state: run
graph:
  intake: []
  design: [intake]
  draft-plan: [design]
  present: [draft-plan]

states:
  run:
    artifact: index.md
    initial: in-spec
    statuses:
      in-spec:
        transitions:
          - to: awaiting-plan-review
            when: the draft is finished and verified against the template checklist
            hooks:
              - frontmatter-update commit=@head
              - script mirror-plan-status
      awaiting-plan-review:
        transitions:
          - to: ready-for-dev
            when: the user approves the plan
            hooks:
              - frontmatter-update planned=@now
              - script mirror-plan-status
          - to: in-spec
            when: the user asks for changes
            hooks:
              - script mirror-plan-status
      ready-for-dev:
        terminal: true
</file>

<file path="playbooks/groom/_scripts/mirror-plan-status.sh">
#!/usr/bin/env bash
# Mirror the run's status onto the plan file the run is grooming.
# Fired as `script mirror-plan-status` from every edge of the `run` machine.
set -euo pipefail

: "${BOOPING_WORKDIR:?script hooks always receive the run workdir}"
: "${BOOPING_ARTIFACT:?script hooks always receive the machine's artifact}"

slug="$(basename "${BOOPING_WORKDIR}")"
status="$(sed -n 's/^status: //p' "${BOOPING_ARTIFACT}" | head -1)"

# The workdir is the plan directory {vault}/plans/{slug}, so the vault is two levels up.
vault="$(cd "${BOOPING_WORKDIR}/../.." && pwd)"

booping frontmatter-update "${vault}/plans/${slug}/plan.md" "status=${status}"
</file>

<file path="playbooks/user-stories/playbook.yaml">
state: main
graph:
  reshake: []
  build-index: [reshake]
  story-map: [build-index]

states:
  main:
    artifact: index.md
    initial: reshaking
    statuses:
      reshaking:
        transitions:
          - to: indexing
            when: the capability inventory is written
            hooks:
              - script stamp-reviewed
      indexing:
        transitions:
          - to: mapping
            when: the user confirms the index
            hooks:
              - frontmatter-update confirmed=@today
              - script stamp-reviewed
      mapping:
        terminal: true
</file>

<file path="playbooks/user-stories/_scripts/stamp-reviewed.sh">
#!/usr/bin/env bash
# Stamp the run's index document with the moment the user confirmed it.
# Fired as `script stamp-reviewed` from the main machine's edges.
set -euo pipefail

: "${BOOPING_WORKDIR:?script hooks always receive the run workdir}"
: "${BOOPING_ARTIFACT:?script hooks always receive the machine's artifact}"

index="${BOOPING_WORKDIR}/specs/features/index.md"
[[ -f "${index}" ]] || exit 0

stamp="$(date -u '+%Y%m%d %H:%M')"
booping frontmatter-update "${index}" "reviewed_at=${stamp}"
</file>

<file path="bin/booping-create-project">
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml"]
# ///
"""Scaffold a booping vault and attach it to the current repo.

Standalone by design: it runs before the plugin's own project exists, so it must not import
anything from booping-python. It shells out to `booping config-get home_dir` for the one value
it cannot resolve on its own.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

VAULT_DIRS = ("plans", "lessons", "notes", "_booping", "plan_templates")


def resolve_home_dir() -> Path:
    result = subprocess.run(
        ["booping", "config-get", "home_dir"], capture_output=True, text=True, check=False
    )
    if result.returncode == 0:
        return Path(result.stdout.strip()).expanduser()
    return Path.home() / "Claude"


def main() -> None:
    name = sys.argv[1]
    vault = resolve_home_dir() / name
    for d in VAULT_DIRS:
        (vault / d).mkdir(parents=True, exist_ok=True)
    Path(".booping").write_text(f"project: {name}\n", encoding="utf-8")
</file>

<file path="booping-python/tests/test_transition.py">
from __future__ import annotations

from booping.commands.transition import _run_hooks


def test_post_hooks_run_on_every_edge(tmp_vault, capsys):
    """Every move ends with render-sprints + vault-commit, whatever the edge declared."""
    ctx = tmp_vault.context()
    report = _run_hooks(ctx, ctx.config["plan"]["hooks"]["post"], tmp_vault.plan, "ready-for-dev")
    assert any(line.startswith("render-sprints:") for line in report)
    assert any(line.startswith("vault-commit:") for line in report)


def test_sprints_snapshot_lists_every_plan(tmp_vault):
    ctx = tmp_vault.context()
    text = (tmp_vault.vault / "sprints.md").read_text()
    assert text.count("\n") == len(ctx.plans) + 3


def test_unknown_hook_aborts(tmp_vault):
    ctx = tmp_vault.context()
    try:
        _run_hooks(ctx, ["render-sprint"], tmp_vault.plan, "done")
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError("an unknown hook name must abort the move")
</file>
