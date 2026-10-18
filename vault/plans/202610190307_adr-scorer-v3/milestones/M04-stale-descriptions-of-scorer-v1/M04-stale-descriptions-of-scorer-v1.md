---
id: "04"
title: "Stale descriptions of scorer v1"
sp: 2
status: pending
plan: "plans/202610190307_adr-scorer-v3/index.md"
---

# M04: Stale descriptions of scorer v1

## Tasks

**Goal:** no shipped text describes the 0–3 `score:` scorer. **Scope:** `CLAUDE.md`, `CHANGELOG.md`.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | CLAUDE.md Layout bullet on `agents/adr-scorer.md`: static body and allowlist kept, "reads nothing beyond its prompt" kept, nothing on the score contract added | `CLAUDE.md` | 1 | pending |
| 4.2 | CHANGELOG unreleased entry: the scorer routes a draft ADR, names what it overlaps and the cheap options it misses; a draft that is not an ADR is routed, «Не взвешено:» joins the brief — user-facing only (booping:rule/0008); the v1 line on this release amended | `CHANGELOG.md` | 1 | pending |

Test surface: none — text only.

Worker returns: the list of changed files.

## Definition of Done

Task 4.1
- [ ] `git grep -n "score: {0-3}\|score of 1 or less"` over shipped files returns nothing outside `vault/`.

Task 4.2
- [ ] CHANGELOG names routing, «Не взвешено:» and the inventory input; no internal file names.

## References

- `CHANGELOG.md:10` — the v1 line.

## Verify

`git grep -n "score: {0-3}" -- ':!vault' ; test $? -eq 1`
