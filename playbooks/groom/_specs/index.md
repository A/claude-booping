---
status: done
reviewed_at: 20260731 19:04
playbook_yaml_reviewed_at: 20260731 19:10
regress: skip
---
# groom — Decomposition

Shape a feature, bug or refactor into a specified, estimated, user-approved plan. Intake frames
the request and challenges scope; two research steps run in parallel — blast radius in the
codebase, current practice on the web when the work is novel; design settles architecture with
the user; the plan is written into the project vault and cross-reviewed in place; a
re-decomposition pass then refines whatever came out oversized — and skips outright when nothing
did; external references are verified against upstream docs; present carries the approval and
the handoff to `/develop`. The user first reads the plan after that refinement — never a draft
still carrying oversized tasks — and approves it at present. Conditional edges do not exist in
the framework, so both optional steps take the same shape: they always run and return a skip
note when they have nothing to do.

Cross-review is not a step: the playbook is `jinja: true`, so `draft-plan`'s prompt renders a
`{% raw %}{% if config.get("cross_review") %}{% endraw %}` block that spawns
`subagent_type={% raw %}{{ config.cross_review.agent }}{% endraw %}` over the finished draft,
after the Quality-Checklist verify and before the move out of `in-spec`; with the key absent
nothing renders and the shared cross-validation gate is vacuously satisfied. That block
*replaces* the Gemini `booping-external-llm-call` path the gate's doc describes — playbook runs
never call it, while the canonical `/groom` skill keeps the doc's path untouched. It also runs
earlier than the doc's Gemini path — on the fresh draft, before the user has seen it — because
the block belongs to the step that writes the plan and is worth exactly one pass; the user's
feedback then lands on a plan whose critical findings are already folded in.

One slug names the whole run: `yyyymmdd-hh-mm_{title}`, minted at run start from the request
title (this playbook's format, deliberately unlike the skill's `{YYYYMMDD}-{kebab-title}.md`).
The plan is `plans/{slug}.md` in the vault and the run workdir is `{vault}/_runs/groom/{slug}/`
— same stem on both, so a run's plan and its working files are found from either end. `intake`
creates the plan file; the run workdir and its `run.md` are the driver's, bootstrapped by the
machine's first transition.

Two files carry status, and the split is deliberate. `run.md` in the workdir is the machine's
artifact: its `status:` is the **run's** position, what `booping playbook-state` reports and
what a resumed run reads. `plans/{slug}.md` carries the **plan's** lifecycle `status:` — the one
`/develop`, `sprints.md` and `/chat` read — mirrored onto it from the machine's edges. The
mirror runs through playbook-local `_scripts/` hooks rather than file-target
`frontmatter-update` hooks: a hook's file target is a static path and only interpolates
`{instance}`, which is out of scope on a flat graph, whereas a script gets `BOOPING_WORKDIR`
and `BOOPING_ARTIFACT` and can derive the slug from the workdir name and read the run status
that was already written before the hooks fired. The same scripts carry the two side effects
`booping transition` used to bring — the `sprints.md` render and the vault commit — resolving
the vault as the workdir's `../../..` or via `booping config-get home_dir`.

The machine is groom's own subset of the plan lifecycle: it starts at `in-spec`, passes through
`awaiting-plan-review`, and ends at `ready-for-dev` where develop's subset picks up. `backlog`
stays outside it, the parking status for plans to groom later. The playbook never calls
`booping transition`; every move is a `booping playbook-transition` on this machine.

Files mode for everything else: each step writes its own artifact under the run workdir,
addressed by the step prompt rather than resolved by the framework, so the run stays reviewable
and resumable from disk.

Out of scope for now, recorded so the shape stays open: a later edge hook could create the
parked sibling stubs of a split automatically. Today `present` only recommends the split and the
user parks the siblings.

The stale core `playbooks/groom/` is deleted so this playbook can take the name; the `/groom`
skill itself is untouched and stays the default entry point through beta-testing.

