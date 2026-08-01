---
name: groom
title: Groom
summary: Shape a feature, bug, or refactor into a specified, estimated, 
  user-approved plan.
trigger: groom a request into a plan — spec out a feature, bug, or refactor 
  before development (playbook variant, parallel to /groom)
jinja: true
requires_project: true
reviewed_at: 20260731 19:10
---

A run ends with a plan the user has explicitly approved, moved to `ready-for-dev`: scope
challenged, blast radius and (where the user asked for it) current practice researched,
architecture agreed, milestones and story points set, external references verified, `summary:`
frontmatter written, and every milestone executable in a fresh session from the plan alone.

One slug names the whole run — `{YYYYMMDD}-{kebab-title}`, minted at run start from the request
title, the date taken from the local clock — run `date +%Y%m%d`, never from memory. The plan is a
**directory**: `plans/{slug}/` in the vault, which is also the run workdir. Pass it as
`--workdir` on every `booping playbook-state` / `booping playbook-transition` call.

Three files live there, and nothing else:

- `plan.md` — the executable plan. Created by `intake` with identity frontmatter only; its body
  is written by `draft-plan` and refined by `decompose-work`.
- `index.md` — the run's main artifact and the machine's artifact, bootstrapped by the first
  transition. One evolving document whose sections the steps own — framing, blast radius, design,
  refinement, references, approval — each revised in place on a loopback, never appended to. Also
  record the id of each agent you delegate to, so a loopback resumes that agent instead of
  spawning a fresh one.
- `research.md` — only when the user asked for deep web research at intake. That decision is
  intake's and mechanical; no later step re-judges it.

Two `status:` fields, deliberately split. `index.md`'s is the **run's** position — what `booping
playbook-state` reports and what a resumed run reads. `plan.md`'s is the **plan's** lifecycle
status, the one `/develop`, `sprints.md` and `/chat` read; it is mirrored onto `plan.md` by the
`script plan-in-spec` / `plan-awaiting-plan-review` / `plan-ready-for-dev` hooks on the edges
that cross a lifecycle boundary, which also render `sprints.md` and commit the vault.

Never call `booping transition` — every move on this run is a `booping playbook-transition` on
the `run` machine above.

The run has one review gate: `awaiting-approval`, after `present`. Framing pauses for the user's
answers inside `framing` (the answers are the confirmation; changed framing re-runs intake within
the status) and design alignment happens in conversation inside `designing` — neither is a status
of its own, and the user first reads the plan at `present`, after refinement.

Cross-review of the finished draft is not a step of its own — it runs inside `draft-plan`, gated
on `config.cross_review` being configured, before the plan leaves `in-spec`.

One run grooms exactly one plan. When `present` recommends a split, the user parks the siblings
as backlog stubs and each is groomed in its own run.
