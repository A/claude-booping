# Clarifications

Autonomous groom run on 2026-10-15: the owner was unavailable, so every question below was settled by the run with the default marked "default applied". Each stays reviewable and amendable before develop starts ([value/0009](../../specs/value/0009-adjustable-control.md), [rule/0002](../../specs/rule/0002-unknown-is-marked.md)).

## C1 — which parked part, and split — answered

**Asked:** 2026-10-15 — intake

**Question:** The previous plan parked part 3 (corrections, adr/0026) and part 4 (autonomy modes, adr/0027). Which is groomed now, and together or apart?

**Options:**

- Part 3 alone; part 4 stays parked (default applied)
- Parts 3 + 4 in one plan
- Part 4 first

**Answer:** First option — default applied. Part 3 is first in the request's order and independent; part 4 is a separate config surface plus a manager path (adr/0028 is its own decision) and together they would pass the 35 SP threshold. Part 4 stays a stub in `index.md` `## Out of scope`.

## C2 — where the sidecar sits — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** adr/0026 puts `corrections.md` beside the run artefact. Code reviews of one plan share `codereviews/{plan-dirname}/`, one `{ts}.md` per review. One sidecar per directory or one per review?

**Options:**

- One per directory: `{dirname(target)}/corrections.md`, every entry naming its artefact (default applied)
- One per review: `codereviews/{dir}/{ts}.corrections.md`

**Answer:** First option — default applied. One rule for every playbook (the target's directory), the file name adr/0026 names, and one file for retro to read per plan's review directory; the `**Artifact:**` line on every entry keeps reviews apart.

## C3 — CLI surface — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** adr/0026 names `booping correction add`. Is a reader verb needed, and does `correction` nest under another command?

**Answer:** Top-level `correction` with `add` and `list --plan` — default applied. Gathering a plan's feed (its own sidecar plus its reviews', via `code_reviews:`) is computable, so it is code, not retro prose (value/0015). `correction` is not a specs concern, so it does not nest under `specs`.

## C4 — the dialogue link — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** The request asks for "session id + message position, the way session-stats finds the transcript". Which handle is the position, how does the CLI find it, and what happens without a transcript?

**Options:**

- The CLI finds it: session id from `CLAUDE_CODE_SESSION_ID` (or `--session`), transcript via `session_stats.locate_transcript`, position = 1-based jsonl line + `uuid` of the last user message containing `--said`; no session or transcript → entry with `not found — …` and a warning, exit 0; transcript found but no match → exit 1 (default applied)
- The agent passes a position itself
- A user-turn ordinal

**Answer:** First option — default applied. The agent cannot see its own transcript position; code can (value/0015). The jsonl is append-only, so the line number stays valid, and the `uuid` survives any re-read. Matching `--said` against the transcript also holds the quote verbatim. The warning fallback follows `stamp-session`, since `CLAUDE_CODE_SESSION_ID` is undocumented. The exact entry content is locked in `index.md` `### corrections.md` (booping:rule/0010).

## C5 — a correction that touches a spec — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** adr/0026: "A correction that touches a spec also becomes an open item." Who files it, with which direction?

**Answer:** `correction add --record REF` files it in the same call — `source: correction` (a sixth source value), `direction: conflict`, title `{step}: {said}` truncated at 100 chars — and both files link each other — default applied. `conflict` because the model's work and the record disagree; the owner settles which way. `--record` accepts a namespaced ref (`booping:rule/0002`) and checks only its shape, since a cross-tier record may not resolve on this machine.

## C6 — what retro does with the feed — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** adr/0026: retro reads the sidecar as its feed, learn proposes rules from it. Does retro stop mining transcripts, and does learn change?

**Options:**

- Retro `prepare` reads `booping correction list --plan` first, each entry an issue item with source `correction`; session-log mining stays, handed the entries' dialogue links; learn unchanged — it reads the retrospective (default applied)
- Retro drops session-log mining
- Learn also reads the sidecars

**Answer:** First option — default applied. The log relies on the agent noticing a correction (adr/0026's own con), and mining also finds tensions and detours that are not corrections, so it stays as a second net, now steered by the links. Learn reads only the retrospective by design; the corrections reach it through retro's issues.

## C7 — the rule's targets — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** Which tier holds the rule, and does it target whole playbooks or specific steps?

**Answer:** Core tier, `specs/rule/0031-corrections-are-logged.md`, `targets: [groom, develop, code-review]` — default applied. It steers every user's runs, so it ships with the plugin; a correction can land in any step, so the target is the playbook, injected once in its `## Rules`.
