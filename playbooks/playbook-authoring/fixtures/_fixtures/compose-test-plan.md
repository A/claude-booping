Playbook `mod-review`, target step `compose`. The confirmed spec of the target step:

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

    - `auth.py:7` — `refresh` extends expiry with no cap. Fix: cap the total extension.

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

| Fixture      | Requirements                                                                          |
| ------------ | ------------------------------------------------------------------------------------- |
| small-module | three-function auth module with two seeded defects (uncapped refresh; parse_header IndexError on a spaceless header) plus the sweep-findings lines compose receives |

## Tests

| Fixture      | Tier    | Title        | Check logic                                         |
| ------------ | ------- | ------------ | --------------------------------------------------- |
| small-module | smoke   | SECTIONS     | Findings and Verdict sections present, in order     |
| small-module | smoke   | HAS-FINDINGS | Findings holds at least one bullet                  |
| small-module | regress | GROUNDED-FIX | each finding's fix sketch names the concrete change |
```
