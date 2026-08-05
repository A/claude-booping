# migrate — Brief

## Goal

Bring a project vault up to the current booping vault format. The plugin ships an ordered,
incremental series of migrations; the repo's `.booping` marker records the id of the last one
applied. When a vault is behind, booping's render surfaces block with a notice telling the user
to run `/playbook migrate`, and this playbook is what they run. It reads the recorded id,
resolves which migrations are pending, presents the whole pending list and what each one will
do, and — on a single approval — applies them all in id order. Every migration is a single file
shipped with the plugin carrying both the prompt (what to change and why, for the model to
judge) and the commands (the mechanical part), so applying one is a matter of following its own
instructions rather than logic baked into this playbook. The canonical example is the plans
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
  afterwards — writes new migration files and bumps the shipped latest id. The migration file
  format is therefore a **shared contract** between the two: `migrate` consumes exactly what
  `makemigration` produces.
- Each migration is one self-contained file shipped with the plugin, carrying its prompt and
  its commands. Adding a migration means adding a file — never editing this playbook.
- **Each migration is a prompt, executed as its own isolated step.** The apply phase is not one
  step looping internally over the pending list: every pending migration is applied by its own
  isolated, context-fresh unit whose entire instruction is that migration file's prompt plus its
  commands. This is a first-class shape of the playbook, not an implementation detail:
    - The migration file's prompt **is** the instruction handed to the isolated unit — the
      playbook itself carries no per-migration logic at all.
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
- The playbook is the user-facing half of the feature only. The `.booping` id key, the on-disk
  migration file format, and the render-time "vault is behind" notice are core Python/config
  work tracked separately; this playbook assumes they exist and consumes them.

## Assumptions on the core plumbing (for the downstream plan)

- A way to read the current migration id from the repo's `.booping` marker and to list the
  migrations the plugin ships with their ids, invokable from a playbook step (a `booping`
  subcommand, or a documented file/key layout the step can read directly).
- A way to advance the recorded id after a migration lands — ideally the same deterministic
  writer pattern the rest of booping uses, not a hand-edit of `.booping`.
- A migration file format that separates its human/model-facing prompt from its executable
  commands, so a step can render one and act on it — the same format `makemigration` will write.
- A run touches **two locations**: the vault (files being transformed, committed per migration)
  and the repo's `.booping` (the id being advanced). The per-migration commit has to account for
  both.

## Open questions (unresolved — for `decompose` to raise)

- **Clean-tree preflight when the vault is repo-local.** The preflight requires a clean vault
  git working tree, and the id lives in the repo's `.booping`. When the vault lives inside the
  repo working tree, those are one and the same tree — so a strict preflight would refuse to
  start whenever any unrelated repo work is in flight, which is most of the time. The user has
  not decided how to handle this (path-scoped cleanliness check? warn instead of refuse? a
  confirmation override?); the brief records the problem, not an answer.
