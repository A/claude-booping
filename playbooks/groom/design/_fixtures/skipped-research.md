Playbook `groom`, target step `design`, first pass — no earlier design exists for this run.

Run-time context:

- project: `claude-booping` (the booping plugin repo)
- run slug: `20260801-11-05_fix-plan-date-stamp-timezone`
- run workdir: `_runs/groom/20260801-11-05_fix-plan-date-stamp-timezone/`
- plan file: `plans/20260801-11-05_fix-plan-date-stamp-timezone.md` — already created by intake,
  identity frontmatter only

The upstream artifacts follow: the confirmed framing, the blast-radius map, and the
external-practice file — which carries a skip verdict and nothing else.

## Confirmed framing — `_runs/groom/20260801-11-05_fix-plan-date-stamp-timezone/intake.md`

```markdown
---
reviewed_at: 20260801 11:18
---
# Intake — plan date stamps land on the wrong day

## Request

> Plan dates come out on the wrong day. I groomed a plan just after midnight and `created:` says
> yesterday; `planned:` and `completed:` are off the same way. I'm on UTC+3.

## Restated problem

`@now` and `@today` interpolation resolves against UTC in both places that implement it, so for
anyone not on UTC the stamped calendar day is the UTC day rather than the user's. Near either end
of the day the plan frontmatter — and every table rendered from it — shows a date the user never
worked on. The fix is to resolve both tokens in the machine's local zone.

## Task type

`bug` — the behaviour diverges from what the field means to the user (their own calendar day). No
new capability, no new surface: the same two call sites keep the same signature.

## Scope boundaries

**In scope**

- both `@now` / `@today` resolution sites and the tests that freeze their output
- every frontmatter key stamped through them (`created`, `planned`, `started`, `completed`,
  `retro`)

**Out of scope**

- values already written into existing plans
- `.booping.log` timestamps
- the `@head` token, which has no timezone dimension

## Scope challenge

- [x] Should the stamp follow the machine's local zone, or a zone configured in `config.yaml`? —
      **Answered:** the machine's local zone. No config key for it; a configured zone is a feature
      request, not this fix.
- [x] Back-fill plans already stamped in UTC? — **Answered:** no. The old values stay as they are.
- [x] Do `.booping.log` lines move to local time too? — **Answered:** no — the log is an event
      log and stays ISO-8601 UTC on purpose.
```

## Blast radius — `_runs/groom/20260801-11-05_fix-plan-date-stamp-timezone/research-codebase.md`

```markdown
# Blast radius — plan date stamps land on the wrong day

## Touched surfaces

| Surface | Where | Why it moves | Risk |
| --- | --- | --- | --- |
| `@now` / `@today` resolver | `booping-python/src/booping/commands/frontmatter_update.py` | resolves `datetime.now(UTC)`; must resolve in the machine's local zone | low — one three-branch function, covered by tests |
| the same resolver, duplicated | `booping-python/src/booping/commands/transition.py` | a second, identical copy of the same three branches | low — the duplication is the reason the bug has two homes |
| resolver tests | `booping-python/tests/test_frontmatter_update.py`, `booping-python/tests/test_transition.py` | freeze the UTC-formatted strings | low |

## Prior art

- `booping-python/src/booping/utils.py` already holds the helpers both command modules import —
  the obvious single home for a shared resolver, and the repo's own precedent for de-duplicating
  a helper that grew two copies.
- `booping-python/src/booping/logger.py` stamps ISO-8601 UTC deliberately: the precedent that not
  every timestamp in this codebase is a user-facing calendar day.
- Existing tests pin a fixed `datetime` rather than reading the clock; the pattern to follow for
  the local-zone assertions.

## Conventions in play

- `just lint`, `just typecheck`, `just test` gate every change under `booping-python/`.
- No comments restating code; only WHY for non-obvious bits.
- Conventional commits with scope (`fix(booping): ...`).

## Unknowns for design

- None. The fix has one shape, the repo carries the prior art for it, and the scope answers
  settle the two policy questions it could have raised.
```

## External practice — `_runs/groom/20260801-11-05_fix-plan-date-stamp-timezone/research-web.md`

```markdown
# research-web — 20260801-11-05_fix-plan-date-stamp-timezone

## Verdict

Skipped — well-trodden: a timezone bug in the project's own date interpolation, no new dependency,
no new surface, and prior art for the fix already in the repository.
```

## Already on disk — `plans/20260801-11-05_fix-plan-date-stamp-timezone.md`

```markdown
---
title: Plan date stamps land on the wrong day
type: bug
status: in-spec
sp: null
split_from: null
created: 2026-08-01
planned: null
started: null
completed: null
retro: null
goal: null
summary: ""
commit: null
---
```
