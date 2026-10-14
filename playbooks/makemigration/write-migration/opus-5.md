{% set shipped = 'core.makemigration_playbook.queries.shipped' | query -%}
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
3. **The prompt** — the model-facing part. One `## What to convert` section, or one
   `## Part N — <what>` section per independent conversion, each stating source → target and every
   edge case as a bullet: already-converted input left alone, absent input reported as success,
   values preserved verbatim, and what a re-run does (nothing).
4. **`## Commands`** — the executable part, fenced `bash` blocks run from the vault root: a
   read-only look at what is there first, then the conversion. The conversion is idempotent and
   prints one line per file it changes or skips, prefixing every failure `FAILED:` (or another
   capitalised marker).
5. **`## Verify`** — a fenced `bash` block proving the target state, then one paragraph naming each
   failure marker and what a clean second run prints.

The body knows nothing of git or `.booping`: no staging, no commits, no marker edits, no reference
to other migrations. Sibling files in the directory are the migration's own workspace — add one
only when the prompt sends the applier there.

## Check

Run the commands in a scratch copy of a vault that holds the old layout, twice: the first run
converts, the second changes nothing. Then, from the plugin repo root:

```bash
bin/booping query --config core.makemigration_playbook.queries.shipped --where 'id:gt={{ latest }}'
```

It must list exactly the new migration, with the approved id, title and summary. Anything else —
no row, two rows, a mangled field — is a frontmatter fault: fix it and re-run.

## Return

Present in chat the path written and the listing row, then one line: every vault recording
`latest_migration` below the new id, this repo's own included, is now gated until it runs
`/playbook migrate`.

```markdown
## Changed:
- [CREATED] migrations/004_plan_tags/migration.md

## Notes:
- migration 4 (plan_tags) written; query lists it as the newest shipped migration
- commands checked on a scratch vault: converted, second run a no-op
```
