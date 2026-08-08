---
reviewed_at: 20260805 08:03
---

# migrate — Brief

## Goal

Bring a project vault up to the current booping vault format. The plugin ships an ordered,
incremental series of migrations; the repo's `.booping` marker records the id of the last one
applied. When a vault is behind, booping's render surfaces block with a notice telling the user
to run `/playbook migrate`, and this playbook is what they run. It reads the recorded id,
resolves which migrations are pending, presents the whole pending list and what each one will
do, and — on a single approval — applies them all in id order. Migrations ship with the plugin
as directories under `migrations/` in the plugin repo — `migrations/NNN_<title>/migration.md`,
e.g. `migrations/001_plans_to_dirs/migration.md` — the zero-padded numeric prefix on the
directory name being the id. Each `migration.md` carries both the prompt (what to change and
why, for the model to judge) and the commands (the mechanical part), so applying one is a
matter of following its own instructions rather than logic baked into this playbook. The
latest shipped id is simply the highest-numbered directory present, so "the vault is behind"
means recorded id < highest shipped id. The canonical example is the plans
reshape: flat `plans/{slug}.md` files converted into plan directories at
`plans/{slug}/index.md`. The recorded id advances as each migration lands and each migration is
its own vault commit, so a re-run is a no-op and an interrupted run resumes from where it
stopped.

## Success result

The recorded migration id in the repo's `.booping` equals the latest id the plugin ships, every
pending migration having been applied in order, with the vault's files transformed as each
migration describes and nothing else touched. Each applied migration is its own vault commit, so
any one of them can be reverted independently. The user approved the whole pending set once, up
front, and is shown a single closing summary of what changed. Render surfaces stop emitting the
"vault is behind" notice, so normal booping work resumes. A vault already current reports that
and changes nothing; a dirty vault working tree is refused before anything is touched. A
migration that cannot complete stops the whole run then and there — no skipping ahead to the
next migration, no silent rollback — and reports concretely which migration id failed and what
failed, together with a proposed remedy, up to and including a manual fix the user performs by
hand. The recorded id and the commit history stay at the last migration that fully succeeded,
so once the user has resolved the issue they simply re-run and the run picks up from that id.

## Artifact home

None — the run is ephemeral, like `setup`. There is no run workdir and no `_runs/` directory;
the migration id in the repo's `.booping` marker is the only state, and resumability comes
purely from re-reading it.

## Wishes

- The repo's `.booping` marker holds a single incremental id for the latest applied migration;
  that id is the run's only state — not a separate ledger, and not a file in the vault.
- Apply-only. A sibling `makemigration` playbook — authored in its own playbook-authoring run
  afterwards — creates a new `migrations/NNN_<title>/migration.md` directory, which by existing
  raises the latest shipped id. That directory layout is therefore a **shared contract** between
  the two: `migrate` consumes exactly what `makemigration` produces.
- Migrations live in `migrations/` in the **booping plugin repo**, alongside `playbooks/`,
  `skills/` and `src/`. Each migration is a **directory**, not a single file:
  `migrations/NNN_<title>/migration.md`, the zero-padded prefix being the incremental id and
  `<title>` a kebab/snake descriptor, and the id also parsed off that prefix. Adding a
  migration means adding a directory — never editing this playbook.
- Listing migrations goes through the **frontmatter query surface** (plan
  `20260805-12-35_frontmatter-query`, M1–M6 landed): a query spec declared in config —
  `glob: migrations/*/migration.md` — addressed by its dotted config path and invoked as
  `booping query --config <dotted.path>` from a step, or via the `| query` filter in a body,
  with `--where` narrowing to the pending set and `--output table` / `| as_table` for
  presentation. Results come back as attribute-accessible rows in deterministic order. No raw
  globbing in the playbook.
- **`migration.md` carries frontmatter.** A query filters and projects on frontmatter keys, so
  each `migration.md` needs at minimum an `id` and a human-facing title/summary — a genuine
  addition to the migration file contract, and one that pays for itself: the up-front approval
  gate can present what each pending migration will do from the frontmatter summaries alone,
  with no unit reading a single body.
- Only `migration.md` is the contract. Because a migration is a directory it may carry siblings
  next to it — helper scripts, fixtures, reference material — the same way a playbook step dir
  carries material next to `prompt.md`. Everything besides `migration.md` is free workspace,
  meaningful only if that migration's own prompt references it; no further convention is
  imposed.
