---
type: rule
title: Private sources stay in vault/notes
summary: This repo is public; another project's data, local paths and raw experiment inputs are written only under the gitignored vault/notes/, and tracked records name them without linking.
created_by: claude
created_at: 2026-10-18
updated_at: 2026-10-18
status: accepted
targets: [specs, retro, learn, project-manager, groom, develop, code-review, docs]
brief: "This repo is public. Write another project's data (its name tied to its numbers, plan or task text, findings), local absolute paths and raw experiment inputs only under the gitignored vault/notes/ (references in vault/notes/references/); a tracked record carries aggregates only and names such a source as \"(private note, not published)\" without a link. Before committing a vault path, grep the staged diff for other projects' names, /tmp/ and /home/."
---

## Rule

github.com/A/claude-booping is public, so every tracked file is published on push. Another project's data — its name tied to its numbers, its plan or task text, its findings — local absolute paths, and raw experiment inputs are written only under `vault/notes/`, which is gitignored; references go to `vault/notes/references/`. A tracked record keeps aggregates only (for example "92 plans across 7 projects", a range instead of a per-project list) and names such a source as "(private note, not published)" without linking it. Before committing a vault path, grep the staged diff for other projects' names, `/tmp/` and `/home/`, and move what matches (owner, 2026-10-18, after a feedback note with local paths, another project's raw task text and a per-project breakdown were moved into a tracked directory and nearly pushed).

## Follows from

- [Everything in one place](../value/0011-everything-in-one-place.md) — the private sources stay in the same vault, beside the records that cite them, just out of git.

## Exceptions

- A project name alone, without its data, may appear where the owner already published it.
