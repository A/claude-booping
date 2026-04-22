---
name: learn
description: Extract lessons from a retrospective and fold improvements into project-local skill/agent extensions under _booping/. Use after /retro writes a retrospective.
argument-hint: [retrospective file path]
user-invocable: true
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash(ls *)
  - Bash(git add *)
  - Bash(git commit *)
  - Agent
  - AskUserQuestion
---

# booping — /learn

Turn retrospective findings into durable behavior changes.

## Project resolution

Follow [docs/project-scoping.md](../../docs/project-scoping.md). After resolving, read `~/Claude/{project}/_booping/skill_learn.md` if present.

## Arguments

`$ARGUMENTS` — retrospective file path. If omitted, default to the most recent in `~/Claude/{project}/retrospectives/`.

## Single-location heuristic

Every rule or fact extracted from a retro lands in exactly one of three places. Pick deliberately; do not duplicate.

| Location | What it holds | Scope |
|----------|---------------|-------|
| The **skill** file (`skills/<name>/SKILL.md` in this plugin) | **Methodology** — how booping itself should behave for *any* project using it | Cross-project / shipped with the plugin |
| `~/Claude/{project}/lessons/{N}_*.md` | **Experience** — concrete incidents, rules with `Why/How to apply`, that apply to this project and constrain future `/groom` and `/develop` runs | Per-project |
| `~/Claude/{project}/CLAUDE.md` or the in-repo `<repo>/CLAUDE.md` | **Project-specific facts** — layout, commands, conventions that a fresh agent needs to know | Per-project |

Test: if a rule would make sense for a totally different codebase (Rust web service, iOS app), it belongs in the skill, not in lessons. If a rule mentions specific file paths, models, or commands, it belongs in the project vault.

This skill does **not** edit `skills/*/SKILL.md` — if the retro identifies a methodology gap, call it out in the user summary and let the user decide whether to send a PR to the plugin repo. `/learn` only writes in the current project vault.

## Phase 1: Classify candidates

Read the retrospective's **Candidate new lessons** and **Root causes** sections. For each candidate, delegate in parallel to:

- `booping-techlead` — is this a tech/architecture rule? (domain: `tech`)
- `booping-product-manager` — is this a requirements / scoping rule? (domain: `product`)
- `booping-qa-lead` — is this a testing / quality rule? (domain: `qa`)

Each agent returns a short verdict: accept / reject / reshape, with the proposed rule text.

**Domain assignment** for the final lesson file:

- Exactly one of techlead / PM / QA accepts → use their domain (`tech`, `product`, or `qa`)
- Rule is about worker-level code discipline (boy-scout, monkey-patch smell, unexpected test pass) → `code`
- Two or more role agents accept, or the rule is cross-cutting → `all`

See [docs/agent-wiring.md](../../docs/agent-wiring.md) for how each domain maps to which agents receive the lesson in later briefings.

## Phase 1.5: Update-vs-create + outdated sweep

Before writing anything new, read every file in `~/Claude/{project}/lessons/` and ask, for each accepted candidate:

1. **Does a lesson already cover this?** If yes, **edit** it — add the new retro reference, refine the `How to apply` if the mechanical check improved, and leave the file ID unchanged. Do not create a duplicate.
2. **Does any existing lesson conflict with this retro's findings?** If yes, the existing lesson is stale. Options, in order of preference:
   - Rewrite the stale lesson's rule and add a `superseded_by:` field in frontmatter pointing to the retro
   - Delete the stale lesson and note the removal in the user summary (user confirms before deletion)

Report in the user summary which lessons were created / updated / deleted.

## Phase 2: Write lesson files

For each accepted candidate that isn't already covered:

1. Pick the next incrementing ID by reading `ls ~/Claude/{project}/lessons/` and finding the highest existing `{N}_*.md`.
2. Write `~/Claude/{project}/lessons/{N}_{kebab-title}.md` with frontmatter:

```yaml
---
id: {N}
title: ...
retro: retrospectives/YYYYMMDD-title.md
created: YYYY-MM-DD
scope: groom | develop | retro | all
domain: tech | product | qa | code | all
---
```

Body structure: **Rule** (1 sentence), **Why** (the incident or constraint), **How to apply** (concrete trigger and check).

`domain:` is load-bearing — orchestrators filter lessons by domain before briefing agents. A wrong tag means an agent either misses a rule that applies to them or gets one they shouldn't care about.

## Phase 3: Skill / agent extensions

If a lesson changes how a specific skill or agent should behave every run, write a project-local extension:

- `~/Claude/{project}/_booping/skill_{name}.md` — read at the start of every invocation of that skill in this project.
- `~/Claude/{project}/_booping/agent_{name}.md` — read at the start of every invocation of that agent in this project.

Keep extensions short — reference the lesson file for the full rationale: `Applies lesson: lessons/0012_...md`.

If multiple lessons touch the same skill/agent, consolidate rules under headed sections rather than appending ad-hoc.

## Phase 4: CLAUDE.md touches

Read the retrospective's **CLAUDE.md impact** section (populated by `/retro`). For each entry:

1. Compose the exact diff (`~/Claude/{project}/CLAUDE.md` and/or `<repo>/CLAUDE.md`).
2. Show the diff to the user via `AskUserQuestion` — never silently edit.
3. On approval, apply. Keep additions small — a bullet, not a paragraph. Deletions are fine; prefer removing stale text to leaving both old and new.

If the retro marked "None required" but the phase 1-3 classification surfaced a project-specific fact that belongs in CLAUDE.md, propose it here anyway — the retro's judgement can be wrong.

## Phase 5: Metrics

Initialize `lesson-hits.md` rows for newly created lessons (hits=0, last_applied=never).

## Phase 5.5: Transition plan to `done`

Read the retrospective frontmatter's `plan:` field (a project-relative path like `plans/YYYYMMDD-title.md`). Transition that plan to terminal success. Full 9-state lifecycle + transition table: [docs/plan-schema.md](../../docs/plan-schema.md).

    booping-plans set --project=<P> <plan-path> status=done
    booping-plans sync-sprints --project=<P>

**CLI fallback:**

- If `booping-plans set --project=<P> <plan-path> status=done` exits non-zero: hand-edit the plan frontmatter to set `status: done` and ensure `completed` is populated (use today's ISO date if absent). Then print `booping-plans set failed (exit N): <stderr>` verbatim to chat.
- If `booping-plans sync-sprints --project=<P>` exits non-zero: do NOT hand-edit `sprints.md`. Print `booping-plans sync-sprints failed (exit N): <stderr>` verbatim.

## Phase 6: Commit

```bash
cd ~/Claude/{project}
git add lessons/ _booping/ CLAUDE.md metrics/lesson-hits.md sprints.md plans/  # sprints.md is the regenerated rollup
git commit -m "lessons: {retro-kebab-title}"
```

If the in-repo `<repo>/CLAUDE.md` was also edited, commit that separately in the repo:

```bash
cd <repo-path>
git add CLAUDE.md
git commit -m "docs(claude-md): {short summary}"
```

## Hard rules

- One lesson per rule. Don't bundle.
- Prefer updating an existing lesson over creating a new one. A lesson file ID is stable; its content evolves.
- Never propose a lesson whose trigger is "try harder" or "be careful". The How-to-apply section must be mechanically checkable.
- Never silently edit `CLAUDE.md` — always confirm the diff with the user.
- **Do not edit `skills/*/SKILL.md`** (the plugin skill files). Methodology changes are out of scope for `/learn`. Flag them to the user as "candidate plugin PR".
