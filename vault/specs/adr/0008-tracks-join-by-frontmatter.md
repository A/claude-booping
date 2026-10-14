---
type: adr
title: Retro and code review are separate tracks joined by plan frontmatter
summary: A plan ends at develop's done and never moves again; retro and code review keep their own artifacts and machines and join the plan through retro and code_reviews keys.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: accepted
values: [values/0001#analysable-history, values/0001#single-source]
sources: [playbooks/retro/_specs/DECISIONS.md, playbooks/retro/_specs/index.md, playbooks/code-review/_specs/DECISIONS.md, CHANGELOG.md, CLAUDE.md]
---

## Context

Retro was first bound to the plan lifecycle: the plan moved through
`awaiting-retro` → `awaiting-learning`, and the retro playbook port put the
retrospective at `plans/{slug}/retro.md` with the plan as the run's main artifact. A
retro run may cover several plans, so the artifact had to live in a "primary" plan's
directory with siblings linking to it. Code review was first authored ephemeral: no
state machine, no artifact, no plan-status move, a re-review being a new run.

## Decision

Plans end at develop's `done` and are never moved again. Retro's artifact is a
standalone `retrospectives/{YYYYMMDDHHMM}_{kebab-title}.md`, one per run however many
plans it covers, with its own machine (`awaiting-retro` → `awaiting-learning`);
code review's artifact is `codereviews/{plan-dirname}/{ts}.md` with
`in-agent-review` → `human-review` → `done`. Both machines declare no `artifact:`
and are addressed with `--target`. The tracks join through plan frontmatter, not
status: `retro:` is null until covered, so `{status: done, retro: null}` is the
retro queue; `code_reviews:` lists every review that closed on the plan — history,
not a queue flag — so every done plan stays reviewable.

## Alternatives

| Option | Status | Complexity | Reversibility | Verdict |
|---|---|---|---|---|
| [Separate tracks joined by frontmatter](#separate-tracks-joined-by-frontmatter) | accepted | medium | medium | Plans stay done; queues are queries |
| [Retro statuses on the plan](#retro-statuses-on-the-plan) | rejected | low | medium | Superseded on 2026-08-07 |
| [Retro file inside the plan directory](#retro-file-inside-the-plan-directory) | rejected | low | high | A multi-plan retro needs a primary plan |
| [Ephemeral code review](#ephemeral-code-review) | rejected | low | high | No record; re-review invisible |

### Separate tracks joined by frontmatter

Each track has its own artifact and machine; a back-link key on the plan records
the join.

- **Pros:** one retrospective per run regardless of plan count; review history
  accumulates on the plan; the queues are frontmatter queries.
- **Cons:** the join keys are written by hook scripts and must be kept in step with
  the artifacts.
- **Complexity:** medium.
- **Reversibility:** medium.

### Retro statuses on the plan

The plan itself moves through the retro and learning statuses.

- **Pros:** one artifact.
- **Cons:** a multi-plan retro moves several plans for one run; the plan lifecycle
  grows another playbook's statuses.
- **Complexity:** low.
- **Reversibility:** medium.

### Retro file inside the plan directory

`plans/{slug}/retro.md`, sibling plans linking to the primary plan's file.

- **Pros:** the retro sits beside what it reviews.
- **Cons:** a primary plan has to be chosen for a multi-plan run.
- **Complexity:** low.
- **Reversibility:** high.

### Ephemeral code review

The review lives only in the conversation.

- **Pros:** nothing to persist.
- **Cons:** no record of findings or verdicts; a reviewed plan is indistinguishable
  from an unreviewed one.
- **Complexity:** low.
- **Reversibility:** high.

## Consequences

- Migration `002_tracks_and_lessons` relocated `plans/{slug}/retro.md` into
  `retrospectives/`.
- A plan dropped from a retro is stamped `retro: skipped` by `_scripts/drop-plan`.
- Ad-hoc code reviews of no plan land in `codereviews/{target-slug}/{ts}.md` with
  `plan: null`.
