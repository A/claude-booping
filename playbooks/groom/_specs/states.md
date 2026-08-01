---
reviewed_at: 20260731 19:04
---
# groom — State chart

## States

One machine, `run` — a **procedure tracker**: its artifact is `run.md` in the run workdir, its
statuses name what was in flight so an interrupted run resumes there, and it dies with the run.
It does not own the plan's lifecycle; it **mirrors** onto it. The superstates are that mapping:
each group is named for the plan-lifecycle status that `plans/{slug}.md` carries while the run
sits in any of the group's states. The mirror is carried by explicit `script plan-{status}` hooks
on the edges that cross a group boundary — not by superstate `on_entry` — so every side effect is
visible in the transitions table. Each such script also renders `sprints.md` and commits the
vault, the two side effects `booping transition` used to bring.

### run

`artifact: run.md`

| Superstate             | States                                                                                          |
| ---------------------- | ----------------------------------------------------------------------------------------------- |
| `in-spec`              | `framing`, `awaiting-framing-confirm`, `researching`, `designing`, `awaiting-design-confirm`, `drafting`, `decomposing` |
| `awaiting-plan-review` | `awaiting-decomposition-confirm`, `verifying-references`, `presenting`, `awaiting-approval`      |
| terminal               | `ready-for-dev`ᵗ                                                                                |

| State                            | To                               | When                                                                                                       | Gates                                                                                                                                         | Hooks                                                                         |
| -------------------------------- | -------------------------------- | ---------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| `none`                           | `framing`                        | the playbook is invoked on a fresh request, or on a parked plan the user names                             |                                                                                                                                               |                                                                               |
| `framing`                        | `awaiting-framing-confirm`       | intake wrote `intake.md` and created `plans/{slug}.md` with its identity frontmatter                       |                                                                                                                                               | `script plan-in-spec`                                                         |
| `awaiting-framing-confirm`       | `framing`                        | the user's answers change the task type, the restated problem or the scope boundaries                      |                                                                                                                                               |                                                                               |
| `awaiting-framing-confirm`       | `researching`                    | the user confirms task type and scope boundaries                                                           | explicit user confirmation captured — silence never counts; every scope-challenge question answered                                           | `frontmatter-update intake.md reviewed_at=@now`                               |
| `researching`                    | `designing`                      | both research steps returned — the blast-radius map, and the external-practice findings or their skip note |                                                                                                                                               |                                                                               |
| `designing`                      | `awaiting-design-confirm`        | design wrote `design.md` with architecture, surface changes, alternatives and risks                        |                                                                                                                                               |                                                                               |
| `awaiting-design-confirm`        | `designing`                      | the user rejects an architecture call or asks for another alternative                                      |                                                                                                                                               |                                                                               |
| `awaiting-design-confirm`        | `researching`                    | the user's objection needs blast radius or external practice the research pass missed                      |                                                                                                                                               |                                                                               |
| `awaiting-design-confirm`        | `drafting`                       | the user confirms architecture, surface changes and trade-offs                                             | explicit user confirmation captured — silence never counts                                                                                    | `frontmatter-update design.md reviewed_at=@now`                               |
| `drafting`                       | `decomposing`                    | draft-plan wrote `plans/{slug}.md` against the template's Plan Body and passed its Quality Checklist       | cross-review run and every CRITICAL finding folded in or recorded as a deferral — vacuously satisfied with no `cross_review` agent configured |                                                                               |
| `decomposing`                    | `awaiting-decomposition-confirm` | decompose-work re-decomposed the oversized tasks and re-summed the totals, or returned the skip note       | every task under the re-decompose threshold; milestone and sprint totals re-summed                                                            | `script plan-awaiting-plan-review`                                            |
| `awaiting-decomposition-confirm` | `decomposing`                    | the user reworks milestones, tasks or estimates                                                            |                                                                                                                                               | `script plan-in-spec`                                                         |
| `awaiting-decomposition-confirm` | `designing`                      | the user's rework reopens an architecture call                                                             |                                                                                                                                               | `script plan-in-spec`                                                         |
| `awaiting-decomposition-confirm` | `verifying-references`           | the user confirms the refined plan and any split candidate                                                 | explicit user confirmation captured — silence never counts                                                                                    | `frontmatter-update decomposition.md reviewed_at=@now`                        |
| `verifying-references`           | `presenting`                     | every external reference the plan names was checked and the corrections folded into the plan               |                                                                                                                                               |                                                                               |
| `presenting`                     | `awaiting-approval`              | present wrote `handoff.md` — approval summary, split recommendation if any, handoff to `/develop`          |                                                                                                                                               |                                                                               |
| `awaiting-approval`              | `decomposing`                    | the user's change request touches milestones, tasks or estimates only                                      |                                                                                                                                               | `script plan-in-spec`                                                         |
| `awaiting-approval`              | `designing`                      | the user's change request reopens architecture or scope                                                    |                                                                                                                                               | `script plan-in-spec`                                                         |
| `awaiting-approval`              | `ready-for-dev`                  | the user explicitly approves the plan — "looks good" counts, silence never does                            | explicit user approval captured                                                                                                               | `frontmatter-update handoff.md reviewed_at=@now`, `script plan-ready-for-dev` |

Scripts the Hooks cells reference, each shipped at `_scripts/{name}`, each deriving the slug from
the workdir basename and the vault from `booping config-get home_dir` (or the workdir's `../../..`):

- `plan-in-spec` / `plan-awaiting-plan-review` / `plan-ready-for-dev` — write that lifecycle
  `status:` into `plans/{slug}.md`, re-render the vault's `sprints.md`, commit both. Three thin
  variants rather than one script reading `run.md`, because a `script` hook takes no arguments and
  the group boundary already names the target status.

