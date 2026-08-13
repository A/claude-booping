# booping plugin — project guide

Claude Code plugin that grooms and executes plans across user projects. Plans and other run artifacts live in the per-project **vault** — `~/Claude/{project}/` by default, or a repo-local directory via the `.booping` marker's `vault_path:` key. Skills, agents, playbooks, templates, and config live in this repo.

One shipped skill (`/playbook`); everything procedural is a **playbook** it drives (`groom`, `develop`, `code-review`, `retro`, `learn`, `setup`, `migrate`, `playbook-authoring`).

## Commands

- `just lint` / `just typecheck` / `just pytest` — ruff / basedpyright / pytest over both uv projects, `booping-python/` then `booping-tracker/`.
- `just snapshots` — diff committed playbook reports against a fresh hermetic render (writes nothing). `just snapshots-accept [playbook]` — the **only** writer of the committed reports.
- `just mdcheck` — structural rule checks over the rendered reports. Needs the `mdcheck` binary: `cargo install markdown-checker` (the crate named `mdcheck` is unrelated).
- `just e2e [pytest args…]` — run both txtar contract corpora through pytest, passing any arguments straight to it (`just e2e -k config-get`, `just e2e --txtar-update`); `--txtar-update` rebaselines the selected cases. A `-k` expression that selects in one corpus only leaves the other collecting nothing, which is not a failure.
- `just ci` — everything CI runs, in order: `lint typecheck pytest snapshots mdcheck e2e`. Run before committing.
- `just eval|smoke|regress <playbook>/<step>` (or `all`) — promptfoo eval suites; `just suites` lists them. Runs on subscription auth (`claude -p`), never in CI; each run posts a sticky, advisory PR comment via `scripts/eval-pr-comment.sh` (`EVAL_PR=0` opts out) — no commit status, no merge gate.
- `just docs` / `just docs-serve` — build / preview the public docs site.
- `bin/booping <subcommand> --help` — the runtime CLI: `render`, `render-playbook`, `playbook-state`, `playbook-transition`, `query`, `config-get`, `marker-set`, `scaffold`, `frontmatter-update`, `session-stats`, `debug-context`.
- `bin/booping-tracker <verb> --help` — the task-tracker CLI: `states`, `show`, `comment`, `issue-create`, `issue-update`, `relate`, `sync`. Reference: [booping-tracker/README.md](booping-tracker/README.md).

## Layout

