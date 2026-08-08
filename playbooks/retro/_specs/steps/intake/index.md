---
status: awaiting-spec-confirm
---

# intake

[← index](../../index.md)

## Contract

- **Needs** —
  - the plan the run opened on — the one named at invocation, else the one the user picked from
    the candidate table
  - each named plan's queue membership: `status:` at `config.core.retro_playbook.status` (today
    `done`, develop's terminal) with `retro:` still null
  - the other plans in that queue, and what the user wants done with each —
    include / postpone / skip
- **Value** — the working set settled before a token is spent on mining: queue membership
  validated so a plan retro has no business touching stops the run before anything is read,
  every queued sibling dispositioned by the user rather than silently swept in or
  out, the dropped ones taken out of the queue by the step's own script. Reading the adopted
  plans is `prepare`'s (the skill's Phase 1), not intake's — the step mirrors the skill's
  Phase 0 exactly.
- **Output files** —
  - none of the step's own — the working set, which plan is primary, and each adopted plan's
    context live in conversation
  - `[UPDATED] plans/{dropped-slug}/index.md` — one per plan the user skips, written by
    `_scripts/drop-plan {slug}` and never by hand; the script stamps `retro: skipped` and
    `goal: skipped` and commits the vault, one commit per plan, all of it before the run
    proceeds. The plan's `status:` is not touched — it stays `done`
  - nothing else — no retrospective, and no frontmatter on the adopted plans: their `retro:`
    and `goal:` stamps are the exit edge's at `save`
- **Harness return** — none: the step is runner-performed, so it runs in the driving
  conversation and returns no block. What it leaves behind is the chat report and the facts the
  later steps read out of it — the primary plan and the adopted working set, and the skip
  transitions already applied.
- **Review gate** —
  - none — the include / postpone / skip question is asked per sibling plan in-step, and the
    user's answers are the confirmation
  - a plan outside the queue — wrong `status:`, or a `retro:` already set — stops the run,
    reported verbatim, with no transition taken and no plan read
- **Delegation** — inline: the runner performs the step in the main context — the status check,
  the per-sibling questions, the drop-plan invocations and the per-plan reads are all its own. The
  working set is small (the plans already in the queue) and every read feeds a judgement the
  runner has to make itself.

## Example artifact

Posted in chat, the `## Retro intake` report:

````markdown
## Retro intake

`plans/20260728-09-15_playbook-run-state/index.md` — `done`, no retrospective yet. Primary plan
for this run.

### Working set

| Plan | Status | Retro | Disposition |
| --- | --- | --- | --- |
| `plans/20260728-09-15_playbook-run-state/index.md` | `done` | — | primary |
| `plans/20260729-11-02_playbook-lessons/index.md` | `done` | — | included — same sprint, shares the run-state work |
| `plans/20260726-08-40_docs-site-refresh/index.md` | `done` | — | postponed — left in the queue |
| `plans/20260722-16-10_install-prompt-copy/index.md` | `done` | — | skipped |

Applied for the skipped plan:

```
drop-plan: plans/20260722-16-10_install-prompt-copy/index.md → retro skipped; vault-commit: ok
```
````

## Return Format

None — the step is runner-performed, so nothing is returned to the harness; the report above is
posted in chat and the run continues in the same conversation.

The wrong-status stop is the one shape worth pinning, posted in place of the whole report:

```markdown
retro requires a plan at `done` with no retrospective yet; got `ready-for-dev` for
`plans/20260730-10-00_render-playbook-flags/index.md`. Pick one of the plans the run listed as
candidates instead.
```

No plan is closed, no plan is read, and the run ends there.
