---
status: done
agents:
  step-prompt: a1c037864972401bf
  step-spec: aa97099ec28d095e9
reviewed_at: 20260802 09:52
fixtures_reviewed_at: 20260802 09:52
suite_reviewed_at: 20260802 09:58
---

[← index](../../index.md)

# wrap-up

## Contract

- **Needs** —
  - the guardrail results as they were reported — which commands ran, each verdict, and the
    evidence behind a red one — taken as given, never re-run here
  - the sprint's completion state as it was reported — every task DoD checkbox and every
    milestone status — taken as given, never re-derived here
  - what the sprint changed: the milestones delivered and the diff they left on the sprint
    branch
  - which of the project's documentation surfaces that diff invalidates or adds to, and where
    the project keeps them
  - the commit-message convention
- **Value** — the run's close, and nothing more: the documentation the sprint invalidated
  brought back in line, one closing commit, the plan committed to the vault, the
  plan moved to the review handoff, and one report that tells the user what shipped and where
  it goes next. Completeness is not this step's question — the DoD checkboxes and milestone
  statuses arrive already checked by verify. What it adds is the one thing the loop could not: documentation only becomes wrong
  once the whole sprint has landed, so it is written once, at the end, against the finished
  diff. Everything else is bookkeeping the run must not leave dangling — a plan stuck at
  `in-progress`, an uncommitted doc edit.
- **Output files** —
  - documentation in the attached repo, updated where the sprint invalidated or extended it —
    README sections, `docs/` pages, a CHANGELOG when the project keeps one, the repo's own
    `CLAUDE.md` when the sprint changed a convention it states. Scope is the sprint's own diff:
    what the work made untrue or newly needed, never a documentation pass of its own and never
    a scope addition. When the sprint invalidated nothing, nothing is written and the report
    says so.
  - the closing commit on the sprint branch, per the commit-message convention, covering the
    documentation edits — one commit, skipped when there is nothing to commit; the milestone
    commits already landed while the loop ran.
  - `[UPDATED] plans/{slug}/index.md` — the machine's write only: the `in-progress` →
    `awaiting-retro` transition, fired once the closing commit exists, which stamps
    `completed=@now`. The plan body is not edited here — no checkbox flipping, no milestone
    status writing, no new sections.
  - the plan committed with `booping vault-commit awaiting-retro <plan-path>`; the playbook
    ships no `_scripts/`, so the vault commit is the step's own call, made after the transition
    so the commit carries the exit status. `sprints.md` is not re-rendered here.
  - the sprint report posted in chat — the branch, the milestones shipped, the guardrail
    verdict as reported, the documentation touched, the closing commit, the plan's new status —
    closing on the handoff line `/retro {plan path}`. The handoff is step prose, not hook
    vocabulary: nothing runs `/retro`, the user does.
  - order is fixed: documentation, then the closing commit, then the transition, then
    `vault-commit`, then the report. A replay that finds the plan already at `awaiting-retro`
    re-reports without a second transition.
- **Harness return** — `## Changed:` one line per documentation file written, the plan entry
  annotated with the transition it fired, and a `repo commit:` line
  carrying the closing commit's message (or the note that there was nothing to commit);
  `## Notes:` the transition report verbatim, which documentation was updated and why — or that
  the sprint invalidated none — the vault-commit sha, and the `/retro` handoff as it was posted.
  `## Questions:` empty — the run is over and nothing here is open.
- **Review gate** —
  - none — verify's green verdict is the pre-condition; once wrap-up starts, it closes without
    stopping
  - the exit edge's gates (`every DoD checkbox [x] and every milestone status done`, `the
    project's guardrails and the plan's Final Verification green`) are satisfied by what the
    step was handed, not re-established by it; a red verdict means this step does not run at
    all
- **Delegation** — inline: the runner renders the step and performs it itself, in the main
  context.

## Example artifact

The documentation edit the sprint made necessary — `README.md`, the quota section:

```markdown
## Rate limits

Public `/api/` endpoints are limited to **120 requests/minute** per API key, with a burst of
20. Anonymous traffic is limited per source IP at the same rate. Every response carries
`X-RateLimit-Limit`, `X-RateLimit-Remaining` and `X-RateLimit-Reset`; a 429 additionally
carries `Retry-After`. Both quotas are configurable via `RATE_LIMIT_PER_MINUTE` and
`RATE_LIMIT_BURST`.
```

The closing commit and the bookkeeping that follows it:

```bash
git commit -m "docs(api): document public rate limits and quota settings"
booping playbook-transition develop awaiting-retro
booping vault-commit awaiting-retro plans/20260731-10-05_rate-limit-public-api/index.md
```

The sprint report posted in chat:

```markdown
**Sprint done — Rate limit public API (24 SP), branch `feat/rate-limit-public-api`.**

| # | Milestone | SP | Status |
| - | --------- | -- | ------ |
| 1 | Bucket primitive | 5 | done |
| 2 | Middleware wiring | 7 | done |
| 3 | Anonymous quota | 12 | done |

Guardrails: green — `just test` (214 passed), `just lint`, `just typecheck`; the plan's Final
Verification passed alongside them.

Docs: `README.md` gained the rate-limit section and `docs/api/errors.md` now lists the 429
response; committed as `docs(api): document public rate limits and quota settings`.

The plan is at `awaiting-retro`. Next: `/retro plans/20260731-10-05_rate-limit-public-api/index.md`.
```

A sprint that invalidated no documentation closes on the same shape, with the docs line
reading `Docs: nothing invalidated — no documentation changes were needed.` and no closing
commit.

## Return Format

```markdown
## Changed:

- [UPDATED] README.md — rate-limit section
- [UPDATED] docs/api/errors.md — 429 response
- [UPDATED] plans/20260731-10-05_rate-limit-public-api/index.md — in-progress → awaiting-retro
- repo commit: `docs(api): document public rate limits and quota settings`

## Notes:

- docs: README rate-limit section + errors page 429 row; nothing else the sprint touched is
  documented
- transition: `in-progress → awaiting-retro`; frontmatter: completed=20260802 14:07
- vault-commit: 9f3c1ab
- handoff posted: `/retro plans/20260731-10-05_rate-limit-public-api/index.md`

## Questions:
```

The documentation lines are omitted when the sprint invalidated none, and the `repo commit:`
line then reads `repo commit: none — no documentation changes to commit`. The plan line is
always present. `## Questions:` is always empty.
