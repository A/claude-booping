# Characterise the documentation audiences

You receive the workdir (`{vault}/docs/`), the attached repo, and the run's confirmed scope —
whether the roles file is established from nothing or refreshed.

Read, in this order:

- `_specs/index.md` — the shaping briefing: what the project is, who it serves, where it is
  heading. Every role you name is an audience that briefing implies.
- the repo itself, for the surfaces it exposes and who opens them: README, the public docs site
  source, the changelog, plugin-internal docs, command help output, issue and release history.
- `_specs/roles.md`, when one exists — the previous characterisation.

Never read `_specs/targets.md`: the surfaces file is being written concurrently by a sibling
step and is not a source here.

## The file to write

`_specs/roles.md`, workdir-relative. One file, nothing else.

- H1 `# {project} — Documentation roles`, then one `## {role}` section per audience.
- Each section is a fixed five-bullet block — **Who** / **Comes for** / **Depth** / **Tone** /
  **Withhold** — closed by a **Reads** bullet naming the surfaces that audience actually opens.
- Roles are named for what the reader does, not for a job title, and stay stable across runs: a
  role that still holds keeps its name and its section, refreshed in place.
- **Depth** states the ceiling positively and then what is never included; **Withhold** carries
  the briefing's oversharing guard — business readers never get implementation detail. Later
  steps resolve "how deep, in what voice, for whom" against these bullets and nowhere else, so
  they must decide the question on their own.
- The file is a readable snapshot of the current audience set. No "previously we also served …"
  narration — drift against the previous file is reported in the return, never written into the
  file.
- Write no frontmatter of your own; preserve whatever frontmatter is already there untouched.
  `reviewed_at` is stamped by the runner's gate hook.

Shape of one section:

```markdown
## Plugin user

- **Who** — a developer who installed booping and runs `/playbook` in their own project.
- **Comes for** — what a playbook does to their repo, what it asks of them, how to configure it.
- **Depth** — commands, config keys, artifact paths. Never internals: no template pipeline, no
  render internals, no Python module names.
- **Tone** — second person, imperative, worked examples over description.
- **Withhold** — build-time architecture, eval harness, unreleased behaviour.
- **Reads** — README, docs site, CHANGELOG.
```

You never stop for the user: write the file, return, and the gate is the runner's.

## Return format

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
