---
status: done
agents:
  step-prompt: a4cb4888f97cd1e00
  step-spec: a61235de0c90dc9e9
  llm-tests: a9ff3c6ef760219c2
reviewed_at: 20260802 09:46
fixtures_reviewed_at: 20260802 09:52
suite_reviewed_at: 20260802 09:58
---

# intake

[← index](../../index.md)

## Contract

- **Needs** —
  - the plan — its milestones, its tasks with their file lists, its DoD and Verify commands,
    and its `status:` and `commit:` baseline
  - whether the user has already approved the plan, when it entered at `awaiting-plan-review`
  - the repo's own conventions
  - the repo's current HEAD and what changed since the plan's baseline — the cheap summary
    (changed names, shortstat, log) first, the plan-named slice of the diff only after the
    user opts to revalidate
  - on a legacy plan with no baseline, the actual shape of the files the plan names
- **Value** — the plan adopted for execution and known to still hold against the code as it is
  now, before a single worker is briefed: the entry status validated against an entry
  transition, the user's approval explicit where the lifecycle asks for it, and drift settled
  one way or the other. Cheap-summary-first keeps the full diff out of the runner's context
  unless the user asks for it, and the legacy file-shape spot-check's bulk reads stay in the
  researcher agent.
- **Output files** —
  - none on the common path — the entry status, the drift summary and the verdict are posted
    in chat, nothing is written
  - `[UPDATED] plans/{slug}/index.md` — only on **trivial** drift the user approved: the
    in-place plan edits that bring a task's file list, a DoD line or a Verify command back in
    line with the code. Frontmatter stays untouched here — `status:` is the machine's, and the
    baseline re-snapshot (`commit=@head`) is the `ready-for-dev` → `in-progress` edge's hook,
    fired at provision
  - nothing else — no branch, no milestone groups, no research notes
- **Harness return** — none: the step is runner-performed, so it runs in the driving
  conversation and returns no block. What it leaves behind is the chat report and the facts
  provision reads from it — the validated entry status, the captured approval, and the drift
  verdict (in sync / trivial drift patched / non-trivial, halted).
- **Review gate** —
  - none — the drift questions are asked in-step, and the answers are the confirmation
  - a `status:` matching no entry transition stops the run and reports it
  - non-trivial drift halts back to grooming verbatim — *"The drift is significant — re-shape
    the plan with `/groom <plan-path>` before continuing."* — with no transition taken; the
    plan stays at its entry status
- **Delegation** — assisted: the runner owns the status check, the cheap-summary commands and
  the drift judgement in the main context; on a legacy plan with no `commit:` baseline the
  file-shape spot-check's reads are delegated to the researcher agent, which returns only the
  mismatches against the plan's assumptions.

## Example artifact

Posted in chat, the `## Plan intake` report:

```markdown
## Plan intake

`plans/20260728-09-15_playbook-run-state/index.md` — status `ready-for-dev`, a valid entry
transition.

### Plan validity

Baseline `a1f3c02` → HEAD `7d9e4b1`: 6 commits, 11 files changed, +240/−58.

| Plan-touched file | Changed since baseline |
| --- | --- |
| `booping-python/src/booping/context/playbook.py` | yes — `load_all` gained a `home_dir` argument |
| `src/templates/_partials/_playbook_driving.j2` | no |
| `playbooks/groom/playbook.yaml` | no |

Revalidated against the plan-named slice on your word. The drift is trivial: M2's task 2 names
`load_all(vault, plugin_root)`, which is now `load_all(vault, home_dir, plugin_root)`. No
milestone changes.
```

The one in-place edit that approval buys, in `plans/20260728-09-15_playbook-run-state/index.md`:

```markdown
| 2 | Thread `home_dir` through `Playbook.load_all(vault, home_dir, plugin_root)` | `booping-python/src/booping/context/playbook.py` | pending |
```

## Return Format

None — the step is runner-performed, so nothing is returned to the harness; the report above
is posted in chat and the run continues in the same conversation.

The halt is the one shape worth pinning, posted in place of the verdict paragraph:

```markdown
Entered at `awaiting-plan-review`; approval captured ("looks good").

4 of the 5 plan-touched files were rewritten since baseline `a1f3c02` — M3 targets a module
that no longer exists.

The drift is significant — re-shape the plan with
`/groom plans/20260728-09-15_playbook-run-state/index.md` before continuing.
```

No transition is taken and the plan stays at its entry status.
