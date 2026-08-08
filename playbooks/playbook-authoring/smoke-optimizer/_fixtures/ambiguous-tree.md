The target step is `compose` of the `mod-review` playbook.

Smoke command for the suite: `just eval-smoke -c mod-review/compose/promptfooconfig.yaml`

Latest smoke report (attempt 1):

```
PASS [JS] SECTIONS
FAIL [JS] FINDING-COUNT — mdcheck review.md: SECTION("Findings") > UL > LI: count 3, found 2

1 case, 1 run, 14k tokens, 66s — 0/1 PASS
```

The step's tree:

<file path="mod-review/_specs/steps/compose/index.md">
---
reviewed_at: 20260730 09:00
---

# compose

[← index](../../index.md)

## Contract

- **Needs** —
  - the module files under review
  - the sweep findings, one line each
- **Value** — one review report the user signs off: every genuine finding, each with a fix
  sketch naming the concrete change.
- **Output files** —
  - `[CREATED] review.md`
- **Harness return** — `## Changed:` list; `## Questions:` empty unless a finding cannot be
  judged from the module alone.
- **Review gate** — the user confirms the findings before anything is filed.

## Example artifact

```markdown
# Review — sample-module

## Findings

- `parser.py:12` — `split(" ")` drops everything after the second space; multi-word values
  are truncated. Fix: split with `maxsplit=1` and validate the remainder.

## Verdict

REQUEST CHANGES — 1 finding, 1 blocking.
```
</file>

<file path="mod-review/_specs/steps/compose/test-plan.md">
---
reviewed_at: 20260730 09:00
---

[← index](../../index.md)

# compose — Tests

## Fixtures

| Fixture      | Requirements                                   |
| ------------ | ---------------------------------------------- |
| small-module | three-function auth module with seeded defects |

## Tests

| Fixture      | Tier    | Title         | Check logic                                         |
| ------------ | ------- | ------------- | --------------------------------------------------- |
| small-module | smoke   | SECTIONS      | Findings and Verdict sections present, in order     |
| small-module | smoke   | FINDING-COUNT | Findings reports the module's 3 seeded defects      |
| small-module | regress | GROUNDED-FIX  | each finding's fix sketch names the concrete change |
</file>

<file path="mod-review/compose/opus-5.md">
# compose — review report

You receive a small module and the sweep findings, one line each. Compose the review report
the user will sign off.

Write `review.md`:

- one H1: `# Review — <module>`
- `## Findings` — one bullet per genuine finding: `path:line`, the defect, and a fix sketch
  naming the concrete change
- `## Verdict` — one line: APPROVE or REQUEST CHANGES, with the finding count

Return:

```
## Changed:
- [CREATED] review.md

## Questions:
(empty unless a finding cannot be judged from the module alone)
```
</file>

<file path="mod-review/compose/tests.yaml">
- description: compose smoke — report contract on the small module
  vars:
    input: file://_fixtures/small-module.md
  metadata:
    playbook: mod-review
    step: compose
    fixture: small-module
    tier: smoke
  assert:
    # SECTIONS
    - type: javascript
      value: file://../../_lib/asserts/mdcheck.js
      config:
        file: 'review\.md$'
        rules: |
          - select: H1
            count: 1

          - select: H1 > H2
            ordered: [Findings, Verdict]
            strict: true
    # FINDING-COUNT — the fixture's own arithmetic
    - type: javascript
      value: file://../../_lib/asserts/mdcheck.js
      config:
        file: 'review\.md$'
        rules: |
          - select: SECTION("Findings") > UL > LI
            count: 3

- description: compose regress — fix sketches grounded in the module
  vars:
    input: file://_fixtures/small-module.md
  metadata:
    playbook: mod-review
    step: compose
    fixture: small-module
    tier: regress
  assert:
    - type: llm-rubric
      value: "GROUNDED-FIX: Each finding's fix sketch names the concrete change to make, not a restatement of the defect. Fails if any sketch merely repeats the finding."
</file>

<file path="mod-review/compose/promptfooconfig.yaml">
description: mod-review compose

prompts:
  - id: file://opus-5.md
    label: opus-5

providers:
  - id: file://../../_lib/claude_provider.py
    config:
      mode: step
      output_mode: files
      model: opus
      effort: medium

defaultTest: file://../../_lib/grader.yaml

tests: file://tests.yaml
</file>

<file path="mod-review/compose/_fixtures/small-module.md">
# small-module

`auth.py`

```python
def is_valid(token, now):
    return now < token.expires_at

def refresh(token):
    token.expires_at += 3600

def parse_header(h):
    return h.split(" ")[1]
```

Sweep findings:

- `auth.py:5` — refresh extends expiry with no cap
- `auth.py:8` — parse_header raises IndexError on a header without a space
- `auth.py:2` — expiry boundary: is `now < expires_at` off by one? unclear whether spec wants
  a token valid through its expiry second
</file>
