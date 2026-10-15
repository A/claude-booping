# Defaults

## D1 — develop/intake — 2026-10-15 22:11

**Asked:** Commit drift 7b70e0b..7959557 — revalidate the plan?

**Default:** Drift is plan files only (owner commit 7959557 amending M05–M07, clarification C-owner); no code drift. Trivial: M08 scope/DoD and index.md Final Verification item 3 patched to the owner decision (no schemas-ru, no init --schemas), a note added atop Decisions.

**Why:** Owner's own amendment; index.md and M08 still described the dropped Russian set, contradicting it

**Artifact:** [index.md](index.md)

## D2 — develop/provision — 2026-10-15 22:11

**Asked:** Confirm the sprint branch name?

**Default:** feat/specs, reused; no branch created or switched

**Why:** Owner fixed the branch for this run: never switch branches

**Artifact:** [index.md](index.md)

## D3 — develop/develop-loop — 2026-10-15 22:11

**Asked:** M01–M04 tests use a Russian _schemas/rule.yaml / adr.yaml override, while M05 says tier schemas are not for translation — keep those fixtures?

**Default:** Kept as planned

**Why:** C-owner says M01-M04 unchanged; the fixtures prove the overlay mechanics, not a shipped translation

**Artifact:** [index.md](index.md)

## D4 — develop/develop-loop — 2026-10-15 22:11

**Asked:** M06 is removed; closing a milestone with an empty tree counts as a failed attempt

**Default:** M06 closed done with no commit after checking its DoD (no --schemas on specs init)

**Why:** Owner decision C-owner: mark this milestone done with no changes

**Artifact:** [index.md](index.md)

## D5 — develop/wrap-up — 2026-10-15 22:11

**Asked:** rule/0013 forbids snapshots-accept; the run's snapshot policy allows plan-described drift

**Default:** Accept only hunks the plan describes, each listed here

**Why:** Owner's standing permission for this feature (2026-10-14), recorded in the plan's Departures

**Artifact:** [index.md](index.md)

## D6 — develop/develop-loop — 2026-10-15 22:25

**Asked:** M01–M04 share check.py, commands/specs.py, items.py and tiers.py — one commit per milestone cannot split those files cleanly

**Default:** Shared source (incl. tags.py and alternatives.py, which check.py imports) landed in M01's commit 0f758af; M02 commit 2953357 carries status/site + its cases; M03 7059fd4 and M04 a376c64 carry their e2e cases

**Why:** Every commit stays importable; no interactive hunk staging in this harness

**Artifact:** [index.md](index.md)

## D7 — develop/develop-loop — 2026-10-15 22:27

**Asked:** src/specs/README.md carries both M05's English-headings paragraph and M08's tier-schemas text

**Default:** README landed whole in M05's commit; M08's commit carries documentation/ and CLAUDE.md

**Why:** Path-scoped staging cannot split one file between milestones

**Artifact:** [index.md](index.md)

## D8 — develop/wrap-up — 2026-10-15 22:28

**Asked:** just snapshots drifted — accept?

**Default:** Accepted playbooks/specs/_reports/output.md (sole drift): one hunk, the guide step's new ## Import scenario (M07). The plan also expected an Init sentence; M07's amended scope dropped it, so none appears

**Why:** Every drifted hunk is plan-described; owner's snapshot policy for this feature (2026-10-14)

**Artifact:** [index.md](index.md)
