---
type: adr
title: Bodies render at skill load, with no build stage
summary: Skill and agent bodies are rendered from templates at load time with full project context; the generated-file build stage is retired.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-17
status: accepted
rules: [rule/0017, rule/0029]
values: [value/0003, value/0005]
sources: [CLAUDE.md, vault/retrospectives/20260425-migrate-retro-skill-to-template-pipeline.md, vault/researches/20260802-01-31_framework-cli-extraction-research.md]
---

## Context

Skill bodies were first hand-written `SKILL.md` files, then generated from
`src/templates/` into committed `SKILL.md` files. A `build` subcommand with
`src/files/` templates and a separate `src/config_files.yaml` produced the
plugin-packaging files. The framework research found that `config_files.yaml`
carried only `effort:` and could fold into normal config, "killing the fourth config
file and possibly the whole build step", and classed the build as plugin packaging
rather than framework. What a body needs — the merged config tiers, the vault,
rules, the playbook set — belongs to one project and is known only when the skill
is loaded in it.

## Decision

One rendering stage, at runtime. `skills/<name>/SKILL.md` and `agents/<name>.md`
are hand-authored thin shells: frontmatter (with `effort:` inlined) plus one
`booping render src/templates/…` line that renders the body at load time with the
full project context. Edits to `src/templates/` are live; nothing in the repo is
rebuilt. The build stage and `config_files.yaml` are gone.

## Alternatives

| Option | Status | Complexity | Reversibility | Verdict |
|---|---|---|---|---|
| [Render at load](#render-at-load) | accepted | medium | medium | Project context available; edits live |
| [Generated files from a build](#generated-files-from-a-build) | rejected | medium | high | A rebuild per edit; no per-project context |
| [Hand-written full bodies](#hand-written-full-bodies) | rejected | low | high | Repeats shared fragments and config literals |

### Render at load

A thin shell calls the renderer when Claude Code loads the skill or agent.

- **Pros:** the body sees the merged config, vault and rules of the project it
  runs in; template edits take effect on the next load.
- **Cons:** every load runs the CLI; other costs are not named in the source.
- **Complexity:** medium.
- **Reversibility:** medium.

### Generated files from a build

A build step renders templates into committed files.

- **Pros:** the rendered body is visible in the repo.
- **Cons:** a rebuild after every edit; a fourth config file; the output cannot carry
  one project's config or rules.
- **Complexity:** medium.
- **Reversibility:** high.

### Hand-written full bodies

Each `SKILL.md` carries its whole body.

- **Pros:** no tooling.
- **Cons:** structured data from config is restated in prose and drifts; shared
  fragments repeat across skills.
- **Complexity:** low.
- **Reversibility:** high.

## Consequences

- Each playbook commits its rendered report (`_reports/output.md`), and
  `just snapshots` diffs it against a fresh render.
- Graph and render problems surface as in-band STOP or Note notices at exit 0,
  never as crashes.
