## Request

> i'd like to split groomed plans into separate milestones files to handle it later by a dev-agents without pipelining them through the runner to agents but just to send the file to development agents

## Task type

`feature` — a new user-visible capability: the groomed plan becomes a multi-file artifact and develop hands a milestone file path to the worker instead of a composed briefing.

- Not `bug` — nothing diverges from expected behaviour; today's single-file plan works as specified.
- Not `refactoring` — the vault artifact shape changes (new files users read in Obsidian) and develop's delegation contract changes, so behaviour is user-visible on both surfaces.

## Problem

Today `groom` writes one plan document, `{vault}/plans/{slug}/index.md`, holding every milestone's tasks, DoD and Verify inline. `develop`'s `develop-loop` step then reads that document into runner context and **composes** a briefing per milestone group — per-milestone request, related files, DoD and Verify, project conventions, scope boundary — and passes that composed text to `booping:booping-developer`.

That pipelining costs runner context on every group and makes the briefing a lossy re-statement of a document that already exists. The plan should instead be split into per-milestone files at groom time, so develop delegates by handing the worker a **path** plus minimal run-time context, and the milestone file itself is the contract.

## Clarifications and Decisions

- Granularity: one file per milestone, at `plans/{slug}/milestones/{nn}-{kebab}.md`.
- `index.md` keeps overview, decisions, architecture, risks and a milestone table with links; milestone bodies live only in their own files — single source, no drift.
- Bookkeeping (DoD checkboxes, task rows, milestone status) lands in the milestone file; each milestone file is a standalone action plan any agent can execute and validate.
- No back-compat: new plans only, no fallback path in develop, no migration of existing plans.
- Bookkeeping is programmatic, not a separate agent step: milestone status in frontmatter flipped by `booping frontmatter-update`; DoD checkboxes flipped by the runner in the body.
- The plan-template tension is resolved by standardising only the milestone file's frontmatter contract plus two required headings (`## Definition of Done`, `## Verify`); body prose stays template-shaped.
- The dev-agent briefing carries two paths — `index.md` for context and scope boundary, the milestone file as the authoritative work contract — and no pasted bodies.
- Milestone files are created by `booping scaffold` (frontmatter seed) with the body appended; the index milestone table is rendered from a `booping query --glob 'plans/{slug}/milestones/*.md'` over their frontmatter.
- No post-implementation prose-shape reshape milestone is expected.
