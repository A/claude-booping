---
name: code-review
title: Code Review
summary: Review a confirmed scope — a sprint's plan, the latest commits, or a 
  named target — through a detached findings pass, a human verdict on those 
  findings, and an approved fix pass.
trigger: reviewing the code a develop sprint just delivered; reviewing the 
  latest commits or a plan awaiting review before it ships
jinja: true
requires_project: true
inline_steps: true
reviewed_at: 20260804 17:18
---

A run reviews one confirmed scope end to end: `scope` settles what to look at and opens the run's artifact, `review` returns severity-classified findings from a detached pass, `present` records them and collects the user's verdict, and `resolve` acts on it and closes.

{% from "_partials/timestamps.md" import slug_ts, human_ts -%}
## Guidance

- Date & time: {{ human_ts }}
- The run's artifact is one code review per run — `codereviews/{plan-dirname}/{{ slug_ts }}.md` when a plan is in scope, `codereviews/{target-slug}/{{ slug_ts }}.md` otherwise.
- The run workdir is the **vault root**; every `booping playbook-state` / `booping playbook-transition` call passes `--target codereviews/{dir}/{ts}.md`, since the machine declares no `artifact:`.
- The artifact carries `plan:` — the reviewed plan's vault-relative path, or `null` for an ad-hoc scope. The exit hook reads it and appends the artifact to that plan's `code_reviews:` list. Plan `status:` is never touched here.

**Resuming a run** — read the frontier with `booping playbook-state code-review --workdir {vault} --target codereviews/{dir}/{ts}.md`, then re-enter at the reported status:
- `in-agent-review` — the artifact exists and the verdict is still pending: re-run `review` over the scope the artifact's `## Scope` records, and continue from `present`.
- `human-review` — the findings are on record: re-post them from the artifact's `## Findings` and collect the verdict, or continue from `resolve` when `## Verdict` is already written.

**Hard rules — hold for the whole run:**
- No hand commits, no pushes. The repo's changes stay for the user; the vault commit is the exit hook's.
- Style the project's linter or formatter already enforces is filtered out — it is noise, not review signal.
- A lesson violation is always a `BLOCKER`. Never softened to `SUGGESTION`.
- No edit beyond a user-approved trivial nit. Every non-trivial fix routes through the worker agent named below.

Eval runs are proposed, never launched — the user triggers them.

{% set playbook_agents = config.core.code_review_playbook -%}
{% include "_partials/playbook_agents.md" %}

{% include "_partials/playbook_shared_instructions.md" %}
