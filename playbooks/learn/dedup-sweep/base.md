Before drafting the review table, check whether each candidate duplicates or conflicts with existing coverage:

The lookup set is:

- `{home_dir}/_lessons/` — global lessons, shared across projects (the vault-home base is `booping config-get home_dir`). Read-only here; a duplicate found in it still becomes an update to that file.
- `{vault}/_lessons/` — this project's lessons, shadowing a global lesson of the same filename. The only root this run writes new lessons into.
- The vault's `_booping/` extension files and the attached repo's `CLAUDE.md` — the non-lesson targets.
- The vault's legacy `lessons/`, if it still exists — **read-only, duplicate context only**. Never write here and never route a row to it; a candidate already covered there is reported as such and, if accepted, written into `{vault}/_lessons/` with `targets:`.

Skip silently when a directory is empty or a file is absent.

Record a sweep verdict per candidate as one of:

- `new` — no prior coverage at any target.
- `update existing at target X` — duplicate or refinement of a rule already written at `X`; the candidate becomes an update to `X`, not a fresh write at a different target.
- `conflict with existing at target X` — surface to the user in the review table as a visible flag.
