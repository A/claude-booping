# Develop defaults

## D1 — develop/provision — 2026-10-15

**Asked:** Sprint branch name confirmation

**Default:** Stay on `feat/specs`, no new branch

**Why:** Owner's run prompt fixes the branch: run in the feat/specs worktree, never switch branches

**Artifact:** [index.md](index.md)

## D2 — develop/provision — 2026-10-15

**Asked:** Rule booping rule/0013 (snapshots accepted by user only) vs the run prompt's snapshot policy

**Default:** Follow the owner's standing permission for this feature (2026-10-14): `just snapshots-accept` only when every drifted hunk is a change the plan describes, each accepted report listed here; any other drift stops the run

**Why:** The owner's explicit instruction for this run narrows the rule; the plan's Decisions repeat the same permission

**Artifact:** [index.md](index.md)

## D3 — develop/develop-loop — 2026-10-16

**Asked:** One commit per milestone when a group's milestones share files

**Default:** One repo commit per milestone group (G1 = M01–M04 in 739b343), body naming each milestone

**Why:** M01–M04 edit the same `pages.py`, `index.py`, templates and goldens; splitting by hunk would invent intermediate states never tested

**Artifact:** [index.md](index.md)

## D4 — develop/develop-loop — 2026-10-16

**Asked:** Commit message format `{agent}: {plan title} {message}` vs vault rule/0022 (conventional commits with scope)

**Default:** Conventional subject `feat(specs): …`, worker and plan title in the body

**Why:** rule/0022 is an accepted project rule; the playbook format is kept in the body

**Artifact:** [index.md](index.md)

## D5 — develop/develop-loop — 2026-10-16

**Asked:** Worker deviations in G1 beyond the contract text

**Default:** Accepted: idle badge styled `--muted` on `--idle-bg` (mockup pair is 4.23:1, under the 4.5 floor the plan sets); seven extra `ui` label ids the templates need to have no hardcoded English; two `.noside` grid rules in `style.css` for site-index (M04)

**Why:** Each serves a DoD line of the same plan (contrast floor, no hardcoded strings, site-index on the shell); none adds scope

**Artifact:** [M03](milestones/M03-theme-and-icons/M03-theme-and-icons.md)

## D6 — develop/develop-loop — 2026-10-16

**Asked:** Fragment-only links on `404.html` under `<base href>` (skip link `#main`, sprite `<use href="#i-…">`) resolve against the base URL

**Default:** Left as C9 locks it; listed as an open issue for review

**Why:** C9 fixes the `<base href>` shape; the effect is limited to the 404 page (skip link may jump to the site root, icons may not render in some browsers); changing it would reopen a locked format

**Artifact:** [M09](milestones/M09-md-copies-and-404/M09-md-copies-and-404.md)

## D7 — develop/develop-loop — 2026-10-16

**Asked:** Worker readings of C9 in M08

**Default:** Accepted: a record without a summary ends right after its link in `llms.txt`; a record without a title has `title: null` in `index.json` and its stem in `llms.txt`; dates serialise `YYYY-MM-DD`

**Why:** C9 names no fallback for these cases; each keeps output deterministic and minimal

**Artifact:** [M08](milestones/M08-llms-and-index-json/M08-llms-and-index-json.md)

## D8 — develop/verify — 2026-10-16

**Asked:** Phone defects found by the Final Verification visual check after every milestone closed (crumbs misaligned and not last-level-only; drawer focus lands on the skip link)

**Default:** Fixed by a fresh worker against M04's contract, findings in M04's `feedback.md`, committed as a `fix(specs)` commit; `just ci` re-run once after the fix

**Why:** The milestone machine has no edge out of `done`; the plan's Final Verification gates the run's `done` edge, so the fix lands before wrap-up

**Artifact:** [M04](milestones/M04-page-shell/M04-page-shell.md)
