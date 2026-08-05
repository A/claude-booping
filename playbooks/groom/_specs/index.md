---
status: done
reviewed_at: 20260731 19:04
playbook_yaml_reviewed_at: 20260731 19:10
regress: skip
agents:
  record-decision: adec7122f03802202
  decompose: a03a86a30dcf3cd9a
  states: a6c091404f3d63634
  step-spec-cross-review: a7b6980b9b3716727
  step-spec-resync: a93fd664402945580
---
# groom — Decomposition

Shape a feature, bug or refactor into a specified, estimated, user-approved plan. Intake frames
the request in a brief — written to `request.md` and posted in chat — challenges scope, and
creates the plan directory; the user's answers to the scope questions are the confirmation, no
separate confirm gate. Research runs next: blast radius in the codebase always, then the
external ground the design rests on — best practice, competing approaches, pitfalls where the
work is uncertain — with the external references the work names checked against current docs in
the same pass. Draft-plan settles architecture, surface changes and trade-offs with the user in
conversation, then writes the plan — refinement against the sizing thresholds is part of
drafting, not a separate pass. The written plan is cross-reviewed by a second model, detached;
present is the run's **single review gate** — a human-targeted approval summary over the full
plan, and the handoff to the `develop` playbook (`/playbook develop {plan path}`).

The plan document is `index.md` in `plans/{slug}/` — there is no separate `plan.md`. One slug
names the whole run: `{YYYYMMDDHHMM}_{kebab-title}`, minted by the preamble — a deliberate
divergence from the `/groom` skill's date-only slug, so parallel runs on one day cannot collide.
The plan directory is also the run workdir (`_runs/` is gone): the machine's first transition
bootstraps `index.md` with the run status, `intake` gives it identity frontmatter and writes the
framing brief to `request.md` beside it, and `draft-plan` writes the plan body into `index.md`.
The research steps write nothing — their findings are posted in chat. The run's `status:` on
`index.md` belongs to the machine; the plan-lifecycle status `/develop`, `sprints.md` and
`/chat` read is stamped as `plan_status:` on the same file by playbook-local `_scripts/` hooks
(`plan-in-spec`, `plan-awaiting-plan-review`, `plan-ready-for-dev`), which also carry the
`sprints.md` render and the vault commit.

`cross-review` is a step: `detached: "{{ config.core.cross_review_agent or '' }}"` resolves at
render time (the playbook is `jinja: true`), the agent reads `plans/{slug}/index.md` and returns
severity findings only — `CRITICAL|RISK|NOTE` lines or `no findings` — writing nothing; the
runner disposes of the findings before advancing. With no `core.cross_review_agent` configured the
step's summary and body both render as skipped, the runner performs nothing, and its gate is
vacuously satisfied. This replaces the Gemini
`booping-external-llm-call` path for playbook runs; the canonical `/groom` skill keeps the doc's
path untouched.

The machine is groom's own subset of the plan lifecycle: it starts at `in-spec`, passes through
`awaiting-plan-review`, and ends at `ready-for-dev` where develop's subset picks up. `backlog`
stays outside it, the parking status for plans to groom later. The playbook never calls
`booping transition`; every move is a `booping playbook-transition` on this machine.

The stale core `playbooks/groom/` was deleted so this playbook could take the name; the `/groom`
skill itself is untouched and stays the default entry point through beta-testing.

## Graph

```yaml
graph:
  intake: []
  research-codebase: [intake]
  research-web: [research-codebase]
  draft-plan: [research-codebase, research-web]
  cross-review: [draft-plan]
  present: [cross-review]
```

One run grooms exactly one plan — a split recommended at `present` is groomed as a separate run.

The two research steps are sequential, not a parallel wave: wave co-members must be `detached:`,
and both research steps are runner-performed (assisted), so a shared wave is impossible — and
would buy nothing, since the runner executes sequentially anyway.

## Steps

Delegation levels (defined in playbook-authoring / `documentation/playbook.md`):

- **inline** — the runner renders the step and performs its instructions itself, in the main
  context.
- **assisted** — the runner renders and owns the step; the heavy work (bulk reads, web
  research) is delegated to a configured agent that returns a compressed summary, keeping the
  runner's context clean. The runner decides *what* is researched; the agent only executes.
- **detached** — the step's agent fetches and performs the step body itself; the runner never
  reads the instructions and operates on the step summary alone.

