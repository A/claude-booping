# Defaults

## D1 — develop/intake — 2026-10-15 23:03

**Asked:** Commit drift 0d0a7e3..b7ee8e1 — revalidate the plan?

**Default:** No revalidation: the drift is the plan's own groom commits (8 vault plan files, no repo code)

**Why:** No plan-named code file changed

**Artifact:** [index.md](index.md)

## D2 — develop/provision — 2026-10-15 23:03

**Asked:** Confirm the sprint branch name?

**Default:** feat/specs, reused; no branch created or switched

**Why:** Owner fixed the branch for this run: never switch branches

**Artifact:** [index.md](index.md)

## D3 — develop/provision — 2026-10-15 23:03

**Asked:** Commit message format: develop's {agent}: {plan title} {message} vs rule/0022 conventional commits

**Default:** Both, as earlier sprints on this branch: booping-developer: {plan title} feat(specs): …

**Why:** Satisfies the playbook format and rule/0022 at once; matches branch history

**Artifact:** [index.md](index.md)

## D4 — develop/provision — 2026-10-15 23:03

**Asked:** rule/0013 forbids snapshots-accept; the run's snapshot policy allows plan-described drift

**Default:** Accept only hunks the plan describes, each listed here; none expected (no playbook source touched)

**Why:** Owner's standing permission for this feature (2026-10-14), recorded in the plan's C6

**Artifact:** [index.md](index.md)
