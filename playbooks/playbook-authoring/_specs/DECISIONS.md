# Decisions

- `[2026-07-29 19:06]` Files mode preferred for every step — on-disk artifacts restart and
  track a run.
- `[2026-07-29 19:06]` Manifest written early, right after `decompose`, body as a guide; the
  final `smoke-optimizer` gate reconciles it against the steps as built.
- `[2026-07-29 19:06]` `fixtures` writes real files into `<name>/<step>/_fixtures/`, not a
  spec section.
- `[2026-07-29 19:06]` Build is per step, end-to-end, as one `step-pipeline` subgraph;
  instances may run in parallel.
- `[2026-07-29 19:06]` `regress-optimizer` is per step; the run-or-skip decision is made once
  per playbook run, user can flip it manually.
- `[2026-07-29 19:06]` `smoke-optimizer` may fix a wrong suite check, not only the prompt —
  the confirmed example IS the contract.
- `[2026-07-29 19:06]` Model column is `model:effort`, default `opus-5:medium`; deviate only
  where another tier clearly fits — cheap for the user to flip at review.
- `[2026-07-29 19:06]` Rewriting the two v2 suites (`decompose`, `eval-scope`) from text mode
  to files mode is part of the build.
- `[2026-07-29 19:44]` Tests before fixtures: `llm-tests` defines what is checked, `fixtures`
  materializes what the confirmed rows name. Success case first, traps by offer — the offer
  lives in `llm-tests`.
- `[2026-07-29 20:02]` A step's specs are a directory: `_specs/steps/<step>/{index,test-plan}.md`
  — tests per step, not one shared file.
- `[2026-07-29 20:02]` test-plan.md covers BOTH tiers; the tier column decides implementation
  (smoke → script assert, regress → judge rubric). Rows are concrete — expected values
  inline, pinned by the fixture. Smoke is no longer implicitly derived from the example.
- `[2026-07-29 20:02]` Brief's Artifact home is a bare path, nothing else.
- `[2026-07-29 22:15]` Contracts are five bullets: Needs / Value / Output files / Harness
  return / Review gate. Needs is INFORMATION, artifact-blind — never upstream step names or
  artifact paths; the harness assembles each item from step returns, artifacts or user
  input. Output files stay concrete paths. Interview is skippable when the user's input
  already carries what the brief would.
- `[2026-07-30]` Optimizer steps never run evals themselves: the step diagnoses a given run
  report and edits, then returns a `## Next:` command; the harness runs the tier between
  invocations and owns the loop and its bounds (3 reds per check for smoke; baseline →
  verify for regress). No exception to "eval runs are proposed, never launched" at step
  level.
- `[2026-07-31]` Every playbook's state machine exists; the authoring question is its
  persistence tier — ephemeral / minimal / rich. `decompose` records the verdict; `states`
  is always in the graph and acts on it (bails on ephemeral, stamps a confirmation chain on
  minimal, designs in full on rich); the user can override at its gate.
- `[2026-07-31]` `## States` tables carry machine-readable Hooks cells
  (`frontmatter-update …` / `script <name>`); `manifest` translates them verbatim, never
  interprets prose.
- `[2026-07-31]` `manifest` always emits `playbook.yaml` (graph + `state:`/`states:` when
  present); `playbook.md` keeps identity + guide body only. Frontmatter `graph:` is a
  loader-fallback for old playbooks, never newly produced.
- `[2026-07-31]` Confirmation is modeled as a status (awaiting-confirm pattern, hook
  `frontmatter-update confirmed=@now`), and every active phase gets an explicit in-progress
  status so an interrupted run resumes where it stopped.
- `[2026-07-31]` Decisions recording extracted to `record-decision`: dep-free, bootstraps
  `_specs/DECISIONS.md` in wave 1, then re-invoked by the runner out of wave order whenever a
  step return or gate outcome carries a user decision. The file is the only decisions log —
  the index `## Decisions` section is retired; the step stamps `[YYYY-MM-DD HH:MM]` itself
  (`date -u`), enforced by its evals. Log stays append-all; narrowing is a later human pass.
- `[2026-07-31 06:14]` playbook-authoring migrated to playbook.yaml with its own machines:
  `main` on `_specs/index.md` (interviewing → … → building-steps → done), per-instance
  `step` on `_specs/steps/{instance}/index.md` (the pipeline with awaiting-confirm statuses).
  Workdir = the target playbook dir. Machine-artifact frontmatter is harness-owned except
  `confirmed:`, which stays the user's in-file signature the gates check.
- `[2026-07-31 06:49]` re-run the authoring run from decompose; prior shape "in general
  good", with two focuses: 1. update frontmatter, 2. design playbook state machine
- `[2026-07-31 06:49]` legacy run artifacts predate state machines; one-time migration: seed
  `status: interviewing` on `_specs/index.md` via `booping frontmatter-update`, all further
  moves via `booping playbook-transition` only
- `[2026-07-31 06:52]` state machine: rich — two persisted machines (`main` on
  `_specs/index.md`, per-instance `step` on `_specs/steps/{instance}/index.md`); the run
  crosses sessions, parallel step-pipeline instances resume independently, and every
  confirmation is a harness-stamped status rather than honor-system
- `[2026-07-31 06:52]` the graph shape from the prior iteration stands unchanged; this pass
  only makes frontmatter ownership and the state-chart design explicit in the index
