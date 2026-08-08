---
---
[← index](../../index.md)

# intake — Tests

## Fixtures

| Fixture              | Requirements                                                                                                                                                                                                                       |
| -------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| fresh-request        | the request verbatim — "make `/develop` resume an interrupted sprint without re-running finished milestones" — plus the task-type catalogue with its per-type guidance, the project's conventions, and a vault listing of four plans (title, type, status; one of them parked) none of which covers the request |
| answered-rerun       | fresh-request's inputs plus the `intake.md` that pass wrote and the user's one-line answers to its scope questions, one answer moving a boundary out of scope                                                                       |
| parked-plan-named    | a vault listing carrying `plans/20260715-retro-template-picker.md` at `status: backlog` with a stale `title` and `type`; the request names that parked plan as the thing to groom                                                   |
| parked-plan-unnamed  | trap — parked-plan-named's vault, with the request restating the parked plan's work in the user's own words and never naming it; provokes a second plan minted for work already parked                                              |

## Tests

| Fixture             | Tier    | Title                 | Check logic                                                                                                                                                                     |
| ------------------- | ------- | --------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| fresh-request       | smoke   | FILES-AND-SLUG        | `_runs/groom/{slug}/intake.md` and `plans/{slug}.md` both written on the same `yyyymmdd-hh-mm_{title}` stem; `intake.md` is the only file in the run workdir                     |
| fresh-request       | smoke   | INTAKE-SHAPE          | frontmatter is exactly `reviewed_at: null`; H1 `# Intake — {title}`; H2s Request, Restated problem, Task type, Scope boundaries, Scope challenge — in that order                 |
| fresh-request       | smoke   | REQUEST-VERBATIM      | Request holds the fixture's request text as a blockquote, character-for-character, nothing added                                                                                 |
| fresh-request       | smoke   | SCOPE-SHAPE           | Scope boundaries carries non-empty **In scope** and **Out of scope** groups; Scope challenge lists at least one `- [ ]` item                                                     |
| fresh-request       | smoke   | PLAN-BODY-EMPTY       | `plans/{slug}.md` holds nothing but whitespace after the closing `---`                                                                                                           |
| fresh-request       | smoke   | PLAN-IDENTITY         | plan frontmatter: `status: in-spec`, `title` and `type` set from the framing, `created` the run date, `sp: null`, `summary: ""`, every remaining key of the plan shape at `null`  |
| fresh-request       | smoke   | RETURN-SHAPE          | `## Changed:` marks both paths `[CREATED]`; `## Notes:` names the task type and the plan path; `## Questions:` is numbered and non-empty                                         |
| fresh-request       | regress | TYPE-DISCRIMINATED    | the type is one of the catalogue's and its rationale rules the sibling types out by name — `feature` here, with bug and refactoring each excluded on a stated test                |
| fresh-request       | regress | PROBLEM-FAITHFUL      | the restated problem names today's behaviour and what must change, in the request's own domain terms; no requirement the request does not carry                                  |
| fresh-request       | regress | BOUNDARIES-DECIDABLE  | every in/out item is decidable on sight, and Out of scope names adjacent work the request could plausibly be read to include — not strawmen                                      |
| fresh-request       | regress | QUESTIONS-CHALLENGE   | each question challenges scope (new components, dependencies, APIs, workflow changes), is answerable in one line, and asks nothing the request already answers                   |
| fresh-request       | regress | NO-RESEARCH-LEAK      | no blast radius, file list, architecture call, milestone or estimate anywhere in `intake.md`                                                                                     |
| answered-rerun      | smoke   | RERUN-UPDATED         | `## Changed:` holds `intake.md` alone, marked `[UPDATED]`, at the first pass's path; no new plan file and no new run workdir                                                     |
| answered-rerun      | smoke   | RERUN-QUESTIONS-EMPTY | `## Questions:` is present and carries nothing — no items, no `(none)` placeholder                                                                                              |
| answered-rerun      | regress | ANSWERS-FOLDED        | each answer lands where it belongs — the moved boundary now sits under Out of scope — and no scope question is left open                                                         |
| answered-rerun      | regress | FRAMING-STABLE        | what the answers did not touch is unchanged — request blockquote intact, type held unless an answer moved it — and `## Notes:` reports what changed                              |
| parked-plan-named   | smoke   | ADOPT-SLUG            | the slug is the parked plan's filename stem: `intake.md` lands at `_runs/groom/20260715-retro-template-picker/intake.md`; no `yyyymmdd-hh-mm_` slug minted                       |
| parked-plan-named   | smoke   | ADOPT-IN-PLACE        | `plans/` gains no file and `plans/20260715-retro-template-picker.md` keeps its name; `## Changed:` marks it `[UPDATED]`                                                          |
| parked-plan-named   | smoke   | ADOPT-STATUS-FLIP     | the parked plan's `status:` reads `in-spec`, `title` and `type` match the framing, and `created` plus every other pre-existing value is untouched                                |
| parked-plan-named   | regress | ADOPT-FRAMING         | `intake.md` frames the parked plan's work as the request restates it — one plan's framing, not a second plan's                                                                   |
| parked-plan-unnamed | smoke   | TRAP-PARKED-CITED     | `plans/20260715-retro-template-picker.md` appears in `## Notes:` or `## Questions:`                                                                                              |
| parked-plan-unnamed | regress | TRAP-NO-DUPLICATE     | the overlap is resolved before framing proceeds — parked plan adopted in place, or raised as a question; a second plan minted for the same work without naming the parked one fails |
