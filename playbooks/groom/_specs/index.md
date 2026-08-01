---
status: done
reviewed_at: 20260731 19:04
playbook_yaml_reviewed_at: 20260731 19:10
regress: skip
---
# groom — Decomposition

Shape a feature, bug or refactor into a specified, estimated, user-approved plan. Intake frames
the request, challenges scope and records whether the user asked for deep web research; the
user's answers to the scope questions are the confirmation — no separate confirm gate. Research
runs next: blast radius in the codebase always, external practice on the web only when the user
requested it — the skip is mechanical, decided at intake, never judged by an agent. Design
settles architecture with the user in conversation: trade-off calls are asked and answered
in-step, with no blocking review status. The plan is written into the plan directory and
cross-reviewed in place; a re-decomposition pass refines whatever came out oversized — and skips
outright when nothing did; the novel, load-bearing external references are verified against
upstream docs; present is the run's **single review gate** — a human-targeted approval summary
over the full plan, and the handoff to `/develop`. The user first reads the plan there, after
refinement — never a draft still carrying oversized tasks. Conditional edges do not exist in the
framework, so optional steps always run and record a skip note when they have nothing to do.

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

One slug names the whole run: `{YYYYMMDD}-{kebab-title}` — the same format the `/groom` skill
mints, converged deliberately so plans look the same however they were groomed. The plan is a
**directory**, `plans/{slug}/` in the vault, and that directory is the run workdir: the plan and
the run's working files live together, and `_runs/` is gone. The machine's first transition
bootstraps `index.md` there with the run status; `intake` fills the framing into it and creates
`plan.md` beside it.

Two files carry status, and the split is deliberate. `index.md` is the machine's artifact: its
`status:` is the **run's** position, what `booping playbook-state` reports and what a resumed
run reads. `plan.md` carries the **plan's** lifecycle `status:` — the one `/develop`,
`sprints.md` and `/chat` read — mirrored onto it from the machine's edges. The mirror runs
through playbook-local `_scripts/` hooks: a script gets `BOOPING_WORKDIR` / `BOOPING_ARTIFACT`,
derives the slug from the workdir basename and the vault as the workdir's `../..` (or via
`booping config-get home_dir`). The same scripts carry the two side effects `booping transition`
used to bring — the `sprints.md` render and the vault commit.

The machine is groom's own subset of the plan lifecycle: it starts at `in-spec`, passes through
`awaiting-plan-review`, and ends at `ready-for-dev` where develop's subset picks up. `backlog`
stays outside it, the parking status for plans to groom later. The playbook never calls
`booping transition`; every move is a `booping playbook-transition` on this machine.

Three files bound the run's artifacts. `plan.md` is the executable plan. `index.md` is the run's
main artifact — one evolving document whose sections the steps own (framing, blast radius,
design, refinement, references, approval), each revised in place on a loopback, never appended
to. `research.md` exists only when the user requested web research. There are no per-step
artifact files beyond these. The runner also records the id of each agent it delegates to in
`index.md`, so a loopback resumes the same agent with its context intact instead of spawning a
fresh one.

Step prompts carry `summary` frontmatter (plus `agent` and `review_gate`); `inputs`/`outputs`
are dropped — the runner operates from step summaries and these specs' contracts. `agent:` is
null on every step: inline steps run in the runner's context, and assisted steps delegate their
heavy work to the researcher agent the configuration maps, not to a step agent.

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

Delegation levels (definitions to be settled into playbook-authoring):

- **inline** (R) — the runner renders the step and performs its instructions itself, in the main
  context.
- **assisted** (RnA) — the runner renders and owns the step; the heavy work (bulk reads, web
  research) is delegated to a configured agent that returns a compressed summary, keeping the
  runner's context clean. The runner decides *what* is researched; the agent only executes.
- **detached** (SA) — the step's agent fetches and performs the step body itself; the runner never
  reads the instructions and operates on the step summary alone. Parallel track — no groom step
  uses it today.

