# Clarifications

## C1 — command shape — answered

**Asked:** 2026-10-15 — groom/intake

**Question:** How is the short report and the detail asked for?

**Options:**
- `booping status [SECTION ...]` plus `--detail`
- `booping status --section S` repeated
- one subcommand per section

**Answer:** Default (autonomous run): `booping status` prints the short report, one line per section; `booping status SECTION ...` prints the named sections in detail; `booping status --detail` prints every section in detail. One command, the section names are its only vocabulary.

## C2 — sections and order — answered

**Asked:** 2026-10-15 — groom/intake

**Question:** Which sections, in which order, and what of the runs section the request names?

**Answer:** Default (autonomous run): `items`, `ideas`, `plans`, `records`, `marks`, in that order. The section list is one ordered table in code that part (3) extends with `runs`; no runs section, no placeholder line here — the registry does not exist yet.

## C3 — items section — answered

**Asked:** 2026-10-15 — groom/intake

**Question:** What does the items line count?

**Answer:** Default (autonomous run): non-terminal items (`open_statuses` of the `open_item` machine), counted per status in the machine's order, then split by source into `request`, `backlog` and spec gap (every other source value). Detail is the table `booping items list` prints, from the same `index_rows`/`index_table` helpers.

## C4 — ideas nobody took — answered

**Asked:** 2026-10-15 — groom/intake

**Question:** No field links an idea to a plan; what does "nobody took it" mean in code?

**Answer:** Default (autonomous run): a project-tier `idea` record with `status: open` whose ref (`idea/NNNN`) is not the `record` (anchor stripped) of any non-terminal item. `validating`, `accepted`, `rejected` are taken or settled. No new frontmatter field.

## C5 — plans section — answered

**Asked:** 2026-10-15 — groom/intake

**Question:** Plan statuses are spread over groom's and develop's machines, and done plans are the review and retro queues. What counts?

**Answer:** Default (autonomous run): a plan is active when its status is declared non-terminal by the `run` machine of `groom` or of `develop` (so `ready-for-dev`, terminal for groom, stays active; `done`, `fail`, `cancelled` do not). Active plans are counted per status; done plans are counted twice more: with an empty `code_reviews` and with a null `retro`. The statuses come from the machines, never from a literal list (rule/0017).

## C6 — unreviewed records — answered

**Asked:** 2026-10-15 — groom/intake

**Question:** Count every record with an empty `reviewed`, or only agent-written ones?

**Answer:** Default (autonomous run): every project-tier record with an empty `reviewed` — the predicate the specs site already uses (`site/pages.py`). It moves into `booping.specs.records` as `unreviewed(record)` and the site imports it, so the site and the status agree (value/0003).

## C7 — marks — answered

**Asked:** 2026-10-15 — groom/intake

**Question:** How are marks found and counted?

**Answer:** Default (autonomous run): by the existing sentence-opening mark parser in `open_items.py` (`mark_candidates`), extended to carry the mark kind without changing `scan`'s dedup key; counted per kind, `clarify` then `unknown`.

## C8 — tiers — answered

**Asked:** 2026-10-15 — groom/intake

**Question:** Which specs tiers feed ideas, records and marks?

**Answer:** Default (autonomous run): the project tier only. The core tier is booping's shipped rules and the global tier is the person's — neither is this project's state.

## C9 — output content — answered

**Asked:** 2026-10-15 — groom/intake

**Question:** Rule/0010 asks for the exact output content now.

**Answer:** Default (autonomous run): locked in `index.md`'s I/O contract — one line per section in the short report, an H2 plus a markdown table per section in detail, `none` for an empty section, exit 0 whenever the vault is readable, `error: …` exit 1 with no project.

## C10 — scope boundary — answered

**Asked:** 2026-10-15 — groom/intake

**Question:** What of the project-manager request lands here?

**Answer:** Default (autonomous run): only the command, its shared helpers, its e2e cases and its docs entries (CLAUDE.md, documentation). Out: the runs section and the run registry (part 3), any playbook calling `booping status` (part 4), project-manager docs and setup linking (part 5) — so no playbook source changes and no snapshot drift.
