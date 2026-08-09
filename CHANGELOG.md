# Changelog

Notable user-visible changes, newest first, in the [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format; versions follow [semantic versioning](https://semver.org/).

## Unreleased

### Changed

- `booping scaffold` and `booping frontmatter-update` now answer with a unified diff of every file they changed, and say nothing about a file whose content did not move — a rendered prompt can act on the receipt instead of reading the file back.
- `booping scaffold` decides per file rather than per destination: an existing target is skipped and named, `--force` overwrites the files the tree names, and a destination that already holds part of the tree no longer aborts the run.
- `booping frontmatter-update` writes a scalar with its YAML type, so `sp=23` lands as an integer; a string whose plain form would reload as something else keeps its quotes.
- Groom seeds the plan directory from the new `core.groom_playbook.scaffold` tree, so a plan carries a real `created` and the repo's `commit` from the moment it exists, and the frontmatter shape lives in the config alone.

## v1.0.0 — 2026-08-08

Everything booping does became a playbook. `/playbook` is now the only skill the plugin ships, procedures carry their own run state and resume across sessions, and retro and code review moved onto tracks of their own.

### Added

- `/playbook` became the single entry point, and groom, develop, code-review, retro, learn, setup, migrate and playbook-authoring now ship as plugin playbooks discovered beside your own global and project ones.
- Playbooks gained run state: a playbook declares named state machines in `playbook.yaml`, each run persists its status to its own artifact, and a later session picks the run up where it stopped. A machine can be authored without a fixed artifact and addressed by path instead.
- An active groom or develop run can be cancelled from any point, ending at `cancelled` and running its own exit hooks.
- A `graph:` node can now be a subgraph — its own dependencies, an inner graph of steps, and an optional `repeat:`.
- Steps declare a delegation level: inline, assisted (heavy reads handed to the configured research agent, which is resumed rather than respawned), or detached in its own sub-agent, set by the step's `detached:` field. It replaces `agent:`, and a leftover `agent:` key stops the run.
- `jinja: true` renders a playbook's preamble and step bodies against live project context.
- Lessons live in two flat `_lessons/` roots — global and vault — and route by a `targets:` list that names playbooks and individual steps as well as agents and skills; an untargeted lesson injects nowhere.
- Frontmatter across the vault became queryable: `booping query`, the `query` and `as_table` template filters, `--where` filters, sorting and projection, with query specs declarable at any config path.
- Config can declare macros that rendered bodies call through `macro()`, each naming its command and whether it resolves against the repo or the vault.
- `booping scaffold` materialises any config-declared file tree — a playbook skeleton, the vault layout, or one of your own.
- `core.research_agent` points any assisted step's delegated reads at the agent you choose.
- A `frontmatter-update` transition hook can write to any workdir-relative file, not only the machine's own artifact.
- Transition hooks resolve scripts from shared `_scripts/` roots, playbook-local first, and accept arguments — one parameterised script replaces near-duplicates.
- Review templates layer across the core, global and project levels, later levels overriding by name, matching how lessons already worked.
- `booping session-stats` mines a plan's stamped sessions for how long the work actually took and what it cost. Active time now excludes every stretch the run spent waiting on you, and four token totals plus the models that ran land beside it as `metrics_`-prefixed frontmatter, surfaced as `sprints.md` columns. Point it at a directory rather than one plan at a time; it prints the same JSON it writes.

### Changed

- Upgrading a vault now runs `/playbook migrate`: a vault behind the shipped migrations blocks renders with a notice, and the playbook applies each pending migration in order and commits it. This release ships migrations that convert flat plan files into plan directories, relocate `plans/{slug}/retro.md` into `retrospectives/`, normalise plan statuses, and move the session metrics keys onto their `metrics_` prefix.
- A plan became a directory — `plans/{slug}/` holds its `index.md`, briefing and web research together — and the discovery shape is the `core.plans.glob` config key.
- Retro became its own track: develop closes a plan at `done` immediately, and retro and learn advance a standalone `retrospectives/{slug}.md` linked back from the plan's `retro:` key.
- Code review became its own track: every review persists as `codereviews/{plan}/{timestamp}.md` with an `in-agent-review` → `human-review` → `done` machine, while the plan carries the full `code_reviews:` history and stays in the queue, so re-review is first class.
- Config settings moved under a `core` namespace — a playbook's own keys at `core.{name}_playbook`, shared keys directly under `core` — and any key loads at any level without an unknown-key warning. Existing `config.yaml` files need re-nesting.
- The shared plan-lifecycle vocabulary is gone; each artifact moves only through its own playbook's `states:` machine, so every playbook owns its statuses.
- Groom runs its steps in the driving session instead of spawning one sub-agent per step, and stops at a single approval gate near the end instead of four confirm points. A detached cross-review step still runs when `core.groom_playbook.cross_review_agent` is set.
- Learn shows the full playbook table of contents and pins each lesson's exact `targets:` in the review table before writing it.
- A playbook step is now a directory holding `prompt.md`, rather than a single file.
- Playbook names must be unique across the core, global and project levels: a same-named playbook no longer shadows silently — the run stops and asks you to rename, and the listing flags the clash.
- Step bodies load one at a time during a run, so a long playbook's context no longer grows with every step it contains.
- `sprints.md` is seeded once at setup as a live Obsidian Bases view and never regenerated; `render-sprints` is gone, and `booping query --config core.plans` is the machine-readable equivalent.

### Removed

- The `/chat` and `/help` skills were retired; `/playbook` is the plugin's only skill.
- Per-playbook `_lessons/` directories and the lesson `step:` key no longer route lessons — legacy content surfaces a migration note instead.
- The `@head` shorthand in `frontmatter-update` hooks was dropped; call the `git_commit` macro to stamp HEAD.
