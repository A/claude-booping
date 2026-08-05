# Author a Playbook

Your goal is a new playbook under a playbook root: steps a fresh, context-isolated agent can
run, review gates that catch drift while review is still cheap, and eval suites that guard
each step's contract. The method is `_playbooks/docs/evals.md` — when a step's instructions
and that document disagree, the document wins.

Run state is harness-managed. The workdir is the target playbook dir `<root>/<slug>/`
(created before the first transition); the machine artifacts are `_specs/index.md` and
`_specs/steps/<step>/index.md`. Sub-agents writing a machine artifact preserve its
frontmatter and never write `status:`, `reviewed_at`, or any stamp — `booping
playbook-transition` is the only writer. There is no `confirmed:` key: confirmation is the
user's explicit chat signal at a gate, captured as the transition out of an
`awaiting-*-confirm` status — never run past a gate on silence. The transition's exit hooks
then stamp `reviewed_at` with the date macro (or, for a subject that cannot carry frontmatter, the
`<subject>_reviewed_at` compromise stamp) on the file that was reviewed.

`record-decision` runs once in wave 1 as bootstrap, then OUT of wave order: re-invoke it
whenever a step's return or a review-gate outcome carries a user decision, passing the
decision summaries verbatim. `_specs/DECISIONS.md` is the only decisions log — no step
writes a `## Decisions` section anywhere else.

Interview is skippable when the user's input already carries what the brief would. Two
decisions travel with every wave after `decompose`: the **target model** (default
`opus:medium`) and the **destination root** (default the global `_playbooks/`); ask both in
one question after the decomposition is confirmed — a sub-agent that does not receive them
will guess.

No step of this playbook runs an eval itself. The harness runs the smoke tier between
`smoke-optimizer` invocations — re-invoke with the fresh report while red; the same check red
three attempts without progress goes to the user — and runs the regress baseline before
`regress-optimizer` and its verify pass after (skip decided once per run, user can flip). All
other eval runs are proposed to the user, never launched.

## Playbook Steps

Execute the steps in the most effective order considering their dependencies.

| Step | Dependencies | Summary | Review gate |
| --- | --- | --- | --- |
| `record-decision` | — | Append every user decision the runner relays to _specs/DECISIONS.md, timestamped; bootstrap the file on first call. | none — mechanical log; the user narrows the file later |
| `interview` | — | Infer the new playbook's slug, goal, success shape and artifact home from the user's description, asking only about real gaps. | While Questions come back the user answers them; once complete the user refines and confirms the brief in-file |
| `decompose` | `interview` | Break the procedure into a light decomposition index — graph, step table, decisions, open questions — the user models against before any detail exists. | The user answers the Questions in-file, edits the table and graph directly where they disagree, and confirms |
| `states` | `decompose` | Design the playbook's persisted state machines from decompose's tier verdict — or skip on ephemeral — as a States chart the manifest translates verbatim. | The user confirms machine granularity — statuses, gates, hooks, artifacts — in-file and re-confirms the index |
| `manifest` | `decompose`, `states` | Write the playbook's manifest early — identity, trigger, and the confirmed graph verbatim; body as a lean guide the renderer completes. | The user confirms name, trigger, graph, target model and destination root before any per-step file is written |
| `step-pipeline` *(subgraph)* | `manifest` | once per step produced by decompose; instances may run in parallel | — |
| `step-spec` *(in step-pipeline)* | — | Write one step's contract and a concrete example of its artifact — the example IS the shape the suite will pin. | The user refines and confirms the spec in-file: the contract bullets and, for a markdown artifact, the example |
| `llm-tests` *(in step-pipeline)* | `step-spec` | Pin every check the step's suite will run as tiered table rows — success cases first, traps by offer. | The user extends, narrows or strikes the rows, then confirms them |
| `fixtures` *(in step-pipeline)* | `llm-tests` | Materialize the fixtures the confirmed test rows name, as real files the step's suite runs against. | The user reads the fixture files themselves and confirms the set |
| `step-prompt` *(in step-pipeline)* | `fixtures` | Write one step's prompt body and Jinja wrapper from its confirmed spec — seed quality, refined later by the optimizers. | The user reads the body and confirms the contract it states |
| `step-suite` *(in step-pipeline)* | `step-prompt` | Implement the suite from the step's confirmed test plan — smoke rows as script asserts, regress rows as named rubrics. | The user reviews the tree; the optimizer steps that follow take the suite to green |
| `smoke-optimizer` *(in step-pipeline)* | `step-suite` | Diagnose a red smoke report against the confirmed example and edit the guilty side — prompt or check; the harness runs the tier between invocations. | None on green — the harness loops run → re-invoke; the same check red three attempts without progress, or a failure the example does not decide, goes to the user |
| `regress-optimizer` *(in step-pipeline)* | `smoke-optimizer` | Read the baseline judge failures and tune the prompt toward the confirmed rubrics — prompt edits only; the harness runs baseline and verify. | None on green — bounded to baseline → edits → one verify run; residual reds ship only by explicit user acceptance; a suspected-wrong rubric goes to the user |