## Graph

```yaml
graph:
  intake: []
  research-codebase: [intake]
  research-web: [intake]
  design: [research-codebase, research-web]
  draft-plan: [design]
  decompose-work: [draft-plan]
  verify-references: [decompose-work]
  present: [verify-references]
```

One run grooms exactly one plan — a split recommended at `present` is groomed as a separate run.

## Steps

| Step              | Summary                                                                                                                                                                                                                                                                                                                                                                                                                                   | Inputs                                                                                                                                                                                                                                                                                                             | Artifact                                                                                                                                                                                                              | Gate                                                                                                                                   | Model           | Spec                                     |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- | --------------- | ---------------------------------------- |
| intake            | restate the request, classify the task type, and challenge scope — what new components, dependencies, APIs or workflow changes this likely pulls in; adopt an existing parked plan when the user names one; create the plan file with its identity frontmatter — title, type, `status: in-spec`                                                                                                                                          | the user's request verbatim; the task-type catalogue and its per-type guidance; project conventions; plans already in the vault, parked ones included                                                                                                                                                              | `_runs/groom/{slug}/intake.md` — restated request, task type, scope boundaries, scope-challenge questions; `plans/{slug}.md` — created, identity frontmatter only                                          | the user answers the scope questions and confirms task type and boundaries                                                             | fable-5:high    | [spec](steps/intake/index.md)            |
| research-codebase | map the blast radius — files, modules, integrations, external surfaces — and the prior art and conventions the work must follow                                                                                                                                                                                                                                                                                                           | the confirmed framing — problem, task type, scope boundaries; the repository's code and conventions                                                                                                                                                                                                                | `_runs/groom/{slug}/research-codebase.md` — blast radius, prior art, conventions in play                                                                                                                              | none — reviewed through the design                                                                                                     | opus-5:medium   | [spec](steps/research-codebase/index.md) |
| research-web      | for novel or non-obvious work, gather current best practice, competing approaches and known pitfalls with sources; return a skip note when the work is well-trodden                                                                                                                                                                                                                                                                       | the confirmed framing; the uncertainty signals it names — unfamiliar surfaces, new dependencies, non-obvious approaches                                                                                                                                                                                            | `_runs/groom/{slug}/research-web.md` — approaches, trade-offs, pitfalls with sources — or a skip note                                                                                                                 | none — reviewed through the design                                                                                                     | opus-5:medium   | [spec](steps/research-web/index.md)      |
| design            | settle architecture, pattern choice, data / API / config surface changes, alternatives and risks; surface every trade-off the user must call                                                                                                                                                                                                                                                                                              | the confirmed framing and the user's scope answers; the blast-radius map; the external-practice findings or their skip note                                                                                                                                                                                        | `_runs/groom/{slug}/design.md` — architecture, surface changes, alternatives, trade-offs, risks                                                                                                                       | the user iterates on the design and confirms it before any plan is written                                                             | opus-5:high     | [spec](steps/design/index.md)            |
| draft-plan        | pick the plan template matching the dominant surface and write the plan against its Plan Body — milestones, tasks with DoD and Verify, story points per task / milestone / sprint, `summary:` frontmatter — then verify against the template's Quality Checklist; when the project configures a cross-review agent, hand the finished draft to it and address every CRITICAL finding, recording deferred ones in the plan's risk register | the confirmed design and the user's scope answers; the blast-radius map; the plan-template catalogue; the plan frontmatter shape; the SP scale and how many consecutive milestones `/develop` bundles per agent, which bounds milestone size; whether a cross-review agent is configured and which                 | `plans/{slug}.md` — the written plan, cross-review findings folded in, deferrals recorded                                                                                                                             | none — the plan is refined once more before the user reads it                                                                          | opus-5:high     | [spec](steps/draft-plan/index.md)        |
| decompose-work    | refine the written plan against the sizing thresholds: re-decompose every task at or over the re-decompose threshold and re-sum the milestone and sprint totals; flag a split candidate — the sibling shape, not a second plan — when the sprint total passes the split threshold; when no task is oversized and the total is under the threshold, change nothing and return a skip note                                                  | the written plan with its per-task, per-milestone and sprint SP totals; the re-decompose and split thresholds; the SP scale                                                                                                                                                                                        | `plans/{slug}.md` — oversized tasks re-decomposed and totals re-summed, untouched on a skip; `_runs/groom/{slug}/decomposition.md` — what was re-decomposed, the new totals and the split candidate, or the skip note | the user reworks and confirms the refined plan — milestones, tasks, estimates and any split candidate; this is the first-pass feedback | opus-5:medium   | [spec](steps/decompose-work/index.md)    |
| verify-references | check every external reference the plan names — package versions, image tags, API endpoints, CLI flags, config options — against current upstream docs and correct what is wrong                                                                                                                                                                                                                                                          | every external reference the plan names; current upstream documentation                                                                                                                                                                                                                                            | `_runs/groom/{slug}/references.md` — checked table with verdict per reference; corrections folded into the plan                                                                                                       | none — corrections surface at present                                                                                                  | opus-5:medium   | [spec](steps/verify-references/index.md) |
| present           | assemble the approval summary — approach, milestones, SP totals, plan path, cross-review and verification outcomes — recommend a split into siblings when the total passes the threshold, each to be parked as a backlog stub and groomed in its own run; offer a plan branch when the vault is repo-local                                                                                                                                | the drafted plan with milestones and SP totals; the split threshold and the split candidate the decomposition flagged, if any; the cross-review findings and recorded deferrals, or the note that no cross-review agent is configured; the reference-verification results; whether the vault lives inside the repo | `_runs/groom/{slug}/handoff.md` — approval summary, split recommendation if any, and the handoff to `/develop`                                                                                                        | explicit user approval — "looks good" counts, silence never does; change requests loop back to the matching earlier status             | sonnet-5:medium | [spec](steps/present/index.md)           |

