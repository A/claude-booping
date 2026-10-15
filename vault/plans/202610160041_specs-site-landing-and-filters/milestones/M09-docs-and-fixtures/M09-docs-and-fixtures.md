---
id: "09"
title: "Docs and the Russian fixture"
sp: 3
status: done
plan: "plans/202610160041_specs-site-landing-and-filters/index.md"
---

# M09: Docs and the Russian fixture

The user docs describe the landing, review filter, list filters and tag pages, and the Russian txtar case covers the new pages' labels.

**Scope**: `documentation/specs.md` (the site section), `booping-python/e2e/cases/specs/site-renders-russian-labels-and-a-tier-own-type.txtar`, `src/config.yaml` (comments on any new `core.specs.site` keys — none expected; label keys commented once). Docs (audience: a booping user publishing a specs site — booping:rule/0008: what they see and can link to, no internal module names): the page list (home, review, all records, type pages, tag pages), the hash format of C3 as a linkable filter (one example per facet key), the review reasons of C4, that tag pages come from each tier's `tags.yaml`, that open items appear on the review page for a vault's default render. Extend the Russian case: add a `tags.yaml`, one tagged record and one record with a `[clarify]` mark so its expected output includes `review.html`, `records.html`, `tags/index.html` and one tag page in Russian — every visible string from the `ru` table.

Tests: the extended txtar case.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 9.1 | Site section of the user docs. | `documentation/specs.md` | 1 | done |
| 9.2 | Russian fixture extended with tags, marks and the new pages. | `booping-python/e2e/cases/specs/site-renders-russian-labels-and-a-tier-own-type.txtar` | 2 | done |

## Definition of Done

### Task 9.1

- [x] Docs name every new page, the hash format with examples, the review reasons and the tag source; no internal module or function names.
- [x] `just docs` builds.

### Task 9.2

- [x] The Russian case's expected pages hold no English UI string (grep the expected blocks for the `en` labels added by M03–M07).

Return: the list of changed and created files, nothing else.

## References

- `documentation/specs.md` — the section part 1 wrote, to extend in the same voice.
- `booping-python/e2e/cases/specs/site-renders-russian-labels-and-a-tier-own-type.txtar` — the case to extend.

## Verify

`cd booping-python && uv run pytest e2e -k site-renders-russian -q`
