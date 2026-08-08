---
status: awaiting-spec-confirm
---

[← index](../../index.md)

# feature-index

## Contract

- **Needs** —
  - the project's shape and direction as the briefing states it — what it is, who it serves,
    where it is heading; the briefing's vocabulary for the project's own parts is the vocabulary
    the features are named in
  - the capabilities the project actually ships, read from the repo itself: the commands it
    exposes, the procedures it runs, the configuration and extension points it honours, the
    behaviour a user can invoke today. Shipped only — planned, half-built and merely designed
    work is not a capability
  - the previous feature index when one exists — its groups, its feature names and the hand-made
    wording in them, which a refresh keeps rather than regenerates
  - the run's confirmed scope — whether the index is established from nothing or refreshed
- **Value** — two things at once. The **documentation structure**: the groups are the sections
  the project's documentation is organised into, decided once here instead of re-invented per
  surface, so `targeting` places a change under a group rather than guessing a home for it. And
  the **capability inventory** the run measures change against: `research` types a delivered item
  by what it did to this list — a capability that appeared is a new feature, one that moved is a
  refactoring, one that vanished is a feature drop — and `sync-specs` folds the confirmed table
  straight back into it. No priorities: documentation covers everything that ships, so the
  ordering that a delivery index needs has no reader here. The file describes the project to
  itself, not to an audience — audience is `roles`' business, written in the same wave and never
  read here.
- **Output files** —
  - `[CREATED|UPDATED] {vault}/docs/_specs/features.md` — the feature index
    - no frontmatter of the step's own: the confirming edge stamps `reviewed_at:`, and an
      existing file's frontmatter survives untouched
    - H1 `# {project} — Feature index`, then a lead of one or two lines naming the rule the file
      obeys — one `##` per group, a feature is something the project delivers, a capability is
      one thing it lets someone do, shipped only
    - one `## {Group}` section per group, in the order the documentation should read; inside it
      one `### {Feature} — {one-line summary}` per feature, followed by its capability bullets,
      each bullet one line naming an action and the thing it acts on
    - a feature belongs to exactly one group, and a capability to exactly one feature; a feature
      whose parts genuinely split across groups is split into two features rather than listed
      twice
    - a closing `## Not features` section naming what was considered and excluded with its
      reason — build artefacts, internal refactors, test and CI machinery — so `research` types
      such deliveries as chores instead of re-litigating them as features
    - a readable snapshot of what ships now: no "this used to be called …" narration, no
      roadmap rows. Drift against the previous index is reported in the return, never written
      into the file
    - a refresh keeps groups, features and wording that still hold and rewrites only what the
      repo moved; a feature that no longer ships leaves the file and is named in the return
      rather than deleted silently
  - no other file — the step never writes the spec-set files its wave-mates own, and never edits
    a documentation surface
- **Harness return** — `## Changed:` with the single `features.md` entry, annotated with the
  group, feature and capability counts. `## Notes:` carries one line per group — the group, then
  its features by name — plus one `added:` / `dropped:` / `regrouped:` line per change against
  the previous index with its reason. The runner presents the index at the gate from these lines
  alone and never reads the file to do it.
- **Review gate** —
  - confirm features, capabilities and groups
  - the step itself stops at nothing: it returns and the wave continues while roles and targets
    are still writing
  - the gate is the runner's, held at `awaiting-features-confirm` — after the roles-and-surfaces
    gate, on its own, since the groups are a structural decision the user settles separately
  - a refine answer sends the run back to `spec-building` and this step runs again over the same
    inputs plus the user's correction; the confirming edge stamps `reviewed_at:` on
    `_specs/features.md`, which is never this step's write
- **Delegation** — detached: `detached: "fable:medium"` — the decomposition's `fable-5:medium`,
  written with the tier name the `detached:` grammar accepts. A generic sub-agent fetches this
  step's body itself (`booping render-playbook docs --step feature-index`) and performs it; the
  sweep over the repo's shipped behaviour stays out of the driving context, which receives only
  the path and the digest lines. The agent needs repo reads plus the briefing at
  `_specs/index.md` and the previous `_specs/features.md`; it writes exactly one file.

## Example artifact

`{vault}/docs/_specs/features.md`, for this project:

````markdown
# claude-booping — Feature index

One `##` per group; the groups are the documentation structure. A feature is something the
project delivers, a capability is one thing it lets someone do. Shipped only.

## Running procedures

### Playbook driver — the `/playbook` skill that discovers a procedure and drives it to completion

- list the playbooks visible from the core, global and vault discovery roots
- select one by its trigger, or by name when the user names it
- drive steps in graph order, running each parallel wave as detached sub-agents
- hold a review gate — present the step's output and continue only on explicit confirmation
- resume an interrupted run from the state frontier rather than from the driving context

### Run state — named state machines that carry a run's artifact across sessions

- declare statuses, superstates and transitions with `when`, `gates` and `hooks` in `playbook.yaml`
- move an artifact between statuses through the single writer, `booping playbook-transition`
- stamp frontmatter and run shell hooks on an edge
- report the frontier of an in-flight run with `booping playbook-state`

## Shipped procedures

### Plan track — grooming a plan and developing it milestone by milestone

- turn a request into a plan directory under the vault, groomed to `ready-for-dev`
- implement a plan milestone by milestone through developer sub-agents
- review the working diff before a commit
- queue a landed plan for review off its frontmatter rather than its status

### Retro track — capturing what a run taught and writing it back

- write a retrospective for a delivered plan
- extract lessons from a retrospective into targeted lesson files
- inject a lesson into exactly the playbooks, steps, agents and skills its `targets:` name

## Extending a project

### Vault — the per-project home for plans, retrospectives, lessons and user playbooks

- resolve the vault from the `.booping` marker, defaulting to `~/Claude/{project}/`
- scaffold a project vault and its marker in one command
- carry vault migrations with an applied watermark every render surface gates on

### Configuration — the three-tier merge that shapes every rendered body

- deep-merge core, global and project config, later tiers winning
- read any mapping as a query spec or a scaffold tree by its dotted path
- pin config-declared command macros for reproducible renders

## Not features

- `just build`, the snapshot suite and the eval harness — contributor machinery; a change here
  is a chore, not a delivered capability
- `skills/`, `agents/` — build artefacts rendered from `src/files/`
- refactors of the Python package that leave every listed capability intact
````

The real file carries every group the project has, not the four shown. A first run writes the
same shape from nothing; a refresh rewrites only the sections the repo moved and leaves the rest
in their existing wording.

## Return Format

```markdown
## Changed:
- [CREATED|UPDATED] {vault}/docs/_specs/features.md — {n} groups, {n} features, {n} capabilities

## Notes:
- {group} — {feature}, {feature}, {feature}
- added: {feature or capability} — {what shipped that surfaced it}
- dropped: {feature or capability} — {why it no longer ships}
- regrouped: {feature} — {from group} → {to group}, {why}

## Questions:
```

One `## Notes:` group line per group, in file order, then the drift lines — omitted entirely on a
first run, where the `## Changed:` marker is already `[CREATED]`. No prose outside the block.
