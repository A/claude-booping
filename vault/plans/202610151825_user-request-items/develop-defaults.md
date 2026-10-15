# Defaults

## D1 — develop/provision — 2026-10-15 18:43

**Asked:** Confirm the sprint branch name.

**Default:** `feat/specs`, the branch the worktree is on — no new branch created

**Why:** the owner's run instruction: run on branch feat/specs, never switch branches

**Artifact:** [index.md](index.md)

## D2 — develop/provision — 2026-10-15 18:43

**Asked:** Milestone groups for the briefings.

**Default:** one group G1 — M01-items-command-group, M02-request-items, M03-index-source-and-safe-ids, M04-consumers-and-docs (4+4+3+4 = 15 SP, at the 15 SP cap)

**Why:** greedy packing under the configured cap; contiguous in id order

**Artifact:** [index.md](index.md)

## D3 — develop/run — 2026-10-15 18:43

**Asked:** rule/0013 forbids a run accepting snapshot baselines; the owner's run instruction permits it for described drift.

**Default:** follow the owner's standing permission of 2026-10-14 for this feature (recorded in the plan's Departures): accept only drift every hunk of which the plan describes, listed below; stop on any other drift

**Why:** the owner's explicit instruction for this run overrides the rule; the departure is recorded in the plan

**Artifact:** [index.md](index.md)

## D4 — develop/develop-loop — 2026-10-15 18:55

**Asked:** The Final Verification expects title `Ship it.` for `printf 'Ship it.\n{{ x }}\n' | booping items add --text -`; the M02 contract and C5 derive the title as `truncate(first_sentence(text))`, which drops the closing punctuation and gives `Ship it`.

**Default:** keep the contract — the title is `Ship it`; the Final Verification item is judged passed on source, null direction and verbatim body, its full stop read as a plan slip

**Why:** C5 names the existing helpers; changing `first_sentence` would also change `confirmation_title` and scan's mark titles — a scope addition

**Artifact:** [index.md](index.md)

## D5 — develop/develop-loop — 2026-10-15 18:55

**Asked:** The plan's I/O contract says `booping items list` prints `null` in the direction column for request items; the shared query-table renderer prints `—` for every empty cell and no milestone asked to change it.

**Default:** leave `—` — request rows show `—` in the direction column, as every empty cell in every query table does

**Why:** changing the shared table renderer is outside every milestone's scope (no scope additions); the item file itself holds `direction: null`

**Artifact:** [index.md](index.md)

## D6 — develop/develop-loop — 2026-10-15 18:55

**Asked:** One commit per milestone, while M01, M02 and M03 changed the same files (`open_items.py`, `commands/items.py`, `src/config.yaml`, the items e2e corpus) in one briefing.

**Default:** M01–M03 land as one code commit `66d9a16` naming all three; M04 (prose) lands as its own commit `723c59b`

**Why:** staging is by path and the shared files cannot be split by milestone without interactive staging

**Artifact:** [index.md](index.md)

## D7 — develop/develop-loop — 2026-10-15 18:55

**Asked:** `just snapshots` drifted in `playbooks/groom/_reports/output.md` and `playbooks/specs/_reports/output.md`; accept?

**Default:** accepted with `just snapshots-accept`, committed with M04 in `723c59b`. groom — one hunk, intake's `booping specs open-items plan` → `booping items plan`; specs — the preamble's `open_item` mover, the five `open_item` machine `When` cells, and the guide's verb lines, each `booping specs open-items` → `booping items`. No `--text` hunk: the guide prompt never named `--body`. No other report drifted.

**Why:** every hunk is the command rename the plan's Snapshots decision describes; owner's standing permission of 2026-10-14 (D3)

**Artifact:** [index.md](index.md)
