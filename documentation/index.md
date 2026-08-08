# booping

A self-learning, project-scoped sprint workflow for Claude Code. booping turns a feature idea into a durable, on-disk loop — **groom → develop → retro → learn** — that effectively utilizes sub-agents to avoid context rot, with an optional second-model cross-review of every plan. Every artifact (plans, retros, lessons, sprint snapshots) lives in the per-project vault — `~/Claude/{project}/` by default, or a repo-local directory — one folder per codebase, so weeks-long programs stay legible long after the session ends.

The vault is plain markdown with YAML frontmatter, so Obsidian renders it natively as Properties. No proprietary database, no lock-in — just files you can grep, version, and edit by hand.

## The loop

```text
        ┌─────────┐
        │  groom  │  spec → cross-review → review gate
        └────┬────┘
             │ ready-for-dev
             ▼
       ┌──────────┐      ┌───────────────┐
       │  develop │─────▶│  code-review  │  stack-aware review
       │          │◀─────│  (optional)   │  of the in-progress diff
       └────┬─────┘      └───────────────┘
            │ done + retro: null
            ▼
        ┌────────┐
        │  retro │  what shipped vs spec → durable findings
        └────┬───┘
             │ retrospectives/{slug}.md
             ▼
        ┌────────┐
        │  learn │  fold findings into targeted lessons
        └────────┘
```

Every plan walks this loop once. The next plan inherits the lessons. Setup, grooming, development, code review, retro and learn are all **playbooks**; `/playbook` is the one shipped skill that drives them. Code review is an optional side-route off the develop playbook — a pass over a finished plan's diff that records its findings and verdict in its own `codereviews/` artifact and moves no plan status before you continue to retro.

## Why booping

- **Artifacts as a meta-source.** Plans, retros, and lessons are not throwaway scratchpads — they are durable on-disk markdown you can mine later for documentation, onboarding material, research notes, or a historical trace of how a codebase actually evolved. The vault becomes its own knowledge base.
- **A benchmarking surface.** Because plans are reproducible files, you can run the same plan twice with different models (Opus vs. Sonnet vs. GLM) and compare the resulting diffs to see how each model behaves on your codebase. The framework gives you the controlled inputs needed for honest comparison.
- **Agile-iteration scaffolding made durable.** Sprint cadence, reviews, retrospectives, and lessons are normally social rituals that decay when nobody writes them down. booping gives each ritual a concrete file and a concrete command, so the loop survives across sessions, machines, and weeks of context loss.
- **Story points as a personal estimation track record.** Every plan carries an SP estimate, every retro records what actually shipped. Over many sprints you accumulate honest data on how your estimates compare to reality on this specific codebase — a private calibration log you can't get from a ticket tracker.

## Read next

- [Quick start](quick_start.md) — install the plugin, run `/playbook setup`, ship your first plan end-to-end.
- [Install](install.md) — prerequisites and what `/playbook setup` scaffolds.
- [Vault](vault.md) — full tour of `~/Claude/{project}/`: what every file and directory is for.
- [groom playbook](groom.md) — spec a sprint, with cross-review and the user-approval gate.
- [develop playbook](develop.md) — claim a ready plan and execute milestones.
- [code-review playbook](code_review.md) — stack-aware review of a confirmed scope, recorded under `codereviews/`.
- [retro playbook](retro.md) — capture what actually shipped vs. the spec.
- [learn playbook](learn.md) — fold retro findings into durable rules.
- [Playbooks](playbook.md) — multi-step procedures driven by `/playbook`. *Unstable — work in progress.*
- [Project config](project_config.md) — tour of `src/config.yaml` and the per-project override mechanic.
