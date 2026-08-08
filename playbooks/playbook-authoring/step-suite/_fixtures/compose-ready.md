The confirmed spec of the target step:

```markdown
---
reviewed_at: 20260730 09:00
---

# compose

## Contract

- **Needs** —
  - the module files under review
  - the sweep findings, one line each
- **Value** — one review report the user signs off: every genuine finding, each with a fix
  sketch naming the concrete change.
- **Output files** —
  - `[CREATED] _review/review.md`
- **Harness return** — `## Changed:` list; `## Questions:` empty unless a finding cannot be
  judged from the module alone.
- **Review gate** —
  - the user confirms the findings before anything is filed

## Example artifact

    # Review — small-module

    ## Findings

    - `auth.py:7` — `refresh` extends expiry with no cap; a token can be refreshed forever.
      Fix: reject refresh once `expires_at - issued_at` exceeds the session ceiling.

    ## Verdict

    REQUEST CHANGES — 1 finding, 1 blocking.
```

The confirmed test plan of the target step:

```markdown
---
reviewed_at: 20260730 09:00
---

# compose — Tests

## Fixtures

| Fixture      | Requirements                                   |
| ------------ | ---------------------------------------------- |
| small-module | three-function auth module with seeded defects |

## Tests

| Fixture      | Tier    | Title        | Check logic                                         |
| ------------ | ------- | ------------ | --------------------------------------------------- |
| small-module | smoke   | SECTIONS     | Findings and Verdict sections present, in order     |
| small-module | smoke   | HAS-FINDINGS | Findings holds at least one bullet                  |
| small-module | regress | GROUNDED-FIX | each finding's fix sketch names the concrete change |
```

The prompt body as shipped (`mod-review/compose/opus-5.md`):

```markdown
# compose — review report

You receive a small module and the sweep findings, one line each. Compose the review report
the user will sign off.

Write `_review/review.md`:

- one H1: `# Review — <module>`
- `## Findings` — one bullet per genuine finding: `path:line`, the defect, and a fix sketch
  naming the concrete change
- `## Verdict` — one line: APPROVE or REQUEST CHANGES, with the finding count
```

The suite conventions:

- Config: the body file as labeled prompt (`file://opus-5.md`, never the wrapper), provider
  `file://../../_lib/claude_provider.py` with `mode: step` and `output_mode: files`,
  `defaultTest: file://../../_lib/grader.yaml`, `tests: file://tests.yaml`. Depth-2 relative
  paths only.
- Tests: one smoke case pinning the example-derived contract via
  `file://../../_lib/asserts/mdcheck.js` inline `rules:`; one regress case per test-plan row,
  each rubric NAMED (`"TITLE: …"`) after its row title, on the row's fixture. Every case
  carries `metadata: {playbook, step, fixture, tier}`.
- The fixture file at `_fixtures/small-module.md` already exists — reference it, do not
  rewrite it.
