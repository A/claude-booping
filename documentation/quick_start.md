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
/install
```

That single step creates `~/Claude/{project}/` with `plans/`, `retrospectives/`, `lessons/`, `notes/`, `_booping/`, and a `.booping` marker file so other skills know the vault is ready. See [Vault](vault.md) for what each directory is for.

## 3. Orient with /chat

Before grooming anything, run:

```text
/chat
```

`/chat` is the orient/working-mode command. It loads the project vault, refreshes the on-disk sprint snapshot at `~/Claude/{project}/sprints.md`, and is the right surface for vault navigation, reading existing plans, and small ad-hoc edits. When scope grows past "small task", `/chat` escalates you into `/groom`.

## 4. Read the sprint snapshot

Open `~/Claude/{project}/sprints.md`. It is a regenerated view of every plan in the vault grouped by status. On a fresh project it will be near-empty — that is expected.

`sprints.md` is a build artefact, never hand-edit it (see [Vault](vault.md)).

## 5. First /groom

Spec your first sprint with a free-text description:

```text
/groom Add per-tenant rate limiting to the public API
```

`/groom` researches the codebase, drafts a plan under `~/Claude/{project}/plans/{YYYYMMDD}-{kebab-title}.md`, optionally cross-validates it against Gemini (if `GEMINI_API_KEY` is set), and stops at `awaiting-plan-review` for your explicit approval. Sharpen it, push back, ask for splits — the more detailed your initial brief, the sharper the resulting plan.

When you approve, `/groom` flips the plan to `ready-for-dev`.

## 6. First /develop

Either auto-claim the next ready plan:

```text
/develop
```

or target a specific one:

```text
/develop plans/20260426-per-tenant-rate-limiting.md
```

`/develop` walks the milestones, delegating implementation to the `booping-developer` agent and reading code via `booping-researcher` when a milestone requires it. When all milestones are done, the plan moves to `awaiting-retro`.

## 7. First /retro

Capture what actually shipped:

```text
/retro plans/20260426-per-tenant-rate-limiting.md
```

`/retro` reads the plan, scans session logs and `git diff`, and writes a retrospective at `~/Claude/{project}/retrospectives/{YYYYMMDD}-{kebab-title}.md`. It also asks you about tensions you noticed during develop. Review the retrospective file — it is the input to `/learn`, and shit in means shit out.

## 8. First /learn

Fold the retro into durable rules:

```text
/learn retrospectives/20260426-per-tenant-rate-limiting.md
```

`/learn` proposes lessons (`~/Claude/{project}/lessons/{N}_{title}.md`) and per-skill / per-agent extension files (`~/Claude/{project}/_booping/skill_<name>.md`, `_booping/agent_<name>.md`) for your confirmation. Approved lessons are loaded by future `/groom` and `/develop` invocations; extensions travel with the matching skill or agent at load time.

When `/learn` finishes, the plan reaches `done` and your first loop is complete. The next `/groom` you run inherits everything you just learned.
