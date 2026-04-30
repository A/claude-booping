# /help

Index of every booping command. Run `/help` inside Claude Code for the in-session version; this page is the same index, with each command linking to its dedicated reference.

For the published documentation site, see [https://A.github.io/claude-booping/](https://A.github.io/claude-booping/).

## Commands

- [`/install`](install.md) — scaffold the per-project vault under `~/Claude/{project}/` and drop the `.booping` marker. Run once per repo.
- [`/chat`](chat.md) — orient inside the project: surface a vault status summary, navigate plans and retros, handle small ad-hoc edits.
- [`/groom`](groom.md) — spec a sprint: turn a free-text request into a reviewable plan file with milestones, story points, and definitions of done.
- [`/develop`](develop.md) — claim a `ready-for-dev` plan and execute it milestone-by-milestone, delegating coding work to `booping-developer`.
- [`/code-review`](code_review.md) — stack-aware review of the current diff against the active plan, with severity-labelled findings and inline or agent-dispatched fixes.
- [`/retro`](retro.md) — capture what actually shipped versus the spec: durable findings recorded under `retrospectives/`.
- [`/learn`](learn.md) — fold retro findings into durable rules under `lessons/` and per-skill / per-agent extension files under `_booping/`.
- [`/help`](help.md) — this index.
