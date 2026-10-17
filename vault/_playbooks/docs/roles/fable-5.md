# Characterise the documentation audiences

You receive the attached repo, the run record `{vault}/docs/_runs/{YYYYMMDDHHmm}-{title}.md`, and
the run's confirmed scope — whether the audience set is established from nothing or refreshed.

Read, in this order:

- the run record's `## Briefing` — what the project is, who it serves, where it is heading. Every
  role you name is an audience that briefing implies.
- the repo itself, for the surfaces it exposes and who opens them: README, the public docs site
  source, the changelog, plugin-internal docs, command help output, issue and release history.
- the audience record `{vault}/reference/0001-audience.md` — the current characterisation,
  and the file you refresh.

Never read reference/0003 (documentation surfaces): it is being refreshed concurrently by a
sibling step and is not a source here.

## The record to refresh

The audience record's `## Facts` section, rewritten in place. Nothing else is written.

- One fact per bullet, in the bullet style the record uses today: a bullet opening with the bold
  role name — who it is and what it **comes for** — then a bullet carrying that role's
  **depth** ceiling, what is **withheld**, its **voice**, and what it **reads**. A fact that holds
  for every role stays its own bullet ahead of the roles.
- Roles are named for what the reader does, not for a job title, and stay stable across runs: a
  role that still holds keeps its name and its bullets, refreshed in place.
- Depth states the ceiling positively and then what is never included; withheld carries the
  briefing's oversharing guard — business readers never get implementation detail. Later steps
  resolve "how deep, in what voice, for whom" against these bullets and nowhere else, so they
  must decide the question on their own.
- The section is a readable snapshot of the current audience set. No "previously we also
  served …" narration — drift against the previous facts is reported in the return, never written
  into the record.
- A default you chose that the briefing and the repo do not settle is marked `[clarify]` with one
  sentence on what to settle (rule/0002).
- Frontmatter stays untouched except `updated_at`, set to today. `reviewed` is the owner's alone —
  never add or change it.
- The H2 order the record shape enforces stays as it is: `## Facts`, then `## How to check?` when
  present.

You never stop for the user: refresh the record, return, and the gate is the runner's.

## Return format

```markdown
## Changed:
- [UPDATED] the audience record — {n} roles

## Notes:
- {role} — {depth in a phrase} — {voice in a phrase}
- added: {role} — {why this run surfaced it}
- dropped: {role} — {why it no longer holds}
- reshaped: {role} — {what changed in depth, voice or withheld set}

## Questions:
```

One `## Notes:` digest line per role, in record order, then the drift lines — omitted when nothing
moved against the previous facts. No prose outside the block.
