# retro — States

One machine, `run` — an **artifact lifecycle**, not a procedure tracker, the same shape
`develop`'s machine has: its statuses *are* the shared plan-lifecycle names, written onto the
`status:` key of the primary plan's own `index.md` (`{vault}/plans/{primary-slug}/index.md`, also
the run workdir). It duplicates nothing — it **is** retro's slice of the plan lifecycle, and this
machine is the only writer of that key for the length of the run. It joins develop's machine at the entry (`awaiting-retro` is
develop's terminal) and hands to `/learn` at the exit (`awaiting-learning` is the status `/learn`
claims).

Retro's slice is **one non-terminal lifecycle status wide**, so the run has one working status and
one exit edge. That is deliberate and follows directly from the decomposition's "nothing
intermediate is persisted": the issue list, the accepted issues and the draft all live in
conversation, so a finer status — `mining`, `triaging`, `drafting` — would name a frontier the run
cannot actually resume at. A status that cannot be resumed from should not exist. The run's single
review gate (the draft approval at `synthesize`) gets no status of its own either: it sits inside
`awaiting-retro` and is restated as a gate on the exit edge, exactly as develop does with verify's
guardrail verdict.

**No `review` superstate.** Both of the machine's statuses sit inside the shared lifecycle's
`review` group, so no boundary is crossed, its `on_entry` stamp (`completed="{{ macro('core.macros.date', '+%Y-%m-%d %H:%M') }}"`) already fired on
develop's exit, and the group carries no edge this slice needs. The only group declared is the
machine's own `terminal`.

### run

`artifact: index.md`

| Superstate | States |
| ---------- | ---------------------- |
| terminal   | `awaiting-learning`ᵗ   |

| State            | To                  | When                                                                                                                                                                                   | Gates                                                                                                                                                                                                                                        | Hooks                                                                      |
| ---------------- | ------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| `none`           | `awaiting-retro`    | declaration only — the preamble resolves an existing plan and the machine attaches at the `status:` already on its `index.md`; retro never creates the artifact, so nothing bootstraps |                                                                                                                                                                                                                                              |                                                                            |
| `awaiting-retro` | `awaiting-learning` | save wrote the approved `retro.md` into the primary plan's directory and linked the sibling plans to it                                                                                | explicit user approval of the draft captured at synthesize — "save it" counts, silence never does; `retro.md`'s `plans:` list covers the whole working set and `goal_verdicts:` carries a verdict for each, since the hook script reads both | `frontmatter-update retro.md reviewed_at="{{ macro('core.macros.date', '+%Y-%m-%d %H:%M') }}"`, `script close-working-set` |

Hook order is load-bearing: `reviewed_at` is stamped on the approved `retro.md` before
`close-working-set` commits the vault. The file target doubles as a guard — a missing `retro.md`
aborts the transition, so the plan cannot move without the retrospective on disk.

Script the Hooks cell references, shipped at `_scripts/close-working-set`, deriving the primary
slug and the vault from `BOOPING_WORKDIR` (`{vault}/plans/{primary-slug}`) and reading the working
set out of `retro.md`'s frontmatter:

- `close-working-set` — for every plan in `retro.md`'s `plans:` list, stamp
  `retro: plans/{primary-slug}/retro.md` (the one shared retrospective, vault-relative like the
  lifecycle's existing `retro=` value) and `goal:` from that plan's entry in `goal_verdicts:`; for
  every plan *other than the primary*, also set `status: awaiting-learning`. Then commit the vault.
  The primary's own `status:` is not the script's: `playbook-transition` writes it before the hooks
  run. Self-contained, like groom's `_scripts/commit-plan` — the vault carries no `.booping`
  marker, so nothing shells back into `booping`.

A script rather than hooks because **both values retro must stamp are runtime-valued** and hook
strings are static: the goal verdict is the user's, per plan, and the retrospective's path carries
the primary slug.

**Sibling plans** — the runner's call on the question decompose left open, split by move:

- **Dropped at intake** (`skip retro and mark done`) → `_scripts/drop-plan {slug}`, which stamps
  `status: done`, `goal: skipped` and `completed:` on that plan and commits it. A machine edge
  could never reach it: this machine's artifact is fixed to the primary plan. Step prose, one
  invocation per plan, before the run proceeds.
- **Adopted at save** → folded into `close-working-set`, for the same reason: a file-targeted
  `frontmatter-update <file> …` hook cannot reach a sibling, since its slug is unknown at
  authoring time and the count varies per run.

Every step re-reads the plan's on-disk state before acting, which makes a replay inside the status
idempotent and keeps the resume frontier complete:

| Status | Where a resume picks up |
| --- | --- |
| `awaiting-retro` | intake, and the run replays whole — nothing intermediate is on disk, so the issue list is re-mined and the user re-answers. One on-disk signal short-circuits it: a `retro.md` already in the workdir means save wrote the approved draft and only the transition is outstanding — re-run the transition, not the run. |
| `awaiting-learning`ᵗ | nothing — the run is over |

The cost is real and accepted: a resumed run re-asks the four open-ended questions and re-walks
triage. Persisting those would mean writing run scaffolding into the user's plan directory, which
the brief rules out.

The multi-plan working set does not repeat the graph, so there are no instances and **no
per-instance machine**: one run produces one retrospective, and each sibling's state is exactly the
`status:` / `retro:` / `goal:` the exit hook stamps on it — `{instance}` would have nothing to key
on.

Paths retro deliberately does **not** own: `done` is stamped by `_scripts/drop-plan` for dropped
siblings and never written by this machine; and both abort paths —
a cancel at synthesize, a wrong-status stop at intake — end the run with no transition at all,
leaving the plan at `awaiting-retro`.
