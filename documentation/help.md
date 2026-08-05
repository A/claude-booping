# /help

Index of every booping command. Run `/help` inside Claude Code for the in-session version; this page is the same index, with each command linking to its dedicated reference.

For the published documentation site, see [https://A.github.io/claude-booping/](https://A.github.io/claude-booping/).

## Commands

- [`/playbook setup`](install.md) — scaffold the per-project vault and drop the `.booping` marker. Run once per repo.
- [`/playbook groom`](groom.md) — spec a sprint: turn a free-text request into a reviewable plan with milestones, story points, and definitions of done.
- [`/playbook develop`](develop.md) — claim a `ready-for-dev` plan and execute it milestone-by-milestone, delegating coding work to `booping-developer`.
- [`/code-review`](code_review.md) — stack-aware review of the current diff against the active plan, with severity-labelled findings and inline or agent-dispatched fixes.
- [`/playbook retro`](retro.md) — capture what actually shipped versus the spec: durable findings recorded as `retro.md` in the plan's directory.
- [`/playbook learn`](learn.md) — fold retro findings into targeted lessons under `_lessons/` and per-skill / per-agent extension files under `_booping/`.
- [`/help`](help.md) — this index.

## Extending booping

- [Integrating external agents](integrating-external-agents.md) — wire a skill or playbook (e.g. `develop` or `/code-review`) to delegate to your own Claude Code agent instead of, or alongside, the built-in workers.
