| Status | Meaning |
|--------|---------|
| `backlog` | Parked plan — not actively being worked on. Split stubs and user-filed ideas not yet in grooming. |
| `in-spec` | `/groom` is actively specifying: research, design, drafting. |
| `awaiting-plan-review` | Plan drafted; `/groom` is presenting and waiting for explicit user approval, change request, or cancellation. |
| `ready-for-dev` | User approved. Queued for `/develop` to claim. |
| `in-progress` | `/develop` has claimed the plan; `started` auto-filled on transition. |
| `awaiting-retro` | All milestones done; `completed` auto-filled; waiting for `/retro`. |
| `awaiting-learning` | Retro written; `retro` and `goal` set; waiting for `/learn` to absorb lessons. |
| `done` | Terminal success. `/learn` has absorbed all lessons. |
| `fail` | Terminal technical failure. `/develop` hit an unrecoverable blocker; `completed` auto-filled. |
| `cancelled` | Terminal product/priority decision. User shelved the plan; `completed` auto-filled. |

After any status transition, regenerate `sprints.md` with `booping-plans --format=md > ~/Claude/{project}/sprints.md` so the vault snapshot stays current. The file is machine-generated — never hand-edit.
