# Quick start

This walkthrough takes you from a fresh checkout to a fully shipped first plan. Run the commands in order; the skills will list candidates if you forget an exact filename.

The shortest possible path is the five-command loop in the [README Quick start](https://github.com/A/claude-booping#quick-start). The walkthrough below adds the orient step and the per-command context a new user benefits from.

## 1. Install the plugin

Inside Claude Code, register the marketplace once and install the plugin:

```text
/plugin marketplace add A/claude-booping
/plugin install booping@booping
```

Update later with `/plugin update booping` (or from the `/plugin` UI).

See [Install](install.md) for prerequisites (`uv`, `git`, optional `GEMINI_API_KEY`).

## 2. Scaffold the project vault

`cd` into the target repository and run:

```text
/playbook setup
```

The `setup` playbook settles the machine level (home dir + machine config) and then the project level: it asks for the vault location — the default `<home_dir>/{project}/` or a repo-local directory (wired via the `.booping` marker's `vault_path:` key) — and creates the vault with `plans/`, `retrospectives/`, `_lessons/`, `notes/`, `_booping/`, plus a `.booping` marker file so other skills know the vault is ready. Anything already in place is detected and skipped. See [Vault](vault.md) for what each directory is for.

## 3. Orient with /chat

Before grooming anything, run:

```text
/chat
```

`/chat` is the orient/working-mode command. It loads the project vault and is the right surface for vault navigation, reading existing plans, and small ad-hoc edits. When scope grows past "small task", `/chat` escalates you into `/playbook groom`.

## 4. Read the sprint view

Open `~/Claude/{project}/sprints.md` in Obsidian. It is an [Obsidian Bases](https://help.obsidian.md/bases) fence — a live table over every plan in the vault, evaluated on open, so it is never stale. On a fresh project it will be near-empty; that is expected.

The fence is seeded once and yours to edit (see [Vault](vault.md)). Outside Obsidian, `bin/booping query --config plans` prints the same listing.

## 5. First groom

Spec your first sprint with a free-text description:

```text
/playbook groom — add per-tenant rate limiting to the public API
```

The [groom playbook](groom.md) researches the codebase and the web, drafts a plan under `~/Claude/{project}/plans/{YYYYMMDD-HH-MM}_{kebab-title}/index.md`, optionally hands it to a second model for cross-review (when `cross_review.agent` is configured), and stops at `awaiting-plan-review` for your explicit approval. Sharpen it, push back, ask for splits — the more detailed your initial brief, the sharper the resulting plan.

When you approve, the run flips the plan to `ready-for-dev`.

## 6. First develop

Run the develop playbook:

```text
/playbook develop
```

or name the plan:

```text
/playbook develop — plans/20260426-09-30_per-tenant-rate-limiting/index.md
```

The [develop playbook](develop.md) confirms the sprint branch with you, then walks the milestones, delegating implementation to the `booping-developer` agent. `booping-researcher` is reserved for the intake drift spot-check — when a plan touches many files, it confirms the actual file shapes still match the plan's assumptions before execution begins. When all milestones are done and verification is green, the plan moves to `awaiting-retro`.

### Optional: /code-review before retro

Once a plan is in `awaiting-retro`, you can run a quality-gate review over the diff before capturing the retro:

```text
/code-review
```

Bare `/code-review` picks the plan in `awaiting-retro` and reviews `<plan commit>..HEAD` against stack-aware checklists, returning severity-labelled findings in chat. It is a **stateless side-skill** — it does not transition the plan, so the next step is still retro. Run it from a fresh session (often under a stronger model than the one that implemented). See [/code-review](code_review.md) for details.

## 7. First retro

Capture what actually shipped:

```text
/playbook retro
```

The [retro playbook](retro.md) takes your raw feedback first, mines the session logs and `git diff` for tensions you did not flag, and writes `retro.md` into the plan's own directory. Review it — it is the input to learn, and shit in means shit out.

## 8. First learn

Fold the retro into durable rules:

```text
/playbook learn
```

The [learn playbook](learn.md) proposes targeted lessons (`~/Claude/{project}/_lessons/{N}_{title}.md`, each carrying a `targets:` list) and per-skill / per-agent extension files (`~/Claude/{project}/_booping/skill_<name>.md`, `_booping/agent_<name>.md`) in one review table for your confirmation. Approved lessons are injected into the playbooks, steps and agents they name.

When learn finishes, the plan reaches `done` and your first loop is complete. The next groom run inherits everything you just learned.
