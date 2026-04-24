Status transitions are manual frontmatter edits — there is no CLI. From `/develop`, the only valid transitions are:

| From | To | When | Also set |
|------|----|------|----------|
| `ready-for-dev` | `in-progress` | /develop claims a previously-approved plan at the start of Phase 3 (Execute), before spawning any worker agent | `started: YYYY-MM-DD` (today) |
| `in-progress` | `awaiting-retro` | all milestones done, Final Verification green, every DoD checkbox marked [x] | `completed: YYYY-MM-DD` (today) |
| `in-progress` | `fail` | unrecoverable blocker after two documented fix attempts on the same milestone (user-approved abort) | `completed: YYYY-MM-DD` (today) |

`/develop` only claims plans in `ready-for-dev`. A plan that has not been through `/groom`'s approval gate must be routed through `/groom` first.

Edit the plan file's `status:` (and date field, if any) directly with the Edit tool. The plan frontmatter is authoritative. For `ready-for-dev → in-progress`, set `status:` and `started:`; for `in-progress → awaiting-retro` or `in-progress → fail`, set `status:` and `completed:`.

After applying a transition, run `booping-plans` to confirm the change shows up correctly:

```bash
booping-plans --status <new-status>
```

Verify the just-edited plan appears in the list with the expected fields. If it doesn't, the frontmatter edit didn't take — re-check.
