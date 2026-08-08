# Implement one step's suite

The input names the target step and carries its confirmed contract and example, its confirmed
test plan, the prompt body as shipped, and the suite conventions with a live-suite pattern.
Produce the **promptfoo suite** — the running guarantee every later change to the prompt must
pass: the smoke tier derived from the confirmed example (its structure becomes the check
rules — no separate shape work), the regress rubrics from the test plan's rows, on the
fixtures the rows name.

## The files to write

`<name>/<step>/promptfooconfig.yaml`:

- the body file as labeled prompt (`file://<model>.md`, never the wrapper)
- provider `file://../../_lib/claude_provider.py` with `mode: step` and the `output_mode` the
  contract implies
- `defaultTest: file://../../_lib/grader.yaml`; `tests: file://tests.yaml`
- depth-2 relative paths only

`<name>/<step>/tests.yaml` — exactly the confirmed sources, nothing invented:

- one smoke case pinning the example-derived contract with deterministic `javascript` asserts;
  a fixture's own arithmetic rides in its own small assert
- one regress case per test-plan regress row, each rubric NAMED (`"TITLE: …"`) after its row
  title, on the row's fixture
- every case carries `metadata: {playbook, step, fixture, tier}`
- comment only what an assert cannot say

Never run an eval; the optimizer steps take the suite to green afterwards.

## Return format

```
## Changed:
- [CREATED] <name>/<step>/promptfooconfig.yaml
- [CREATED] <name>/<step>/tests.yaml

## Notes:
- just eval-smoke -c <name>/<step>/promptfooconfig.yaml
- just eval-regress -c <name>/<step>/promptfooconfig.yaml
```
