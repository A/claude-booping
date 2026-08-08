---
status: spec-ing
---

# step-suite

[← index](../../index.md)

## Contract

- **Needs** —
  - the target step name
  - the target step's confirmed contract and example
  - the step's confirmed test plan
  - the step's prompt body as shipped
  - ONE live suite as the pattern to follow — `user-stories/build-index/` (files mode) or
    `user-stories/reshake/` (text mode) — plus the compact conventions below; no reference to
    `docs/eval-checks.md`
- **Value** — implements everything from its confirmed sources: the smoke tier derived from
  the spec's example artifact (its structure becomes the mdcheck rules — no separate shape
  work), the regress rubrics from the step's rows in `_specs/steps/<step>/test-plan.md`, the fixture files
  from the spec's Fixtures section. The result is the running guarantee every later change to
  the prompt must pass.
- **Output files** —
  - `[CREATED] <name>/<step>/promptfooconfig.yaml`
  - `[CREATED] <name>/<step>/tests.yaml`
  - `[CREATED] <name>/<step>/_fixtures/<case>.md`
- **Harness return** — `## Changed:` list; `## Notes:` proposing `just eval-smoke` /
  `just eval-regress` commands — proposed, never executed by this step.
- **Review gate** —
  - the user reviews the tree; the optimizer steps that follow take the suite to green — the
    harness runs the tiers between their invocations

## Conventions (compact, replaces docs/eval-checks.md references)

- Config: the body file as labeled prompt (`file://<model>.md`, never the wrapper), provider
  `file://../../_lib/claude_provider.py` with `mode: step` and `output_mode` per the
  contract, `defaultTest: file://../../_lib/grader.yaml`, `tests: file://tests.yaml`.
  Depth-2 relative paths only.
- Tests: exactly the confirmed sources — one smoke case pinning the example-derived contract,
  one regress case per `test-plan.md` row, same fixture as the row names. Every case
  `metadata: {playbook, step, fixture, tier}`. The example's structure becomes inline mdcheck
  `rules:`; the fixture-agnostic contract is shared smoke↔regress by YAML anchor; a
  fixture's own arithmetic rides in its own small assert. Rubrics are NAMED (`"NAME: …"`)
  after their `test-plan.md` titles. Comments only where an assert cannot speak.
- Fixture: a real corpus — every named trap built in and discoverable, every rubric's demand
  grounded in it.
- The suite is dry-runnable free: parse the YAMLs, run the deterministic asserts against a
  synthetic good output and mutants; `just eval-list` must discover it. Never run an eval.

## Example artifact

```yaml
- description: compose smoke — report contract on the small module
  vars: { input: file://_fixtures/small-module.md }
  metadata: { playbook: mod-review, step: compose, fixture: small-module, tier: smoke }
  assert:
    - &a_contract
      type: javascript
      value: file://../../_lib/asserts/mdcheck.js
      config: { file: 'review\.md$', rules: "- select: H1\n  count: 1" }
```
