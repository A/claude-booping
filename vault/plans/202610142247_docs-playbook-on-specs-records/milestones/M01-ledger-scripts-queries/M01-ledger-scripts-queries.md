---
id: "01"
title: "Ledger move, hook scripts and story/value query specs"
sp: 4
status: in-progress
plan: "plans/202610142247_docs-playbook-on-specs-records/index.md"
---

# M01: Ledger move, hook scripts and story/value query specs

The docs playbook's ledger lives at `vault/docs/documented.md`, its hooks commit the specs records, and the feature index and value list are query specs any docs body can render.

**Scope:** `vault/docs/_specs/documented.md` (moved), `vault/_playbooks/docs/_scripts/close-documented`, `vault/_playbooks/docs/_scripts/commit-docs`, `vault/config.yaml`. No step body changes here.

**Test:** `close-documented` at its CLI surface (env `BOOPING_WORKDIR`, `BOOPING_ARTIFACT`), integration tier, three cases in a temp workdir — ledger absent (seeded at `documented.md` in the workdir root with the two items), ledger present with one of two items (one row appended), both present (nothing appended); expectations hand-written. The query specs: `booping query --config` returns one row per record.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Move the ledger with `git mv vault/docs/_specs/documented.md vault/docs/documented.md`; `close-documented` reads and writes `{workdir}/documented.md` instead of `{workdir}/_specs/documented.md`, docstring updated to match. | `vault/docs/documented.md`, `vault/_playbooks/docs/_scripts/close-documented` | 2 | pending |
| 1.2 | `commit-docs` stages and commits `$workdir` and the sibling specs tier `$workdir/../specs` (resolved; skipped silently when absent) with an explicit pathspec — never anything outside the two; its header comment says so. | `vault/_playbooks/docs/_scripts/commit-docs` | 1 | pending |
| 1.3 | Add `core.docs_playbook.queries.features` (glob `specs/story/*.md`, columns `title, summary, status`) and `core.docs_playbook.queries.values` (glob `specs/value/*.md`, columns `title, kind, summary`) to `vault/config.yaml`, each with a one-line comment naming its consumer (the feature index for `research` and `targeting`; the value list for `briefing` and `research`). | `vault/config.yaml` | 1 | pending |

## Definition of Done

### Task 1.1

- [ ] `vault/docs/documented.md` exists with the ledger's rows unchanged; `vault/docs/_specs/documented.md` is gone (git sees a rename).
- [ ] `close-documented` contains no `_specs` path; the three test cases above pass.

### Task 1.2

- [ ] `commit-docs` pathspec covers exactly `$workdir` and the resolved specs dir; no `git add -A` without a pathspec.
- [ ] `bash -n vault/_playbooks/docs/_scripts/commit-docs` passes.

### Task 1.3

- [ ] `bin/booping query --config core.docs_playbook.queries.features` prints one row per `vault/specs/story/*.md` record; `...queries.values` one row per value record.
- [ ] Keys sit under `core.docs_playbook` (placement rule in `CLAUDE.md`, Config).

## References

- `src/config.yaml` — `core.learn_playbook.queries.candidates` (a `glob` + `columns` query spec, commented with its consumer).
- `vault/_playbooks/docs/_scripts/close-documented` — the current script; keep its shape.

## Verify

```
cd vault && T=$(mktemp -d) && mkdir -p $T/_runs && printf -- '---\ndocumented:\n  - plans/a/index.md\n  - plans/b/index.md\n---\n' > $T/_runs/r.md && BOOPING_WORKDIR=$T BOOPING_ARTIFACT=$T/_runs/r.md python3 _playbooks/docs/_scripts/close-documented && test -f $T/documented.md && grep -c '^| `plans/' $T/documented.md && BOOPING_WORKDIR=$T BOOPING_ARTIFACT=$T/_runs/r.md python3 _playbooks/docs/_scripts/close-documented && bash -n _playbooks/docs/_scripts/commit-docs && ../bin/booping query --config core.docs_playbook.queries.features | wc -l
```

Final reply: only the list of changed files and the Verify output's last line.
