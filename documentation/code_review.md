# /code-review

Run a quality-gate review over the current diff against the active plan, producing a categorised feedback list with inline trivial fixes and `booping-developer` briefings for non-trivial ones.

## Why

`/code-review` is the explicit second pair of eyes between `/develop` and `/retro`. It is most useful when the implementation pass ran on a cheaper or faster model — for example you let `/develop` run under Sonnet or GLM and want Opus to catch what the implementer missed. Even on a single-model loop, a fresh-session review surfaces issues the orchestrator's growing context tends to wave through.

It is a **stateless side-skill**: it does not own a plan-lifecycle status, does not transition the plan, and does not write a persistent report file. The output is a feedback list in the chat session, plus any inline fixes it applies and any follow-up briefings it dispatches.

## Command

```text
/code-review                                  # review the current diff against the in-progress plan
/code-review plans/YYYYMMDD-{kebab-title}.md  # review against a specific plan
```

Run it from a fresh Claude Code session — see [Run code review in a fresh session](develop.md#run-code-review-in-a-fresh-session) on the `/develop` page for why.

## Best practices

### Define your own review templates

The plugin ships a small set of stack-agnostic and stack-specific review templates under `docs/review_templates/`. Project-local templates live in `~/Claude/{project}/review_templates/` and are loaded alongside the core ones; a project template with the same name overrides its core counterpart.

Use this directory for checklists specific to your stack or domain — house style, perf budgets, security rules, framework-specific footguns. See [Vault](vault.md#review_templates) for the directory layout.

## Behaviour notes

### Stack auto-detect

`/code-review` scans the repo's manifest files (`pyproject.toml`, `package.json`, `Cargo.toml`, `go.mod`, etc.) for substrings declared in `code_review.stack_markers` and selects the matching review templates. You do not pass the stack on the command line — it is inferred from what is actually pinned.

### Severity labels

Findings are categorised so the post-review triage is mechanical:

- **BLOCKER** — must be applied before merge. Bugs, security issues, broken contracts, missed plan DoDs.
- **SUGGESTION** — apply if the cost is low; defer with an explicit one-liner otherwise.
- **NIT** — apply or skip on judgment; no record needed.

This is the same triage shape `/develop` uses on the feedback list — see [Review the code-review feedback list](develop.md#review-the-code-review-feedback-list).

### Trivial inline, non-trivial via agent

`/code-review` applies trivial fixes (typos, obvious dead code, single-line corrections) inline within the review session. Non-trivial fixes are dispatched as a follow-up briefing to `booping-developer` so the orchestrator stays a reviewer and the implementation channel stays consistent with the rest of the loop.

## Config

`/code-review` reads the following key from `src/config.yaml`. See [Project config](project_config.md) for the deep-merge override mechanics; per-project tweaks live in `~/Claude/{project}/config.yaml`.

- **`code_review.stack_markers`** — map of `{dependency-substring: template-name}` used to auto-detect which review templates apply. Example:

  ```yaml
  code_review:
    stack_markers:
      django: django
      react: react
  ```

  When `/code-review` finds the substring `django` anywhere in the repo's manifest files, it loads `docs/review_templates/django.md` (and `~/Claude/{project}/review_templates/django.md` if present) into the review pass. Add an entry per dependency you want to gate on; the matching template name resolves against both core and project-local template directories.
