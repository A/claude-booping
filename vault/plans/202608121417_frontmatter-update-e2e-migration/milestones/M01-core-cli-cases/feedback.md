**Blocked (1/2)**: DoD Task 1.2 incomplete — the YAML-1.1 boolean-word coercion family has no corpus case.

What was checked: commit 4466bdc's 16 txtar cases against the milestone's Definition of Done. Tasks 1.1 and 1.3 are covered; Task 1.2 requires a case per coercion family from the unit suite's scalar-typing tests, and the milestone names the YAML-1.1 `yes` quirk explicitly ("YAML-1.1 `yes` quirk stays string").

What was wrong: no case asserts that a YAML-1.1 boolean word (`yes`, `no`, `on`, `off`) set as a value stays a plain string in the written frontmatter. The six coercion cases cover int, float, bool, null, ambiguous-quoted and newline/tab only.

What the next attempt must do: add one txtar case under `booping-python/e2e/cases/frontmatter-update/` asserting a YAML-1.1 boolean word round-trips as a string, authored per the milestone's procedure — hand-write description, fixtures and cmd, then baseline with `--txtar-update` and confirm the recorded contract. Then re-run the milestone's `## Verify` and commit. Touch nothing else.
