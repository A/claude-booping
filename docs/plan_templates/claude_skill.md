---
name: claude-skill
description: Authoring or refactoring a Claude Code skill — skill bodies, partials, config schema, rendered outputs, skill-level agents.
---

# Plan Body

## Context

What skill (or skill family) this plan affects. The gap or wrinkle, what changes after.

## Decisions

Typical topics: what moves to config vs stays in skill body, which partials to extract, what the skill's phases / craft become, what lazy-loads vs embeds.

## Architecture

How the skill interacts with other skills via shared config (statuses, agents, task types), and its load-time inputs (config, partials, `!`commands``, lazy docs).

## Milestones

One `### M{nn} — {title}` block per milestone, in the format draft-plan states. Its content:

- **Tasks** — opens with a **Goal** line (one sentence: the observable change in the rendered skill or shared config) and a **Scope** line (the templates, partials, config keys and rendered artefacts this milestone touches, and which other skills read the same config), then one row per task:

  | Task | Description | Files | SP | Status |
  |------|-------------|-------|----|--------|
  | 1.1 | ... | `src/templates/skills/{name}.md.j2`, `src/config.yaml` | 2 | pending |

- **Definition of Done** — one `Task {n}.{m}` block per task, checkbox bullets only: rendered diff matches the intended shape, no hardcoded values that duplicate config, lazy-load links resolve.
- **References** — where such files exist, 1–3 existing templates, partials or rendered reports whose shape this milestone copies, by path, plus the path of any config block it must not go looking for.
- **Verify** — render and sanity check (e.g. `bin/booping render src/templates/skills/{name}.md.j2` and review output) — the rebuild plus the surfaces this milestone touched.

## Final Verification

- [ ] `bin/booping render src/templates/skills/<name>.md.j2` produces clean output (for skill/agent body changes).
- [ ] Rendered skill body reviewed (no stale state names, no prose that duplicates rendered tables, no `{{placeholder}}` leaks).
- [ ] Targeted rules (`skill:{name}`, `agent:{id}`) still inline correctly into the rendered body.

## Out of scope

Explicit exclusions — e.g. "the `playbook` skill body only; its thin shell unchanged", "no plan-template changes".

## CLAUDE.md impact

Name sections to update, or state "No CLAUDE.md changes required — {justification}".

---

# Quality Checklist

## Frontmatter

- [ ] `title` matches the plan's H1 and `type` is the task type chosen at intake.

## Content

- [ ] Context names the behavior change visible in rendered skills, not "refactor internals".
- [ ] DoD bullets are verifiable by reading the rendered output or a diff.
- [ ] Every task DoD uses checkboxes, not prose.
- [ ] Every milestone's References names 1–3 existing files to copy the shape of where such files exist, or states that none applies.
- [ ] No milestone asks for a deliverable in the worker's report — each is named as a path plus "Create" or "Append to", relative to the repo root or the plan directory.

## Skill-design hygiene

- [ ] Structured facts (statuses, transitions, task types, agents) go in `src/config.yaml`, not prose.
- [ ] Single-consumer content lives in the skill body, not config.
- [ ] Long-form reference content (> a paragraph) is a lazy-load doc under `docs/`, not inlined.
- [ ] `!`commands`` are used for dynamic content (project context, rules), not baked facts.
- [ ] No restated flow / state descriptions — the rendered transitions table is the contract.
- [ ] No stack-specific details in the skill body (Django, React, etc.) — project specifics belong in rule records in the project specs tier.

## CLAUDE.md impact

- [ ] Any change to config schema, partial API, or rendered-artifact paths is reflected in `CLAUDE.md` via an owning task.
