# Retrospective template

Retrospective files are written by `/retro`, which analyzes sprint outcomes against the plan and identifies patterns in what worked, what didn't, and why.

The frontmatter below captures the retrospective's scope (which plans it covers) and date. Fill in the body sections following the structure and guidance provided.

---

## Frontmatter example

```yaml
plans:
  - plans/20260401-feature-x-implementation.md
  - plans/20260408-feature-x-integration.md
date: 2026-04-23
goal_summary: Feature X shipped on time with clean integration; auth layer needed pre-review validation.
```

---

## What went well

Concrete wins. What was achieved, what worked as designed. Keep it brief — 3–5 bullet points with specifics, not vague praise (avoid "good communication"; say "API contract locked before implementation" instead).

- ...
- ...

---

## What went wrong

For each issue, include a subsection with this three-line format:

### {{Issue name}}

**What happened**: Factual description of the problem.

**Why**: Trace to the plan decision or blind spot that caused it.

**Impact**: What does this cost now (rework, tech debt, user confusion, process delay)?

---

## Root causes

Synthesize the "why" lines from the issues above into 2–4 underlying patterns. These should be general enough to apply to future sprints — not restatements of individual bugs, but systemic themes.

### Ignored / unapplied lessons

List existing lessons (from `~/Claude/{project}/lessons/` or project `CLAUDE.md` instructions) that should have prevented or caught one or more flagged problems but were not applied. For each:

- `lessons/XXXX_lesson-title.md` — rule was "...", but we did "..." instead, which caused [which issue(s)].

---

## Action items

Specific, owned, traceable next steps that address root causes or issues identified above.

| # | Action | Owner | Status |
|---|--------|-------|--------|
| 1 | ... | Next sprint / Person | Planned |

---

## Takeaways for this project

3–5 concrete behavioral changes for this project going forward. Not platitudes ("communicate better") — specific heuristics ("when replacing a module, design the new interface before mapping old code to new structure"; "add a SOLID review step to the plan before implementation").

- ...
- ...

---

## Self-review checklist

Before committing a retrospective, confirm all items below are true:

- [ ] Each "what went wrong" item has a traceable cause (plan decision, blind spot, or carried debt).
- [ ] Root causes are patterns, not restatements of individual issues.
- [ ] Ignored-lesson flags cite existing lessons by path and explain the gap.
- [ ] Action items are specific with an owner and a clear next step.
- [ ] Takeaways are heuristics, not platitudes — someone could apply them next sprint.
- [ ] "What went well" is honest, not inflated to balance criticism.
- [ ] No blame language — focus on decisions and processes, not people.
