---
status: awaiting-spec-confirm
---

[← index](../../index.md)

# roles

## Contract

- **Needs** —
  - the shaping briefing — what the project is, who it serves, where it is heading
  - the surfaces the project exposes and who consumes them, read from the repo itself: the
    README, the public docs site, the changelog, plugin-internal docs, command help output,
    issue and release history. The sibling surfaces file is being written concurrently and is
    never read here
  - the previous roles characterisation, when one exists
  - the run's confirmed scope — whether roles is established from nothing or refreshed
- **Value** — the audience layer every later step reads from: who the documentation is written
  for, and per audience the depth ceiling, the tone and what must be withheld. `research`,
  `targeting`, `write`, `compact` and `verify` all resolve "how deep, in what voice, for whom"
  against this file, so the brief's oversharing guard — business readers never get
  implementation detail — is enforced here once instead of re-argued per document.
- **Output files** —
  - `[CREATED|UPDATED] _specs/roles.md` (workdir-relative; `{vault}/docs/_specs/roles.md`):
    - H1 `# {project} — Documentation roles`, then one `## {role}` section per audience, each a
      fixed five-bullet block — **Who** / **Comes for** / **Depth** / **Tone** / **Withhold** —
      closed by a **Reads** bullet naming the surfaces that audience actually opens
    - roles are named for what the reader does, not for a job title, and stay stable across
      runs: a role that still holds keeps its name and section, refreshed in place
    - a readable snapshot of the current audience set — no "previously we also served …"
      narration; drift against the previous file is reported in the return, never written into
      the file
    - no frontmatter of the step's own; whatever frontmatter exists is preserved untouched —
      `reviewed_at` is stamped by the gate's `frontmatter-update _specs/roles.md` hook
- **Harness return** — `## Changed:` one line, the role count appended; `## Notes:` one digest
  line per role (name — depth — tone), then one `added:` / `dropped:` / `reshaped:` line per
  change against the previous file with its reason, so the runner can hold the gate without
  reading the file.
- **Review gate** —
  - confirm or refine — presented together with surfaces. The runner holds it at
    `awaiting-roles-targets-confirm`, presenting this file and `_specs/targets.md` in one pass;
    a refinement re-enters `spec-building`. The step itself never stops for the user — it
    writes, returns, and the gate is the runner's.
- **Delegation** — detached: `detached: "fable:medium"` — a generic sub-agent fetches this
  step's body itself and performs it; the repo reading stays out of the runner's context, which
  receives only the path and the digest. The agent needs reads over the attached repo plus the
  briefing at `_specs/index.md` and the previous `_specs/roles.md`; it writes exactly one file.

## Example artifact

`{vault}/docs/_specs/roles.md`, for this project:

```markdown
# claude-booping — Documentation roles

## Plugin user

- **Who** — a developer who installed booping and runs `/playbook` in their own project.
- **Comes for** — what a playbook does to their repo, what it asks of them, how to configure it.
- **Depth** — commands, config keys, artifact paths. Never internals: no template pipeline, no
  render internals, no Python module names.
- **Tone** — second person, imperative, worked examples over description.
- **Withhold** — build-time architecture, eval harness, unreleased behaviour.
- **Reads** — README, docs site, CHANGELOG.

## Playbook author

- **Who** — a user writing their own playbook in a vault `_playbooks/` directory.
- **Comes for** — the manifest schema, the graph and state grammar, what a step body may assume.
- **Depth** — full schema and mechanics, worked manifests; still no implementation source.
- **Tone** — reference-first, schema before prose, every field named exactly as it appears.
- **Withhold** — rationale for design choices already settled; migration history.
- **Reads** — docs site (playbook + config reference), plugin-internal `docs/`.

## Contributor

- **Who** — someone changing this repo: templates, playbooks, the CLI.
- **Comes for** — layout, the two render pipelines, what to run before committing.
- **Depth** — unrestricted, including build artefacts and test tiers.
- **Tone** — dense, conventions as rules.
- **Withhold** — nothing; onboarding narration is what gets cut instead.
- **Reads** — CLAUDE.md, plugin-internal `docs/`, CHANGELOG.
```

## Return Format

```markdown
## Changed:
- [CREATED|UPDATED] _specs/roles.md — {n} roles

## Notes:
- {role} — {depth in a phrase} — {tone in a phrase}
- added: {role} — {why this run surfaced it}
- dropped: {role} — {why it no longer holds}
- reshaped: {role} — {what changed in depth, tone or withheld set}

## Questions:
```

One `## Notes:` digest line per role, in file order, then the drift lines — omitted entirely on a
first run, where the `## Changed:` marker is already `[CREATED]`. No prose outside the block.
