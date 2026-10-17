# Feedback

**Blocked (1/2)**: the milestone goal — "no live file in the repo names `vault/specs/` or the old `{vault}/specs` default" — is not met; the docs playbook's value and feature tables render empty.

- Checked: worker report, `git status`, `grep -n 'specs/' vault/config.yaml`. Everything listed in Scope is done and its Verify passes; the work is uncommitted in the tree and correct — keep it.
- Wrong: `vault/config.yaml` still carries `core.docs_playbook.queries.features.glob: [specs/story/*.md]` and `core.docs_playbook.queries.values.glob: [specs/value/*.md]`. Both resolve against the vault, where `specs/` no longer exists, so a docs render shows "_No value records._" and an empty feature table. That is a live reference to the old default, which this milestone's goal covers even though Scope's file list missed it.
- Next attempt: point both globs at the vault-root type directories (`story/*.md`, `value/*.md`). Sweep the rest of the live vault config and `vault/_playbooks/` once more for any other `specs/{type}` glob or path. Re-run M08's `## Verify`, then render the docs playbook (`bin/booping render-playbook docs`, no writing of `_reports/`) and confirm the value and feature tables list records again. Report the remaining docs-report drift against `vault/_playbooks/docs/_reports/output.md` (expected: record paths and the date line only).