- `[2026-07-31 06:52]` `states` appends `## States` and re-opens the index (`confirmed: No`),
  so graph, Steps table and state chart are confirmed together in one review pass
- `[2026-07-31 06:52]` `record-decision` stays outside both machines — dep-free, idempotent
  append, re-invoked out of wave order
- `[2026-07-31 06:58]` no `confirmed:` in frontmatter — confirmation is a status now: transitions out of `awaiting-*-confirm` statuses (with their `*_confirmed=@now` stamps) replace the in-file flip; resolves the fixtures/prompt/suite signing question too
- `[2026-07-31 06:59]` confirmation is the transition out of an `awaiting-*-confirm` status (user signals in chat, harness moves status and stamps `*_confirmed`)
- `[2026-07-31 06:59]` fixtures / prompt / suite get no signable marker of their own — their confirmations land as status transitions on `_specs/steps/<step>/index.md`
- `[2026-07-31 07:08]` confirmed and brief_confirmed-style stamps look redundant — need a hook that sets reviewed_at dates on specific files; reviewed_at sits on the reviewed file itself, not on the main state artifact
- `[2026-07-31 07:13]` hook vocabulary — path-target extension `frontmatter-update <path> <key>=<val>` (workdir-relative, `{instance}` interpolated) chosen over `script` hooks; implies a booping framework change in `dispatch_frontmatter_update` / `_parse_pairs`
- `[2026-07-31 07:13]` regress persistence settled — `regress: run|skip` on `_specs/index.md`, written by the `step` machine's two `smoke-greening` exit edges; asked once when absent, read on resume
- `[2026-07-31 07:13]` stamps retired — all `*_confirmed=@now`, `smoke_green=@now`, `completed=@now` on state artifacts; the status transition carries fact and time
- `[2026-07-31 07:13]` `reviewed_at` fires only where the reviewed subject is a single frontmattered markdown file (`_specs/brief.md`, `playbook.md`, `test-plan.md`, `prompt.md`); decomposition/states/spec/fixtures/suite gates get no stamp
- `[2026-07-31 07:13]` statuses added — `awaiting-suite-confirm`, `smoke-blocked`, `awaiting-brief-confirm` promoted to its own status; rework loopbacks on every `awaiting-*` status plus `awaiting-states-confirm → decomposing`
- `[2026-07-31 07:23]` state machines extracted into their own file `_specs/states.md`; index links them right after the graph yaml fence (no subsection), and the `states` step's artifact is now `_specs/states.md`
- `[2026-07-31 07:31]` rule — each artifact that must be reviewed must have `reviewed_at`; the four gate exemptions (decomposition, states, spec, fixtures/suite) are overruled
- `[2026-07-31 07:33]` rule applied — every `awaiting-*-confirm` exit stamps `reviewed_at=@now`, one hook per reviewed file: own-artifact form where the reviewed file IS the machine's artifact (decomposition and spec gates), path-target form otherwise (`_specs/brief.md`, `_specs/states.md`, `playbook.md`, `test-plan.md`, `prompt.md`); `_specs/states.md` gains a frontmatter block the first time its gate fires; the states gate carries two hooks (states.md + the re-confirmed index); a re-review overwrites `reviewed_at`
- `[2026-07-31 07:33]` no-frontmatter-slot compromise — a reviewed subject that cannot legally carry frontmatter stamps `<subject>_reviewed_at=@now` on the machine's own state artifact: `fixtures_reviewed_at` and `suite_reviewed_at` on `_specs/steps/{instance}/index.md`, `playbook_yaml_reviewed_at` on `_specs/index.md`. Rejected alternatives: stamping the fixture files themselves (mutating a fixture corrupts the artifact under review and the checks pinned to it), a `---` block on `promptfooconfig.yaml` / `tests.yaml` / `playbook.yaml` (turns a parsed YAML file into two documents and breaks its loader), a `_fixtures/README.md` sidecar (invented structure). This is the rule's only compromise; retired stamps stay retired
- `[2026-07-31 08:06]` explicit paths everywhere in hooks — the pathless own-artifact `frontmatter-update` form is dropped; every hook names its target file
- `[2026-07-31 08:34]` legacy `brief_confirmed` / `decomposition_confirmed` stamps removed from `_specs/index.md` frontmatter — retired vocabulary; state artifact carries only `status:` (plus future `reviewed_at` / `regress:` / compromise stamps)
- `[2026-07-31 08:44]` legacy migration completed — all 12 `_specs/steps/*/index.md` seeded `status: spec-ing`, retired `confirmed:` stripped from step specs, test-plans and brief; `_specs/brief.md` stamped `reviewed_at` (its review already passed)
- `[2026-07-31 08:44]` manifest rewritten from the new design — `playbook.yaml` carries the two-machine chart verbatim (explicit-path hooks, `superstates.terminal`), `playbook.md` preamble rewritten to the no-`confirmed:` convention
- `[2026-07-31 09:50]` step `inputs:` describe the INFORMATION a step needs to operate, never specific files — a step may run in another context where those files don't exist; the harness resolves each need and may recommend the step-related files when supplying it
- `[2026-07-31 10:13]` decompose's Steps table gains an Inputs column — compact, `;`-separated, artifact-blind information per step, reviewed by the user at the decomposition gate; step specs seed their Needs from these cells (disagreement → Questions item, never silent divergence)