- `booping-python/` — uv Python project with the `booping` CLI. Source `src/booping/`, tests `tests/`, contract corpus `e2e/` — cases plus a `conftest.py` configuring the `pytest-txtar` plugin, which owns the runner and the case-format spec (https://github.com/A/pytest-txtar); `scaffold` is verified there, not by the unit tests.
- `booping-tracker/` — second uv project with the `booping-tracker` CLI, holding every tracker concern (and `httpx`) out of `booping-python`. Source `src/booping_tracker/` — `cli.py`, `config.py`, `facade.py` (the operation set) and one module per provider under `providers/` — tests `tests/`, contract corpus `e2e/` with its own `conftest.py` and `README.md`. Config is not re-implemented: it shells to `bin/booping config-get core.tracker`.
- `bin/booping`, `bin/booping-tracker` — the two product entry points: shell wrappers exec'ing `uv run --project {booping-python|booping-tracker} … "$@"`.
- `scripts/` — dev tooling behind `just`: `snapshots.py`, `mdcheck.py` (uv inline Python), and the eval harness (`eval-*.sh`, `report-*.jq`). Not shipped to users.
- `src/config.yaml` — runtime config, single source of truth for structured data (macros, query specs, scaffold trees, task types, sprint scale, per-playbook agents). Heavily commented — read it for key semantics.
- `src/templates/` — runtime skill/agent templates + `_partials/`, rendered at skill-load time. Edits are **live**, no rebuild.
- `skills/<name>/SKILL.md`, `agents/<name>.md` — hand-authored thin shells: frontmatter (including `effort:`) plus one `!`booping render src/templates/…`` line that pulls in the body at load time.
- `playbooks/<name>/` — core playbooks. Also: `_partials/` (shared fragments), `_scripts/` (shared hook scripts), `_lib/` (eval harness), `_fixtures/vault/` (hermetic render fixture). Each playbook commits its rendered report at `playbooks/<name>/_reports/output.md`.
- `playbooks/*/_specs/` — playbook-authoring run artefacts and design history; intentionally stale, not a spec of current behaviour.
- `migrations/<NNN>_<slug>/migration.md` — plugin-shipped vault migrations. Frontmatter `id` is the authority; a vault's applied watermark is the `.booping` marker's `latest_migration` key, and every render surface gates on it. Authoring primitives: query specs with `root: core` scan plugin-shipped files, numeric `--where` ordering (`gt`/`lt`), `{{ booping.latest_migration }}` in templates, marker writes via `booping marker-set`.
- `docs/` — hand-authored plugin-internal fragments, lazy-loaded by skills via `${CLAUDE_PLUGIN_ROOT}/docs/<name>.md` links. No build step.
- `documentation/` — public docs site source (MkDocs → gh-pages on push to `master`). Hand-authored.

## Rendering pipeline

One stage, at **runtime** (skill load): a thin shell's `!`booping render src/templates/…`` line renders the body with full project context — config merge, vault, lessons, playbooks.

## Config

- Three-tier deep merge, **core → global → project**: `src/config.yaml` ← `${XDG_CONFIG_HOME:-~/.config}/booping/config.yaml` ← `{vault}/config.yaml`. Later tiers win; lists replace wholesale. No schema gate and no tier restriction — any key loads in any tier.
- Top level is exactly `home_dir` + `core`. **Placement rule** under `core`: a key one playbook owns lives at `core.{name}_playbook`; a shared key sits directly under `core`. A user's own playbook namespace copies this shape.
- Any mapping in the merged config can be a **query spec** (`booping query --config <dotted.path>`, `| query` filter) or a **scaffold tree** (`booping scaffold <dotted.path> <dest>`) — the value at the dotted path is the spec/tree, no wrapper key. Specs live beside their consumer (`core.{name}_playbook.queries.<id>`), never in a central registry.
- `core.plans` — plan shape shared by groom and develop: `glob` (plan discovery) and `milestones` (`glob` relative to the plan dir, matching the milestone file inside each milestone directory and never a sidecar beside it, + `table_columns` for the generated table). Never restate either literal in prose.
- `core.tracker` — task-tracker surface, directly under `core` because several playbooks mirror outward through it: `driver` (`cli` | `linear`, `--driver` overrides per invocation, an unknown name is a hard error) plus one settings block per driver. Secrets are named, never carried: `api_key_env` holds the *name* of the environment variable the token lives in — **no config value anywhere is env-interpolated**, in any tier.
- `core.macros.<name>` — an argv list, or a mapping with `command:` plus `cwd: repo|vault` scoping; rendered bodies call them via the `macro()` global; `--stub-macro` (or a vault `macro_stubs:` mapping) pins them for reproducible renders.
- Full reference: [documentation/project_config.md](documentation/project_config.md).

## Playbooks

Multi-step guided procedures discovered from three roots — core `playbooks/`, global `<home_dir>/_playbooks/`, local `{vault}/_playbooks/` — names unique across roots. Each dir: `playbook.md` (identity frontmatter + preamble body), optional `playbook.yaml` (`graph:` + optional `state:`/`states:`), and one directory per step holding `prompt.md`.

- `graph:` defines order and parallelism via topological waves; a mapping node is a one-level **subgraph**. Parallel co-members must be `detached:`.
- Delegation per step via the single `detached:` frontmatter field: absent → runner-performed; `<model>:<effort>` → generic sub-agent; other string → named sub-agent.
- `jinja: true` opts all bodies into Jinja through the full context env, each with a loader chain body → step dir → playbook dir → discovery roots (local → global → core) → `src/templates/`.
- **Run state** is opt-in via `states:` (named state machines: `artifact`, `initial`, `statuses`, transitions with `when`/`gates`/`hooks`). `booping playbook-transition` is the **only** writer of run state; its printed mutation report is authoritative — never re-read to verify. `booping playbook-state` is the read-only frontier report used to resume; both address the run artifact via `--target` when the machine declares no `artifact:`. Hooks: `frontmatter-update` and `script <name> [args…]` (argv passed through; playbook `_scripts/` first, then the discovery roots' `_scripts/`, most specific wins).
- **Tracker mirroring**: `playbooks/_scripts/tracker-sync` (push the artifact's status) and `tracker-comment <workdir-relative-path>` (post a file as a comment) are `script` hooks on groom's edges. Both absorb the tracker's exit code and warn on stderr — a hook failing after `status:` is written would abort the transition with the vault advanced and the tracker behind; `booping-tracker sync --artifact …` by hand is the reconcile.
- **Driver-conditional injection**: `playbooks/_partials/tracker_driver.md` is included by groom's preamble, and `intake` / `present` carry their own blocks, all gated on `config.core.tracker.driver == 'linear'` — under `cli` they render nothing and every body is byte-identical to before. The shared `src/templates/_partials/_playbook_driving.j2` is deliberately untouched.
- **Lessons**: markdown files in `<home_dir>/_lessons/` and `{vault}/_lessons/` with a `targets:` list (`{playbook}`, `{playbook}/{step}`, `agent:{id}`, `skill:{name}`), injected by `render-playbook` and by internal agent and skill bodies. Untargeted lessons inject nowhere.
- Graph/render problems surface as in-band `**STOP — tell the user:**` / `**Note — tell the user:**` notices at exit 0, never crashes.
- The driving protocol lives in `src/templates/_partials/_playbook_driving.j2`. Full mechanics: [documentation/playbook.md](documentation/playbook.md).

## Lifecycle

Each playbook owns its own status vocabulary in its `states:` block — there is no shared lifecycle, and those blocks are the authoritative sets.

- **Plan track** (`groom` + `develop`): the plan is a directory `{vault}/plans/{slug}/` whose `index.md` is both run artifact and plan document; groom ends at `ready-for-dev`, develop at `done` | `fail`, both also `cancelled`. Shape is the `core.plans.glob` config key (`plans/*/index.md`).
- **Parked groom runs**: `awaiting-clarification` holds a groom run that raised a question it cannot answer itself — entered from `framing` and from `drafting`, each entering edge stamping `return_to` with its own source and each return edge clearing it, so the mapping is static per edge rather than computed. The questions live in the `clarifications.md` sidecar beside `index.md` (format: `docs/clarifications.md`), one H2 per question with an id and an `open`/`answered` state; the sidecar is what a later invocation reads to resume, and what `tracker-comment` posts verbatim. `tracker_provider` / `tracker_request` / `tracker_issue` on `index.md` record the mirror, hook- and CLI-written only.
- **Milestone directories**: each milestone is a directory `milestones/M{nn}-{kebab}/` under the plan directory, holding the milestone file named after it (`core.plans.milestones.glob`, `milestones/*/M*.md`) — frontmatter `id`/`title`/`sp`/`status`/`plan` plus tasks, DoD and Verify — and any sidecar the sprint writes beside it, currently `feedback.md`, the runner's findings on a rejected attempt and the only place attempts are counted. The milestone file is the contract handed to a worker by path — `index.md` is context only, its `## Milestones` table (`core.plans.milestones.table_columns`) and the plan's `sp` are generated. Milestone `status:` is develop's per-instance run state (`pending` → `in-progress` → `done`, `blocked` off in-progress), instance `M{nn}-{kebab}`; every edge runs the `refresh-milestone-table` hook. The worker runs its milestone's `## Verify` and makes the repo commit; the runner validates that commit against the DoD, flips the checkboxes and takes the transitions.
- **Retro track** (`retro` + `learn`): artifact is a standalone `{vault}/retrospectives/{slug}.md` (`awaiting-retro` → `awaiting-learning` → `done`); plans stay at `done` throughout. Addressed with `--target` since the machines declare no `artifact:`.
- **Code-review track** (`code-review`): artifact is `{vault}/codereviews/{plan-dirname}/{ts}.md` (ad-hoc scopes: `codereviews/{target-slug}/{ts}.md`, `plan: null`), machine `in-agent-review` → `human-review` → `done`; plans stay at `done`. Addressed with `--target` since the machine declares no `artifact:`.
- The tracks join through **plan frontmatter, not status**: `retro:` is null until covered, so `{status: done, retro: null}` is the retro queue; `code_reviews:` is a list of every review that closed on the plan — history, not a queue flag — so the review queue is every `{status: done}` plan, re-review included.
- Vault commits are each playbook's own business, via `script` hooks on its edges.

## Vault (out of framework scope, authored per project)

`plans/`, `retrospectives/`, `codereviews/`, `_lessons/` (targeted), `_playbooks/` (user playbooks), `plan_templates/`, `review_templates/`, `notes/`, `sprints.md` (Obsidian Bases fence, seeded once, written by nothing), `.booping.log` (CLI log at the vault root, gitignored there). Obsidian-ready: markdown + YAML frontmatter only. See [documentation/vault.md](documentation/vault.md).

## Principles

- **Minimum useful context**: a skill or step body carries only what it needs; lazy-link route-specific detail via `docs/` instead of inlining.
- **Less prose, less drift**: cut motivation, restated context, and preambles. The schema is the source of truth; prose decays.
- **Schema over prose**: structured data lives in `src/config.yaml` and is rendered from there — never restated in body prose.
- **Reference the source, never the literal**: dynamic values (statuses, queues, agent ids) render from config/query specs.
- **Wide-domain**: skills and playbooks stay stack-agnostic. Project specifics live in the vault's `_lessons/` and the attached repo's own `CLAUDE.md` — the only two destinations learn writes.
- **Agent wiring**: the driver owns all vault reads/writes; worker agents touch only repo code. Project-local shaping of an agent or a skill is a targeted lesson (`agent:{id}`, `skill:{name}`), not a separate extension file. External global agents at `~/.claude/agents/` wire in via config — see [documentation/integrating-external-agents.md](documentation/integrating-external-agents.md).

## Editing conventions

- `src/templates/**` edits are live — no rebuild step anywhere in the repo.
- Playbook source edits (manifests, step `prompt.md`, shared partials) drift the committed reports. Loop: edit → `just snapshots` (read the diff) → `just snapshots-accept` → commit source and report together.
- Eval suites sit beside their step (`tests.yaml` + `promptfooconfig.yaml` + `_fixtures/`); two tiers per fixture, `smoke` (deterministic) and `regress` (llm-rubric judges). Shared asserts, graders and rubric prompts live in `playbooks/_lib/`.
- No comments that restate code — only WHY for non-obvious bits.
- Conventional commits with scope: `feat(booping): …`, `fix(groom): …`.
- README's Statuses section is hand-maintained narrative over the per-playbook `states:` blocks — revisit it when one changes.
- New procedures should be playbooks, not skills; a skill is only for a surface `/playbook` cannot drive. Reference for the rare new skill: `src/templates/skills/playbook.md.j2` + its thin shell at `skills/playbook/SKILL.md`.
