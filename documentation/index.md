# booping

A self-learning, project-scoped sprint workflow for Claude Code. booping turns a feature idea into a durable, on-disk loop — **groom → develop → retro → learn** — spread across sub-agents to avoid context rot, with an optional second-model cross-review of every plan. Plans, retros and code reviews live in the per-project vault (`~/Claude/{project}/` by default, or a repo-local directory), one folder per codebase, so weeks-long programs stay legible.

The vault is plain markdown with YAML frontmatter, so Obsidian renders it natively as Properties. No database, no lock-in — files you can grep, version, and edit by hand.

## The loop

You enter the loop through the [project-manager](project_manager.md): every session in a booping repo starts with it, you tell it what you want, and it files each request as an open item and carries it through the steps below — or you run each step yourself.

```text
        ┌─────────┐
        │  groom  │  spec → cross-review → review gate
        └────┬────┘
             │ ready-for-dev
             ▼
        ┌─────────┐
        │ develop │  claim → milestones → done
        └────┬────┘
             │ plan: done
      ┌──────┴──────────────┐
      ▼                     ▼
  ┌────────┐        ┌─────────────┐
  │  retro │        │ code-review │  stack-aware review of the
  └────┬───┘        └─────────────┘  shipped diff → codereviews/
       │ retrospectives/{slug}.md
       ▼
  ┌────────┐
  │  learn │  fold findings into targeted rules
  └────────┘
```

Every plan walks this loop once; the next inherits the rules. Setup, grooming, development, code review, retro and learn are all **playbooks**, driven by `/playbook` — the plugin's only shipped skill. develop closes the plan at `done`; retro + learn and code-review then run as separate tracks over their own standalone artifacts — `retrospectives/{slug}.md` and per-review files under `codereviews/` — while the plan stays `done`.

## Why booping

- **Artifacts as a meta-source.** Plans, retros and rules are durable on-disk markdown you can mine for documentation, onboarding material, research notes, or a historical trace of how a codebase actually evolved.
- **A benchmarking surface.** Plans are reproducible files: run the same one with different models (Opus vs. Sonnet vs. GLM) and compare the diffs — the controlled inputs an honest comparison needs.
- **Agile-iteration scaffolding made durable.** Sprint cadence, reviews, retrospectives and lessons are social rituals that decay unwritten; booping gives each a concrete file and a concrete command, so the loop survives sessions, machines and weeks of context loss.
- **Story points as a personal estimation track record.** Every plan carries an SP estimate; every retro records what actually shipped. Over many sprints that accumulates into honest data on your estimates versus reality on this specific codebase — a private calibration log no ticket tracker gives you.

## Read next

- [Quick start](quick_start.md) — install the plugin, run `/playbook setup`, ship your first plan end-to-end.
- [project-manager playbook](project_manager.md) — the entry point: tell it what you want, it files open items and drives them through groom, develop, code review and merge.
- [Install](install.md) — prerequisites and what `/playbook setup` creates.
- [Vault](vault.md) — full tour of `~/Claude/{project}/`: what every file and directory is for.
- [groom playbook](groom.md) — spec a sprint, with cross-review and the user-approval gate.
- [develop playbook](develop.md) — claim a ready plan and execute milestones.
- [code-review playbook](code_review.md) — `/playbook code-review`: stack-aware review of a confirmed scope, recorded under `codereviews/`.
- [retro playbook](retro.md) — capture what actually shipped vs. the spec.
- [learn playbook](learn.md) — fold retro findings into durable rules.
- [Playbooks](playbook.md) — multi-step procedures driven by `/playbook`, the framework at the plugin's core.
- [Project config](project_config.md) — the `config.yaml` you can drop in your vault, and how it overrides booping's defaults.
