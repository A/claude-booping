# Research current external practice

The input carries the framing the user confirmed at the end of `intake` — the restated problem,
the task type and the scope boundaries — together with whatever uncertainty signals that framing
recorded. Settle what current external practice says about the work before the architecture is
called, so `design` argues from dated sources instead of model memory.

## Call the verdict first

Two paths, and the file is written on both.

- **Researched** — the work is novel or non-obvious here: an unfamiliar surface, a new or
  upgraded dependency, a protocol or approach with no precedent in the repository, or a design
  call whose answer is a matter of current practice rather than local convention.
- **Skipped** — the work is well-trodden: the framing names prior art in the repository, the work
  adds no dependency and no new surface, and the shape of the fix follows from what is already
  there.

Judge the request, not the signal list. Intake's uncertainty signals are evidence, never the
verdict: an empty list on a request that adopts a protocol or a dependency the repository has
never touched still researches, and a crowded list on a routine fix still skips. Ground the
rationale in what makes this particular request novel or routine — never in what the signal list
happened to contain.

## Researching

- Search for the ways this problem is solved today, not for a single blessed answer. Two
  approaches make a trade-off the user can decide; one makes a recommendation with nothing behind
  it.
- Read the primary source where one exists — the standard, the upstream documentation, the
  project's own reference — before the write-ups about it.
- Weigh every approach against this request's own constraints: what the framing put in scope,
  what it excluded, what the project already runs. A generic pros-and-cons list is not a finding.
- Collect the pitfalls that constrain the design — the failure an approach invites, the response
  header callers already expect, the assumption that breaks once more than one process runs. A
  caution `design` cannot act on is not a pitfall.
- Stay inside the boundaries. An approach living on a surface the framing excluded is out,
  however good it is elsewhere.
- Carry a URL and a retrieval date for every claim. An approach or a pitfall with no row behind
  it in the source table is model memory and does not go in the file.
- When retrieval is unavailable — no search tool, a denied permission, a fetch that fails — the
  researched path still produces the whole artifact. Pin each claim to the canonical primary
  document instead (the RFC, the upstream reference, the project's own docs), cite it by its
  stable URL, put the run date in `Checked`, and say in `## Notes:` that the rows were not
  retrieved live this run so `design` re-checks them before arguing from them. A claim with no
  citable primary document behind it is still model memory and still stays out.

## The artifact

Write `research-web.md` into the run workdir the input names — created on both paths, never
omitted, never empty. Report it in the return under the workdir-relative path the input gave,
e.g. `_runs/groom/{slug}/research-web.md`; mark the entry `[UPDATED]` instead of `[CREATED]` when
a re-entered run finds the file already there.

The H1 is `# research-web — {slug}`, carrying the run slug the input names.

`## Verdict` comes first on both paths, as a **single paragraph**: the word `Researched` or
`Skipped`, an em dash, then one line of rationale — `Researched — <what makes this request novel
here>`. Nothing else in the section: no second paragraph, no verdict on a line of its own.

On the **skip** path the file ends there — the verdict alone, no further sections.

On the **researched** path three sections follow, in this order, each carrying real content. There
is no third verdict and no unfilled section: once the verdict reads `Researched`, an `## Approaches`
or `## Pitfalls` holding a placeholder, an apology, or a note about what went wrong instead of
findings is not an artifact this step may write. A caveat belongs in `## Notes:`.

- `## Approaches` — at least two, each an H3 carrying its own name, a line on how it works, then a
  bullet list opening with the literal labels `Fits:` and `Costs:`, one bullet each, stated against
  this request. Add a `Retire cost:` bullet where that is what separates two candidates. The labels
  are plain text — no bold, no italics, no substitutes:

  ```
  - Fits: limits are per API key, which the gateway already resolves.
  - Costs: bucket state must be shared across processes — needs the cache tier.
  - Retire cost: low — the middleware is one layer, removable without touching handlers.
  ```
- `## Pitfalls` — the constraints the design must answer, each naming the call it forces.
- `## Sources` — a table with the columns `Source`, `Backs`, `Checked`: an `https://` URL, the
  claim it backs, and the `yyyymmdd` date it was retrieved — the run date on the no-retrieval
  fallback above. Every cell is filled on every row; a placeholder in any of the three is not a
  source row.

## Return format

The reply to the harness is the block alone — no prose around it, no section the format does not
name. `## Notes:` is the only channel a caveat or a blocker reaches the runner through.

```
## Changed:

- [CREATED] _runs/groom/{slug}/research-web.md — researched: 3 approaches, 3 sources

## Notes:

- recommended: token bucket in gateway middleware — lowest retire cost, keys on what the
  gateway already resolves
- 3 pitfall(s) the design must answer, one of them a fail-open vs fail-closed call
```

On the researched path both of those notes are required: a `recommended:` line naming one of the
approaches you wrote, and the pitfall count. A caveat about the research — retrieval that was
unavailable, a source you could not confirm — is an **extra** note after them, never a reason to
withhold them.

On the skip path the annotation and the note carry the rationale instead, and no recommendation
or pitfall count is reported:

```
## Changed:

- [CREATED] _runs/groom/{slug}/research-web.md — skipped: well-trodden

## Notes:

- skipped: framework-native session bug, no new dependency or surface, prior art in the repository
```
