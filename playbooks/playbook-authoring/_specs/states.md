# playbook-authoring — State machines

Two machines, both procedure trackers: `main` follows the run, `step` follows one
`step-pipeline` instance. Every hook is the explicit-path form
`frontmatter-update <path> <key>=<val>` — path relative to the run workdir, `{instance}`
interpolated, even when the target is the machine's own artifact. A cell carrying more than one
hook separates them with `;`, in order. booping's current hook parser supports neither the path
token nor `{instance}` interpolation — this form is a prerequisite framework change
(`dispatch_frontmatter_update` / `_parse_pairs`) before `manifest` output runs green.

**Rule — every artifact the user reviews carries `reviewed_at`.** Each exit from an
`awaiting-*-confirm` status stamps `reviewed_at=@now` on what was reviewed, one hook per
reviewed file; no gate is exempt. A re-review overwrites the key. `_specs/brief.md` and
`_specs/states.md` carry no frontmatter block until their gate first fires — `booping
frontmatter-update` creates one.

**The rule's only compromise.** Three subjects cannot legally carry frontmatter: the fixtures
directory (a directory, and stamping the fixture files themselves would mutate the very
artifact under review and break the checks pinned to it), and `promptfooconfig.yaml` /
`tests.yaml` / `playbook.yaml` (a `---` block on a parsed YAML file turns it into two documents
and breaks its loader). Their gates stamp a subject-keyed `<subject>_reviewed_at=@now` on the
machine's own state artifact, explicit path and all — `fixtures_reviewed_at`,
`suite_reviewed_at`, `playbook_yaml_reviewed_at`. That is the whole stamp vocabulary left on the
state artifacts: `*_confirmed`, `smoke_green` and `completed` stay retired.

## main

artifact: `_specs/index.md`

Also carries `regress: run|skip` — run-level, written by the `step` machine (see below), read
on resume — plus its own `reviewed_at` (the index is reviewed at the decomposition and states
gates) and `playbook_yaml_reviewed_at`, the compromise stamp for `playbook.yaml`.

| Superstate | States  |
| ---------- | ------- |
| terminal   | `done`ᵗ |

| State                            | To                               | When                                                                   | Gates                                                        | Hooks                                                                                                                |
| -------------------------------- | -------------------------------- | ---------------------------------------------------------------------- | ------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------- |
| `none`                           | `interviewing`                   | the runner starts the run and bootstraps the index                     |                                                              |                                                                                                                      |
| `interviewing`                   | `awaiting-brief-confirm`         | `interview` wrote `_specs/brief.md`                                    |                                                              |                                                                                                                      |
| `interviewing`                   | `decomposing`                    | the user's input already carried the brief, `interview` was skipped    | the input names goal, success shape and artifact home        |                                                                                                                      |
| `awaiting-brief-confirm`         | `interviewing`                   | the user reworks goal, success shape or artifact home                  |                                                              |                                                                                                                      |
| `awaiting-brief-confirm`         | `decomposing`                    | the user confirms the brief                                            | explicit user confirmation captured — silence never counts   | `frontmatter-update _specs/brief.md reviewed_at=@now`                                                                |
| `decomposing`                    | `awaiting-decomposition-confirm` | `decompose` wrote the graph, the Steps table and the open Questions    |                                                              |                                                                                                                      |
| `awaiting-decomposition-confirm` | `decomposing`                    | the user's answers or rework request reshape the graph                 |                                                              |                                                                                                                      |
| `awaiting-decomposition-confirm` | `designing-states`               | the user confirms the decomposition                                    | explicit user confirmation captured; no open Questions items | `frontmatter-update _specs/index.md reviewed_at=@now`                                                                |
| `designing-states`               | `awaiting-states-confirm`        | `states` wrote `_specs/states.md` and linked it from the index         |                                                              |                                                                                                                      |
| `designing-states`               | `manifesting`                    | ephemeral verdict — `states` returned the skip note, nothing to review |                                                              |                                                                                                                      |
| `awaiting-states-confirm`        | `designing-states`               | the user wants different machines, statuses, gates or hooks            |                                                              |                                                                                                                      |
| `awaiting-states-confirm`        | `decomposing`                    | the user's rework reshapes the graph or the Steps table                |                                                              |                                                                                                                      |
| `awaiting-states-confirm`        | `manifesting`                    | the user confirms the state chart and re-confirms the index            | explicit user confirmation captured                          | `frontmatter-update _specs/states.md reviewed_at=@now; frontmatter-update _specs/index.md reviewed_at=@now`          |
| `manifesting`                    | `awaiting-manifest-confirm`      | `manifest` wrote `playbook.yaml` and `playbook.md`                     |                                                              |                                                                                                                      |
| `awaiting-manifest-confirm`      | `manifesting`                    | the user wants a different name, trigger, model or destination root    |                                                              |                                                                                                                      |
| `awaiting-manifest-confirm`      | `building-steps`                 | the user confirms name, trigger, graph, states, model and root         | explicit user confirmation captured                          | `frontmatter-update playbook.md reviewed_at=@now; frontmatter-update _specs/index.md playbook_yaml_reviewed_at=@now` |
| `building-steps`                 | `done`ᵗ                          | every `step-pipeline` instance reached its terminal                    | every `_specs/steps/*/index.md` carries `status: done`       |                                                                                                                      |

