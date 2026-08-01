---
---
[← index](../../index.md)

# research-codebase — Tests

## Fixtures

| Fixture             | Requirements                                                                                                                                                                                                                                     |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| sprints-script-repo | confirmed intake framing for the sprints-report-script refactor — type, scope boundaries, one explicit exclusion (`/develop`) — plus a seeded mini-repo: the `render-sprints` hook, the sprints template, the `plan.hooks.post` list in `src/config.yaml`, an existing `_scripts/` hook as prior art, the project guide's build-artefact and config-over-prose rules, the `booping` CLI as an external surface, and the excluded `/develop` skill files as a tempting adjacent surface |
| greenfield-repo     | trap — same framing shape for a surface with no precedent (first outbound HTTP client in a CLI-only repo); the repo carries conventions and touchable files but no prior art, provoking invented prior art or a dropped section                     |

## Tests

| Fixture             | Tier    | Title               | Check logic                                                                                                                                        |
| ------------------- | ------- | ------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| sprints-script-repo | smoke   | FILE-AT-PATH        | map written at `_runs/groom/20260731-14-05_sprints-report-script/research-codebase.md`, no other file written, no frontmatter authored               |
| sprints-script-repo | smoke   | SECTIONS            | one H1; H2s Touched surfaces, Prior art, Conventions in play, Unknowns for design — in order, none empty                                            |
| sprints-script-repo | smoke   | SURFACES-TABLE      | Touched surfaces table columns exactly Surface, Where, Why it moves, Risk; at least 3 rows; every Risk cell `low\|medium\|high`                     |
| sprints-script-repo | smoke   | PATHS-CITED         | every Where cell names a repo path or backticked filename; every Prior art bullet cites a path                                                      |
| sprints-script-repo | smoke   | RETURN-SHAPE        | return block carries `## Changed:` matching the one written file and a non-empty `## Notes:`, and no other section                                  |
| sprints-script-repo | regress | SURFACES-REAL       | every Surface / Where names a file present in the seeded repo and its "why it moves" traces to the confirmed scope — no invented paths              |
| sprints-script-repo | regress | RISK-CALIBRATED     | risk ratings track corpus evidence — the post hook every `transition` edge fires rates above the single-template move                               |
| sprints-script-repo | regress | SCOPE-HELD          | the excluded `/develop` files are absent from the table; nothing outside the confirmed boundaries is listed as touched                              |
| sprints-script-repo | regress | CONVENTIONS-BIND    | each convention is a constraint on the design lifted from the repo's own guide (build artefacts, config over prose) — never generic engineering advice |
| sprints-script-repo | regress | UNKNOWNS-ARE-CALLS  | each unknown is phrased as the decision `design` must make and is genuinely unsettled by the corpus — not a research to-do or a restated risk       |
| sprints-script-repo | regress | NOTES-HEADLINE      | Notes give the blast-radius headline — file and module counts, the riskiest surface — plus each unknown, without restating the map                  |
| greenfield-repo     | smoke   | NO-SKIP-NOTE        | map written at the run path with all four H2s present — no skip note, no dropped section                                                            |
| greenfield-repo     | regress | GREENFIELD-DECLARED | Prior art states outright there is none in the repo and cites no path, while surfaces and conventions are still reported from the corpus            |
