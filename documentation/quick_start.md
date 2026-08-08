# Quick start

From a fresh checkout to a fully shipped first plan. Run the commands in order; the skills list candidates if you forget an exact filename.

The shortest path is the five-command loop in the [README Quick start](https://github.com/A/claude-booping#quick-start). This walkthrough adds the per-command context.

## 1. Install the plugin

Inside Claude Code, register the marketplace once and install the plugin:

```text
/plugin marketplace add A/claude-booping
/plugin install booping@booping
```

Update later with `/plugin update booping` (or from the `/plugin` UI).

See [Install](install.md) for prerequisites (`uv`, `git`).

## 2. Scaffold the project vault

`cd` into the target repository and run:

```text
/playbook setup
```

The `setup` playbook settles the machine level (home dir + machine config), then the project level: it asks for the vault location — the default `<home_dir>/{project}/` or a repo-local directory (wired via the `.booping` marker's `vault_path:` key) — and creates the vault with `plans/`, `retrospectives/`, `codereviews/`, `_lessons/`, `notes/`, plus a `.booping` marker file in the repo. Anything already in place is detected and skipped. See [Vault](vault.md) for what each directory is for.

## 3. See what is available

`/playbook` is the only skill booping ships — every procedure in this walkthrough is a playbook it drives. With no argument it lists every playbook booping discovered, shipped or written in your vault, with its trigger and scope:

```text
/playbook
```

Everything below is one of those entries.

## 4. Read the sprint view

Open `~/Claude/{project}/sprints.md` in Obsidian. It is an [Obsidian Bases](https://help.obsidian.md/bases) fence — a live table over every plan in the vault, evaluated on open, so it is never stale. On a fresh project it is near-empty.

The fence is seeded once and yours to edit (see [Vault](vault.md)). Outside Obsidian, `bin/booping query --config core.plans` prints the same listing, and `--where` narrows it — `k=v`, `k!=v`, `k:in=a,b`, `k:gt=n`, `k:lt=n`, repeatable and all applying at once:

```bash
bin/booping query --config core.plans --where status:in=ready-for-dev,in-progress
```

## 5. First groom

Spec your first sprint with a free-text description:

```text
/playbook groom — add per-tenant rate limiting to the public API
```

The [groom playbook](groom.md) maps the blast radius in your codebase and checks every external reference the plan names against current docs, working in your conversation — running each step itself and handing only heavy reads to a research agent. It drafts a plan under `~/Claude/{project}/plans/{YYYYMMDDHHMM}_{kebab-title}/index.md`, optionally hands it to a second model for cross-review (when `core.groom_playbook.cross_review_agent` is configured), and stops for approval once, at its single approval gate near the end, with the plan at `awaiting-approval`. Sharpen it there, push back, ask for splits — the more detailed your brief, the sharper the plan.

When you approve, the run flips the plan to `ready-for-dev`.

## 6. First develop

Run the develop playbook:

```text
/playbook develop
```

or name the plan:

```text
/playbook develop — plans/202604260930_per-tenant-rate-limiting/index.md
```

The [develop playbook](develop.md) confirms the sprint branch with you, then walks the milestones, delegating implementation to the `booping-developer` agent. `booping-researcher` is reserved for the intake drift spot-check — when a plan touches many files, it confirms the actual file shapes still match the plan's assumptions before execution begins. When all milestones are done and verification is green, the plan moves to `done` — the end of its lifecycle. Code review, retro and learn are follow-up `/playbook` invocations that advance their own artifacts; the plan itself never leaves `done`.

### Optional: code review before retro

Once a plan is `done`, you can run a quality-gate review over the diff before capturing the retro:

```text
/playbook code-review
```

It offers every `done` plan — each listed with its review history, so a re-review is as ordinary as a first pass — and reviews `{plan commit}..HEAD` against stack-aware checklists. Findings, your verdict and what came of it land in a persisted review file under `codereviews/`, which carries the run's own `in-agent-review → human-review → done` status; the plan stays at `done` and only gains the review's path in its `code_reviews:` list, so it remains in the review queue and the next step is still retro. Run it from a fresh session, often under a stronger model than the one that implemented. See [code-review](code_review.md) for details.

## 7. First retro

Capture what actually shipped:

```text
/playbook retro
```

The [retro playbook](retro.md) takes your raw feedback first, mines the session logs and `git diff` for tensions you did not flag, and writes a standalone `retrospectives/{slug}.md`, stamping its path onto every plan it covers. That file is the artifact retro and learn advance; the covered plans stay at `done`. Review it — it is the input to learn, and shit in means shit out.

## 8. First learn

Fold the retro into durable rules:

```text
/playbook learn
```

The [learn playbook](learn.md) proposes targeted lessons (`~/Claude/{project}/_lessons/{N}_{kebab-title}.md`, each carrying a `targets:` list) and one-line bullets for the repo's own `CLAUDE.md`, in one review table for your confirmation. Approved lessons are injected into the playbooks, steps, agents and skills they name.

When learn finishes, the retrospective reaches `done` and your first loop is complete. The next groom run inherits everything you just learned.
