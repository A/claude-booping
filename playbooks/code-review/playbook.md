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

A run reviews one confirmed scope end to end: `scope` settles what to look at, `review` returns
severity-classified findings from a detached pass, `present` puts them in front of the user and
collects their verdict, and `resolve` acts on it. The run is ephemeral — no workdir, no persisted
state, no review artefact — so a second look after fixes is a new run.

**Hard rules — hold for the whole run:**
- No commits, no pushes. The user owns those.
- Style the project's linter or formatter already enforces is filtered out — it is noise, not
  review signal.
- A lesson violation is always a `BLOCKER`. Never softened to `SUGGESTION`.
- No persistent report. Findings and feedback live in this conversation.
- No edit beyond a user-approved trivial nit. Every non-trivial fix routes through the worker
  agent named below.

Eval runs are proposed, never launched — the user triggers them.

{% set playbook_agents = config.core.code_review_playbook -%}
{% include "_partials/playbook_agents.md" %}

{% include "_partials/playbook_shared_instructions.md" %}
