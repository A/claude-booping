---
id: "03"
title: "E2E fixtures seed project records at the vault root"
sp: 3
status: in-progress
plan: "plans/202610151727_project-specs-at-vault-root/index.md"
---

# M03: E2E fixtures seed project records at the vault root

Every e2e case that seeds project records under `fixtures/cwd/vault/specs/{type}/` seeds them at `fixtures/cwd/vault/{type}/` and passes again, asserting what it asserted before.

**Scope**: the cases listed by `grep -rlE '^-- [^ ]*vault[^ ]*/specs/' booping-python/e2e/cases`, minus every case named `init-*` or `check-layout-*` (their subject is the layout itself — M04 and M05 own them). In each remaining case one `sed -i -E` pass rewrites the segment `vault/specs/` to `vault/` in file headers, in expected output, in links and in `sources` entries. Then run the corpus. A case still failing after the rewrite: read its command and expected output against the diff. When the remaining difference is only a path the rewrite missed (a relative link depth, an absolute path in output), fix that path by hand. Any other difference is a behaviour change — leave the case failing and name it in the return for the runner; never change an assertion's meaning and never `--txtar-update`. A case seeding a non-type directory under the old tier (e.g. `vault/specs/notes/`) keeps its meaning by taking an explicit `core.specs.tiers.project.path` in its vault config instead of the rewrite.

Tests: the rewritten cases themselves — integration tier, assertions unchanged but for the path segment.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | The sed pass over the listed cases. | `booping-python/e2e/cases/**/*.txtar` (the grep's list minus `init-*`, `check-layout-*`) | 2 | pending |
| 3.2 | Run the corpus; fix missed paths by hand, report any other failure. | same | 1 | pending |

## Definition of Done

### Task 3.1

- [ ] `grep -rlE '^-- [^ ]*vault[^ ]*/specs/' booping-python/e2e/cases` lists only `init-*` and `check-layout-*` cases, and any case pinned to an explicit path.

### Task 3.2

- [ ] The Verify command passes; no case was rebaselined with `--txtar-update`.

Return: the list of changed files, plus each case fixed by hand with one line on why.

## References

- `booping-python/e2e/README.md` — the case format (pytest-txtar).

## Verify

`just e2e -k 'not init- and not check-layout'`
