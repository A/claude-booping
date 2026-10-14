---
id: "01"
title: "Shipped specs format at src/specs"
sp: 4
status: pending
plan: "plans/202610141731_specs-core-format-cli-injection/index.md"
---

# M01: Shipped specs format at src/specs

The format guide and the eight mdcheck schemas live at `src/specs/`; `vault/specs/` keeps only booping's own records and `just specs-check` validates them against the shipped schemas.

**Scope**: move `vault/specs/schemas/*.yaml` to `src/specs/schemas/` with `mv` (no `git mv` — the runner stages); split `vault/specs/README.md` into the generic format guide (`src/specs/README.md`) and a short intro to booping's own records (`vault/specs/README.md`); repoint the `specs-check` recipe in `justfile`. `vault/specs/` is booping's shipped core tier, so this milestone edits it as plugin content (plan Decisions). No Python changes. Tests: none new — the existing `just specs-check` over the moved schemas is the check.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Move the eight schema files to `src/specs/schemas/`, unchanged; delete the emptied `vault/specs/schemas/`. | `src/specs/schemas/*.yaml`, `vault/specs/schemas/` | 1 | pending |
| 1.2 | Create `src/specs/README.md` — the generic format guide: Tiers, Types, Files, Frontmatter, Body, Marks, Check sections from `vault/specs/README.md`, rewritten tier-neutral (no booping-only paths: "this directory" → the tier root, `vault/specs/` → the core tier's records). Schema paths point at `schemas/{type}.yaml` beside it. The Check section names `booping specs check` and states what it checks per the plan's Decisions → Check scope. | `src/specs/README.md` | 2 | pending |
| 1.3 | Rewrite `vault/specs/README.md` to booping's own records only: the opening paragraph, the "What lives where" list and the deprecation paragraph stay; Tiers/Types/Files/Frontmatter/Body/Marks are replaced by one line linking `../../src/specs/README.md` for the format; the Check section keeps `just specs-check`. Update `justfile` `specs-check` to loop over `src/specs/schemas/*.yaml` while checking `vault/specs/{type}/*.md`. | `vault/specs/README.md`, `justfile` | 1 | pending |

## Definition of Done

### Task 1.1

- [ ] `ls src/specs/schemas` lists exactly `adr conflict idea reference rule runbook story value` `.yaml` files, byte-identical to the originals.
- [ ] `vault/specs/schemas` no longer exists.

### Task 1.2

- [ ] `src/specs/README.md` contains every type, every frontmatter field, every body rule and both marks from the original guide.
- [ ] `rg -n 'vault/specs' src/specs/README.md` prints nothing except as the example of the core tier's location.
- [ ] Every relative link in `src/specs/README.md` resolves.

### Task 1.3

- [ ] `vault/specs/README.md` links the shipped guide and restates no format rule.
- [ ] `just specs-check` exits 0.

Return: the list of changed files, nothing else.

## References

- `vault/specs/README.md` — the source being split (read it first).
- `justfile` recipe `specs-check` — the loop being repointed.
- `src/config.yaml` header comment — the voice of shipped runtime data under `src/`.

## Verify

```
just specs-check
```

Exit 0.
