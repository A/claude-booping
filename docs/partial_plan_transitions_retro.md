Status transitions are manual frontmatter edits — there is no CLI. From `/retro`, the only valid transitions are:

| From | To | When | Also set |
|------|----|------|----------|
| `awaiting-retro` | `awaiting-learning` | retrospective markdown written and saved to retrospectives/; self-review checklist passed | `retro: retrospectives/YYYYMMDD-{kebab-title}.md`, `goal: success | partial | fail` |

**Multi-plan retrospectives.** When a retrospective covers multiple plans, the transition applies per plan in the retrospective's `plans:` list. Each plan's frontmatter gets its `status:` flipped to `awaiting-learning`, `retro:` pointed at the shared retrospective path, and `goal:` set to that plan's per-plan verdict.

**Fail does not redirect status.** Setting `goal: fail` does not prevent the plan's status from moving to `awaiting-learning` — `goal` captures the retrospective verdict, while `status` captures the pipeline stage. The plan still transits to `awaiting-learning` for learning follow-up, regardless of the outcome.

Edit the plan file's `status:` (and `retro:` and `goal:` fields) directly with the Edit tool. For `awaiting-retro → awaiting-learning`, set `status:`, `retro:`, and `goal:`. The plan frontmatter is authoritative.

After applying a transition, run `booping-plans` to confirm the change shows up correctly:

```bash
booping-plans --status awaiting-learning
```

Verify the just-edited plan appears in the list with the expected fields. If it doesn't, the frontmatter edit didn't take — re-check.
