---
name: migrate
title: Migrate
summary: Bring a project vault up to date by applying every pending migration 
  the plugin ships, in id order, on one up-front approval.
trigger: a render surface reports the vault is behind and tells the user to run 
  `/playbook migrate`; an explicit ask to migrate or update a vault
jinja: true
requires_project: true
inline_steps: true
reviewed_at: 20260805 08:52
---

Brings the vault current: every pending migration applied in id order, each its own vault
commit, closing with one summary. Scope is the vault only — a repo-local vault is no special
case.

Migrations complete one full cycle before the next starts — apply, advance the recorded id,
commit everything — never batched to the end and never in parallel. A failing instance halts
the sequence immediately: name the failing id, what failed, and a remedy the user can apply by
hand. No skipping ahead, no silent rollback.

`migration.md`'s `id` frontmatter is authoritative; the `NNN_` directory prefix is a cosmetic
sort hint only. Migrations know nothing of git or `.booping` — the playbook owns every commit
and the id advance.
