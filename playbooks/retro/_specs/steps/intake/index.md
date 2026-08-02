---
status: awaiting-spec-confirm
---

# intake

[← index](../../index.md)

## Contract

- **Needs** —
  - the plan the run opened on — the one named at invocation, else the one the user picked from
    the candidate table
  - each named plan's current lifecycle status, and whether that status is retro's entry point
    (`config.skills.retro.status`, today `awaiting-retro`)
  - the other plans sitting at that same status, and what the user wants done with each —
    include / postpone / skip-and-mark-done
- **Value** — the working set settled before a token is spent on mining: the entry status
  validated so a plan retro has no business touching stops the run before anything is read,
  every sibling at the same status dispositioned by the user rather than silently swept in or
  out, the dropped ones closed through the lifecycle's own skip-ahead edge. Reading the adopted
  plans is `prepare`'s (the skill's Phase 1), not intake's — the step mirrors the skill's
  Phase 0 exactly.
- **Output files** —
  - none of the step's own — the working set, which plan is primary, and each adopted plan's
    context live in conversation
  - `[UPDATED] plans/{dropped-slug}/index.md` — one per plan the user skips, written by
    `booping transition done <plan>` and never by hand; the command's own hooks stamp
    `goal=skipped` / `completed`, re-render `sprints.md` and commit the vault, one commit per
    plan, all of it before the run proceeds
  - nothing else — no retrospective, and no frontmatter on the adopted plans: their `retro:`,
    `goal:` and status stamps are the exit edge's at `save`
- **Harness return** — none: the step is runner-performed, so it runs in the driving
  conversation and returns no block. What it leaves behind is the chat report and the facts the
  later steps read out of it — the primary plan and the adopted working set, and the skip
  transitions already applied.
- **Review gate** —
  - none — the include / postpone / skip question is asked per sibling plan in-step, and the
    user's answers are the confirmation
  - a plan whose `status:` is not retro's entry status stops the run, reported verbatim, with no
    transition taken and no plan read
- **Delegation** — inline: the runner performs the step in the main context — the status check,
  the per-sibling questions, the skip transitions and the per-plan reads are all its own. The
  working set is small (the plans already at one status) and every read feeds a judgement the
  runner has to make itself.

## Example artifact

Posted in chat, the `## Retro intake` report:

````markdown
## Retro intake

`plans/20260728-09-15_playbook-run-state/index.md` — status `awaiting-retro`, retro's entry
status. Primary plan for this run.

### Working set

| Plan | Status | Disposition |
| --- | --- | --- |
| `plans/20260728-09-15_playbook-run-state/index.md` | `awaiting-retro` | primary |
| `plans/20260729-11-02_playbook-lessons/index.md` | `awaiting-retro` | included — same sprint, shares the run-state work |
| `plans/20260726-08-40_docs-site-refresh/index.md` | `awaiting-retro` | postponed — left where it is |
| `plans/20260722-16-10_install-prompt-copy/index.md` | `awaiting-retro` | skipped and marked done |

Applied for the skipped plan:

```
awaiting-retro → done
frontmatter: goal=skipped
frontmatter: completed="20260802 15:12"
render-sprints: 14 plans → /home/anton/Claude/booping/sprints.md
vault-commit: 3f9a1c2
```
````

## Return Format

None — the step is runner-performed, so nothing is returned to the harness; the report above is
posted in chat and the run continues in the same conversation.

The wrong-status stop is the one shape worth pinning, posted in place of the whole report:

```markdown
retro requires a plan in status `awaiting-retro`; got `ready-for-dev` for
`plans/20260730-10-00_render-playbook-flags/index.md`. Pick one of the plans the run listed as
candidates instead.
```

No transition is taken, no plan is read, and the run ends there.
