---
name: docs
title: Docs
summary: Keep the project's documentation matched to what the repo actually is —
  establish a stable spec set, detect delivered work not yet documented, 
  research it against that spec set, and write every affected surface in the 
  tone and depth its audience needs.
trigger: keep the project's documentation matched to what shipped; catch the 
  docs up with recent development; refresh README, docs site, CHANGELOG or 
  plugin-internal docs after a batch of work
jinja: true
inline_steps: true
requires_project: true
reviewed_at: 2026-08-08 13:46
---
A run ends with the project's documentation surfaces matched to the current state of the repo:
the spec set current, a reviewed run record listing what changed and where it landed, and every
affected surface rewritten in the tone and depth its audience needs. Steps already satisfied by
a current file are skipped rather than redone.

{% from "_partials/timestamps.md" import human_ts -%}
## Guidance

- Date & time: {{ human_ts }}
- The run workdir is `{vault}/docs/`; run records live under its `_runs/` subdirectory, never
  loose in `docs/` beside real documentation. Every `booping playbook-state` / `booping
  playbook-transition` call passes `--workdir {vault}/docs --target
  _runs/{YYYYMMDDHHmm}-{title}.md`, since the machine declares no `artifact:`.
- The spec set — `_specs/index.md` (briefing), `_specs/roles.md`, `_specs/targets.md`,
  `_specs/features.md`, `_specs/glossary.md` (canonical terms every spec file and destination
  uses) — persists across runs and is only ever refreshed, never rebuilt from scratch once
  established. `_specs/documented.md` is the ledger of already-documented work;
  `research` reads it to surface only the delivered items still missing from it.
- The spec set is **both this run's context and one of its targets**. It is compact documentation
  on how to document this project, and its audience is Claude itself — every later step resolves
  "what does this project ship, for whom, at what depth, on which surface" against it, so a stale
  spec file mis-aims every destination downstream. It carries a row in `_specs/targets.md` like
  any other surface, written vault-relative as `docs/_specs/`, and `sync-specs` keeps it current
  from the confirmed change table before `targeting` reads it. Load it for context at every step
  that resolves audience or destination; never let a run write a destination document from a spec
  set the same run has already found stale.
- Source files are never edited: every destination the `update` loop writes is markdown.
  Code-level documentation stays with `develop`.
- Roles drive tone in both `research` and `write` — a business-facing surface never gets
  implementation detail a technical one would carry.

## The `update` loop

`update` repeats once per row of the confirmed targeting plan — one instance per destination
document, `write` → `compact` → `verify` — and instances may run in parallel, but no two ever
touch the same file. The loop carries no state machine of its own: per-row progress (pending →
written → compacted → verified) is a column on the targeting-plan table in the run record body,
resumed from `updating` the same way `develop` resumes its milestone loop from plan-body
checkboxes, since a destination document cannot carry frontmatter.

## Runner-held state

Every step reports back what the runner must carry forward, never the raw reading behind it:
file paths written or to write next, the confirmed change table, the targeting plan, and the
changed/updated set. Heavy reads — the delivered-work sweep in `research`, the sub-agent writes
in the spec-set and `update` waves — stay in their sub-agent; only the summary returns.

Eval runs are proposed, never launched — the user triggers them.

{% include "_partials/playbook_shared_instructions.md" %}
