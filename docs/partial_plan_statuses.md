| Status | Meaning |
|--------|---------|
| `backlog` | Draft or parked idea; `/groom` writes here initially. |
| `in-spec` | `/groom` is actively refining: running agents, filling frontmatter, computing estimates. |
| `ready-for-dev` | Spec accepted; `sp` and `planned` set; queued for `/develop` to claim. |
| `in-progress` | `/develop` has claimed the plan; `started` auto-filled on transition. |
| `awaiting-retro` | All milestones done; `completed` auto-filled; waiting for `/retro`. |
| `awaiting-learning` | Retro written; `retro` and `goal` set; waiting for `/learn` to absorb lessons. |
| `done` | Terminal success. `/learn` has absorbed all lessons. |
| `fail` | Terminal technical failure. `/develop` hit an unrecoverable blocker; `completed` auto-filled. |
| `cancelled` | Terminal product/priority decision. User shelved the plan; `completed` auto-filled. |
