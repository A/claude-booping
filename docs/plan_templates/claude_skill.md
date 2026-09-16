---
name: claude-skill
description: Authoring or refactoring a Claude Code skill — skill bodies, partials, config schema, rendered outputs, skill-level agents.
---

# Plan Body

## Context

What skill (or skill family) this plan affects. Current behavior, the gap or wrinkle, what changes after.

## Decisions

- **{Topic}**: {decision} — {why}

Typical topics: what moves to config vs stays in skill body, which partials to extract, what the skill's phases / craft become, what lazy-loads vs embeds.

## Architecture

How the skill interacts with other skills via shared config (statuses, agents, task types). Diagram the skill's load-time inputs (config, partials, `!`commands``, lazy docs) if non-trivial.

## Milestones

Generated table — one row per milestone file, projected with `core.plans.milestones.table_columns` by `booping query`. Derived output: no hand-written rows, no milestone bodies in this file.

## Milestone files

One file per milestone directory under the plan directory's `milestones/`, named after that directory and seeded by `booping scaffold core.groom_playbook.milestone_scaffold` — the seed owns the file's frontmatter keys and its required headings. Write the body into that skeleton:

- **Goal** — one sentence directly under the H1: the observable change in the rendered skill or shared config.
- **Scope** — the templates, partials, config keys and rendered artefacts this milestone touches, and which other skills read the same config.
- `## Tasks` — one row per task:

  | Task | Description | Files | SP | Status |
  |------|-------------|-------|----|--------|
  | 1.1 | ... | `src/templates/skills/{name}.md.j2`, `src/config.yaml` | 2 | pending |

- `## Definition of Done` — one `### Task {n}.{m}` block per task, checkbox bullets only: rendered diff matches the intended shape, no hardcoded values that duplicate config, lazy-load links resolve.
- `## References` — where such files exist, 1–3 existing templates, partials or rendered reports whose shape this milestone copies, by path, plus the path of any config block it must not go looking for.
- `## Verify` — render and sanity check (e.g. `bin/booping render src/templates/skills/{name}.md.j2` and review output) — the rebuild plus the surfaces this milestone touched. Whole-repo gates (full test suite, repo-wide lint/typecheck, an aggregate `ci` target) run once in `index.md`'s Final Verification, never per milestone.

## Final Verification

- [ ] `bin/booping render src/templates/skills/<name>.md.j2` produces clean output (for skill/agent body changes).
- [ ] Rendered skill body reviewed (no stale state names, no prose that duplicates rendered tables, no `{{placeholder}}` leaks).
- [ ] Targeted lessons (`skill:{name}`, `agent:{id}`) still inline correctly into the rendered body.

## Out of scope

Explicit exclusions — e.g. "the `playbook` skill body only; its thin shell unchanged", "no plan-template changes".

## CLAUDE.md impact

Name sections to update, or state "No CLAUDE.md changes required — {justification}".

---

# Quality Checklist

## Frontmatter

- [ ] `title` matches the plan's H1 and `type` is the task type chosen at intake.
- [ ] `sp` equals the sum of the milestone files' `sp`.

## Content

- [ ] Context names the behavior change visible in rendered skills, not "refactor internals".
- [ ] DoD bullets are verifiable by reading the rendered output or a diff.
- [ ] Every task lists exact template / partial / config paths.
- [ ] Every task DoD uses checkboxes, not prose.
- [ ] Every milestone is a file in `milestones/` carrying its own goal, tasks, DoD and Verify — no milestone body in `index.md`.
- [ ] `index.md`'s milestone table has one row per milestone file and matches their frontmatter.
- [ ] Every milestone file's `## Verify` includes a rebuild and stays scoped to the surfaces that milestone touched — no whole-repo gate (full suite, repo-wide lint/typecheck, aggregate `ci` target); those belong to `index.md`'s Final Verification.
- [ ] Every milestone file's `## References` names 1–3 existing files to copy the shape of where such files exist, or states that none applies.
- [ ] No milestone's Scope or Tasks offers two ways to do the same thing ("by hand or via X").
- [ ] No milestone asks for a deliverable in the worker's report — each is named as a path plus "Create" or "Append to", relative to the repo root or the plan directory.
- [ ] Each milestone file executable from a fresh session with only it and `index.md` as context.

## Skill-design hygiene

- [ ] Structured facts (statuses, transitions, task types, agents) go in `src/config.yaml`, not prose.
- [ ] Single-consumer content lives in the skill body, not config.
- [ ] Long-form reference content (> a paragraph) is a lazy-load doc under `docs/`, not inlined.
- [ ] `!`commands`` are used for dynamic content (project context, lessons), not baked facts.
- [ ] No restated flow / state descriptions — the rendered transitions table is the contract.
- [ ] No stack-specific details in the skill body (Django, React, etc.) — project specifics belong in `~/Claude/{project}/_lessons/`.

## Anti-patterns (must be absent)

- [ ] No "TBD", "TODO", "implement later", "details to follow".
- [ ] No task spanning unrelated concerns (config schema + renderer + multiple skills in one row).
- [ ] No prose section that duplicates a rendered table or partial.
- [ ] No "Phase 1..N" numbered workflow when the transitions table already carries the flow.
- [ ] No stale state names (e.g. references to removed/orphaned statuses).

## External references validated

- [ ] Template paths reference files that exist.
- [ ] Lazy-load doc links resolve from the rendered skill's location.

## CLAUDE.md impact

- [ ] Any change to config schema, partial API, or rendered-artifact paths is reflected in `CLAUDE.md` via an owning task.
