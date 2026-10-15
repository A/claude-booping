---
id: "05"
title: "Core rule 0031 and the corrections format doc"
sp: 2
status: pending
plan: "plans/202610151532_corrections-log/index.md"
---

# M05: Core rule 0031 and the corrections format doc

A core rule tells the groom, develop and code-review drivers to log corrections, and `docs/corrections.md` holds the sidecar format.

**Scope**: create `specs/rule/0031-corrections-are-logged.md` — `type: rule`, `created_by: claude`, `status: accepted`, `targets: [groom, develop, code-review]`, `brief:` one or two lines: when the user corrects you — rejects a proposal, rewrites an output, says it is wrong, answers a gate other than you suggested — run `booping correction add --target {run artefact} --step {playbook}/{step} --did … --said '{the user's words verbatim}'`, with `--why` when the user states it and `--record {ref}` when the correction names a spec record; a plain confirmation is not a correction. Body `## Rule` (the same, plus where the sidecar goes and a link to `docs/corrections.md`) and `## Follows from` linking `vault/specs/value/0001`, `vault/specs/value/0004` and `vault/specs/adr/0026` with relative links shaped as in rule/0030. Create `docs/corrections.md` — the format doc, shaped like `docs/clarifications.md`: where the sidecar sits, the entry shape and each field of `index.md` `### corrections.md`, `booping correction add` as its only writer and `booping correction list` as its reader, one example.

Tests: none new — `specs check` holds the record's schema, targets and links.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | The core rule record. | `specs/rule/0031-corrections-are-logged.md` | 1 | pending |
| 5.2 | The format doc. | `docs/corrections.md` | 1 | pending |

## Definition of Done

### Task 5.1

- [ ] `bin/booping specs check --tier core` reports nothing for `rule/0031`.
- [ ] `bin/booping render-playbook groom`, `develop` and `code-review` each show the brief in `## Rules`.

### Task 5.2

- [ ] Every field of `index.md` `### corrections.md` is described once; no flag list restated beyond the command names.

Return: the list of changed files, nothing else.

## References

- `specs/rule/0030-planning-shows-values-in-play.md` — a core rule with `targets` and `brief`, and its `## Follows from` link shape.
- `docs/clarifications.md` — the sidecar format doc to copy.

## Verify

`bin/booping specs check --tier core`