## step

artifact: `_specs/steps/{instance}/index.md`

The run-or-skip regress call is asked once — when `_specs/index.md` carries no `regress:` key;
the `smoke-greening` exit hooks persist the answer for every later instance and every resume.
The instance artifact also carries its own `reviewed_at` (it is what the spec gate reviews)
plus `fixtures_reviewed_at` and `suite_reviewed_at`, the compromise stamps for the fixtures
directory and the suite YAML.

| Superstate | States  |
| ---------- | ------- |
| terminal   | `done`ᵗ |

| State                       | To                          | When                                                                                                      | Gates                                                      | Hooks                                                                           |
| --------------------------- | --------------------------- | --------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------- | ------------------------------------------------------------------------------- |
| `none`                      | `spec-ing`                  | the instance starts and the runner bootstraps its spec artifact                                           |                                                            |                                                                                 |
| `spec-ing`                  | `awaiting-spec-confirm`     | `step-spec` wrote the contract and the example artifact                                                   |                                                            |                                                                                 |
| `awaiting-spec-confirm`     | `spec-ing`                  | the user reworks the contract or the example                                                              |                                                            |                                                                                 |
| `awaiting-spec-confirm`     | `test-planning`             | the user confirms the contract and example                                                                | explicit user confirmation captured — silence never counts | `frontmatter-update _specs/steps/{instance}/index.md reviewed_at=@now`          |
| `test-planning`             | `awaiting-tests-confirm`    | `llm-tests` wrote the tiered test rows                                                                    |                                                            |                                                                                 |
| `awaiting-tests-confirm`    | `test-planning`             | the user drops, adds or re-tiers rows                                                                     |                                                            |                                                                                 |
| `awaiting-tests-confirm`    | `fixturing`                 | the user confirms the test rows                                                                           | explicit user confirmation captured                        | `frontmatter-update _specs/steps/{instance}/test-plan.md reviewed_at=@now`      |
| `fixturing`                 | `awaiting-fixtures-confirm` | `fixtures` materialized the files the confirmed rows name                                                 |                                                            |                                                                                 |
| `awaiting-fixtures-confirm` | `fixturing`                 | the user wants fixture edits or additions                                                                 |                                                            |                                                                                 |
| `awaiting-fixtures-confirm` | `prompting`                 | the user confirms the fixture set                                                                         | explicit user confirmation captured                        | `frontmatter-update _specs/steps/{instance}/index.md fixtures_reviewed_at=@now` |
| `prompting`                 | `awaiting-prompt-confirm`   | `step-prompt` wrote the prompt body and its wrapper                                                       |                                                            |                                                                                 |
| `awaiting-prompt-confirm`   | `prompting`                 | the user reworks the prompt                                                                               |                                                            |                                                                                 |
| `awaiting-prompt-confirm`   | `suiting`                   | the user confirms the prompt contract                                                                     | explicit user confirmation captured                        | `frontmatter-update {instance}/prompt.md reviewed_at=@now`                      |
| `suiting`                   | `awaiting-suite-confirm`    | `step-suite` implemented `promptfooconfig.yaml` and `tests.yaml`                                          |                                                            |                                                                                 |
| `awaiting-suite-confirm`    | `suiting`                   | the user wants suite changes after reading the tree                                                       |                                                            |                                                                                 |
| `awaiting-suite-confirm`    | `smoke-greening`            | the user reviewed the tree and triggered the smoke run                                                    | explicit user confirmation captured                        | `frontmatter-update _specs/steps/{instance}/index.md suite_reviewed_at=@now`    |
| `smoke-greening`            | `smoke-blocked`             | the harness hit the loop bound — 3 reds on one check                                                      |                                                            |                                                                                 |
| `smoke-greening`            | `regressing`                | the harness reports the smoke tier green and the run's regress call is `run`                              | latest smoke report green                                  | `frontmatter-update _specs/index.md regress=run`                                |
| `smoke-greening`            | `done`ᵗ                     | the harness reports the smoke tier green and the run's regress call is `skip`                             | latest smoke report green                                  | `frontmatter-update _specs/index.md regress=skip`                               |
| `smoke-blocked`             | `smoke-greening`            | the user resolves the block — guidance, a corrected check or a fixture fix                                |                                                            |                                                                                 |
| `regressing`                | `done`ᵗ                     | `regress-optimizer` finished the baseline → verify pass, or the user calls the tier off for this instance |                                                            |                                                                                 |
