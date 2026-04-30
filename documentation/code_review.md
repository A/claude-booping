# /code-review

Run a quality-gate review over the current diff against the active plan, producing a categorised feedback list with inline trivial fixes and `booping-developer` briefings for non-trivial ones.

## Why

`/code-review` is the explicit second pair of eyes between `/develop` and `/retro`. It is most useful when the implementation pass ran on a cheaper or faster model — for example you let `/develop` run under Sonnet or GLM and want Opus to catch what the implementer missed. Even on a single-model loop, a fresh-session review surfaces issues the orchestrator's growing context tends to wave through.

It is a **stateless side-skill**: it does not own a plan-lifecycle status, does not transition the plan, and does not write a persistent report file. The output is a feedback list in the chat session, plus any inline fixes it applies and any follow-up briefings it dispatches.

## Command

```text
/code-review
/code-review plans/20260430-user-facing-documentation-site.md
```

Bare `/code-review` picks the plan currently in `awaiting-retro` (the queue `/develop` just finished). Pass a plan path to review against a different one — useful when you ran `/develop` in another session and want to review the diff before retro.

Run it from a fresh Claude Code session — see [Run code review in a fresh session](develop.md#run-code-review-in-a-fresh-session) on the `/develop` page for why.

## Best practices

### Define your own review templates

The plugin ships a small set of stack-agnostic and stack-specific review templates under `docs/review_templates/`. Project-local templates live in `~/Claude/{project}/review_templates/` and are loaded alongside the core ones; a project template with the same name overrides its core counterpart.

Use this directory for checklists specific to your stack or domain — house style, perf budgets, security rules, framework-specific footguns. See [Vault](vault.md#review_templates) for the directory layout.

## Behaviour notes

### Stack auto-detect

`/code-review` inspects the repo's manifest files (`pyproject.toml`, `package.json`, `Cargo.toml`, `go.mod`, etc.) and source code, then picks the review templates whose `description` frontmatter matches the stack it identified. Generic templates always run; language and framework templates load only when a real signal for them exists. You do not pass the stack on the command line — it is inferred from what is actually pinned.

### Severity labels

Findings are categorised so the post-review triage is mechanical:

- **BLOCKER** — must be applied before merge. Bugs, security issues, broken contracts, missed plan DoDs.
- **SUGGESTION** — apply if the cost is low; defer with an explicit one-liner otherwise.
- **NIT** — apply or skip on judgment; no record needed.

This is the same triage shape `/develop` uses on the feedback list — see [Review the code-review feedback list](develop.md#review-the-code-review-feedback-list).

### Trivial inline, non-trivial via agent

`/code-review` applies trivial fixes (typos, obvious dead code, single-line corrections) inline within the review session. Non-trivial fixes are dispatched as a follow-up briefing to `booping-developer` so the orchestrator stays a reviewer and the implementation channel stays consistent with the rest of the loop.

## Config

`/code-review` has no dedicated config keys. Template selection is driven by the `description` frontmatter on each review template under `docs/review_templates/` and `~/Claude/{project}/review_templates/`. To make a project-local checklist available to the review pass, drop it under your vault's `review_templates/` with a clear `description` — the skill loads it when the repo's stack matches.
