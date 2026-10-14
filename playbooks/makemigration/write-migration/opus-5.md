{% set shipped = 'core.migrate_playbook.queries.pending' | query -%}
{% set latest = (shipped | map(attribute='id') | list | max) if shipped else 0 -%}
# Write the migration

Create the directory and `migration.md` approved in `survey`, and nothing else. A shipped
migration — `{{ (shipped | last).path if shipped else 'none yet' }}` — is the structural model;
read one before writing.

## The file

`migration.md` is the whole instruction a context-fresh sub-agent gets when `migrate` applies it,
run from the vault root. Its layout, in order:

1. **Frontmatter** — exactly `id` (integer, unquoted), `title`, `summary`, as approved.
2. **`# <title>`**, then a short paragraph: what changed in the plugin, and why vaults need
   converting.
3. **What to convert** — the model-facing part: source → target, and every edge case as a
   bullet: already-converted input left alone, absent input reported as success, values preserved
   verbatim, and what a re-run does (nothing). A conversion the applier must judge rather than
   script adds a **How to convert** section after it.
4. **Commands** — the executable part, fenced `bash` blocks run from the vault root: a read-only
   look at what is there first, then the conversion. The conversion is idempotent and prints one
   line per file it changes or skips, prefixing every failure `FAILED:` (or another capitalised
   marker).
5. **Verify** — a fenced `bash` block proving the target state, then one paragraph naming each
   failure marker and what a clean second run prints.

A single conversion puts 3–5 at top level as `## What to convert`, `## Commands`, `## Verify`.
Independent conversions each get a `## Part N — <what>` section — its own source → target
paragraph, then 3–5 nested as `### What to convert`, `### Commands`, `### Verify` — and the intro
paragraph says how the parts relate and in which order they run. A step the applier must not
perform itself (a file outside the vault) gets its own `###` section telling it to report instead.

The body knows nothing of git or `.booping`: no staging, no commits, no marker edits, no reference
to other migrations. Sibling files in the directory are the migration's own workspace — add one
only when the prompt sends the applier there.

## Check

Run the commands in a scratch copy of a vault that holds the old layout, twice: the first run
converts, the second changes nothing. Then, from the plugin repo root:

```bash
bin/booping query --config core.migrate_playbook.queries.pending --where 'id:gt={{ latest }}' --columns id,title,summary
```

It must list exactly the new migration, with the approved id, title and summary. Anything else —
no row, two rows, a mangled field — is a frontmatter fault: fix it and re-run.

## Return

Present in chat the path written and the listing row, then one line: every vault recording
`latest_migration` below the new id, this repo's own included, is now gated until it runs
`/playbook migrate`.

```markdown
## Changed:
- [CREATED] migrations/{{ '%03d' | format(latest + 1) }}_<slug>/migration.md

## Notes:
- migration {{ latest + 1 }} (<slug>) written; query lists it as the newest shipped migration
- commands checked on a scratch vault: converted, second run a no-op
```