| Step              | Summary                                                                                                                                                                                                                                                                             | Artifact                                                                                               | Gate                                                                                                               | Delegation                              | Spec                                     |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------ | --------------------------------------- | ---------------------------------------- |
| intake            | restate the request, classify the task type, challenge scope, and record whether the user asked for deep web research; adopt an existing parked plan when the user names one; create the plan directory                                                                             | `plans/{slug}/index.md` — framing section; `plans/{slug}/plan.md` — created, identity frontmatter only | the user answers the scope questions — clear intent is enough, no separate confirm                                 | inline                                  | [spec](steps/intake/index.md)            |
| research-codebase | map the blast radius — files, modules, integrations, external surfaces — and the prior art and conventions the work must follow; targeted web fact-checks allowed, local ground truth first                                                                                         | `## Blast radius` section of `index.md`                                                                | none — reviewed through the design                                                                                 | assisted — researcher agent from config | [spec](steps/research-codebase/index.md) |
| research-web      | when the user requested it, gather current best practice, competing approaches and known pitfalls with sources; otherwise record the skip — the decision is intake's, never judged here                                                                                             | `plans/{slug}/research.md` when requested; otherwise a skip line in `index.md`                         | none — reviewed through the design                                                                                 | assisted — researcher agent from config | [spec](steps/research-web/index.md)      |
| design            | settle architecture, pattern choice, data / API / config surface changes, alternatives and risks with the user in conversation; every trade-off that is the user's to call is asked and answered in-step                                                                            | `## Design` section of `index.md` — approach, surface changes, alternatives, settled trade-offs, risks | none as a status — alignment happens in conversation during the step                                               | inline                                  | [spec](steps/design/index.md)            |
| draft-plan        | pick the plan template matching the dominant surface and write the plan against its Plan Body — milestones, tasks with DoD and Verify, story points, `summary:` frontmatter — verify against the Quality Checklist; hand the draft to the cross-review agent when one is configured | `plans/{slug}/plan.md` — body written, cross-review findings folded in, deferrals recorded             | none — the plan is refined once more before the user reads it                                                      | inline                                  | [spec](steps/draft-plan/index.md)        |
| decompose-work    | refine the written plan against the sizing thresholds: re-decompose oversized tasks, re-sum totals, flag a split candidate past the split threshold; skip when nothing is oversized                                                                                                 | `plans/{slug}/plan.md` — refined; `## Refinement` section of `index.md`                                | none — the user's first read happens at present                                                                    | inline                                  | [spec](steps/decompose-work/index.md)    |
| verify-references | check the novel, load-bearing external references the plan names against current upstream docs and correct what is wrong; well-known stable syntax is not re-verified, and sources `research.md` already dated are reused                                                           | `## References` section of `index.md`; corrections folded into `plan.md`                               | none — corrections surface at present                                                                              | assisted — researcher agent from config | [spec](steps/verify-references/index.md) |
| present           | assemble the human-targeted approval summary — approach, milestones, SP totals, plan path, check outcomes — recommend a split when the total passes the threshold; offer a plan branch when the vault is repo-local                                                                 | `## Approval` section of `index.md`                                                                    | the run's single review gate: explicit user approval over the summary and the full plan; change requests loop back | inline                                  | [spec](steps/present/index.md)           |

## States

One machine, `run` — a **procedure tracker** whose artifact is `index.md` in the plan directory;
its superstates name the plan-lifecycle status mirrored onto `plan.md`, and playbook-local
`_scripts/` hooks on the boundary-crossing edges carry that mirror, the `sprints.md` render and
the vault commit. Full chart — inventory, transitions, script contracts: [states](states.md).

## Questions

- [x] ~~How does the machine's `artifact:` reach a plan whose filename is only known mid-run?~~ —
      it does not have to: the artifact is `index.md` in the plan directory, and the plan's
      lifecycle `status:` is mirrored onto `plan.md` from the machine's edges.
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
      superseded: the plan is now a directory, `plans/{slug}/`, which is also the run workdir;
      the machine's artifact is `index.md` there.
- [ ] Plan-as-directory breaks `Plan.load_all`'s `plans/*.md` glob and every consumer expecting
      a plan *file* (`/develop`, `sprints.md`, `/chat`, parked stubs) — the loader change is
      settled in the groom run for this respec.
