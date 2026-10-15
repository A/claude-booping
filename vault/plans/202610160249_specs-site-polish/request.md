# Request

> Request — specs site polish after parts 1-3 (read the brief's "Found after part 1/2" sections in /tmp/claude-1000/-home-anton-Dev--A-hermes-pet/36dbf90d-0102-4f43-add1-4a69775c2e2f/scratchpad/site/brief.md and compare with the approved prototype specs-site-mockup.html beside it): the home page becomes the landing the prototype shows (lead line, one "N need you →" link, scenario cards with a quiet count, recently updated; marks only in the review filter), the record body is capped at ~68-70ch, relations align with the facts grid. Render booping's own vault and a Russian fixture, screenshot desktop 1300 and phone 390 with chromium, and compare with the prototype before closing.
>
> AUTONOMOUS RUN. The owner is not available: do not ask questions and do not wait at review gates — auto-confirm them yourself; settle unclear points with a sensible default and record every default in the plan's clarifications.md (groom) or a develop-defaults.md beside the plan (develop). You run in the worktree /home/anton/Dev/@A/claude-booping-specs on branch feat/specs: never switch branches, never push, stage by path (never git add -A). Read vault/specs (value/, rule/, adr/0001) and src/specs/README.md before deciding anything; a choice that contradicts a value or rule is wrong. Snapshot policy for this run (owner's standing permission for this feature, 2026-10-14): when `just snapshots` drifts, you may run `just snapshots-accept` only if every drifted hunk is a change the plan describes; list each accepted report and why in the run's defaults file. Any other drift: stop and report. A red `just ci` is fixed by a worker, never by weakening a check. If a groom splits the request, groom only the first plan and list the rest as parked stubs. Speed: while working a milestone run only the tests that cover it; run the full just ci once at the end, in the foreground, and do not end the run before it returns. Do not end the run while a check is still running: wait for just ci to finish and report its result. End at ready-for-dev.

## Task type

`feature` — the change adds user-visible layout behaviour the approved prototype specifies and parts 1–3 did not deliver (a reading measure on home and record pages, relations as rows of the facts grid, a callout that names its breakdown). Not `bug`: no shipped DoD is contradicted — parts 1–3 closed `done` against their own DoDs, and there is no defect to reproduce or root-cause, only a remaining gap to the prototype. Not `refactoring`: the rendered pages change for the reader, so the no-behaviour-change test fails.

## Problem

Rendered today (`bin/booping specs site` over booping's vault, Chromium 1300 and 390): the home page already carries the lead line, one "N need you →" link, scenario cards with a count and Recently updated, and no mark list — but its lead, callout and Recently updated run the full ~990px content width instead of the prototype's 68ch column, the callout says "115 need you → · 12 open questions" without naming the unreviewed part, the sidebar tag tree renders every tag in monospace chips including tags with 0 records, and on the phone a Recently-updated title is squeezed between the ref and the date into a 4-word column. A record page's reading column runs ~78ch (no measure is applied, `.measure` exists in CSS but no template uses it), and its relations (Rules, Serves values) sit in a separate `<dl>` below the facts box, with label and value columns offset from the facts grid. The prototype puts every record element in one 68ch column and the relations ("Служит ценностям") as rows of the facts `<dl>`.

## Clarifications and Decisions

- Autonomous run: every call below is a default recorded in `clarifications.md` (C1–C6), answered by the run.
- Measure: the existing `.measure` token, 68ch, on home lead/callout/recent and on the whole record column (C1).
- Facts and relations: relations become rows of the facts `<dl>` inside the 68ch column, as in the prototype; the extra raw-frontmatter box stays a separate box (C2).
- Callout line: "{n} need you →" link followed by "· {u} unreviewed · {q} open questions", zero parts omitted, exact en/ru strings locked (C3).
- Sidebar tags: plain text, not code; tags with 0 records hidden from the sidebar, kept on the tag tree page (C4).
- Phone Recently updated: date moves under the title below 760px (C5).
- Russian visual check: the swarmlight vault from the brief's scratchpad rendered from a temp project whose vault config sets `core.specs.site.lang: ru` (C6).
