# Framing brief

## Request

> groom. We have a development cycle, we measure SPs of each sprint. Can we measure and record CT/LT (don't remember what is what). I mean session active time, so we can see how much it took to take a plan from groom to done based on claude code sessions jsonl not on walltime?

## Task type

`feature` — new user-visible capability: time metrics recorded on plans and readable from the vault. Not `bug`: nothing observed diverges from expected behavior — no metric exists today, so there is no defect to reproduce. Not `refactoring`: the change adds visible data (new frontmatter keys / reports), which fails the no-user-visible-behavior-change test.

## Problem

Sprints today carry only story points (`sp` frontmatter). Plan frontmatter already records walltime waypoints — `created`, `planned`, `started`, `completed` — so walltime Lead Time (created → completed) and Cycle Time (started → completed) are derivable but never computed or shown. Nothing measures how much *active work time* a plan actually consumed: Claude Code writes per-session `.jsonl` transcripts (`~/.claude/projects/{project-slug}/*.jsonl`) with per-message timestamps, but no mechanism attributes sessions to a plan or sums their active time across the groom → develop → done arc. The plan must define what is measured (active time, and whether walltime CT/LT ride along), how sessions map to a plan, how "active time" is computed from a transcript, and where the result is recorded.

## Clarifications and Decisions

- Terminology settled: LT = lead time (created → completed), CT = cycle time (started → completed); the ask is a third metric — active session time.
- Metrics scope: active time only; walltime LT/CT and per-phase breakdown are out of scope.
- Attribution: playbook runs stamp their Claude Code session id into plan frontmatter (a `sessions:` list) as they go; no retroactive time-window matching.
- Active-time computation: assistant-turns only — sum API/tool-execution spans from the transcript, measuring Claude compute time, not user idle/thinking time between turns.
- No post-implementation prose-shape reshape milestone expected.
- Metric shape: `active_minutes:` integer (sortable); no human-formatted duration string.
- Stamp scope: groom + develop transition edges only; compute + stamp at develop `in-progress → done` / `→ fail`, CLI also runnable manually.
- Existing vault's sprints.md updated via migration 005; scaffold updated for future vaults.
- Validated against delivered code-review-track-split plan: frontmatter key is now `code_reviews:` list; `--append` is the canonical list-append path (porting `close-code-review` onto it out of scope); stamp-session ordered before stamp-active-time on develop close edges; migration id 5 confirmed free.
- Added mid-draft: `models:` metric — sorted distinct `message.model` ids from assistant events of stamped sessions (full ids carry the version); no per-model time split.
