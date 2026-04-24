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

### M1: {Milestone name} — {SP} SP | pending

**Goal**: one sentence — the observable change in the rendered skill or shared config.

**Verify**: rebuild command and sanity check (e.g. `bin/booping-build && diff skills/<name>/SKILL.md`).

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | ... | `src/templates/skills/<name>.md.j2`, `src/config.yaml` | 2 | pending |

#### Task 1.1 DoD

- [ ] Rendered skill diff matches intended shape.
- [ ] No hardcoded values that duplicate config.
- [ ] Lazy-load links resolve.

---

## Final Verification

- [ ] `bin/booping-build` renders cleanly.
- [ ] Rendered skill body reviewed (no stale state names, no prose that duplicates rendered tables, no `{{placeholder}}` leaks).
- [ ] Project-local extension points (`_booping/skill_<name>.md`) still inline correctly.

## Out of scope

Explicit exclusions — e.g. "groom skill only; develop/retro/learn unchanged", "no plan-template changes".

## CLAUDE.md impact

Name sections to update, or state "No CLAUDE.md changes required — {justification}".

---

# Quality Checklist

## Frontmatter

- [ ] Frontmatter matches [plan frontmatter](../../docs/template_plan_frontmatter.md).
- [ ] `sp` equals the sum of per-task SP across milestones.

## Content

- [ ] Context names the behavior change visible in rendered skills, not "refactor internals".
- [ ] DoD bullets are verifiable by reading the rendered output or a diff.
- [ ] Every task lists exact template / partial / config paths.
- [ ] Every task DoD uses checkboxes, not prose.
- [ ] Every milestone has a `Verify` step that includes a rebuild.
- [ ] Each milestone executable from a fresh session with only the plan as context.

## Skill-design hygiene

- [ ] Structured facts (statuses, transitions, task types, agents) go in `src/config.yaml`, not prose.
- [ ] Single-consumer content lives in the skill body, not config.
- [ ] Long-form reference content (> a paragraph) is a lazy-load doc under `docs/`, not inlined.
- [ ] `!`commands`` are used for dynamic content (project context, lessons, extra instructions), not baked facts.
- [ ] No restated flow / state descriptions — the rendered transitions table is the contract.
- [ ] No stack-specific details in the skill body (Django, React, etc.) — project specifics belong in `~/Claude/{project}/_booping/`.

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
