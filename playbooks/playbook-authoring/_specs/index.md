---
status: awaiting-manifest-confirm
---
# playbook-authoring — Decomposition

Turn a procedure description into a working playbook. An interview pins the goal, the success
shape and where process artifacts live; `decompose` and `states` set up the tree and its run
chart, `manifest` writes them out early, then one `step-pipeline` per authored step carries it
from contract to green suite. Files mode throughout: every review point is an on-disk artifact,
so a run restarts from disk. Run state persists on two artifacts — `_specs/index.md` and each
`_specs/steps/<step>/index.md`; on both, `status:` and the stamped keys belong to
`booping playbook-transition` and steps preserve them. Confirmation is not a key of its own: it
is the transition out of an `awaiting-*-confirm` status — the user signals in chat and the
harness moves the status. The state artifacts carry `status:` (plus the run-level `regress:`
call); every confirm gate stamps `reviewed_at` on the file the user actually reviewed, with no
exemption — where the reviewed subject cannot carry frontmatter (the fixtures directory, the
suite YAML, `playbook.yaml`) the stamp lands on the state artifact as `<subject>_reviewed_at`.

## Graph

```yaml
graph:
  record-decision: []
  interview: []
  decompose: [interview]
  states: [decompose]
  manifest: [decompose, states]
  step-pipeline:
    dependencies: [manifest]
    repeat: once per step produced by decompose; instances may run in parallel
    graph:
      step-spec: []
      llm-tests: [step-spec]
      fixtures: [llm-tests]
      step-prompt: [fixtures]
      step-suite: [step-prompt]
      smoke-optimizer: [step-suite]
      regress-optimizer: [smoke-optimizer]
```

State machines: [main](states.md#main) · [step](states.md#step)

## Steps

| Step              | Summary                                                                                                                                                                            | Artifact                                                                                 | Gate                                                                            | Model           | Spec                                     |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- | --------------- | ---------------------------------------- |
| record-decision   | append every user decision the runner relays to the decisions log, timestamped; bootstrap in wave 1, then re-invoked out of wave order                                             | `_specs/DECISIONS.md`                                                                    | none — mechanical log, outside both machines                                    | haiku-4-5:low   | [spec](steps/record-decision/index.md)   |
| interview         | infer goal, success shape and artifact home from what the user gave; ask only the gaps                                                                                             | `_specs/brief.md` — goal + success + artifact home + wishes                              | confirm brief                                                                   | opus-5:medium   | [spec](steps/interview/index.md)         |
| decompose         | break the procedure into steps, judge the run-state persistence tier, surface the open questions                                                                                   | `_specs/index.md` — this index; harness frontmatter preserved                            | answer Questions, confirm decomposition                                         | opus-5:high     | [spec](steps/decompose/index.md)         |
| states            | design the run's state chart from the tier verdict — machines, statuses, gates, machine-readable hooks — or bail on ephemeral                                                      | `_specs/states.md` — the machines, linked from this index                                | confirm machine granularity, re-confirm index (`states` re-opens it for review) | opus-5:high     | [spec](steps/states/index.md)            |
| manifest          | write the playbook's manifest early — structure and state chart as `playbook.yaml` (hooks copied verbatim), identity and guide body as `playbook.md`; model and root made concrete | `<name>/playbook.yaml` + `playbook.md`                                                   | confirm name, trigger, graph, states, model, root                               | sonnet-5:medium | [spec](steps/manifest/index.md)          |
| step-spec         | write one step's contract and an example of its artifact — the example IS the shape                                                                                                | `_specs/steps/<step>/index.md` — contract + example; also this instance's state artifact | refine, then confirm contract + example                                         | opus-5:medium   | [spec](steps/step-spec/index.md)         |
| llm-tests         | pin every check the step's suite will run as tiered rows — success case first, traps by offer                                                                                      | `_specs/steps/<step>/test-plan.md` — fixture, tier, title, check logic                   | confirm the step's test rows                                                    | opus-5:medium   | [spec](steps/llm-tests/index.md)         |
| fixtures          | materialize the fixtures the confirmed test rows name, as real files                                                                                                               | `<name>/<step>/_fixtures/` — the fixture files                                           | confirm fixtures                                                                | opus-5:medium   | [spec](steps/fixtures/index.md)          |
| step-prompt       | write one step's prompt body and wrapper                                                                                                                                           | `<step>/opus-5.md` + `prompt.md`                                                         | confirm prompt contract                                                         | opus-5:medium   | [spec](steps/step-prompt/index.md)       |
| step-suite        | implement the suite from the step's test-plan.md: smoke rows → script asserts, regress rows → rubrics                                                                              | `<step>/promptfooconfig.yaml` + `tests.yaml`                                             | review tree, trigger runs                                                       | sonnet-5:medium | [spec](steps/step-suite/index.md)        |
| smoke-optimizer   | diagnose a red smoke report, fix the prompt — or a wrong check, the confirmed example is the contract; the harness runs the tier until green                                       | prompt and/or check edits                                                                | green smoke; blocked → user                                                     | opus-5:medium   | [spec](steps/smoke-optimizer/index.md)   |
| regress-optimizer | best effort: read baseline judge failures, tune the prompt; the harness runs baseline and verify                                                                                   | prompt edits                                                                             | run-or-skip decided once per playbook run; user can change the call             | opus-5:medium   | [spec](steps/regress-optimizer/index.md) |

## Questions

- [x] ~~Should the once-per-run regress run-or-skip choice persist on `_specs/index.md` (e.g.
      `regress: run|skip`) so a resumed run does not re-ask, or stay conversational?~~ —
      settled in [states.md](states.md): it persists as `regress: run|skip` on
      `_specs/index.md`, written by the `step` machine's `smoke-greening` exit hooks; a
      resumed run reads the key instead of re-asking, and the user flips it by editing the
      key.
