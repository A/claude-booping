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

## D5 — develop/develop-loop — 2026-10-15 23:10

**Asked:** The worker built site-index in its M02 shape at once — commands/specs.py and index.py carry M01 and M02 together; one commit per milestone cannot split them

**Default:** Shared source landed in M01's commit 0b0d338; M02's commit 9dc8d4e carries its six e2e cases

**Why:** Every commit stays importable; path-scoped staging cannot split one file

**Artifact:** [index.md](index.md)

## D6 — develop/develop-loop — 2026-10-15 23:10

**Asked:** M04 DoD allows no host besides github.com/A/claude-booping and the uv image, yet the templates' header names raw.githubusercontent.com/A/claude-booping

**Default:** Accepted: the include: remote: URL is the plan's own (C1, M04 header, M05)

**Why:** The DoD's intent is no homelab host; the raw URL is the same repo

**Artifact:** [index.md](index.md)

## D7 — develop/develop-loop — 2026-10-15 23:10

**Asked:** Wording of the validation errors M02 left open, and BOOPING_REF pin example in docs

**Default:** Worker's wording kept (projects: not a list; projects[i]: not a mapping / `name` must be a non-empty string / …); docs pin example v1.1.1, the latest tag

**Why:** C3 fixes only shape (one error: line naming projects[i]); the latest real tag is the honest example

**Artifact:** [index.md](index.md)
