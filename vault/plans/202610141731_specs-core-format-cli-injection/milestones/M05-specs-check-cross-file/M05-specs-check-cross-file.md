---
id: "05"
title: "booping specs check \u2014 links, refs and namespaces"
sp: 8
status: pending
plan: "plans/202610141731_specs-core-format-cli-injection/index.md"
---

# M05: booping specs check — links, refs and namespaces

`booping specs check` also reports broken relative links, unresolved reference fields and `sources`, and resolves namespaced refs across the three tiers — an unresolved namespace as a warning, everything else as an error.

**Scope**: new `booping-python/src/booping/specs/links.py` (link extraction) and the cross-file checks appended in `booping-python/src/booping/specs/check.py` at the place M04 left. The check loads every resolved tier (M02 `resolve_tiers`) once to build a `{namespace → {type → {number}}}` index; the checked tier's own records answer un-namespaced refs. Rules:

- `link` — every inline markdown link `[text](dest)` in the body, outside fenced code blocks and inline code spans; skip a `dest` containing `://`, starting with `mailto:`, `/` or `#`; strip a `#anchor` and a `<…>` wrapper; the remainder must exist relative to the record's directory. Anchors are not checked.
- `ref` — the fields `values` → `value`, `rules` → `rule`, `supersedes` → `adr`: the field must be a list (else ``{field}: must be a list``); each item must parse as a ref (`parse_ref`) of the field's type; the target must exist in its tier — existence of the file only, never whether the target passes its own checks.
- `sources` — a list; each entry not containing `://` must exist relative to the tier's anchor (core → plugin root, global → `home_dir`, project → repo root).
- `namespace` (warning) — a namespaced ref whose namespace names no resolved tier, or whose tier's root does not exist; no `ref` error is raised for it.

Tests: unit tests for `links.py` only (pure logic with tricky branches — parametrized: plain link, link with anchor, URL, mailto, absolute, anchor-only, link inside a fenced block, inside inline code, two links on one line). Txtar e2e cases under `booping-python/e2e/cases/specs/`: a missing link target, an existing one; a wrong-type ref, a missing target, an existing target; a missing `sources` path; `booping:value/0001` resolving against the real core tier (no finding); `booping:value/9999` (error `ref`); `ghost:rule/0001` (warning, exit 0); the global namespace pinned in `xdg/booping/config.yaml` (`core.specs.tiers.global.namespace`) with fixture records under `home/Claude/_specs/{type}/` resolving.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | `links.py` link extraction + the `link` check; unit tests and e2e cases per Scope. | `booping-python/src/booping/specs/links.py`, `booping-python/src/booping/specs/check.py`, `booping-python/tests/specs/links_test.py`, `booping-python/e2e/cases/specs/check-link-*.txtar` | 2 | pending |
| 5.2 | `ref` (un-namespaced) and `sources` checks with the plan's message texts; e2e cases per Scope. | `booping-python/src/booping/specs/check.py`, `booping-python/e2e/cases/specs/check-ref-*.txtar`, `booping-python/e2e/cases/specs/check-sources-*.txtar` | 3 | pending |
| 5.3 | Cross-tier index, namespaced ref resolution and the `namespace` warning; e2e cases per Scope. | `booping-python/src/booping/specs/check.py`, `booping-python/e2e/cases/specs/check-namespace-*.txtar` | 3 | pending |

## Definition of Done

### Task 5.1

- [ ] A link to a missing file → `{path}:{line}  error  link  link target `{dest}` does not exist`, the link's own line.
- [ ] URLs, mailto, absolute paths, anchor-only links and links in code produce no finding.

### Task 5.2

- [ ] `values: [rule/0001]` → ``values: `rule/0001` is not a value ref``; `values: [value/9999]` → ``values: `value/9999` does not exist``.
- [ ] A missing `sources` entry → ``sources: `{entry}` does not exist``.

### Task 5.3

- [ ] `values: [booping:value/0001]` in a project-tier record → no finding.
- [ ] `rules: [ghost:rule/0001]` → `warning  namespace` finding, trailer counts it under warnings, exit 0.
- [ ] A ref into the global namespace resolves when the fixture global tier holds the record, and is a `namespace` warning when the fixture has no global tier directory.

Return: the list of changed files, nothing else.

## References

- `booping-python/src/booping/specs/check.py` (from M04) — where the checks append.
- `src/specs/README.md` (from M01) — reference fields and ref syntax.
- `booping-python/tests/context/lesson_test.py` — parametrized unit test style.

## Verify

```
cd booping-python && uv run pytest tests/specs e2e -k specs -q
```

All pass.
