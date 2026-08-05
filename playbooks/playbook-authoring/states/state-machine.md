## State machine anatomy

A machine tracks one of two roles — name which before drafting:

- **procedure tracker** — tracks the run itself; its artifact lives in the run workdir,
  enables resume, and matters only while the run does.
- **artifact lifecycle** — tracks the deliverable; statuses are handoff points other
  playbooks and skills gate on; superstates are likely; terminal means archived. Never
  duplicate a lifecycle the artifact already owns elsewhere — a run machine tracks the
  procedure, not a foreign artifact.

### Artifacts

A machine's `artifact` is the main entry point of what its scope produces, relative to the
run workdir: outer machine → `index.md`; per-instance machine (a repeated subgraph) →
`steps/{instance}/index.md`. The decomposition's Artifact column is the suggestion; deviate
only when the entry point genuinely differs.

### Tables

Per machine: a `### <name>` heading, an `artifact:` line, then tables. The inventory table
appears only when there are superstates or terminals to declare:

| Superstate | States |
| -- | -- |
| `<group>` | `<state>`, `<state>` |
| terminal | `<state>`ᵗ |

Transitions, one row per edge — no transition names; a move is addressed by its target
status:

| State | To | When | Gates | Hooks |
| -- | -- | -- | -- | -- |
| `none` | `<initial>` | `<what starts the run>` | | |
| `drafting` | `awaiting-confirm` | draft written | | `frontmatter-update drafted="{{ macro('core.macros.date', '+%Y-%m-%d %H:%M') }}"` |

- **When** — the concrete trigger: a step outcome, a user action, an ack. Never a bare arrow.
- **Gates** — only where the condition isn't trivially true; a condition the source state
  already guarantees stays out of the cell.
- **Hooks** — machine-readable strings ONLY, translated verbatim into playbook.yaml:
  `frontmatter-update <key>=<val>` (a value is Jinja-rendered with the `macro` global —
  `"{{ macro('core.macros.date', '+%Y-%m-%d %H:%M') }}"` — or the literal `@head`; quote any value carrying
  spaces, the hook string is shlex-tokenised) or
  `script <name>` (an executable the playbook ships at `_scripts/<name>`). Prose in a Hooks
  cell is a defect.
- A terminal carries `ᵗ` everywhere it appears and never has an outgoing row.
- A shared edge (same trigger and destination from several states) lives once on a superstate
  row in a second transitions table, never copied per state.

### Statuses

- Every active phase gets an explicit in-progress status (`drafting`, `researching`, …) — an
  interrupted run's status must name what was in flight so the harness resumes there. A pure
  chain of confirm checkpoints loses that.
- Confirmation is a status, not a flag: `… → awaiting-<x>-confirm → …`, the edge out gated
  "explicit user confirmation captured — silence never counts", hook
  `frontmatter-update <path> reviewed_at="{{ macro('core.macros.date', '+%Y-%m-%d %H:%M') }}"` on the reviewed file. The harness's
  transition command is the only writer.
- The author owns granularity: a parallel wave sits inside ONE status; merge waves a resume
  would replay cheaply anyway.

### Minimal pattern (tier: minimal)

One machine, artifact `index.md`, stamped per gated wave:
`<wave>-ing → awaiting-<wave>-confirm`, the confirm edge as above, chained wave to wave;
terminal `done`ᵗ. Nothing else — no superstates, no scripts.

### Checks

- Inventory and transition tables agree; every state is reachable from `none`; every
  non-terminal has a way out; a terminal never does.
- Gates only where non-trivial; Hooks cells machine-readable; shared edges live once.
- One machine per scope: the outer graph one; a repeated subgraph optionally its own —
  `{instance}` in the artifact path is legal only there.
