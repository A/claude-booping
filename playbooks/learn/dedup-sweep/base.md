Before drafting the review table, check whether each candidate duplicates or conflicts with existing coverage:

Read every lesson under the vault's `lessons/`, every extension file under the vault's `_booping/`, and the attached repo's `CLAUDE.md`. Skip silently when a directory is empty or a file is absent. Together these are the lookup set for the dup-check sweep.

Record a sweep verdict per candidate as one of:

- `new` — no prior coverage at any target.
- `update existing at target X` — duplicate or refinement of a rule already written at `X`; the candidate becomes an update to `X`, not a fresh write at a different target.
- `conflict with existing at target X` — surface to the user in the review table as a visible flag.
