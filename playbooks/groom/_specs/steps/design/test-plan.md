---
---
[← index](../../index.md)

# design — Tests

## Fixtures

| Fixture               | Requirements                                                                                                                                                                                                                                                                                    |
| --------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| researched-first-pass | slug `20260801-09-15_sprints-report-script`: confirmed `intake.md` (type feature, in/out boundaries, every scope question answered) + `research-codebase.md` naming `booping-python/src/booping/hooks.py`, `src/templates/sprints.md.j2`, `src/config.yaml` (`plan.hooks.post`) and leaving one unknown for design (vault resolution from `BOOPING_WORKDIR` on a repo-local vault) + `research-web.md` verdict Researched, 3 approaches, 3 pitfalls, 3 sources |
| loopback-objection    | the researched-first-pass set plus a confirmed `design.md` (frontmatter `reviewed_at: 20260801 10:40`, all five sections filled) and the user's objection reopening exactly one call — the vault-commit trade-off — every other call settled                                                     |
| skipped-research      | trap: well-trodden bug, slug `20260801-11-05_fix-plan-date-stamp-timezone` — `intake.md` type bug + `research-codebase.md` with prior art and no unknowns + `research-web.md` carrying verdict Skipped alone; provokes invented external practice and manufactured trade-off calls              |

## Tests

| Fixture               | Tier    | Title                   | Check logic                                                                                                                                                                     |
| --------------------- | ------- | ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| researched-first-pass | smoke   | FILE-AT-PATH            | single file written, at `_runs/groom/20260801-09-15_sprints-report-script/design.md`; `plans/20260801-09-15_sprints-report-script.md` untouched                                  |
| researched-first-pass | smoke   | H1-SLUG                 | H1 is exactly `# design — 20260801-09-15_sprints-report-script`                                                                                                                 |
| researched-first-pass | smoke   | SECTIONS                | H2s exactly Approach, Surface changes, Alternatives, Trade-offs, Risks — in that order, none extra                                                                              |
| researched-first-pass | smoke   | NO-FRONTMATTER          | file opens at the H1 — the step authors no frontmatter of its own                                                                                                              |
| researched-first-pass | smoke   | TRADEOFF-SHAPE          | every `## Trade-offs` entry names its options, the consequence of each, and one recommendation                                                                                  |
| researched-first-pass | smoke   | RISKS-MITIGATED         | every `## Risks` entry carries a mitigation                                                                                                                                    |
| researched-first-pass | smoke   | QUESTIONS-MATCH         | return is `## Changed:` with the one `[CREATED]` line plus one numbered question per `## Trade-offs` entry — no extra question, none missing                                    |
| researched-first-pass | regress | GROUNDED-IN-BLAST-RADIUS| Approach is argued against the fixture's real paths — `hooks.py`, `sprints.md.j2`, the `plan.hooks.post` list — with the rationale that made it win; no invented path            |
| researched-first-pass | regress | ANSWERS-UNKNOWN         | the map's unknown (vault resolution from `BOOPING_WORKDIR` on a repo-local vault) is decided in Approach or surfaced as a trade-off or risk — never silently dropped            |
| researched-first-pass | regress | ALTERNATIVES-FROM-RESEARCH | the research approaches not taken appear in `## Alternatives`, each with the single reason it lost                                                                           |
| researched-first-pass | regress | PITFALLS-ANSWERED       | each of the 3 pitfalls is designed against in Approach/Surface changes or carried into Risks with a mitigation                                                                  |
| researched-first-pass | regress | SURFACE-CONCRETE        | Surface changes name implementable specifics — script name, config key removed from `plan.hooks.post`, env vars read, defaults — not "config will change"                       |
| researched-first-pass | regress | USER-CALLS-ONLY         | Trade-offs hold calls that are the user's (policy, cost, blast radius), not implementation details design should have settled itself                                            |
| loopback-objection    | smoke   | REVISED-IN-PLACE        | same path returned `[UPDATED]`, one file only; section set still the five H2s — no appended round/revision section                                                              |
| loopback-objection    | smoke   | FRONTMATTER-PRESERVED   | the fixture's `reviewed_at: 20260801 10:40` frontmatter survives unchanged                                                                                                     |
| loopback-objection    | regress | ONLY-REOPENED-REWRITTEN | sections carrying settled calls come through unchanged in substance; only the vault-commit call and what depends on it is rewritten                                            |
| loopback-objection    | regress | OBJECTION-ADDRESSED     | the rewritten call states the choice the objection asks for, and the displaced option moves into `## Alternatives` with the reason it lost                                      |
| skipped-research      | smoke   | NO-CITATIONS            | `_runs/groom/20260801-11-05_fix-plan-date-stamp-timezone/design.md` carries no URL, no source table, no retrieval date                                                          |
| skipped-research      | regress | NO-INVENTED-PRACTICE    | no "current practice", library-comparison or version claim appears — the design argues from the blast radius and prior art alone                                                |
| skipped-research      | regress | NO-MANUFACTURED-CALLS   | `## Trade-offs` invents no call the fix does not carry (an explicit none is correct), and `## Questions:` matches it rather than padding                                        |