| Step              | Summary                                                                                                                                                                                                                                                  | Artifact                                                                                                       | Gate                                                                                                                                                       | Delegation                                            | Spec                                     |
| ----------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------- | ---------------------------------------- |
| intake            | restate the request, classify the task type, set the scope boundaries and challenge the scope in a brief; create the plan directory with its `index.md`, or adopt a parked plan into it                                                                    | `plans/{slug}/index.md` — created, identity frontmatter; `plans/{slug}/request.md` — framing brief              | the user answers the scope-challenge questions — clear intent is the confirmation; answers that change type, problem or a boundary re-run the step          | inline                                                | [spec](steps/intake/index.md)            |
| research-codebase | map the blast radius in the attached repo — touched surfaces, prior art, the conventions that bind the design, and the calls left for it; bulk reads delegated                                                                                             | blast-radius map posted in chat                                                                                 | none — reviewed through drafting                                                                                                                            | assisted — researcher agent from `config.research_agent` | [spec](steps/research-codebase/index.md) |
| research-web      | research the external ground the design rests on — current best practice, competing approaches and known pitfalls where the work is uncertain — and check the external references it names against current docs                                           | web-research findings posted in chat                                                                            | none — reviewed through drafting                                                                                                                            | assisted — researcher agent from `config.research_agent` | [spec](steps/research-web/index.md)      |
| draft-plan        | settle architecture, surface changes and trade-offs with the user, then pick the plan template matching the dominant surface and write the plan — milestones, tasks with DoD and Verify, story points, `sp` / `summary` frontmatter — against its Checklist | `plans/{slug}/index.md` — plan body written, Quality Checklist passed                                           | none as a status — alignment happens in conversation during the step                                                                                        | inline                                                | [spec](steps/draft-plan/index.md)        |
| cross-review      | second-model review of the written plan `plans/{slug}/index.md`; returns severity findings only, writes nothing; skipped when no `core.cross_review_agent` agent is configured                                                                                        | none — findings returned to the runner, who disposes of them                                                    | every CRITICAL finding folded in or recorded as a deferral — vacuously satisfied when the step is skipped                                                    | detached — `config.cross_review.agent`                | [spec](steps/cross-review/index.md)      |
| present           | assemble the approval summary — approach, milestones, SP totals, plan path, check outcomes — recommend a split past the threshold, offer a plan branch on a repo-local vault, and carry the approval                                                       | approval summary posted in chat                                                                                 | the run's single review gate: explicit user approval over the summary and the full plan; a change request to the plan itself loops the run back to drafting  | inline                                                | [spec](steps/present/index.md)           |

## States

One machine, `run` — a **procedure tracker** whose artifact is `index.md` in the plan directory;
its superstates name the plan-lifecycle status stamped as `plan_status:` on the same file, and
playbook-local `_scripts/` hooks on the boundary-crossing edges carry that mirror, the
`sprints.md` render and the vault commit. Full chart — inventory, transitions, script contracts:
[states](states.md).

## Questions

- [x] ~~How does the machine's `artifact:` reach a plan whose filename is only known mid-run?~~ —
      it does not have to: the plan document and the machine's artifact are the same file,
      `index.md` in the plan directory; the plan-lifecycle status is stamped onto it as
      `plan_status:` by the machine's edge hooks.
- [x] ~~Does the playbook still call `booping transition` for status moves?~~ — no. `booping
      playbook-transition` on this machine owns every move; the plan-status mirror, the
      `sprints.md` render and the vault commit are playbook-local `_scripts/` hooks on its edges.
- [x] ~~Does the machine cover the `backlog → in-spec` entry edge?~~ — no. It starts at
      `in-spec`; `backlog` stays outside it as the parking status for plans to groom later.
- [x] ~~Which steps read the vault's `lessons/`?~~ — none declare it. Lessons are injected by the
      renderer from the playbook's `_lessons/` dirs; steps carry nothing about them.
- [x] ~~Cross-review return-contract shape?~~ — findings-only confirmed: `- CRITICAL|RISK|NOTE:
      {finding} — {plan section}` lines or the literal `no findings`, nothing else (lesson
      0007); wording is locked in the `cross-review` step spec, never negotiated mid-run.
- [x] ~~Accept the two costs the vault-as-workdir mechanism carries, or change one of them?~~ —
      superseded: the plan is a directory, `plans/{slug}/`, which is also the run workdir;
      the machine's artifact is `index.md` there.
- [x] ~~Plan-as-directory breaks `Plan.load_all`'s `plans/*.md` glob and every consumer expecting
      a plan *file* (`/develop`, `sprints.md`, `/chat`, parked stubs)~~ — landed: `Plan.load_all`
      discovers directory plans by slug alongside flat `plans/{slug}.md` files, the directory
      shape shadowing a same-slug file (shadowed file warns on stderr). Parked stubs stay files
      until `intake` adopts one into its directory.
