**Blocked (1/2)**: cross-check table leaves three unit tests unmapped — DoD 3.1 requires every row to carry a corpus case filename or a recorded drop rationale, and "(no direct case) / not covered in corpus" is an admitted coverage gap, not a rationale.

What was checked: commit `181f1d2` — unit file deleted, corpus green, grep sweep clean; `coverage-cross-check.md` rows.

What was wrong, row by row:
- `TestParsePairs.test_value_with_equals_sign` — "(no direct case)". The behavior (a value containing `=` signs parses as one pair) is CLI-observable and must have a corpus case.
- `TestFrontmatterUpdateCLI.test_logs_to_booping_log` — "(no direct case)". The corpus already holds `log-when-vault-attached.txtar` from M01; map the row to it.
- `TestFrontmatterUpdateCLI.test_does_not_write_to_real_home` — "(no direct case)". The pytest-txtar sandbox env-maps `HOME`/`XDG_CONFIG_HOME` for every case, so home isolation is enforced by the harness itself; record that as the drop rationale instead of a gap.

What the next attempt must do:
- Author one new txtar case asserting a value containing `=` signs lands intact (M01 authoring procedure: hand-write description/fixtures/cmd, fill expected blocks via `uv run pytest e2e --txtar-update -k frontmatter` from `booping-python/`, then confirm green without the flag).
- Update the three rows in `coverage-cross-check.md`: new case filename; `log-when-vault-attached.txtar`; harness-isolation drop rationale.
- Run the milestone's full `## Verify` line and land everything as a new commit; never amend.
