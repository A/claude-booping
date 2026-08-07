# Vault

Every booping project gets its own vault, scaffolded by the [setup playbook](install.md). By default it lives at `~/Claude/{project}/`; you can instead keep it **inside the repo** (a local vault) by setting the `.booping` marker's `vault_path:` key. The vault is plain markdown with YAML frontmatter — open the directory in Obsidian for graph view and backlinks across plans, retros, and lessons.

This page is the reference for every file and directory inside the vault. For the lifecycle that ties them together, start at [Quick start](quick_start.md).

## `plans/`

A plan is a directory: `{YYYYMMDDHHMM}_{kebab-title}/` holding `index.md`. That is the only shape booping discovers (the `core.plans.glob` config key, one entry — `plans/*/index.md`); a legacy flat `{YYYYMMDD}-{kebab-title}.md` has to be moved into a directory of its own to be seen. Each plan carries YAML frontmatter (status, type, story points, a one-line `summary`, etc.) and a body of milestones with tasks. Authored by the [groom playbook](groom.md), executed by the [develop playbook](develop.md).

A plan's `status:` is **run state**, not a shared lifecycle: `index.md` doubles as the run artifact of whichever playbook is operating on the plan, so the status vocabulary is the one that playbook declares in its own `states:` block. Only groom and develop run on a plan, and they are wired so one's terminal status is the next one's entry — groom ends at `ready-for-dev`, develop claims from there and ends at `done`. `done` is the end of the plan lifecycle. Only `booping playbook-transition` writes the status, and it refuses any move the machine does not declare. See [Playbooks → Run state](playbook.md#run-state).

Two frontmatter keys carry a finished plan into the tracks that run beside the lifecycle rather than inside it. `retro:` is null until a retrospective covers the plan, then holds that file's path (or `skipped`); `code_review:` is null until a review closes on the plan, then holds the review date. Each null is a queue.

Sibling stubs created by a groom-driven split point at the primary plan via `split_from: plans/...` in their frontmatter.

## `retrospectives/`

Standalone retrospectives written by the [retro playbook](retro.md), named `{YYYYMMDDHHMM}_{kebab-title}.md` — one per retro run, whatever the size of its working set.

A retrospective records what actually shipped vs. the original spec, divergences, and the tensions you flagged during development. Its frontmatter carries `plan:` (the primary), `plans:` (every plan covered), `goal_verdicts:` (a verdict per plan) and its own `status:`.

That `status:` is the retro track's run state — `awaiting-retro → awaiting-learning` under retro, then `awaiting-learning → done` under [learn](learn.md). It is the retrospective's status, never a plan's: the plans it covers stay at `done` and only gain a `retro:` back-link. Both playbooks run with the vault root as their workdir and address the file with `--target retrospectives/{slug}.md`.

## `lessons/`

Durable, project-wide rules accumulated over many sprints. Files are named `{N}_{title}.md` where `N` is a monotonic counter so the directory stays ordered chronologically.

Legacy lesson surface, authored by the retired `/learn` skill. Still read by the skills and playbook steps that include the lessons partial, but nothing writes it any more — the [learn playbook](learn.md) writes `_lessons/` below.

Scope note: this is the *untargeted* surface — everything in it reaches every body that includes the lessons partial (`/code-review`, the researcher agent, and the groom, retro and code-review playbook steps that include it). Targeted lessons live in `_lessons/` below, and a render of any playbook emits a non-blocking note while this directory still holds files.

## `_lessons/`

Targeted lessons — the playbook-side lesson system. Same `{N}_{title}.md` naming, but each file carries a `targets:` frontmatter list saying what it applies to: `{playbook}`, `{playbook}/{step}`, or `agent:{id}`. A file with no valid `targets:` is injected nowhere.

Written by the core `learn` [playbook](playbook.md). Injected by `booping render-playbook` into the composed procedure or a step prompt, and into the bodies of booping's own agents at load time.

