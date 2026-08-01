---
reviewed_at: 20260731 19:04
---
# groom — State chart

## States

One machine, `run` — a **procedure tracker**: its artifact is `index.md` in the plan directory
(`plans/{slug}/`, also the run workdir), its statuses name what was in flight so an interrupted
run resumes there, and it dies with the run. It does not own the plan's lifecycle; it **mirrors**
onto it. The superstates are that mapping: each group is named for the plan-lifecycle status that
`plan.md` carries while the run sits in any of the group's states. The mirror is carried by
explicit `script plan-{status}` hooks on the edges that cross a group boundary — not by
superstate `on_entry` — so every side effect is visible in the transitions table. Each such
script also renders `sprints.md` and commits the vault, the two side effects `booping
transition` used to bring.

The run has **one review-gate status** — `awaiting-approval`, at present. Framing pauses for the
user's answers inside `framing` (the answers are the confirmation; changed framing re-runs
intake within the status), and design alignment happens in conversation inside `designing`;
neither holds a confirm status of its own.

### run

`artifact: index.md`

| Superstate             | States                                                                  |
| ---------------------- | ----------------------------------------------------------------------- |
| `in-spec`              | `framing`, `researching`, `designing`, `drafting`, `decomposing`        |
| `awaiting-plan-review` | `verifying-references`, `presenting`, `awaiting-approval`               |
| terminal               | `ready-for-dev`ᵗ                                                        |

| State                  | To                     | When                                                                                                                                        | Gates                                                                                                                                         | Hooks                                                                        |
| ---------------------- | ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| `none`                 | `framing`              | the playbook is invoked on a fresh request, or on a parked plan the user names                                                              |                                                                                                                                               |                                                                              |
| `framing`              | `researching`          | intake filled the framing into `index.md`, created `plan.md`, and the user's answers settled the scope questions — clear intent is enough   | answers that change the task type, the restated problem or a boundary re-run intake first                                                     | `script plan-in-spec`                                                        |
| `researching`          | `designing`            | the blast radius is recorded, and `research.md` is written or the skip recorded — per intake's web-research decision                        |                                                                                                                                               |                                                                              |
| `designing`            | `drafting`             | architecture, surface changes and trade-offs are settled with the user in conversation — every call that is the user's is answered          |                                                                                                                                               |                                                                              |
| `designing`            | `researching`          | the conversation needs blast radius or external practice the research pass missed — including a mid-design request for web research         |                                                                                                                                               |                                                                              |
| `drafting`             | `decomposing`          | draft-plan wrote `plan.md`'s body against the template's Plan Body and passed its Quality Checklist                                         | cross-review run and every CRITICAL finding folded in or recorded as a deferral — vacuously satisfied with no `cross_review` agent configured |                                                                              |
| `decomposing`          | `verifying-references` | decompose-work re-decomposed the oversized tasks and re-summed the totals, or recorded the skip                                             | every task under the re-decompose threshold; milestone and sprint totals re-summed                                                            | `script plan-awaiting-plan-review`                                           |
| `verifying-references` | `presenting`           | the novel, load-bearing references were checked and the corrections folded into the plan                                                    |                                                                                                                                               |                                                                              |
| `presenting`           | `awaiting-approval`    | present wrote the `## Approval` section — summary, split recommendation if any, handoff to `/develop`                                       |                                                                                                                                               |                                                                              |
| `awaiting-approval`    | `decomposing`          | the user's change request touches milestones, tasks or estimates only                                                                       |                                                                                                                                               | `script plan-in-spec`                                                        |
| `awaiting-approval`    | `designing`            | the user's change request reopens architecture or scope                                                                                     |                                                                                                                                               | `script plan-in-spec`                                                        |
| `awaiting-approval`    | `ready-for-dev`        | the user explicitly approves the plan — "looks good" counts, silence never does                                                             | explicit user approval captured                                                                                                               | `frontmatter-update index.md reviewed_at=@now`, `script plan-ready-for-dev`  |

Scripts the Hooks cells reference, each shipped at `_scripts/{name}`, each deriving the slug from
the workdir basename and the vault from `booping config-get home_dir` (or the workdir's `../..`):

- `plan-in-spec` / `plan-awaiting-plan-review` / `plan-ready-for-dev` — write that lifecycle
  `status:` into `plan.md`, re-render the vault's `sprints.md`, commit both. Three thin variants
  rather than one script reading `index.md`, because a `script` hook takes no arguments and the
  group boundary already names the target status.
