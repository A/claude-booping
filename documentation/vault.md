# Vault

Every booping project gets its own Project Vault, scaffolded by the [setup playbook](install.md). By default it lives at `~/Claude/{project}/`; set the `.booping` marker's `vault_path:` key to keep it **inside the repo** instead (a local vault). The vault is plain markdown with YAML frontmatter — open the directory in Obsidian for graph view and backlinks across plans, retros, and lessons.

This page is the reference for every file and directory inside the vault. For the lifecycle that ties them together, start at [Quick start](quick_start.md).

## `plans/`

A plan is a directory `{YYYYMMDDHHMM}_{kebab-title}/` holding `index.md` — the shape the groom playbook authors. The `core.plans.glob` config key governs discovery: an ordered list of globs, `plans/*/index.md` as shipped, so the plan shape is data rather than engine logic — a vault laying plans out differently edits that one key and every consumer follows. Each plan carries YAML frontmatter (status, type, story points, a one-line `summary`, etc.) and a body of milestones with tasks. Authored by the [groom playbook](groom.md), executed by the [develop playbook](develop.md).

A plan's `status:` is **run state**, not a shared lifecycle: `index.md` doubles as the run artifact of whichever playbook is operating on the plan, so the status vocabulary is the one that playbook declares in its own `states:` block. Groom ends at `ready-for-dev`; develop claims from there and ends at `done` — or at `fail` when a blocker survives two fix attempts, or `cancelled` when you call the run off. All three are terminal: the end of the plan lifecycle. Only `booping playbook-transition` writes the status, and it refuses any move the machine does not declare. See [Playbooks → Run state](playbook.md#run-state).

Two frontmatter keys carry a finished plan into the tracks that run beside the lifecycle rather than inside it. `retro:` is null until a retrospective covers the plan, then holds that file's path (or `skipped`) — that null is the retro queue. `code_reviews:` is a **list**: seeded null, then appended with the vault-relative path of every review that closes on the plan, so it reads as review history rather than a queue flag. The code-review queue is every plan at `done`, reviewed or not.

Seven further keys carry session metrics. `sessions:` is the list of Claude Code session ids that groomed and developed the plan, appended by transition hooks on the groom and develop edges (a run started outside a Claude Code session adds nothing). When develop closes the plan, six flat `metrics_`-prefixed keys are stamped from those transcripts — `metrics_active_minutes:` (whole minutes of active work), `metrics_models:` (the sorted distinct model ids that ran them), and the token totals `metrics_tokens_input:`, `metrics_tokens_output:`, `metrics_tokens_cache_creation:`, `metrics_tokens_cache_read:`. They are flat rather than a nested `metrics:` mapping because Obsidian Properties and Bases cannot address a nested mapping as a column, and all six surface as columns in `sprints.md`. `bin/booping session-stats {vault}/plans --mask index.md` recomputes them at any time — it stamps by default, `--force` overwrites existing values and `--dry-run` prints the same JSON without writing.

Active time is turn time minus every interval the run spent blocked on a human: an `AskUserQuestion` tool call up to its matching `tool_result`, and any span ending in a user rejection. System decisions (`permission-rule`, `automode-blocked`, `automode-unavailable`) are never subtracted. **The metric under-reports wait**: a tool call auto-approved by a permission rule and one a human approved after ten minutes are structurally identical in the transcript — no field distinguishes them — so that wait stays inside active time rather than being guessed at.

Sibling stubs created by a groom-driven split point at the primary plan via `split_from: plans/...` in their frontmatter.

## `retrospectives/`

Standalone retrospectives written by the [retro playbook](retro.md), named `{YYYYMMDDHHMM}_{kebab-title}.md` — one per retro run, whatever the size of its working set.

A retrospective records what actually shipped vs. the original spec, divergences, and the tensions you flagged during development. Its frontmatter carries `plan:` (the primary), `plans:` (every plan covered), `goal_verdicts:` (a verdict per plan) and its own `status:`.

That `status:` is the retro track's run state — `awaiting-retro → awaiting-learning` under retro, then `awaiting-learning → done` under [learn](learn.md). It is the retrospective's, never a plan's: covered plans stay at `done` and only gain a `retro:` back-link. Both playbooks run with the vault root as their workdir and address the file with `--target retrospectives/{slug}.md`.

## `codereviews/`

One file per code-review run, written by the [code-review playbook](code_review.md), grouped by what was reviewed: `codereviews/{plan-dirname}/{YYYYMMDDHHmm}.md` when a plan is in scope, `codereviews/{target-slug}/{YYYYMMDDHHmm}.md` for an ad-hoc scope such as the latest commits. Scaffolded for new vaults and created lazily in older ones, so an existing vault needs no migration.

