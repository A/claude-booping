# Decompose the procedure into steps

The input is the confirmed brief — goal, success result, artifact home, wishes — plus the
user's procedure description and anything else they provided. Produce the **decomposition
index**: the light, high-level map the user models against — reorder steps, redraw
boundaries, answer scope questions — before any per-step detail exists. Detail lives in the
step specs later; this file stays small enough to review in one sitting, and nothing under
the graph restates what the graph or the table already says.

## The file to write

`<slug>/_specs/index.md` (the slug comes from the brief):

- frontmatter: write none of your own — the file may already exist with harness-owned keys
  (`status:`, stamps); preserve them untouched
- a one-paragraph intro
- `## Graph` — a yaml fence with a `graph:` mapping. Step names are kebab-case — lowercase,
  hyphens, never underscores. A node whose value is a LIST is a step,
  the list its dependencies. A node whose value is a MAPPING is a subgraph: `dependencies:`
  and `graph:` required, `repeat:` prose optional — use one when the procedure repeats work
  per enumerated item.
- `## Steps` — table with columns Step, Summary, Inputs, Artifact, Gate, Model, Spec.
  Inputs is the INFORMATION the step consumes — compact, `;`-separated, artifact-blind:
  never upstream step names or file paths; the user reviews the information flow here
  before any spec exists, and the step specs seed their Needs from these cells. Model is
  `model:effort` — model one of `opus-5`, `sonnet-5`, `haiku-4-5`; default `opus-5:medium`,
  deviate only where another tier clearly fits.
  Spec links the future `steps/<step>/index.md`.
- `## Questions` — a checklist of everything the user must settle before step specs are
  written; omit when nothing is open.

No `## Decisions` section — settled items (the brief's wishes, the state-machine verdict) go
into the return's `## Notes:` as `decision: <summary>` lines; the runner records them into
`_specs/DECISIONS.md`.

## State-machine verdict

Every playbook has a state machine; judge whether a run must **persist** it, and return the
verdict as a decision line — `state machine: <ephemeral|minimal|rich> — <rationale>` — or
raise a `## Questions` item when the brief leaves it open. The `states` step acts on the verdict:
it bails on ephemeral, stamps a confirmation chain on minimal, designs in full on rich; the
user can override at its gate.

- **ephemeral** — nothing persisted; review gates and the conversation carry the run. Right
  for a short, single-session, linear procedure with purely conversational gates.
- **minimal** — a persisted confirmation chain: resume across sessions plus harness-enforced
  confirmations, nothing else.
- **rich** — superstates, script hooks, per-instance machines, or an artifact-lifecycle
  contract.

For persisting: the run likely crosses sessions (long or expensive waves); a repeated
subgraph whose per-instance progress is worth resuming independently; boundary side effects
that must run deterministically; confirmations that must be harness-enforced rather than
honor-system. Strongest signal — the artifact outlives the run and OTHER playbooks gate on
its status: the machine is then the artifact's lifecycle contract, not run bookkeeping.
Against: the artifact already owns a lifecycle elsewhere (never duplicate it — a run machine
tracks the procedure); repetition over many cheap stateless instances. Repetition alone
never forces a machine; long steps matter only when a session boundary is likely.

## Return format

```
## Changed:
- [CREATED] <slug>/_specs/index.md

## Notes:
- <n> question(s) open
- decision: <each settled item, one line, including the state-machine verdict>
```
