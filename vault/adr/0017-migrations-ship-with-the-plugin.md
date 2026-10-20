---
type: adr
title: Vault migrations ship with the plugin, keyed by a frontmatter id
summary: Migrations live in the plugin's migrations/ directory; the id in migration.md frontmatter is the only authority, and the .booping marker's latest_migration is the applied watermark.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: accepted
values: [value/0003, value/0013]
sources: [playbooks/migrate/_specs/DECISIONS.md, CHANGELOG.md, CLAUDE.md]
---

## Context

Vault layout changes — flat plan files into plan directories, retro into its own
track, renamed metrics keys — had to reach existing vaults. A migration needs an
order, a record of what a vault has applied, and a way for booping to notice a
vault that is behind.

## Decision

Each migration is a directory `migrations/NNN_{slug}/` in the plugin repo whose
`migration.md` carries the prompt and commands handed to the unit applying it, with
frontmatter `id`, `title` and `summary`. The frontmatter `id` is the single source
of truth: the `NNN_` prefix is a cosmetic sort hint that nothing parses, so
directories can be renamed freely. A vault's applied watermark is the `.booping`
marker's `latest_migration` key (`-1` when nothing is applied). The pending set is
a config-declared query spec with `root: core` — so its glob scans the plugin's
files, not the vault — filtered by the numeric operator `id:gt` against
`booping.latest_migration`. Every render surface gates on the watermark: a vault
behind the shipped migrations gets a blocking notice to run `/playbook migrate`.

## Alternatives

| Option | Status | Complexity | Reversibility | Verdict |
|---|---|---|---|---|
| [Frontmatter id as authority](#frontmatter-id-as-authority) | accepted | low | high | What the query surface filters and sorts on |
| [Directory prefix as authority](#directory-prefix-as-authority) | rejected | low | high | Parsed from a name; frontmatter is queryable |
| [One self-contained file per migration](#one-self-contained-file-per-migration) | rejected | low | high | No room for material beside the prompt |

### Frontmatter id as authority

The id lives in frontmatter; the prefix is for humans.

- **Pros:** the generic query surface lists, filters and sorts migrations; the
  approval gate shows each migration's summary without reading bodies; no mismatch
  detection is needed.
- **Cons:** the id appears twice, once only cosmetically; `makemigration` must
  write it into frontmatter.
- **Complexity:** low.
- **Reversibility:** high.

### Directory prefix as authority

The zero-padded `NNN_` prefix is parsed as the id.

- **Pros:** the id is visible in a listing.
- **Cons:** needs its own parser beside the query surface; frontmatter and prefix
  could disagree.
- **Complexity:** low.
- **Reversibility:** high.

### One self-contained file per migration

`migrations/NNN_{slug}.md` with no directory.

- **Pros:** fewer paths.
- **Cons:** no place for sibling material, the way a playbook step dir carries
  material next to `prompt.md`.
- **Complexity:** low.
- **Reversibility:** high.

## Consequences

- The query surface gained the `root:` key (`core`), the numeric `id:gt` operator
  and the `booping` Jinja global. A try-vault-then-core lookup was rejected as
  ambiguous when both roots match, and a root prefix inside the glob as an invented
  path microsyntax.
- `id:gt` compares numerically, so the `-1` sentinel works and id 10 sorts after 9.
- The `makemigration` playbook in `playbooks/makemigration/` authors a migration at the
  next id (moved there from a skill, BL-0016).