The file records `## Scope`, `## Findings`, `## Verdict` and `## Resolution`. Its frontmatter carries `plan:` — the reviewed plan's vault-relative path, or `null` — and its own `status:`, the code-review track's run state: `in-agent-review → human-review → done`. That status is the review's, never a plan's: the reviewed plan stays at `done` and only gains the review's path in its `code_reviews:` list. The playbook runs with the vault root as its workdir and addresses the file with `--target codereviews/{dir}/{ts}.md`.

## `_lessons/`

Targeted lessons — durable rules accumulated over many sprints, and the only file surface the [learn playbook](learn.md) writes inside the Project Vault. Lessons live in exactly two flat roots: this directory, scoped to the project, and its machine-wide sibling at `<home_dir>/_lessons/` (default `~/Claude/_lessons/`), which applies to every project — a file of the same name here shadows the global one. Files are named `{N}_{title}.md`, `N` a monotonic counter keeping each directory chronologically ordered.

Each file carries a `targets:` frontmatter list saying what it applies to: `{playbook}`, `{playbook}/{step}`, `agent:{id}`, or `skill:{name}`. That list is the only routing there is — a file with no valid `targets:` is injected nowhere.

Injected by `booping render-playbook` into the composed procedure or a step prompt, and into the bodies of booping's own agents and skills at load time. See [Playbooks → Lessons](playbook.md#lessons) for the full reference.

## `notes/`

Free-form user notes — plan-review comments, code-review threads, ideas for next sprints, anything else. **Skills and agents do not read this directory.** It is a scratchpad for you, kept in the same vault for convenience and Obsidian graph visibility.

## `.booping.log`

Append-only log of `booping` CLI invocations, at the vault root. Written by the CLI, read by nobody — it is there for debugging a render or a transition. The seeded `.gitignore` excludes it, so it never lands in a vault commit.

## `plan_templates/`

Project-local plan templates. Each file has frontmatter (`name`, `description`) plus two top-level sections (`# Plan Body`, `# Quality Checklist`). Discovered by the [groom playbook](groom.md) alongside the core templates the plugin ships; a file overrides a core template by sharing its `name`, or adds an entirely new template flavour suited to the project.

## `review_templates/`

Project-local code-review templates. Loaded by the [code-review playbook](code_review.md); it picks the matching subset by inspecting the repo's manifests and reading each template's `description` frontmatter. Use this directory for review checklists specific to your stack or domain.

Templates come from three tiers, least → most specific:

| Tier | Location |
|---|---|
| core | the plugin's own `docs/review_templates/` |
| global | `{home_dir}/review_templates/` — every project on the machine |
| project | `{vault}/review_templates/` — this project only |

A later tier overrides an earlier one by `name`, keeping the earlier entry's position; a name no earlier tier carries is appended. The rendered checklist table labels each entry with its tier.

## `sprints.md`

An at-a-glance view of every plan in the vault — an [Obsidian Bases](https://help.obsidian.md/bases) fence over the `plans/*/index.md` files, its columns led by status and its rows sorted newest-first by `created`. Bases resolves every path against the *Obsidian* vault root, so the seeded filter scopes itself with `file.inFolder(this.file.folder + "/plans")` — the folder of the note holding the fence — which keeps it correct when the booping vault is nested inside a larger Obsidian vault.

**Seeded once at setup (`booping scaffold core.setup_playbook.scaffold`); no run ever rewrites or regenerates it.** The one thing that touches the fence again is a shipped vault migration, and only to append a new column your existing view predates. Obsidian evaluates the query live against the plan files, so the view is never stale and needs no refresh step. Edit the fence to change columns, sorting or filters — it is yours from the moment it is written.

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

The marker that ties a repo to its vault. Unlike everything else on this page, `.booping` lives in the **attached repo's working tree** (its root), not inside the vault. Written by the [setup playbook](install.md), it carries `project_name: {project}` — how every skill resolves which vault to operate on. An optional `vault_path:` key resolves the vault to that path instead of `~/Claude/{project}/` (relative paths against the repo root, absolute paths and `~` honoured) — this is how a repo-local vault is wired. A third key, `latest_migration:`, is the watermark recording which of the plugin's shipped vault migrations this project has already applied, written only by `bin/booping marker-set latest_migration=<id>` as the [migrate playbook](playbook.md) finishes one. When the watermark falls behind the shipped migrations, every render stops with a notice telling you to run `/playbook migrate`; nothing else renders until the vault catches up. Commit `.booping` with the repo so the binding travels with the checkout.

## `config.yaml`

Optional per-project override for the plugin's `src/config.yaml`. Deep-merges over the plugin defaults at render time (no rebuild step): dict keys merge, list keys replace wholesale. The natural targets for per-project tuning are the sprint scale, task types, branch conventions and agent wiring. Nothing is validated and no key is restricted to a tier, so your own playbooks' config lives here too.

See [Project config](project_config.md) for the full key tour and override mechanics.
