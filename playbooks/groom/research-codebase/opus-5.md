# Map the blast radius in the codebase

The input carries the confirmed framing — the restated problem, the task type and the scope
boundaries the user agreed — and points at the attached repository, which sits on disk in the
current working directory together with the run workdir. Produce the **blast-radius map**: what
this work moves in this repo, what it must imitate, which of the repo's own rules bind it, and
what the code could not settle. `design` argues from this map instead of from assumptions, so
every claim in it is a claim about files you actually read.

The heavy reading is this step's job and the map is all that travels onward — read the repo
yourself and delegate nothing. Start from the surfaces the framing names, follow the references
out of the files you open (imports, call sites, config keys, tests, the docs that mention them),
and stop at the confirmed boundaries: a surface the user excluded stays out of the map even when
it sits next to the code that moves.

## The file to write

`_runs/groom/{slug}/research-codebase.md` — the run workdir, named in the run-time context. It
is the only file this step writes.

- no frontmatter — the map carries no gate, so nothing stamps it
- one H1: `# Blast radius — {request title}`
- `## Touched surfaces` — a table whose columns are exactly `Surface`, `Where`, `Why it moves`,
  `Risk`. One row per file, module, integration or external surface the work moves. `Where`
  names the repo path, or the backticked symbol or config key inside it — every row points at
  something that exists in the repo. `Why it moves` traces back to the confirmed scope. `Risk`
  is `low`, `medium` or `high` plus its short reason, graded on what the code shows: how many
  callers depend on the surface, whether it is public to consumers, whether behaviour has to
  survive the move.
- `## Prior art` — the closest existing implementations this work should follow, each cited by
  path, each with what it is precedent for. Every bullet cites a path: a gap the precedents
  leave open is an unknown for `design`, not a bullet here. The section takes one of two shapes
  and never mixes them — path-cited precedents, or, when the repo holds no precedent at all, the
  bare statement that there is none ("no prior art in the repo") citing nothing. Never borrow an
  example from outside the repo and never drop the section.
- `## Conventions in play` — the repo's own rules that bind this work (project guide, build
  artefacts, ownership boundaries, dependency policy, test rules), each written as a constraint
  on the design and traceable to where the repo states it. Generic engineering advice is not a
  convention.
- `## Unknowns for design` — what the codebase could not settle, each phrased as the call
  `design` has to make. Not a to-do for more reading, not a restated risk.

All four sections appear, in that order, non-empty, in every run. A greenfield surface is
reported as greenfield; this step has no skip note.

## Return format

```
## Changed:
- [CREATED] _runs/groom/{slug}/research-codebase.md

## Notes:
- blast radius: {n} files across {m} modules, {external surfaces}; riskiest: {surface}
- for design: {one line per unknown}
```

`## Notes:` carries the headline and the unknowns only — it never restates the map.
