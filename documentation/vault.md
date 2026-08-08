# Vault

Every booping project gets its own vault, scaffolded by the [setup playbook](install.md). By default it lives at `~/Claude/{project}/`; you can instead keep it **inside the repo** (a local vault) by setting the `.booping` marker's `vault_path:` key. The vault is plain markdown with YAML frontmatter — open the directory in Obsidian for graph view and backlinks across plans, retros, and lessons.

This page is the reference for every file and directory inside the vault. For the lifecycle that ties them together, start at [Quick start](quick_start.md).

## `plans/`

A plan is a directory: `{YYYYMMDDHHMM}_{kebab-title}/` holding `index.md`. That is the only shape booping discovers (the `core.plans.glob` config key, one entry — `plans/*/index.md`); a legacy flat `{YYYYMMDD}-{kebab-title}.md` has to be moved into a directory of its own to be seen. Each plan carries YAML frontmatter (status, type, story points, a one-line `summary`, etc.) and a body of milestones with tasks. Authored by the [groom playbook](groom.md), executed by the [develop playbook](develop.md).

A plan's `status:` is **run state**, not a shared lifecycle: `index.md` doubles as the run artifact of whichever playbook is operating on the plan, so the status vocabulary is the one that playbook declares in its own `states:` block. Only groom and develop run on a plan, and they are wired so one's terminal status is the next one's entry — groom ends at `ready-for-dev`, develop claims from there and ends at `done`. `done` is the end of the plan lifecycle. Only `booping playbook-transition` writes the status, and it refuses any move the machine does not declare. See [Playbooks → Run state](playbook.md#run-state).

Two frontmatter keys carry a finished plan into the tracks that run beside the lifecycle rather than inside it. `retro:` is null until a retrospective covers the plan, then holds that file's path (or `skipped`) — that null is the retro queue. `code_reviews:` is a **list**: seeded null, then appended to with the vault-relative path of every review that closes on the plan, so it reads as review history rather than a queue flag. The code-review queue is every plan at `done`, reviewed or not.

Three further keys carry the plan's session metrics. `sessions:` is the list of Claude Code session ids that groomed and developed it, appended by transition hooks on the groom and develop edges (a run started outside a Claude Code session simply adds nothing). When develop closes the plan, `active_minutes:` is stamped with the whole minutes of assistant-turn time summed across those transcripts and `models:` with the sorted distinct model ids that ran them. Both surface as columns in `sprints.md`, and `bin/booping session-time {vault}/plans/{slug}/index.md` recomputes them at any time — `--write` stamps the result back.

Sibling stubs created by a groom-driven split point at the primary plan via `split_from: plans/...` in their frontmatter.

## `retrospectives/`

Standalone retrospectives written by the [retro playbook](retro.md), named `{YYYYMMDDHHMM}_{kebab-title}.md` — one per retro run, whatever the size of its working set.

A retrospective records what actually shipped vs. the original spec, divergences, and the tensions you flagged during development. Its frontmatter carries `plan:` (the primary), `plans:` (every plan covered), `goal_verdicts:` (a verdict per plan) and its own `status:`.

That `status:` is the retro track's run state — `awaiting-retro → awaiting-learning` under retro, then `awaiting-learning → done` under [learn](learn.md). It is the retrospective's status, never a plan's: the plans it covers stay at `done` and only gain a `retro:` back-link. Both playbooks run with the vault root as their workdir and address the file with `--target retrospectives/{slug}.md`.

## `codereviews/`

One file per code-review run, written by the [code-review playbook](code_review.md), grouped by what was reviewed: `codereviews/{plan-dirname}/{YYYYMMDDHHmm}.md` when a plan is in scope, `codereviews/{target-slug}/{YYYYMMDDHHmm}.md` for an ad-hoc scope such as the latest commits. Scaffolded for new vaults and created lazily in older ones, so an existing vault needs no migration.

The file records `## Scope`, `## Findings`, `## Verdict` and `## Resolution`. Its frontmatter carries `plan:` — the reviewed plan's vault-relative path, or `null` — and its own `status:`, the code-review track's run state: `in-agent-review → human-review → done`. That status is the review's, never a plan's: the reviewed plan stays at `done` and only gains the review's path in its `code_reviews:` list. The playbook runs with the vault root as its workdir and addresses the file with `--target codereviews/{dir}/{ts}.md`.

## `lessons/`

Durable, project-wide rules accumulated over many sprints. Files are named `{N}_{title}.md` where `N` is a monotonic counter so the directory stays ordered chronologically.

Legacy lesson surface, authored by the retired `/learn` skill. Still read by the skills and playbook steps that include the lessons partial, but nothing writes it any more — the [learn playbook](learn.md) writes `_lessons/` below.

Scope note: this is the *untargeted* surface — everything in it reaches every body that includes the lessons partial. Targeted lessons live in `_lessons/` below, and a render of any playbook emits a non-blocking note while this directory still holds files.

## `_lessons/`

Targeted lessons — the lesson system, and the only file surface learn writes inside the vault. Same `{N}_{title}.md` naming, but each file carries a `targets:` frontmatter list saying what it applies to: `{playbook}`, `{playbook}/{step}`, `agent:{id}`, or `skill:{name}`. A file with no valid `targets:` is injected nowhere.

Written by the core `learn` [playbook](playbook.md). Injected by `booping render-playbook` into the composed procedure or a step prompt, and into the bodies of booping's own agents and skills at load time.

A machine-wide sibling at `<home_dir>/_lessons/` (default `~/Claude/_lessons/`) applies to every project; a file of the same name here shadows it. See [Playbooks → Lessons](playbook.md#lessons) for the full reference.

## `notes/`

Free-form user notes — plan-review comments, code-review threads, ideas for next sprints, anything else. **Skills and agents do not read this directory.** It is purely a scratchpad for you, kept in the same vault for convenience and Obsidian graph visibility.

## `.booping.log`

Append-only log of `booping` CLI invocations, at the vault root. Written by the CLI itself, read by nobody — it is there for debugging a render or a transition. The seeded `.gitignore` excludes it, so it never lands in a vault commit.

## `plan_templates/`

Project-local plan templates. Each file has frontmatter (`name`, `description`) plus two top-level sections (`# Plan Body`, `# Quality Checklist`). Discovered by the [groom playbook](groom.md) alongside the core templates that ship with the plugin; can override a core template by sharing its `name`, or add entirely new template flavours suited to the project.

## `review_templates/`

Project-local code-review templates. Loaded by the [code-review playbook](code_review.md); it picks the matching subset by inspecting the repo's manifests and reading each template's `description` frontmatter. Use this directory to add review checklists specific to your stack or domain.

Templates come from three tiers, least → most specific:

| Tier | Location |
|---|---|
| core | the plugin's own `docs/review_templates/` |
| global | `{home_dir}/review_templates/` — every project on the machine |
| project | `{vault}/review_templates/` — this project only |

A later tier overrides an earlier one by `name`, keeping the earlier entry's position; a name no earlier tier carries is appended. The rendered checklist table labels each entry with its tier.

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
