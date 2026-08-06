# Input — accepted-table

Write the accepted rows below. The project is `taskflow`; the current working directory is its vault root. The attached repo is checked out at `repo/`, so the repo's `CLAUDE.md` is `repo/CLAUDE.md`. The primary plan is `plans/20260805-notification-center/`; its retrospective sits at `plans/20260805-notification-center/retro.md`. Run date: **2026-08-06**.

The user accepted the review table exactly as presented — every row below is accepted, none rejected, none added.

## Accepted review table

| # | Rule | Example | Target | Lands at | Targets |
|---|------|---------|--------|----------|---------|
| 1 | Include a user-testing gate in every plan's Definition of Done before the sprint may close. | The notification center shipped with two UX dead-ends nobody had clicked through. | Lesson | `_lessons/` next free number | `groom` |
| 2 | Never restate in prose what an adjacent config block already declares — render from config. | A settings skill narrated its own notification-channel matrix in three paragraphs and drifted from it. | Lesson | `_lessons/` next free number | `groom` |
| 3 | Record that `just api` starts the API service and `just e2e` runs the end-to-end tests against the compose stack. | Two worker sessions stalled rediscovering both commands. | Repository CLAUDE.md | `repo/CLAUDE.md` | — |

## Context files

<file path="plans/20260805-notification-center/retro.md">
---
plans:
  - plans/20260805-notification-center
sprint: 20260805-notification-center
---

# Retrospective — notification center

## Finding 1 — nobody ever clicked through the feature

The sprint was, by every mechanical measure, a success: all five milestone groups landed, the
verify step ran the full lint, typecheck and test suite green on the first try, and the plan's
every written Verify command passed. The orchestrator closed the develop run at 16:40 and the
plan moved to awaiting-retro with a clean conscience.

Then the user opened the app. Within ten minutes of ordinary clicking around they had found two
UX dead-ends: dismissing a notification from the popover left the unread badge stale until a
full page reload, and the "mark all read" affordance disappeared entirely on viewports narrower
than 900px because the toolbar collapsed it behind an overflow menu that was never wired up.
Neither is subtle; either would have been caught by any human trying the feature for five
minutes. No automated check could plausibly have caught the second one — it is a judgment call
about an interaction, not an assertion about a DOM node.

The structural gap is that nothing in the plan ever asked a human to try the feature. The
Definition of Done enumerated code-level checks exhaustively — tests, types, lint, migration
reversibility — and stopped there. The develop playbook dutifully verified everything the plan
told it to verify, and the plan never told it to put the feature in front of a person. The
user's conclusion, stated twice in feedback: every plan must carry a user-testing gate in its
Definition of Done, and a sprint must not be allowed to close until that gate has actually been
exercised. This belongs at grooming time — the step that authors the DoD is where the gate has
to be written in, because by the time develop is running, the DoD is fixed and the omission is
invisible.

## Finding 2 — prose restating what config already says

During the mid-sprint review of the settings skill, the reviewer noticed the skill body spent
three full paragraphs describing, in careful prose, exactly the notification-channel matrix
that the config block directly above it already declared: every channel name, every default,
every override rule, all restated in sentences. The prose had already drifted from the config
once — it still described the retired `digest` channel — and it was pure weight: the model
reads the config table perfectly well without the narration.

The reviewer traced the habit through two more skill bodies and found the same pattern in
both: a long narrative paragraph faithfully paraphrasing a structured block sitting right
next to it, written once when the config was young and never updated since. Every one of
those paragraphs was either redundant on the day it was written or wrong by the day it was
read. The conclusion the team settled on: prose must never restate what an adjacent config
block already declares — render from the config, and let the structure speak.

## Finding 3 — rediscovering the run commands, twice

Two separate worker sessions this sprint burned their opening minutes rediscovering the same
two facts: that the API service starts with `just api`, and that the end-to-end tests only run
against the compose stack via `just e2e`. Both facts are tribal knowledge; neither is written
anywhere an agent reads at session start. Both sessions eventually found the justfile by
listing the repo root, but one of them first tried `npm run dev`, `make api` and a stale README
section in that order. Plain repo facts like these belong in the repo's own CLAUDE.md as
one-line bullets.
</file>

<file path="_lessons/0004_information-architecture-pass.md">
---
id: 4
title: Run every prompt artefact through the four-check information architecture pass
targets:
  - groom
retro: plans/20260423-skill-refactors/retro.md
created: 2026-04-23
---

Before saving any prompt-bearing artefact (skill, agent, partial, template, briefing), every block must pass four checks:
- **Scoping** — does this component need this information to do its job? If not, move it up or delete it.
- **Duplication** — does the same block live in other components? Extract to a partial.
- **Configurability** — is this behaviour a user might want to tweak? Partial it so the knob is in one place.
- **Hierarchy** — does every block sit at the right level of detail? Top-level docs describe *what*; deeper docs describe *how*.

**Example**: A skill body carried an inline sub-component roster (hierarchy), duplicated in two sibling skills (duplication), with one orphaned negative rule (scoping) and a hard-coded tunable threshold (configurability) — one pass caught all four.
</file>

<file path="repo/CLAUDE.md">
# taskflow — project guide

Django + React task manager. Backend under `api/`, frontend under `web/`.

## Conventions

- `just test` runs the backend test suite; `just lint` runs ruff + eslint.
- Conventional commits with scope: `feat(api): ...`, `fix(web): ...`.
</file>
