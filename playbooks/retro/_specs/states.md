# retro — States

One machine, `run` — an **artifact lifecycle**, not a procedure tracker. Its artifact is the standalone retrospective the run writes, `{vault}/retrospectives/{YYYYMMDDHHMM}_{kebab-title}.md`, and its statuses are that file's, never a plan's.

The machine declares no `artifact:`, because the path is chosen per run: the workdir is the **vault root** and every `booping playbook-state` / `booping playbook-transition` call names the file with `--target retrospectives/{slug}.md`.

Retro is a **separate track from the plan lifecycle**, not a slice of it. The plans a run covers are already `done` — develop's terminal — and stay there; retro moves none of them. The join is frontmatter: a plan enters the queue by carrying `retro: null`, and leaves it when the exit hook stamps the retrospective's path there (or when `_scripts/drop-plan` stamps `retro: skipped`). Learn picks the retrospective up at `awaiting-learning`, the same way.

The machine is **one non-terminal status wide**, so the run has one working status and one exit edge. That follows from the decomposition's "nothing intermediate is persisted": the issue list, the accepted issues and the draft all live in conversation, so a finer status — `mining`, `triaging`, `drafting` — would name a frontier the run cannot actually resume at. A status that cannot be resumed from should not exist. The run's single review gate (the draft approval at `synthesize`) gets no status of its own either: it sits inside `awaiting-retro` and is restated as a gate on the exit edge.

### run

no `artifact:` — the run passes `--target retrospectives/{slug}.md`

| Superstate | States |
| ---------- | ---------------------- |
| terminal   | `awaiting-learning`ᵗ   |

| State | To | When | Gates | Hooks |
| --- | --- | --- | --- | --- |
| `none` | `awaiting-retro` | bootstrap — the artifact does not exist until save writes it, so the machine is `not-started` for most of the run | | |
| `awaiting-retro` | `awaiting-learning` | save wrote the approved retrospective to `retrospectives/{slug}.md`, the run's `--target` | explicit user approval of the draft captured at synthesize — "save it" counts, silence never does; the retrospective's `plans:` list covers the whole working set and `goal_verdicts:` carries a verdict for each, since the hook script reads both | `frontmatter-update reviewed_at="{{ macro('core.macros.date', '+%Y-%m-%d %H:%M') }}"`, `script close-working-set --verdicts --prefix retro --stage retrospectives` |

Hook order is load-bearing: `reviewed_at` is stamped on the approved retrospective before `close-working-set` commits the vault. The artifact doubles as a guard — the transition cannot run against a file that is not on disk, so no plan is stamped without the retrospective written.

The script is the **shared** `playbooks/_scripts/close-working-set`, which `learn` also fires; the per-playbook difference lives in the hook line's argv. It reads `BOOPING_WORKDIR` (the vault root) and `BOOPING_ARTIFACT` (the resolved retrospective), takes the working set out of the artifact's `plans:` list, and under `--verdicts` stamps `retro:` (the vault-relative artifact path) plus `goal:` from that plan's entry in `goal_verdicts:` on every plan in it, then commits the artifact and every touched plan. No plan `status:` is written — `--status` exists for learn's use, and retro does not pass it. Self-contained, like groom's `_scripts/commit-plan`: the vault carries no `.booping` marker, so nothing shells back into `booping`.

A script rather than hooks because **both values retro must stamp are runtime-valued** and hook strings are static: the goal verdict is the user's, per plan, and the retrospective's path carries the run's own slug.

**Sibling plans** — the runner's call on the question decompose left open, split by move:

- **Dropped at intake** (`skip`) → `_scripts/drop-plan {slug}`, which stamps `retro: skipped` and `goal: skipped` on that plan and commits it, leaving its `status: done` alone. A machine edge could never reach it: this machine's artifact is the retrospective, and a dropped plan is by definition not in it. Step prose, one invocation per plan, before the run proceeds.
- **Adopted at save** → folded into `close-working-set`, for the same reason: a file-targeted `frontmatter-update <file> …` hook cannot reach a plan whose slug is unknown at authoring time and whose count varies per run.

Every step re-reads the plans' on-disk state before acting, which makes a replay inside the status idempotent and keeps the resume frontier complete:

| Status | Where a resume picks up |
| --- | --- |
| `not-started` | intake, and the run replays whole — nothing intermediate is on disk, so the issue list is re-mined and the user re-answers |
| `awaiting-retro` | the transition alone: the artifact exists, so save wrote the approved draft and only the exit edge is outstanding — re-run the transition, not the run |
| `awaiting-learning`ᵗ | nothing — the run is over |

The cost is real and accepted: a resumed run re-asks the four open-ended questions and re-walks triage. Persisting those would mean writing run scaffolding into the vault, which the brief rules out.

The multi-plan working set does not repeat the graph, so there are no instances and **no per-instance machine**: one run produces one retrospective, whatever the size of the working set, and each covered plan's state is exactly the `retro:` / `goal:` the exit hook stamps on it — `{instance}` would have nothing to key on.

Paths retro deliberately does **not** own: any plan `status:`, which belongs to groom and develop alone; and both abort paths — a cancel at synthesize, a wrong-queue stop at intake — end the run with no transition and no artifact at all.
