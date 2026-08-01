---
---
[← index](../../index.md)

# research-web — Tests

## Fixtures

| Fixture              | Requirements                                                                                                                                                                                                                                              |
| -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| novel-framing        | confirmed framing for a novel request — restated problem, task type `feature`, scope boundaries carrying one explicit exclusion, plus uncertainty signals naming a new dependency and a request-admission approach with no prior art; run slug supplied      |
| well-trodden-framing | confirmed framing for a framework-native session-cookie bug — task type `bug`, no new dependency, no new surface, the framing itself naming prior art in the repository; uncertainty-signal list empty on grounds the framing states; run slug supplied     |
| unsignalled-novelty  | confirmed framing adopting an external protocol the repository has never touched, with the uncertainty-signal list left empty by intake — provokes skipping because the signal list is silent instead of judging the request; run slug supplied             |

## Tests

| Fixture              | Tier    | Title                | Check logic                                                                                                                                     |
| -------------------- | ------- | -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| novel-framing        | smoke   | FILE-AT-PATH         | file written at `_runs/groom/{slug}/research-web.md` under the run workdir; H1 is `# research-web — {slug}`                                     |
| novel-framing        | smoke   | SECTIONS             | `## Verdict` first, then `## Approaches`, `## Pitfalls`, `## Sources` — present and in that order                                               |
| novel-framing        | smoke   | VERDICT-RESEARCHED   | the Verdict section reads `Researched` plus one line of rationale, nothing more                                                                 |
| novel-framing        | smoke   | APPROACHES-SHAPED    | at least two named approaches, each carrying both a fit line and a cost line                                                                    |
| novel-framing        | smoke   | SOURCES-DATED        | Sources table columns Source, Backs, Checked; every row an `https://` URL and a `yyyymmdd` retrieval date                                       |
| novel-framing        | smoke   | RETURN-ANNOTATED     | Changed entry annotated `researched: N approaches, M sources` matching the file's counts; Notes carries a recommendation line and a pitfall count |
| novel-framing        | regress | CLAIMS-SOURCED       | every approach and every pitfall traces to a row of the Sources table — no claim resting on undated model memory                                |
| novel-framing        | regress | TRADEOFFS-DECIDABLE  | each approach's fit and cost are stated against this request's own constraints, not as generic pros and cons                                    |
| novel-framing        | regress | PITFALLS-CONSTRAIN   | each pitfall names the design call it forces, not a general caution the design cannot act on                                                    |
| novel-framing        | regress | SCOPE-RESPECTED      | no approach targets the surface the framing's boundaries excluded                                                                               |
| well-trodden-framing | smoke   | SKIP-FILE-WRITTEN    | the file exists at `_runs/groom/{slug}/research-web.md` with the same H1 shape — never omitted on the skip path                                 |
| well-trodden-framing | smoke   | VERDICT-SKIPPED      | the Verdict section reads `Skipped` plus one line of rationale                                                                                  |
| well-trodden-framing | smoke   | SKIP-VERDICT-ONLY    | no Approaches, Pitfalls or Sources section — the verdict alone                                                                                  |
| well-trodden-framing | smoke   | SKIP-RETURN          | Changed entry annotated `skipped: {rationale}`; Notes carries the skip rationale and no recommendation or pitfall count                         |
| well-trodden-framing | regress | SKIP-JUSTIFIED       | the rationale names the concrete grounds the framing gave — framework-native, no new dependency or surface, prior art in the repository         |
| unsignalled-novelty  | smoke   | TRAP-VERDICT-RESEARCHED | verdict reads `Researched` and the Approaches, Pitfalls and Sources sections are present despite the empty signal list                       |
| unsignalled-novelty  | regress | TRAP-VERDICT-JUDGED  | the rationale grounds the verdict in the request's own novelty — unfamiliar protocol, no prior art — not in what the signal list contained      |
