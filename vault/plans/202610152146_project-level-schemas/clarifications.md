# Clarifications

Autonomous run — the owner was unavailable; every question below was settled by the run with a default.

## C1 — where a tier's own schemas live — answered

**Asked:** 2026-10-15 — intake

**Question:** The request suggests `{tier root}/_schemas/{type}.yaml` and asks for a location that never collides with record type directories at the vault root. Which?

**Answer:**

`{tier root}/_schemas/{type}.yaml`. A type name is a schema stem — a kebab-case latin word — so a leading underscore can never name a type, and the vault already uses `_`-prefixed directories (`_playbooks/`, `_runs/`) for booping-owned non-record content, which a vault-rooted tier ignores. swarmlight's `specs/schemas/` moves to `specs/_schemas/` when it adopts the feature.

## C2 — one plan or a split — answered

**Asked:** 2026-10-15 — intake

**Question:** The request bundles per-tier schemas, the Russian set with `init --schemas ru`, a tags dictionary, ADR alternatives checks and area-file guidance. One plan or several?

**Answer:**

Decided at draft-plan against the 35 SP split threshold. The per-tier schema mechanism is the seam everything else stands on, so it is the first slice either way.
