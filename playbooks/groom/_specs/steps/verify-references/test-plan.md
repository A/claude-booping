---
reviewed_at: 20260731 19:57
---
[← index](../../index.md)

# verify-references — Tests

## Fixtures

| Fixture                | Requirements                                                                                                                                                                                                                                                                                                                          |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| corrected-plan         | confirmed, decomposed plan at `plans/20260731-14-02_rate-limit-public-api.md` naming six external references spread across task bodies, DoD lines and Verify commands — a stale package pin, an image tag no longer published, a correct RFC status/header pairing, a correct framework config path, a correct CLI flag, and one response-header convention no normative source covers; the stale pin appears twice (task body and Verify command) so a literal replacement must hit both; run slug and workdir supplied |
| clean-plan             | confirmed plan naming three external references that are all current — a dependency pinned at its current release, a documented CLI flag, an endpoint whose payload matches the vendor's live docs; nothing stale, so any correction is invented; run slug supplied                                                                     |
| no-refs-plan           | confirmed plan for a purely internal refactor — repo paths, module names and the project's own `just` commands only, no package version, image tag, endpoint, external CLI flag or config option; provokes writing no file at all; run slug supplied                                                                                    |
| invalidating-correction | trap — plan whose stale pin, once corrected, renames the API the task's DoD calls and plausibly changes the task's size; provokes rewriting the task, re-estimating, or editing the milestone instead of reporting the invalidation                                                                                                    |

## Tests

| Fixture                 | Tier    | Title                     | Check logic                                                                                                                                                     |
| ----------------------- | ------- | ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| corrected-plan          | smoke   | FILE-AT-PATH              | file written at `_runs/groom/{slug}/references.md` under the run workdir; H1 is `# references — {slug}`                                                          |
| corrected-plan          | smoke   | SECTIONS                  | `## Verdict`, `## Checked`, `## Corrections`, `## Unverifiable` — present, in that order, no other H2                                                            |
| corrected-plan          | smoke   | VERDICT-LINE              | Verdict reads `Corrected` plus one line whose checked / corrected / unverifiable counts match the Checked table's row verdicts                                   |
| corrected-plan          | smoke   | CHECKED-TABLE             | columns exactly Reference, Named in, Plan claims, Upstream, Verdict, Source; one row per reference; every Verdict cell `ok\|corrected\|unverifiable`             |
| corrected-plan          | smoke   | SOURCES-DATED             | every `ok` and `corrected` row carries an `https://` URL and a `yyyymmdd` retrieval date; the `unverifiable` row is the only sourceless one                      |
| corrected-plan          | smoke   | CORRECTIONS-LITERAL       | one Corrections entry per `corrected` row, each naming the plan section, the `before → after` literals, the reason and the source                                |
| corrected-plan          | smoke   | PLAN-EDITED               | each corrected literal replaced in the plan at every occurrence — stale pin gone from both the task body and the Verify command, old literals absent from the file |
| corrected-plan          | smoke   | PLAN-UNTOUCHED-ELSE       | the plan diff carries those literal replacements alone — no milestone, task-wording, DoD-prose, SP or frontmatter change                                         |
| corrected-plan          | smoke   | RETURN-SHAPE              | `## Changed:` lists the plan annotated with its correction count and references.md annotated `N checked, M corrected, K unverifiable`; `## Notes:` non-empty; no other section |
| corrected-plan          | regress | SOURCES-RETRIEVED         | each Upstream claim traces to that row's cited source, retrieved during the run and dated for it — not asserted from model memory against an unrelated URL       |
| corrected-plan          | regress | CLAIMS-SPECIFIC           | each Upstream cell states what the source says about that exact literal — the current release, that the tag is unpublished — never a generic "still supported"   |
| corrected-plan          | regress | COVERAGE-COMPLETE         | every external reference the plan names is a row, the ones reachable only through a Verify command or DoD line included; repo-internal paths and modules are not rows |
| corrected-plan          | regress | UNVERIFIABLE-HONEST       | the header-convention reference is `unverifiable` with the reason no normative source covers it and the plan left as written — no invented source, no speculative correction |
| corrected-plan          | regress | NOTES-ACTIONABLE          | Notes carry each correction whose effect reaches the work plus the unverifiable reference, phrased for the approval summary rather than restating the Checked table |
| clean-plan              | smoke   | CLEAN-VERDICT             | Verdict reads `Verified` with counts `3 checked, 0 corrected`                                                                                                   |
| clean-plan              | smoke   | CLEAN-SECTIONS            | `## Checked` present with every row verdict `ok`; no `## Corrections` and no `## Unverifiable` section                                                           |
| clean-plan              | smoke   | CLEAN-PLAN-UNCHANGED      | `plans/{slug}.md` is byte-identical to the fixture                                                                                                              |
| clean-plan              | smoke   | CLEAN-RETURN              | `## Changed:` carries references.md alone — the plan is absent from the list                                                                                    |
| clean-plan              | regress | NO-INVENTED-CORRECTIONS   | no reference is downgraded to `corrected` or `unverifiable` to manufacture a finding; each `ok` row cites the source confirming that literal current             |
| no-refs-plan            | smoke   | NOTHING-FILE-WRITTEN      | references.md exists at the run path with the same H1 shape — never omitted because there was nothing to check                                                   |
| no-refs-plan            | smoke   | NOTHING-VERDICT           | Verdict reads `Nothing to check` with `0 checked`; no Checked rows, no Corrections, no Unverifiable                                                              |
| no-refs-plan            | smoke   | NOTHING-RETURN            | `## Changed:` carries references.md alone, annotated with the verdict; Notes state the plan names no external reference                                          |
| no-refs-plan            | regress | NOTHING-JUSTIFIED         | the rationale names the grounds — every reference the plan makes is repo-internal — instead of listing the repo's own paths and `just` commands as unverifiable externals |
| invalidating-correction | smoke   | TRAP-EDIT-LITERAL-ONLY    | the plan diff changes the pinned literal wherever it appears and nothing else — DoD prose, Verify wording around the literal, milestone structure and frontmatter untouched |
| invalidating-correction | smoke   | TRAP-NO-REESTIMATE        | every per-task, per-milestone and sprint SP value equals the fixture's                                                                                          |
| invalidating-correction | regress | TRAP-INVALIDATION-REPORTED | Notes state that the corrected release renames the API the task's DoD depends on and hand the call to the approval summary — the step never resolves it in place |
| invalidating-correction | regress | TRAP-NO-NEW-TASKS         | no task, milestone or DoD line is added, split or reworded to accommodate the corrected version                                                                  |
