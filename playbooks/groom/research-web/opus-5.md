# Research current external practice

This step is yours: you decide what is researched and you write the artifact. The web reads are
not — delegate them to `{{ config.research_agent }}` and let only the findings and their sources
come back.

Which path runs was settled at intake and written into the `### Web research` line of `## Framing`
in `index.md`. Read that line and execute it. This step never judges whether the work is novel,
well-trodden or worth researching.

## Not requested

Make sure `## Framing` carries the line `Web research: not requested`, add it if intake's framing
does not already state it, and stop. No `research.md`, no findings, no reasoning about whether
research would have helped. An open external question the user may want escalated is already in
`## Blast radius`.

## Requested

Size the research to the open questions the framing carries — one primary source per question,
stopping once the design call it blocks is constrained. A fact local ground truth answers is not
fetched.

Spawn `{{ config.research_agent }}` with those questions, the restated problem and the confirmed
scope boundaries, and this return contract:

- per question: the candidate approaches with how each fits and what it costs **this** request,
  the pitfalls that constrain the design, and a URL plus a `yyyymmdd` retrieval date per claim
- primary sources first — the standard, the upstream documentation, the project's own reference —
  before the write-ups about them
- findings only: no page dumps, no quoted articles, at most ~100 lines
- a claim it cannot cite is dropped, not softened

Retrieval unavailable — no search tool, a denied permission, a failed fetch — still produces the
whole artifact: pin each claim to the canonical primary document, cite it by its stable URL, put
the run date in `Checked`, and say in `## Notes:` that the rows were not retrieved live this run
so `design` re-checks them. A claim with no citable primary document stays out.

Write `plans/{slug}/research.md`:

- H1 `# research — {slug}`
- `## Approaches` — at least two, each an H3 carrying its own name, a line on how it works, then a
  bullet list opening with the literal labels `Fits:` and `Costs:`, one bullet each, stated
  against this request. Add a `Retire cost:` bullet where that is what separates two candidates.
  The labels are plain text — no bold, no italics, no substitutes:

  ```
  - Fits: limits are per API key, which the gateway already resolves.
  - Costs: bucket state must be shared across processes — needs the cache tier.
  - Retire cost: low — the middleware is one layer, removable without touching handlers.
  ```
- `## Pitfalls` — the constraints the design must answer, each naming the call it forces. A
  caution `design` cannot act on is not a pitfall.
- `## Sources` — a table with the columns `Source`, `Backs`, `Checked`: an `https://` URL, the
  claim it backs, and the `yyyymmdd` date it was retrieved. Every cell filled on every row; a
  placeholder in any of the three is not a source row.

An approach that lives on a surface the framing excluded stays out, however good it is elsewhere.
A section holding a placeholder, an apology or a note about what went wrong instead of findings is
not an artifact this step may write — a caveat belongs in `## Notes:`.

## Return format

The reply is the block alone — no prose around it, no section the format does not name.

Requested path:

```
## Changed:

- [CREATED] plans/{slug}/research.md — {n} approaches, {m} sources

## Notes:

- recommended: {one of the approaches you wrote} — {why it wins here}
- {n} pitfall(s) the design must answer
```

Both notes are required; a caveat about the research is an extra note after them, never a reason
to withhold them.

Not-requested path:

```
## Changed:

- [UPDATED] plans/{slug}/index.md — web research: not requested

## Notes:

- web research not requested at intake; open external questions, if any, are in the blast radius
  for the user to escalate
```