A machine-wide sibling at `<home_dir>/_lessons/` (default `~/Claude/_lessons/`) applies to every project; a file of the same name here shadows it. See [Playbooks → Lessons](playbook.md#lessons) for the full reference.

## `notes/`

Free-form user notes — plan-review comments, code-review threads, ideas for next sprints, anything else. **Skills and agents do not read this directory.** It is purely a scratchpad for you, kept in the same vault for convenience and Obsidian graph visibility.

## `_booping/skill_<name>.md`

Per-skill extension file. Loaded automatically into the matching skill's context at invocation time, so the project's local conventions reach it without you having to restate them. Two skills ship — `code-review` and `playbook` — so `skill_code-review.md` and `skill_playbook.md` are the files that reach a skill body. Authored and updated by the [learn playbook](learn.md) — do not hand-edit unless you know what learn would have written.

To correct a **playbook** rather than a skill, write a targeted lesson in `_lessons/` instead (see below): playbooks have no extension file.

The [setup playbook](install.md) creates `_booping/` but seeds no extension files. Learn writes them as findings accumulate — typically:

- `_booping/agent_booping-developer.md` — stack + conventions for the developer agent.
- `_booping/skill_code-review.md` — project-local signal the repo `CLAUDE.md` doesn't carry (e.g. house review rules, env / service notes).

Nothing here is required: an empty `_booping/` is a valid vault.

## `_booping/agent_<full-agent-name>.md`

Per-agent extension file. Injected into the matching worker agent's body at agent load time, so subagents inherit project rules without separate reads. The filename uses the agent's full name (which starts with `booping-`) — e.g. `_booping/agent_booping-developer.md`, `_booping/agent_booping-researcher.md`. Authored and updated by the [learn playbook](learn.md).

## `plan_templates/`

Project-local plan templates. Each file has frontmatter (`name`, `description`) plus two top-level sections (`# Plan Body`, `# Quality Checklist`). Discovered by the [groom playbook](groom.md) alongside the core templates that ship with the plugin; can override a core template by sharing its `name`, or add entirely new template flavours suited to the project.

## `review_templates/`

Project-local code-review templates. Loaded by [/code-review](code_review.md) alongside the core templates; the skill picks the matching subset by inspecting the repo's manifests and reading each template's `description` frontmatter. Use this directory to add review checklists specific to your stack or domain.

## `sprints.md`

An at-a-glance view of every plan in the vault — an [Obsidian Bases](https://help.obsidian.md/bases) fence over the `plans/*/index.md` files, ordered by status and sorted newest-first. Bases resolves every path against the *Obsidian* vault root, so the seeded filter scopes itself with `file.inFolder(this.file.folder)` — the folder of the note holding the fence — which keeps it correct when the booping vault is nested inside a larger Obsidian vault.

**Seeded once by `booping scaffold core.setup_playbook.scaffold`; nothing rewrites it.** Obsidian evaluates the query live against the plan files, so the view is never stale. Edit the fence to change columns, sorting or filters — it is yours from the moment it is written.

Outside Obsidian the file is an inert code block. For a machine-readable listing of the same data, use `bin/booping query`:

```bash
bin/booping query --config core.plans --where status=ready-for-dev --sort -created
```

`--where` is a fixed operator vocabulary, not an expression language. The clause key carries the operator as a suffix:

| Clause | Meaning |
|---|---|
| `k=v` | equals |
| `k!=v` | does not equal |
| `k:in=a,b` | is one of |
| `k:gt=n` | greater than `n`, numerically |
| `k:lt=n` | less than `n`, numerically |

Clauses are repeatable and all of them apply. A row whose frontmatter lacks the field fails every operator, and so does a value that will not read as a number under `:gt` / `:lt`.

## `.booping`

The marker that ties a repo to its vault. Unlike everything else on this page, `.booping` lives in the **attached repo's working tree** (its root), not inside the vault. It is written by the [setup playbook](install.md) and carries the `project_name: {project}` key — how every skill resolves which vault to operate on. It may also carry an optional `vault_path:` key: when present, the vault resolves to that path (relative paths against the repo root, absolute paths and `~` honoured) instead of `~/Claude/{project}/` — this is how a repo-local vault is wired. A third key, `latest_migration:`, records which of the plugin's shipped vault migrations this project has already applied — a watermark, written only by `bin/booping marker-set latest_migration=<id>` as the [migrate playbook](playbook.md) finishes one. When it falls behind the plugin, every render stops with a notice telling you to run `/playbook migrate`. Commit `.booping` with the repo so the binding travels with the checkout.

## `config.yaml`

Optional per-project override for the plugin's `src/config.yaml`. Deep-merges over the plugin defaults at render time (no rebuild step): dict keys merge, list keys replace wholesale. The natural targets for per-project tuning are the sprint scale, task types, branch conventions and agent wiring. Nothing is validated and no key is restricted to a tier, so your own playbooks' config lives here too.

See [Project config](project_config.md) for the full key tour and override mechanics.