- **Each migration is a prompt, executed as its own isolated step.** The apply phase is not one
  step looping internally over the pending list: every pending migration is applied by its own
  isolated, context-fresh unit whose entire instruction is that migration's `migration.md` —
  prompt plus commands. This is a first-class shape of the playbook, not an implementation
  detail:
    - `migration.md` **is** the instruction handed verbatim to the isolated unit — the playbook
      itself carries no per-migration logic at all.
    - Isolation means one migration's context never leaks into the next; each unit gets a clean
      read of the vault exactly as the previous migration left it.
    - The number of applied units is data-driven — however many migrations are pending — not
      fixed by the graph. For `decompose`: this is a repeat-per-pending-migration shape, and
      instances must run **sequentially in id order, never in parallel**, since each migration
      assumes the previous one landed.
    - Tension for `decompose` to resolve: a failure inside one isolated unit must stop the whole
      sequence, rather than letting later units start.
- On failure: stop the run, name the failing migration id and what went wrong, and propose a
  remedy — a manual fix the user performs by hand is an acceptable and expected proposal. Never
  skip ahead, never silently roll back. The user resolves the issue and re-runs.
- One review gate, up front: resolve the pending list, present every pending migration and what
  each will do, ask once. On approval apply them all in id order, closing with a single
  summary. No gate per migration.
- Git safety: a clean vault git working tree is a preflight requirement — refuse to start on a
  dirty tree — and each migration is committed as it lands, keeping every migration
  independently revertable despite the single approval.
- Migrations apply strictly in id order, one at a time, and the recorded id advances per
  migration so a partial run is resumable and a current vault is a no-op.
- The example migration to carry through the design: flat `plans/{slug}.md` files becoming plan
  directories `plans/{slug}/index.md`.
- The playbook is the user-facing half of the feature only. The `.booping` id key, the
  `migrations/` layout, and the render-time "vault is behind" notice are core Python/config work
  tracked separately; this playbook assumes they exist and consumes them.

## Assumptions on the core plumbing (for the downstream plan)

These all land in the one downstream groom plan the user runs right after this playbook's
prompts are done.

- Listing itself is settled: a config-declared query spec globbing `migrations/*/migration.md`,
  addressed by dotted path via `booping query --config <dotted.path>`. What is missing is below.
- **`--where` needs a numeric/ordering comparison it does not have.** The query plan fixes the
  vocabulary at `k=v`, `k!=v`, `k:in=a,b` — deliberately, noting it "can grow later; it cannot
  shrink." Selecting the pending set is an ordering comparison (`<` / `>`) on the id, so the
  vocabulary has to grow by exactly that.
- **`booping` must be available in Jinja as a dict**, so the filter can be written as
  `--where id>{booping.latest_migration}` — the recorded migration id interpolated from a `booping` context
  global. No such global exists today.
- Still core work: a way to **read** the current migration id from the repo's `.booping` marker
  and to **advance** it after a migration lands — ideally the same deterministic writer pattern
  the rest of booping uses, not a hand-edit of `.booping`. The `booping` Jinja global above is
  the read side of this.
- `migration.md` separates its human/model-facing prompt from its executable commands, so a step
  can hand it to an isolated unit and act on it — the same file `makemigration` will write.
- A run touches **two locations**: the vault (files being transformed, committed per migration)
  and the repo's `.booping` (the id being advanced). The per-migration commit has to account for
  both.

## Open questions (unresolved — for `decompose` to raise)

- **The id is stated twice** — once as the `NNN_` directory-name prefix, once as the `id`
  frontmatter key the query filters on. Which is authoritative, and whether the two are checked
  against each other, is undecided.
- **Direction of the pending filter.** The user wrote the filter as `--where id<{booping.latest_migration}`,
  but pending migrations are the ones the vault has *not* applied — shipped id **greater than**
  the recorded id; `id<{booping.latest_migration}` selects the already-applied set. Intended semantics:
  pending = shipped id > recorded id. Confirm the operator direction rather than assume the
  wording was a slip.
- **Clean-tree preflight when the vault is repo-local.** The preflight requires a clean vault
  git working tree, and the id lives in the repo's `.booping`. When the vault lives inside the
  repo working tree, those are one and the same tree — so a strict preflight would refuse to
  start whenever any unrelated repo work is in flight, which is most of the time. The user has
  not decided how to handle this (path-scoped cleanliness check? warn instead of refuse? a
  confirmation override?); the brief records the problem, not an answer.
