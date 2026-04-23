Status transitions are manual frontmatter edits — there is no CLI. From `/learn`, the only valid transition is:

| From | To | When | Also set |
|------|----|------|----------|
| `awaiting-learning` | `done` | All accepted learnings written to their targets; review table confirmed by user | `completed: YYYY-MM-DD` (today) |

Edit the plan file's `status:` and `completed:` directly with the Edit tool. The plan frontmatter is authoritative.

After applying the transition, run `booping-plans` to confirm the change shows up correctly:

```bash
booping-plans --status done
```

Verify the just-edited plan appears in the list with the expected fields. If it doesn't, the frontmatter edit didn't take — re-check.
