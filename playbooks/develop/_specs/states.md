# develop — States

One machine, `run` — an **artifact lifecycle**, not a procedure tracker: its statuses *are* the
shared plan-lifecycle names, written straight onto the `status:` key of the plan's own `index.md`
(`{vault}/plans/{slug}/index.md`, also the run workdir). It duplicates nothing — it **is** develop's
slice of the plan lifecycle, the same key `booping transition` writes, and the two never run on one
plan at once because develop owns the plan for the length of the sprint. `awaiting-retro` is the
handoff `/retro` gates on; `fail` is the abort branch.

Two consequences of writing lifecycle statuses directly, both deliberate:

- **No superstates.** Every group the shared lifecycle would contribute is a singleton here
  (`executing` = {`in-progress`}, `review` = {`awaiting-retro`}, `terminal` = {`fail`}) and the one
  group with two members (`planned`) carries no boundary hooks. The stamps those boundaries would
  fire — `started`, `commit`, `completed` — sit on the edges instead, so every side effect is
  visible in the transitions table.
- **No `_scripts/`.** The playbook ships none, so the vault-side effects `booping transition`
  brings are not hook-driven — the vault commit is step prose calling `booping vault-commit`
  in develop-loop and wrap-up; `sprints.md` is not re-rendered by this playbook.

Granularity is coarser than one status per active phase, because the status vocabulary is the
lifecycle's and not the run's — verify's guardrail verdict gets no status of its own either: it
lives inside `in-progress`, decided by the guardrails alone and restated as a gate on the exit
edge (no user confirmation). Every step re-reads the plan's
on-disk state before acting, which makes a replay inside a status idempotent and keeps the resume
frontier complete:

| Status | Where a resume picks up |
| --- | --- |
| `awaiting-plan-review`, `ready-for-dev` | intake, then provision — cheap to replay; at most the sprint branch exists and no sprint work is committed |
| `in-progress` | develop-loop first — the plan's milestone statuses and DoD checkboxes say which groups closed and the branch's commits say what shipped, so a finished loop walks straight through — then verify, whose guardrails simply run again, then wrap-up |
| `awaiting-retro`ᵗ, `fail`ᵗ | nothing — the run is over |

The group loop is internal to `develop-loop`, so there are no instances and **no per-instance
machine**: a group's state is already on disk in the plan's milestone table and the branch's
commits, and a per-group run file would put scaffolding inside the user's plan directory to
restate it.

Two paths develop deliberately does **not** own: non-trivial commit drift at intake halts the run
back to grooming with no transition (the plan stays at its entry status), and `cancelled` stays
groom's edge — develop never writes it.

### run

`artifact: index.md`

| Superstate | States |
| --- | --- |
| terminal | `awaiting-retro`ᵗ, `fail`ᵗ |

| State | To | When | Gates | Hooks |
| --- | --- | --- | --- | --- |
| `none` | `awaiting-plan-review` | declaration only — the preamble resolves an existing plan and the machine attaches at the `status:` already on its `index.md`; develop never creates the artifact, so nothing bootstraps | | |
| `awaiting-plan-review` | `ready-for-dev` | intake captured the user's explicit approval of the plan it entered on — "looks good" counts, silence never does | explicit user approval captured | `frontmatter-update reviewed_at=@now` |
| `ready-for-dev` | `in-progress` | provision created the confirmed sprint branch and settled the milestone groups; the first group is about to be delegated | the user confirmed the branch name; no unresolved non-trivial drift — that halts back to grooming instead | `frontmatter-update started=@now`, `frontmatter-update commit=@head` |
| `in-progress` | `awaiting-retro` | verify came back green on the project's guardrails and wrap-up made the closing commit and reported the sprint | every DoD checkbox `[x]` and every milestone status `done`; the project's guardrails and the plan's Final Verification green | `frontmatter-update completed=@now` |
| `in-progress` | `fail` | an unrecoverable blocker at any point in the sprint, verification included, after two fix attempts on the same issue | two fix attempts documented in the plan; the user approved the abort | `frontmatter-update completed=@now` |

The entry statuses arrive on disk — a plan already at `ready-for-dev` is the common path and needs
no edge; the `awaiting-plan-review` → `ready-for-dev` row is the approval intake captures when the
plan entered one step earlier in the lifecycle. `commit=@head` re-snapshots the baseline at sprint
entry, after intake settled plan validity, exactly as the shared lifecycle's `executing` boundary
does. The shared `in-progress` → `awaiting-retro` edge's `suggest /retro` is prose, not hook
vocabulary — the handoff line belongs in wrap-up's step body.