## State

Run state is persisted in artifacts under the run workdir. Only `booping playbook-transition` writes it — never hand-edit an artifact's `status`.

Read the whole run's frontier before starting or resuming:

```
booping playbook-state playbook-authoring --workdir <run workdir>
```

### State: main

- Referenced by: outer graph
- Artifact: `_specs/index.md` (relative to the run workdir)
- Initial status: `interviewing`
- Advance: `booping playbook-transition playbook-authoring <to> --workdir <run workdir>`

| Status | To | When | Gates |
| --- | --- | --- | --- |
| `interviewing` | `awaiting-brief-confirm` | interview wrote _specs/brief.md | — |
| `interviewing` | `decomposing` | the user's input already carried the brief, interview was skipped | the input names goal, success shape and artifact home |
| `awaiting-brief-confirm` | `interviewing` | the user reworks goal, success shape or artifact home | — |
| `awaiting-brief-confirm` | `decomposing` | the user confirms the brief | explicit user confirmation captured — silence never counts |
| `decomposing` | `awaiting-decomposition-confirm` | decompose wrote the graph, the Steps table and the open Questions | — |
| `awaiting-decomposition-confirm` | `decomposing` | the user's answers or rework request reshape the graph | — |
| `awaiting-decomposition-confirm` | `designing-states` | the user confirms the decomposition | explicit user confirmation captured; no open Questions items |
| `designing-states` | `awaiting-states-confirm` | states wrote _specs/states.md and linked it from the index | — |
| `designing-states` | `manifesting` | ephemeral verdict — states returned the skip note, nothing to review | — |
| `awaiting-states-confirm` | `designing-states` | the user wants different machines, statuses, gates or hooks | — |
| `awaiting-states-confirm` | `decomposing` | the user's rework reshapes the graph or the Steps table | — |
| `awaiting-states-confirm` | `manifesting` | the user confirms the state chart and re-confirms the index | explicit user confirmation captured |
| `manifesting` | `awaiting-manifest-confirm` | manifest wrote playbook.yaml and playbook.md | — |
| `awaiting-manifest-confirm` | `manifesting` | the user wants a different name, trigger, model or destination root | — |
| `awaiting-manifest-confirm` | `building-steps` | the user confirms name, trigger, graph, states, model and root | explicit user confirmation captured |
| `building-steps` | `done` | every step-pipeline instance reached its terminal | every _specs/steps/*/index.md carries status: done |
| `done` | *(terminal)* | — | — |

### State: step

- Referenced by: subgraph `step-pipeline`
- Artifact: `_specs/steps/{instance}/index.md` (relative to the run workdir)
- Initial status: `spec-ing`
- Advance: `booping playbook-transition playbook-authoring <to> --state step --instance <slug> --workdir <run workdir>`

| Status | To | When | Gates |
| --- | --- | --- | --- |
| `spec-ing` | `awaiting-spec-confirm` | step-spec wrote the contract and the example artifact | — |
| `awaiting-spec-confirm` | `spec-ing` | the user requests changes | — |
| `awaiting-spec-confirm` | `test-planning` | the user confirms the contract and example | explicit user confirmation captured — silence never counts |
| `test-planning` | `awaiting-tests-confirm` | llm-tests wrote the tiered test rows | — |
| `awaiting-tests-confirm` | `test-planning` | the user drops, adds or re-tiers rows | — |
| `awaiting-tests-confirm` | `fixturing` | the user confirms the test rows | explicit user confirmation captured |
| `fixturing` | `awaiting-fixtures-confirm` | fixture files written | — |
| `awaiting-fixtures-confirm` | `fixturing` | the user wants fixture edits or additions | — |
| `awaiting-fixtures-confirm` | `prompting` | the user confirms the fixture set | explicit user confirmation captured |
| `prompting` | `awaiting-prompt-confirm` | step-prompt wrote the prompt body and its wrapper | — |
| `awaiting-prompt-confirm` | `prompting` | the user reworks the prompt | — |
| `awaiting-prompt-confirm` | `suiting` | the user confirms the prompt contract | explicit user confirmation captured |
| `suiting` | `awaiting-suite-confirm` | step-suite implemented promptfooconfig.yaml and tests.yaml | — |
| `awaiting-suite-confirm` | `suiting` | the user wants suite changes after reading the tree | — |
| `awaiting-suite-confirm` | `smoke-greening` | the user reviewed the tree and triggered the smoke run | explicit user confirmation captured |
| `smoke-greening` | `smoke-blocked` | the harness hit the loop bound — 3 reds on one check | — |
| `smoke-greening` | `regressing` | the harness reports the smoke tier green and the run's regress call is run | latest smoke report green |
| `smoke-greening` | `done` | the harness reports the smoke tier green and the run's regress call is skip | latest smoke report green |
| `smoke-blocked` | `smoke-greening` | the user resolves the block — guidance, a corrected check or a fixture fix | — |
| `regressing` | `done` | regress-optimizer finished the baseline → verify pass, or the user calls the tier off for this instance | — |
| `done` | *(terminal)* | — | — |

## Step: Record Decision

Append every user decision the runner relays to _specs/DECISIONS.md, timestamped; bootstrap the file on first call.

Review gate: stop after this step — "none — mechanical log; the user narrows the file later"; continue only on explicit user confirmation.

Tell a sub-agent — model haiku, effort low — to get its instructions by calling this command: `booping render-playbook playbook-authoring --step record-decision`.

## Step: Interview

Infer the new playbook's slug, goal, success shape and artifact home from the user's description, asking only about real gaps.

Review gate: stop after this step — "While Questions come back the user answers them; once complete the user refines and confirms the brief in-file"; continue only on explicit user confirmation.

Tell a sub-agent — model opus, effort medium — to get its instructions by calling this command: `booping render-playbook playbook-authoring --step interview`.

## Step: Decompose

Break the procedure into a light decomposition index — graph, step table, decisions, open questions — the user models against before any detail exists.

Review gate: stop after this step — "The user answers the Questions in-file, edits the table and graph directly where they disagree, and confirms"; continue only on explicit user confirmation.

Tell a sub-agent — model opus, effort high — to get its instructions by calling this command: `booping render-playbook playbook-authoring --step decompose`.

## Step: States

Design the playbook's persisted state machines from decompose's tier verdict — or skip on ephemeral — as a States chart the manifest translates verbatim.

Review gate: stop after this step — "The user confirms machine granularity — statuses, gates, hooks, artifacts — in-file and re-confirms the index"; continue only on explicit user confirmation.

Tell a sub-agent — model opus, effort high — to get its instructions by calling this command: `booping render-playbook playbook-authoring --step states`.

## Step: Manifest

Write the playbook's manifest early — identity, trigger, and the confirmed graph verbatim; body as a lean guide the renderer completes.

Review gate: stop after this step — "The user confirms name, trigger, graph, target model and destination root before any per-step file is written"; continue only on explicit user confirmation.

Tell a sub-agent — model sonnet, effort medium — to get its instructions by calling this command: `booping render-playbook playbook-authoring --step manifest`.

## Subgraph: step-pipeline

Instructions:
- After: manifest
- Repeat: once per step produced by decompose; instances may run in parallel
- Inner waves: 1. `step-spec` 2. `llm-tests` 3. `fixtures` 4. `step-prompt` 5. `step-suite` 6. `smoke-optimizer` 7. `regress-optimizer`

## Step: Step Spec

Write one step's contract and a concrete example of its artifact — the example IS the shape the suite will pin.

Part of: step-pipeline (repeated)

Review gate: stop after this step — "The user refines and confirms the spec in-file: the contract bullets and, for a markdown artifact, the example"; continue only on explicit user confirmation.

Tell a sub-agent — model opus, effort medium — to get its instructions by calling this command: `booping render-playbook playbook-authoring --step step-spec`.

## Step: Llm Tests

Pin every check the step's suite will run as tiered table rows — success cases first, traps by offer.

Part of: step-pipeline (repeated)

Review gate: stop after this step — "The user extends, narrows or strikes the rows, then confirms them"; continue only on explicit user confirmation.

Tell a sub-agent — model opus, effort medium — to get its instructions by calling this command: `booping render-playbook playbook-authoring --step llm-tests`.

## Step: Fixtures

Materialize the fixtures the confirmed test rows name, as real files the step's suite runs against.

Part of: step-pipeline (repeated)

Review gate: stop after this step — "The user reads the fixture files themselves and confirms the set"; continue only on explicit user confirmation.

Tell a sub-agent — model opus, effort medium — to get its instructions by calling this command: `booping render-playbook playbook-authoring --step fixtures`.

## Step: Step Prompt

Write one step's prompt body and Jinja wrapper from its confirmed spec — seed quality, refined later by the optimizers.

Part of: step-pipeline (repeated)

Review gate: stop after this step — "The user reads the body and confirms the contract it states"; continue only on explicit user confirmation.

Tell a sub-agent — model opus, effort medium — to get its instructions by calling this command: `booping render-playbook playbook-authoring --step step-prompt`.

## Step: Step Suite

Implement the suite from the step's confirmed test plan — smoke rows as script asserts, regress rows as named rubrics.

Part of: step-pipeline (repeated)

Review gate: stop after this step — "The user reviews the tree; the optimizer steps that follow take the suite to green"; continue only on explicit user confirmation.

Tell a sub-agent — model sonnet, effort medium — to get its instructions by calling this command: `booping render-playbook playbook-authoring --step step-suite`.

## Step: Smoke Optimizer

Diagnose a red smoke report against the confirmed example and edit the guilty side — prompt or check; the harness runs the tier between invocations.

Part of: step-pipeline (repeated)

Review gate: stop after this step — "None on green — the harness loops run → re-invoke; the same check red three attempts without progress, or a failure the example does not decide, goes to the user"; continue only on explicit user confirmation.

Tell a sub-agent — model opus, effort medium — to get its instructions by calling this command: `booping render-playbook playbook-authoring --step smoke-optimizer`.

## Step: Regress Optimizer

Read the baseline judge failures and tune the prompt toward the confirmed rubrics — prompt edits only; the harness runs baseline and verify.

Part of: step-pipeline (repeated)

Review gate: stop after this step — "None on green — bounded to baseline → edits → one verify run; residual reds ship only by explicit user acceptance; a suspected-wrong rubric goes to the user"; continue only on explicit user confirmation.

Tell a sub-agent — model opus, effort medium — to get its instructions by calling this command: `booping render-playbook playbook-authoring --step regress-optimizer`.
