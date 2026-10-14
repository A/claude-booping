---
name: makemigration
title: Make migration
summary: Author one new plugin-shipped vault migration — a 
  `migrations/NNN_<slug>/migration.md` at the next id, in exactly the format 
  `migrate` consumes.
trigger: a change to the plugin moves or reshapes something existing vaults 
  hold, and those vaults need converting; an explicit ask to make or add a 
  migration
jinja: true
requires_project: false
inline_steps: true
reviewed_at: 20261015 12:00
---

Authors one migration in the booping plugin repo — the counterpart of `migrate`, which applies
what this writes. Scope is the plugin repo's `migrations/` directory; no vault is read or written.

`migration.md`'s `id` frontmatter is authoritative and is the highest shipped id plus one; the
`NNN_` directory prefix is the same id zero-padded to three digits, a cosmetic sort hint only.
A migration transforms the vault only — it knows nothing of git or `.booping`, which `migrate`
owns.
