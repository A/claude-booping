# booping

A self-learning, project-scoped sprint workflow for Claude Code. booping turns a feature idea into a durable, on-disk loop — **groom → develop → retro → learn** — that effectively utilizes sub-agents to avoid context rot, with optional Gemini cross-validation when `GEMINI_API_KEY` is set. Every artifact (plans, retros, lessons, sprint snapshots) lives under `~/Claude/{project}/`, one folder per codebase, so weeks-long programs stay legible long after the session ends.

The vault at `~/Claude/{project}/` is plain markdown with YAML frontmatter, so Obsidian renders it natively as Properties. No proprietary database, no lock-in — just files you can grep, version, and edit by hand.

## The loop

```text
        ┌─────────┐
        │  groom  │  spec → cross-validate → review gate
        └────┬────┘
             │ ready-for-dev
             ▼
       ┌──────────┐
       │  develop │  claim → execute milestone-by-milestone
       └────┬─────┘
            │ awaiting-retro
            │   (optional side-route: /code-review on the in-progress diff)
            ▼
        ┌────────┐
        │  retro │  what shipped vs spec → durable findings
        └────┬───┘
             │ awaiting-learning
             ▼
        ┌────────┐
        │  learn │  fold findings into lessons + extension files
        └────────┘
```

Every plan walks this loop once. The next plan inherits the lessons.

## Why booping

- **Artifacts as a meta-source.** Plans, retros, and lessons are not throwaway scratchpads — they are durable on-disk markdown you can mine later for documentation, onboarding material, research notes, or a historical trace of how a codebase actually evolved. The vault becomes its own knowledge base.
- **A benchmarking surface.** Because plans are reproducible files, you can run the same plan twice with different models (Opus vs. Sonnet vs. GLM) and compare the resulting diffs to see how each model behaves on your codebase. The framework gives you the controlled inputs needed for honest comparison.
- **Agile-iteration scaffolding made durable.** Sprint cadence, reviews, retrospectives, and lessons are normally social rituals that decay when nobody writes them down. booping gives each ritual a concrete file and a concrete command, so the loop survives across sessions, machines, and weeks of context loss.
- **Story points as a personal estimation track record.** Every plan carries an SP estimate, every retro records what actually shipped. Over many sprints you accumulate honest data on how your estimates compare to reality on this specific codebase — a private calibration log you can't get from a ticket tracker.

## Read next

- [Quick start](quick_start.md) — install the plugin, run `/install`, ship your first plan end-to-end.
- [Install](install.md) — prerequisites and what `/install` scaffolds.
- [Vault](vault.md) — full tour of `~/Claude/{project}/`: what every file and directory is for.
- [/groom](groom.md) — spec a sprint, with cross-validation and the user-approval gate.
- [/develop](develop.md) — claim a ready plan and execute milestones.
- [/code-review](code_review.md) — stack-aware review of the in-progress diff.
- [/retro](retro.md) — capture what actually shipped vs. the spec.
- [/learn](learn.md) — fold retro findings into durable rules.
- [/chat](chat.md) — orient inside the vault and handle ad-hoc small tasks.
- [/help](help.md) — command index.
- [Project config](project_config.md) — tour of `src/config.yaml` and the per-project override mechanic.
