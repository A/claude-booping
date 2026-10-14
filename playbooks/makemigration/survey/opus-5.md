{% set shipped = 'core.makemigration_playbook.queries.shipped' | query -%}
{% set ids = shipped | map(attribute='id') | list -%}
{% set next_id = (ids | max + 1) if ids else 1 -%}
# Open the authoring run

## Ground

Confirm the working repo is the booping plugin repo — it holds `migrations/` and
`playbooks/migrate/playbook.md` at its root. If it does not, say so and end the run: a migration
ships with the plugin, never with a project.

The migrations below were resolved from the plugin root this render ran from. When that is not
the working repo (an installed plugin rendering while you sit in a checkout), re-list them with
the checkout's own `bin/booping query --config core.makemigration_playbook.queries.shipped` and use
that listing and its highest `id` instead.

## Shipped migrations

{% if shipped -%}
{{ shipped | as_table(columns=['id', 'title', 'summary']) }}
{%- else -%}
None — this is the first migration.
{%- endif %}

Next id: **{{ next_id }}** — the highest shipped `id` plus one. Ids are set from frontmatter,
never parsed off a directory name.

## The change

Establish, from the conversation and the repo, the vault layout change this migration converts:
what an existing vault holds today, what it must hold afterwards, and which plugin change made
the difference. Read the diff or plan that introduced it when one is named. Ask only for what
neither source settles — one question at a time, through `AskUserQuestion`.

A migration transforms vault files only. A change that needs code, config defaults or the
`.booping` marker rewritten is not a migration — say so and end the run.

## Present

In chat, in this order:

- the change in two or three lines: before, after, what is left alone
- the shipped table above
- the proposal:
  - id `{{ next_id }}`
  - directory `migrations/{{ '%03d' | format(next_id) }}_<slug>/` — `<slug>` snake_case, two or
    three words naming the change, like the shipped ones
  - `title` — one sentence stating the vault's new state
  - `summary` — one sentence naming each conversion concretely, the line `migrate` shows the user
    before applying

Close on one question — `Write migration {{ next_id }} as proposed?` — asked in **prose**, never
through `AskUserQuestion`. Wait for the answer; fold any correction into the proposal and ask again.

## Return

```markdown
## Changed:

## Notes:
- id: {{ next_id }}; dir: migrations/{{ '%03d' | format(next_id) }}_<slug>/
- title: <title>
- summary: <summary>
- converts: <before → after, one line per part>
- approved by the user
```

`## Changed:` stays empty — this step writes no file.
