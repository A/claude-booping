# Map the blast radius in the codebase

This step is yours: you scope what gets mapped and you write the map. The bulk reading is not —
delegate it to `{{ config.research_agent }}` and let only the compressed map come back, so the
files never enter your context.

The map answers what this work moves in the attached repo, what it must imitate, which of the
repo's own rules bind it, and what the code could not settle. `design` argues from it instead of
from assumptions, so every claim in it is a claim about files that were actually read.

## Scope the reading

- Start from the surfaces the framing names, and follow the references out of them — imports, call
  sites, config keys, tests, the docs that mention them.
- Stop at the confirmed boundaries: a surface the user excluded stays out of the map even when it
  sits next to the code that moves.
- A specific fact the repo cannot settle — an installed tool's flag, a pinned version's behaviour
  — is checked against local ground truth first (`tool --help`, lockfiles, the vendored source),
  and against the web only for that one fact, through the same agent. Surveying external practice
  is `research-web`'s job, behind the user's request.

## Delegate the reading

Spawn `{{ config.research_agent }}` with the surfaces to map, the restated problem and the
confirmed scope boundaries, and this return contract:

- the raw material for the four sections below and nothing else: touched surfaces by path, prior
  art by path, the conventions it found stated with where the repo states them, and what the code
  left unsettled
- paths, symbols and config keys only — no file contents, no quoted blocks, no diffs
- at most ~80 lines; a longer answer is a failed one — narrow the surfaces and re-ask

Surfaces too far apart for one pass → one agent per slice, each with its own contract. Read in
your own context only what the returned map leaves ambiguous.

## The section to write

`## Blast radius` in `index.md` — the only thing this step writes. Preserve the file's frontmatter
and the sections other steps own; write these four H3s, in this order, non-empty in every run:

- `### Touched surfaces` — a table whose columns are exactly `Surface`, `Where`, `Why it moves`,
  `Risk`. One row per file, module, integration or external surface the work moves. `Where` names
  the repo path, or the backticked symbol or config key inside it — every row points at something
  that exists in the repo. `Why it moves` traces back to the confirmed scope. `Risk` is `low`,
  `medium` or `high` plus its short reason, graded on what the code shows: how many callers depend
  on the surface, whether it is public to consumers, whether behaviour has to survive the move.
- `### Prior art` — the closest existing implementations this work should follow, each cited by
  path, each with what it is precedent for. A gap the precedents leave open is an unknown for
  `design`, not a bullet here. The section takes one of two shapes and never mixes them —
  path-cited precedents, or, when the repo holds no precedent at all, the bare statement that
  there is none ("no prior art in the repo") citing nothing. Never borrow an example from outside
  the repo and never drop the section.
- `### Conventions in play` — the repo's own rules that bind this work (project guide, build
  artefacts, ownership boundaries, dependency policy, test rules), each written as a constraint on
  the design and traceable to where the repo states it. Generic engineering advice is not a
  convention.
- `### Unknowns for design` — what the codebase could not settle, each phrased as the call
  `design` has to make. Not a to-do for more reading, not a restated risk. An open external
  question lands here too, so the user can ask for web research when it matters.

A greenfield surface is reported as greenfield; this step has no skip note.

## Return format

```
## Changed:
- [UPDATED] plans/{slug}/index.md — blast radius

## Notes:
- blast radius: {n} files across {m} modules, {external surfaces}; riskiest: {surface}
- for design: {one line per unknown}
```

`## Notes:` carries the headline and the unknowns only — it never restates the map.
