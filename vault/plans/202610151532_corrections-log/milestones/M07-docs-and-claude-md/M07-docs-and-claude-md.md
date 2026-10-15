---
id: "07"
title: "Docs and CLAUDE.md name corrections"
sp: 2
status: pending
plan: "plans/202610151532_corrections-log/index.md"
---

# M07: Docs and CLAUDE.md name corrections

The public docs and the plugin's CLAUDE.md name corrections where users and maintainers look for them.

**Scope**: `CLAUDE.md` per `index.md` `## CLAUDE.md impact`; `documentation/retro.md` — prepare starts from the corrections feed; `documentation/vault.md` — `corrections.md` in the plan-directory tree and beside code reviews; `documentation/groom.md`, `documentation/develop.md`, `documentation/code_review.md` — one line each: corrections are logged to `corrections.md`, described in the page's own words (`docs/corrections.md` is plugin-internal); `documentation/specs_playbook.md` — `correction` among the open-item sources wherever the source values are listed. Audience filter (booping:rule/0008): the public pages say what a user sees — the file, when it is written, what retro does with it — no module names or test layout.

Tests: none new — the docs build covers the pages.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 7.1 | CLAUDE.md lines. | `CLAUDE.md` | 1 | pending |
| 7.2 | Public docs lines. | `documentation/retro.md`, `documentation/vault.md`, `documentation/groom.md`, `documentation/develop.md`, `documentation/code_review.md`, `documentation/specs_playbook.md` | 1 | pending |

## Definition of Done

### Task 7.1

- [ ] `CLAUDE.md` `## Commands` lists `correction` with `add` and `list`; `## Lifecycle` has the Corrections bullet of `index.md` `## CLAUDE.md impact`.

### Task 7.2

- [ ] Each listed page names `corrections.md` once per place it describes; no module path, test path or flag beyond `booping correction add` and `list`.
- [ ] Every place under `documentation/` that lists the open-item `source` values includes `correction`.

Return: the list of changed files, nothing else.

## References

- `documentation/vault.md` — the plan-directory tree to extend.
- `CLAUDE.md` `## Lifecycle` — the Parked groom runs bullet, the shape of a sidecar bullet.

## Verify

`just docs`
