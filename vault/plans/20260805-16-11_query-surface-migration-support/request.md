# Framing brief

## Request

> /home/anton/Dev/@A/notes/projects/claude-booping/plans/20260805-12-35_frontmatter-query - check this plans. I want migrations to be listed by this query. ideally with some condition like `--where id<{booping.id}`. So booping also should be available in jinja as `booping` dict. After you finish this playbook prompts, go run groom, to plan this changes for query, then i'll give the plan for develop.

## Task type

`feature`

New authored surface that does not exist today: a config key (`root:`), an operator (`id:gt`), and a context global (`booping`). Playbook and config authors write against all three.

- Not `bug` — nothing diverges from expected behaviour. The query surface does exactly what its plan specified; these are capabilities it deliberately scoped out ("the vocabulary can grow later; it cannot shrink").
- Not `refactoring` — a refactor changes internal structure with no user-visible behaviour change. Each item here adds a surface an author can use and could not before.

## Problem

The `migrate` playbook, authored in this session at `playbooks/migrate/`, resolves its pending-migration set through the frontmatter query surface. Its `survey` step pins this spelling:

```jinja
{% set pending = 'migrations.pending' | query(where={'id:gt': booping.latest_migration}) %}
{{ pending | as_table(columns=['id', 'title', 'summary']) }}
```

backed by a config-declared spec:

```yaml
migrations:
  pending:
    root: core
    glob: migrations/*/migration.md
    sort: id
```

Three pieces of that do not exist:

1. **No ordering operator.** `--where` is fixed at `k=v`, `k!=v`, `k:in=a,b` — a deliberate choice in the query plan's Decisions. Selecting "every migration above the recorded id" needs an ordering comparison. Confirmed spelling is `id:gt`, the clause-key suffix form, a sibling of `:in` — not a symbolic `>`, because the CLI parser splits on the first `=`. The comparison must be **numeric, not lexical**: the fresh-vault sentinel is `-1`, and id 10 must sort after id 9.

2. **No `booping` context global.** Nothing exposes booping's own state to a template. `booping.latest_migration` reads the repo `.booping` marker's `latest_migration` key — the id of the last applied migration, `-1` when none. The global mirrors the marker's key names rather than inventing aliases, so the template spelling and the file spelling are the same word.

3. **No glob root.** The query engine resolves a spec's `glob:` against the vault. Migrations ship in the plugin repo, so `migrations/*/migration.md` would search `<vault>/migrations/` and match nothing. Resolution is an explicit `root:` key on the spec taking the value `core` — matching the config-tier vocabulary (core → global → project). A spec omitting `root:` keeps today's vault-relative behaviour, so no existing spec changes.

Without all three, `booping render-playbook migrate --step survey` fails with `no query spec at config path: migrations.pending`, and the `migrate` playbook cannot run.

## Clarifications and Decisions

- Ordering operator is `id:gt` (suffix form), superseding the symbolic `id>` first sketched — the shipped surface carries every operator as a clause-key suffix and the CLI splits on the first `=`.
- Comparison is numeric, not lexical.
- `.booping` marker key is `latest_migration`, sentinel `-1` for "nothing applied".
- Glob root value is `core`, not `plugin` — it names the config tier the plugin's own files sit in.
- All three capabilities are planned together in one run, not split across plans.
- The context global is spelled `booping.latest_migration`, mirroring the marker key — not `booping.id`.
- The `migrate` playbook itself is already authored and out of scope here; this plan is only what `migrate` depends on.

## Scope

In scope, settled at intake:

- The three query-surface capabilities — `id:gt` (numeric), the `booping` context global, and the `root:` spec key.
- The render-time blocking notice: `booping render` / `render-playbook` refuse normal output and tell the user to run `/playbook migrate` when the vault is behind. The feature works end to end on merge rather than arriving in halves.
- A `migrations/` directory in the plugin repo carrying a first real migration, `001_plans_to_dirs/migration.md` — converting flat `plans/{slug}.md` files into plan directories at `plans/{slug}/index.md`. Gives the query something real to find and `migrate` something to apply.
- Both sides of `latest_migration`: the context global that reads it, and a deterministic setter that advances it after each migration lands. `apply-migration`'s spec forbids a hand-edit of `.booping`, and without the setter the playbook could survey but never land — which would leave the blocking notice pointing at a playbook that halts.

Out of scope:

- The `migrate` playbook itself — already authored at `playbooks/migrate/`.
- The `makemigration` playbook — a separate authoring run; it writes migration directories in the format this plan establishes.

Plan shape: a new standalone plan, not milestones appended to `plans/20260805-12-35_frontmatter-query/`. That plan is `in-progress` with M1–M6 landed; appending would shift scope and SP under an active sprint.
