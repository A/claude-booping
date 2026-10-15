Authors one migration in the booping plugin repo — the counterpart of `migrate`, which applies
what this writes. Scope is the plugin repo's `migrations/` directory; no vault is read or written.

`migration.md`'s `id` frontmatter is authoritative and is the highest shipped id plus one; the
`NNN_` directory prefix is the same id zero-padded to three digits, a cosmetic sort hint only.
A migration transforms the vault only — it knows nothing of git or `.booping`, which `migrate`
owns.

## Playbook Steps

Execute the steps in the most effective order considering their dependencies.

| Step | Dependencies | Summary | Review gate |
| --- | --- | --- | --- |
| `survey` | — | Open the run — confirm the working repo is the booping plugin repo, pin down the vault change the migration converts, present the shipped migrations and the next id, and confirm id, slug and what the migration does. | The user approves the migration's id, directory name, title and conversion scope — the run's only gate. Nothing is written before it. |
| `write-migration` | `survey` | Create the approved `migrations/NNN_<slug>/migration.md` — frontmatter `id`/`title`/`summary`, a prompt stating the conversion, then Commands and Verify — and confirm the core query lists it as the newest shipped migration. | — |

## Step: Survey
# Open the authoring run

## Ground

Confirm the working repo is the booping plugin repo — it holds `migrations/` and
`playbooks/migrate/playbook.md` at its root. If it does not, say so and end the run: a migration
ships with the plugin, never with a project.

The migrations below were resolved from the plugin root this render ran from. When that is not
the working repo (an installed plugin rendering while you sit in a checkout), re-list them with
the checkout's own `bin/booping query --config core.migrate_playbook.queries.pending` and use
that listing and its highest `id` instead.

## Shipped migrations

| id | title | summary | path | slug |
| --- | --- | --- | --- | --- |
| 1 | Pre-1.0 vault layout — plans as directories, config under `core` | Convert every flat `plans/{slug}.md` into `plans/{slug}/index.md`, and rewrite a vault `config.yaml` onto the `core.*` namespace, dropping the retired `skills:` and `plan:` blocks. | migrations/001_vault_layout/migration.md | 001_vault_layout |
| 2 | Retro becomes its own track; extension files become targeted lessons | End the plan lifecycle at `done` and move every `plans/{slug}/retro.md` out to a standalone `retrospectives/{slug}.md`; convert every `_booping/skill_*.md` and `_booping/agent_*.md` into a targeted `_lessons/NNNN_*.md`, and move the invocation log to the vault root. | migrations/002_tracks_and_lessons/migration.md | 002_tracks_and_lessons |
| 3 | Session metrics live in flat `metrics_` frontmatter and the sprints view | Rename `active_minutes` → `metrics_active_minutes` and `models` → `metrics_models` on every plan, and rewrite the `sprints.md` Bases fence to the six `metrics_*` columns. | migrations/003_session_metrics/migration.md | 003_session_metrics |
| 4 | Lessons become rules | Turn every lesson in `{home_dir}/_lessons/` and `{vault}/_lessons/` into a rule record of its tier, or drop it as a duplicate of an existing rule; rewrite references to the removed files and remove both directories. | migrations/004_lessons_to_rules/migration.md | 004_lessons_to_rules |
| 5 | Project specs move to the vault root | Move a vault's project spec records from `{vault}/specs/{type}/` to `{vault}/{type}/` and re-point the links inside them; a project tier the old default placed elsewhere is pinned there with an explicit `path`. | migrations/005_project_specs_to_vault_root/migration.md | 005_project_specs_to_vault_root |


Next id: **6** — the highest shipped `id` plus one. Ids are set from frontmatter,
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
  - id `6`
  - directory `migrations/006_<slug>/` — `<slug>` snake_case, two or
    three words naming the change, like the shipped ones
  - `title` — one sentence stating the vault's new state
  - `summary` — one sentence naming each conversion concretely, the line `migrate` shows the user
    before applying

Close on one question — `Write migration 6 as proposed?` — asked in **prose**, never
through `AskUserQuestion`. Wait for the answer; fold any correction into the proposal and ask again.

## Return

```markdown
## Changed:

## Notes:
- id: 6; dir: migrations/006_<slug>/
- title: <title>
- summary: <summary>
- converts: <before → after, one line per part>
- approved by the user
```

`## Changed:` stays empty — this step writes no file.

## Step: Write Migration
# Write the migration

Create the directory and `migration.md` approved in `survey`, and nothing else. A shipped
migration — `migrations/005_project_specs_to_vault_root/migration.md` — is the structural model;
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
bin/booping query --config core.migrate_playbook.queries.pending --where 'id:gt=5' --columns id,title,summary
```

It must list exactly the new migration, with the approved id, title and summary. Anything else —
no row, two rows, a mangled field — is a frontmatter fault: fix it and re-run.

## Return

Present in chat the path written and the listing row, then one line: every vault recording
`latest_migration` below the new id, this repo's own included, is now gated until it runs
`/playbook migrate`.

```markdown
## Changed:
- [CREATED] migrations/006_<slug>/migration.md

## Notes:
- migration 6 (<slug>) written; query lists it as the newest shipped migration
- commands checked on a scratch vault: converted, second run a no-op
```
