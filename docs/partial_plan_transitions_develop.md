Status transitions are manual frontmatter edits — there is no CLI. From `/develop`, the only valid transitions are:

| From | To | When | Also set |
|------|----|------|----------|
| `ready-for-dev` | `in-progress` | /develop claims a previously-confirmed plan at the start of Phase 3 (Execute), before spawning any worker agent | `started: YYYY-MM-DD` (today) |
| `backlog` | `in-progress` | user invokes /develop directly after groom confirmation, skipping the ready-for-dev stopover | `planned: YYYY-MM-DD` (today), `started: YYYY-MM-DD` (today) |
| `in-progress` | `awaiting-retro` | all milestones done, Final Verification green, every DoD checkbox marked [x] | `completed: YYYY-MM-DD` (today) |
| `in-progress` | `fail` | unrecoverable blocker after two documented fix attempts on the same milestone (user-approved abort) | `completed: YYYY-MM-DD` (today) |

The `backlog → in-progress` row fills BOTH `planned` and `started` in the same edit, because the plan skipped the `ready-for-dev` stopover where `planned` would normally be written.

Edit the plan file's `status:` (and date field, if any) directly with the Edit tool. The plan frontmatter is authoritative. For `ready-for-dev → in-progress`, set `status:` and `started:`; for `backlog → in-progress`, set `status:`, `planned:`, and `started:`; for `in-progress → awaiting-retro` or `in-progress → fail`, set `status:` and `completed:`.

After applying a transition, run `booping-plans` to confirm the change shows up correctly:

```bash
booping-plans --status <new-status>
```

Verify the just-edited plan appears in the list with the expected fields. If it doesn't, the frontmatter edit didn't take — re-check.
