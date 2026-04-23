Status transitions are manual frontmatter edits — there is no CLI. From `/groom`, the only valid transitions are:

| From | To | When | Also set |
|------|----|------|----------|
| `backlog` | `ready-for-dev` | Explicit user confirmation | `planned: YYYY-MM-DD` (today) |
| `backlog` | `cancelled` | User shelves the work | `completed: YYYY-MM-DD` (today) |
| `backlog` | `backlog` | More iteration needed | — |

Edit the plan file's `status:` (and date field, if any) directly with the Edit tool. The plan frontmatter is authoritative.

After applying a transition, run `booping-plans` to confirm the change shows up correctly:

```bash
booping-plans --status <new-status>
```

Verify the just-edited plan appears in the list with the expected fields. If it doesn't, the frontmatter edit didn't take — re-check.
