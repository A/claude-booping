# Build the feature index

You receive the workdir (`{vault}/docs/`), the attached repo, and the run's confirmed scope —
whether the index is established from nothing or refreshed.

Read, in this order:

- `_specs/index.md` — the confirmed briefing: what the project is, who it serves, where it is
  heading. Name the project's own parts in that briefing's vocabulary.
- the repo itself, for the capabilities it actually ships: the commands it exposes, the
  procedures it runs, the configuration and extension points it honours, the behaviour a user
  can invoke today. Shipped only — planned, half-built and merely designed work is not a
  capability.
- `_specs/features.md`, when one exists — the previous index, whose groups, feature names and
  hand-made wording a refresh keeps rather than regenerates.

Never read `_specs/roles.md` or `_specs/targets.md`: they are being written concurrently by
wave-mates, and audience is not a question this file answers.

## The file to write

`{vault}/docs/_specs/features.md`, plus the glossary `{vault}/docs/_specs/glossary.md` it
references. Nothing else — never a wave-mate's spec file, never a documentation surface.

- no frontmatter of your own — the confirming edge stamps `reviewed_at:`, and an existing
  file's frontmatter survives untouched
- H1 `# {project} — Feature index`, then a lead of one or two lines naming the rule the file
  obeys: a feature is something the project delivers, a capability is one thing it lets someone
  do, shipped only
- the features as tables with exactly the columns `group | feature | capabilities` — one row
  per feature, groups in the order the documentation should read and repeated per row, the
  capabilities cell a `<br>`-separated list of one-line items each naming an action and the
  thing it acts on. No priority column and no other column. When the briefing splits the
  project into major parts, one `## {Part}` section per part, each with its own table;
  otherwise a single `## Features` table
- every capability line ends with one or more role hashtags naming the briefing audiences it
  serves, lower-snake (`#user`, `#advanced_user`, `#contributor`), derived from the briefing's
  "who it serves" — never invented roles
- a `## NFRs` section after the tables — qualities the project guarantees rather than things it
  lets someone do (determinism, token economy, reproducibility), one bullet each; a candidate
  capability that is really a quality lands here instead of a table cell
- a glossary at `_specs/glossary.md`, created or refreshed beside the index — the canonical
  name for every recurring term the spec set must use consistently, one `- **{Term}** —
  {definition}` line each; the index's lead references it, and every file you write uses the
  glossary's term, never a synonym
- the groups are the documentation structure, decided once here so `targeting` places a change
  under a group instead of guessing a home for it
- a feature belongs to exactly one group, a capability to exactly one feature; a feature whose
  parts genuinely split across groups is split into two features rather than listed twice
- no priorities and no ordering by importance — documentation covers everything that ships
- a closing `## Not features` section naming what was considered and excluded with its reason —
  build artefacts, internal refactors, test and CI machinery — so `research` types such
  deliveries as chores instead of re-litigating them as features
- a readable snapshot of what ships now: no "this used to be called …" narration, no roadmap
  rows. Drift against the previous index is reported in your return, never written into the file
- on a refresh: keep the groups, features and wording that still hold, and rewrite only what the
  repo moved. A feature that no longer ships leaves the file and is named in your return rather
  than deleted silently.

Shape of the table:

```markdown
## Features

| group | feature | capabilities |
| --- | --- | --- |
| **Running procedures** | Playbook driver — the `/playbook` skill that discovers a procedure and drives it to completion | - list the playbooks visible from the core, global and vault discovery roots<br>- select one by its trigger, or by name when the user names it<br>- drive steps in graph order, running each parallel wave as detached sub-agents<br>- resume an interrupted run from the state frontier rather than from the driving context |
```

You never stop for the user: write the file, return, and the gate is the runner's.

## Return format

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

One `## Notes:` group line per group, in file order, then the drift lines — omitted entirely on
a first run, where the `## Changed:` marker is already `[CREATED]`. The runner presents the
index at the gate from these lines alone and never opens the file. No prose outside the block.
