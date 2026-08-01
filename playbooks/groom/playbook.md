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
challenged, blast radius and (where warranted) current practice researched, architecture agreed,
milestones and story points set, external references verified, `summary:` frontmatter written,
and every milestone executable in a fresh session from the plan alone.

One slug names the whole run — `yyyymmdd-hh-mm_{title}`, minted at run start from the request
title, the timestamp taken from the local clock — run `date +%Y%m%d-%H-%M`, never from memory. The plan lands at `plans/{slug}.md` in the vault; the run workdir is
`{vault}/_runs/groom/{slug}/` — same stem on both. `intake` creates the plan file; the run
workdir and its `run.md` are bootstrapped by the machine's first transition.

Never call `booping transition` — every move on this run is a `booping playbook-transition` on
the `run` machine above. Its states track the run's own position, not the plan's lifecycle
status; the plan's status is mirrored onto `plans/{slug}.md` by the `script plan-in-spec` /
`plan-awaiting-plan-review` / `plan-ready-for-dev` hooks on the edges that cross a lifecycle
boundary, which also render `sprints.md` and commit the vault.

Cross-review of the finished draft is not a step of its own — it runs inside `draft-plan`, gated
on `config.cross_review` being configured, before the plan leaves `in-spec`.

One run grooms exactly one plan. When `present` recommends a split, the user parks the siblings
as backlog stubs and each is groomed in its own run.
