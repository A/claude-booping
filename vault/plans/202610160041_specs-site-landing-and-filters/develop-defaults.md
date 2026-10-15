# Develop defaults

## D1 — develop/provision — 2026-10-16

**Asked:** Sprint branch name confirmation

**Default:** Stay on `feat/specs`, no new branch

**Why:** Owner's run prompt fixes the branch: run in the feat/specs worktree, never switch branches

**Artifact:** [index.md](index.md)

## D2 — develop/provision — 2026-10-16

**Asked:** Rule rule/0013 (snapshots accepted by user only) vs the run prompt's snapshot policy

**Default:** Follow the owner's standing permission for this feature (2026-10-14): `just snapshots-accept` only when every drifted hunk is a change the plan describes, each accepted report listed here; any other drift stops the run

**Why:** The owner's explicit instruction for this run narrows the rule; the plan's Decisions repeat the same permission

**Artifact:** [index.md](index.md)

## D3 — develop/develop-loop — 2026-10-16

**Asked:** Commit message format `{agent}: {plan title} {message}` vs vault rule/0022 (conventional commits with scope)

**Default:** Conventional subject `feat(specs): …`, worker and plan title in the body

**Why:** rule/0022 is an accepted project rule; part 1 of this feature settled the same way; the playbook format is kept in the body

**Artifact:** [index.md](index.md)

## D4 — develop/develop-loop — 2026-10-16

**Asked:** One commit per milestone when a group's milestones share files

**Default:** One repo commit per milestone group (G1 = M01–M04 in da1d5f8), body naming each milestone

**Why:** M01–M04 edit the same `pages.py`, templates and goldens, and M02's `tags.py` imports M01's moved `SiteWarning`; splitting by hunk would invent intermediate states never tested

**Artifact:** [index.md](index.md)

## D5 — develop/develop-loop — 2026-10-16

**Asked:** Worker touched files outside the G1 contracts (`site/model.py` for `SiteWarning`, `site/labels.py` for `plural_forms`, one assertion in `tests/specs/site_test.py`)

**Default:** Accepted and committed with G1

**Why:** Each is the minimum the contracted change needs (import cycle, client-side plurals, a dataclass equality test); no behaviour beyond the plan

**Artifact:** [index.md](index.md)

## D6 — develop/develop-loop — 2026-10-16

**Asked:** One commit per milestone for G2 (M05–M09)

**Default:** Code of M05–M09 in one commit (38eb26a), M09's documentation in its own commit (6ba0d65)

**Why:** M05–M07 edit the same `pages.py`, `_macros.html.j2` and site goldens, and M09's Russian golden changes with them; the docs edit is separable

**Artifact:** [index.md](index.md)
