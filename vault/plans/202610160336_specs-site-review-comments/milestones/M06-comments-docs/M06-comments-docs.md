---
id: "06"
title: "Document review comments and the root landing"
sp: 2
status: done
plan: "/home/anton/Dev/@A/claude-booping-specs/vault/plans/202610160336_specs-site-review-comments/index.md"
---

# M06: Document review comments and the root landing

The public docs describe the site as it now ships: review comments with their export, and the root page as a landing.

**Scope**: `documentation/specs.md`, section `### booping specs site` only. Audience: a professional publishing or reading a specs site — what they see and do, no internal churn (booping:rule/0008):

- The root-page sentence(s): `{root}/index.html` is that root's landing — callout, scenario cards, Recently updated; the mark list is no longer there.
- A new paragraph or short subsection on review comments: where the affordances are (selection, paragraph, § heading), the record panel and `comments.html` with the sidebar count, the export block shape (show the C2 template from `../../clarifications.md`), Clear sent, storage per site in this browser only, and the Firefox `file://` limitation from C7.
- The output-directory file list gains `comments.html`, `comments.js` and `comments-format.js`.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 6.1 | Update the `booping specs site` section per Scope. | `documentation/specs.md` | 2 | done |

## Definition of Done

### Task 6.1

- [x] Every bullet of Scope is in the section; nothing about internal modules, tests or the plan.
- [x] No sentence still says the root page lists marks or "Records: N".
- [x] `just docs` passes.

Return: the list of changed files, nothing else.

## References

- `documentation/specs.md` — the current `### booping specs site` section (page shell, `index.html` shape, search, output file list) to extend in its own voice.

## Verify

`just docs`