## States

One machine, `run` — a **procedure tracker** whose artifact is `run.md` in the run workdir; its
superstates name the plan-lifecycle status mirrored onto `plans/{slug}.md`, and playbook-local
`_scripts/` hooks on the boundary-crossing edges carry that mirror, the `sprints.md` render and
the vault commit. Full chart — inventory, transitions, script contracts: [states](states.md).

## Questions

- [x] ~~How does the machine's `artifact:` reach a plan whose filename is only known mid-run?~~ —
      it does not have to: the artifact is `run.md` in the run workdir, and the plan's lifecycle
      `status:` is mirrored onto `plans/{slug}.md` from the machine's edges.
- [x] ~~Does the playbook still call `booping transition` for status moves?~~ — no. `booping
      playbook-transition` on this machine owns every move; the plan-status mirror, the
      `sprints.md` render and the vault commit are playbook-local `_scripts/` hooks on its edges.
- [x] ~~Does the machine cover the `backlog → in-spec` entry edge?~~ — no. It starts at
      `in-spec`; `backlog` stays outside it as the parking status for plans to groom later.
- [x] ~~Which steps read the vault's `lessons/`?~~ — none declare it. Lessons are injected by the
      renderer from the playbook's `_lessons/` dirs; steps carry nothing about them.
- [x] ~~Cross-review return-contract shape?~~ — findings-only confirmed: `- CRITICAL|RISK|NOTE:
      {finding} — {plan section}` lines or the literal `no findings`, nothing else (lesson
      0007); wording is locked in the `draft-plan` step spec, never negotiated mid-run.
- [x] ~~Accept the two costs the vault-as-workdir mechanism carries, or change one of them?~~ —
      rejected, option (a) taken instead: a workdir-local `run.md` machine, the plan stamped
      from its edges. Both costs disappear with it — the `plan` subgraph dissolves back into a
      flat eight-step graph, and `playbook-state` reports one `run.md` per workdir instead of
      every plan in the vault.
