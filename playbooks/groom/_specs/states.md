---
reviewed_at: 20260731 19:04
---
# groom — State chart

## States

One machine, `run` — a **procedure tracker**: its artifact is `index.md` in the plan directory
(`plans/{slug}/`, also the run workdir), its statuses name what was in flight so an interrupted
run resumes there, and it dies with the run. `index.md` is also the plan document itself, so the
machine does not track a foreign artifact — but it does not own the plan's *lifecycle*; it
**mirrors** onto it. The superstates are that mapping: each group is named for the
plan-lifecycle status stamped as `plan_status:` on `index.md` while the run sits in any of the
group's states. The mirror is carried by explicit `script plan-{status}` hooks on the edges that
cross a group boundary — not by superstate `on_entry` — so every side effect is visible in the
transitions table. Each such script also renders `sprints.md` and commits the vault, the two
side effects `booping transition` used to bring.

The run has **one review-gate status** — `awaiting-approval`. Framing pauses for the user's
answers inside `framing` (the answers are the confirmation; changed framing re-runs intake
within the status), and design alignment happens in conversation inside `drafting`; neither
holds a confirm status of its own.

### run

`artifact: index.md`

| Superstate             | States                                                 |
| ---------------------- | ------------------------------------------------------ |
| `in-spec`              | `framing`, `researching`, `drafting`, `cross-reviewing` |
| `awaiting-plan-review` | `presenting`, `awaiting-approval`                      |
| terminal               | `ready-for-dev`ᵗ                                       |

| State               | To                  | When                                                                                                                                                                     | Gates                                                                                                                                         | Hooks                                                                       |
| ------------------- | ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| `none`              | `framing`           | the playbook is invoked on a fresh request, or on a parked plan the user names                                                                                           |                                                                                                                                               |                                                                             |
| `framing`           | `researching`       | intake posted the framing brief in chat, created `index.md` with its identity frontmatter, and the user's answers settled the scope questions — clear intent is enough   | answers that change the task type, the restated problem or a boundary re-run intake first                                                     | `script commit-plan`                                                       |
| `researching`       | `drafting`          | the blast-radius map and the web-research findings are both posted in chat                                                                                               |                                                                                                                                               |                                                                             |
| `drafting`          | `cross-reviewing`   | architecture, surface changes and trade-offs are settled with the user in conversation, and draft-plan wrote `index.md`'s body against the template's Plan Body and passed its Quality Checklist | every call that is the user's is answered                                                                                                     |                                                                             |
| `drafting`          | `researching`       | the design needs blast radius or external practice the research pass missed                                                                                              |                                                                                                                                               |                                                                             |
| `cross-reviewing`   | `presenting`        | the cross-review pass disposed of every finding, or no `core.cross_review_agent` is configured and the pass was skipped                                                       | every CRITICAL finding folded in or recorded as a deferral — vacuously satisfied with no `cross_review` agent configured                      | `script commit-plan`                                          |
| `presenting`        | `awaiting-approval` | present posted the approval screen in chat — summary, split recommendation if any, handoff to the `develop` playbook                                                              |                                                                                                                                               |                                                                             |
| `awaiting-approval` | `drafting`          | the user's change request touches the plan itself — architecture, scope, milestones, tasks or estimates                                                                  |                                                                                                                                               | `script commit-plan`                                                       |
| `awaiting-approval` | `ready-for-dev`     | the user explicitly approves the plan — "looks good" counts, silence never does                                                                                          | explicit user approval captured                                                                                                               | `frontmatter-update index.md reviewed_at="{{ macro('core.macros.date', '+%Y-%m-%d %H:%M') }}"`, `script commit-plan` |

Scripts the Hooks cells reference, each shipped at `_scripts/{name}`, each deriving the slug and
vault from `BOOPING_WORKDIR` (`{vault}/plans/{slug}`):

- `commit-plan` — stage the run's plan directory and commit it, tagging the message with the
  `status:` `playbook-transition` already wrote to `index.md`. Fired on the edges that close a
  superstate, so the vault carries one commit per boundary. It takes no arguments (a `script`
  hook carries none) and reads the target status off the artifact instead.
