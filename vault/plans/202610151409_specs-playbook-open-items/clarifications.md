# Clarifications

Autonomous groom run on 2026-10-15: the owner was unavailable, so every question below was settled by the run with the default marked "default applied". Each stays reviewable and amendable before develop starts ([value/0009](../../specs/value/0009-adjustable-control.md), [rule/0002](../../specs/rule/0002-unknown-is-marked.md)).

## C1 — split — answered

**Asked:** 2026-10-15 — intake

**Question:** The request holds four parts (specs playbook, open items, corrections, autonomy modes), together well past the 35 SP threshold. Where is the seam, and which slice is this plan?

**Options:**

- This plan: parts 1 + 2 — the specs playbook and open items. Parked: part 3 corrections, part 4 autonomy modes (default applied)
- This plan: part 1 alone; parts 2–4 parked
- One plan over the threshold

**Answer:** First option — default applied. The playbook's open-items scenario is useless without the open-items store, and part 4 (autonomy) is defined over that scenario, so 1 + 2 is the slice the rest builds on; part 3 (corrections) is independent and parked as its own stub. Each parked part is a stub in `index.md` `## Out of scope`, groomed in its own run.

## C2 — playbook shape — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** adr/0024 makes `specs` a guide. How many steps, and does its run keep state?

**Options:**

- One inline step `guide`, no run-state machine — the setup playbook's ephemeral shape (default applied)
- One step per scenario behind a route step
- A stateful run artifact per specs session

**Answer:** First option — default applied. A route step is the rejected alternative of adr/0024; a specs session has no artifact of its own to carry state (records and items are the outputs). The alignment guide is a lazy-linked doc, `docs/specs-alignment.md`, read only in the init and alignment scenarios (value/0002).

## C3 — where the open_item machine lives — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** adr/0025 asks for a state machine over open-item files. Where is it declared, and who moves it?

**Options:**

- `states.open_item` in `playbooks/specs/playbook.yaml`, `artifact: open-items/{instance}.md`, workdir the vault; only `booping specs open-items` moves it, calling the transition engine in-process (default applied)
- The CLI writes `status:` itself, no machine
- A separate `open-items` playbook owning only the machine

**Answer:** First option — default applied. `booping playbook-transition` stays the only writer of status (the CLI reuses its engine rather than shelling out); the global backlog-manage playbook's `task` machine, moved by its scripts with `--state task --instance BL-NNNN`, is the prior art. A playbook that exists only to hold a machine would be a second surface for one concern. Cost: the `specs` render shows a `## State` section its own run never uses — the preamble says so.

## C4 — config placement — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** Where do the open-items directory, file scaffold and index query live in config?

**Answer:** `core.specs.open_items` — default applied. The specs CLI, the specs playbook and the develop/groom hooks all read it, so by the placement rule it is shared and sits under `core.specs`, not `core.specs_playbook`. Keys: `dir: open-items`, `scaffold` (the scaffold tree for one item file), `index` (the query spec `list` renders).

## C5 — which sources file items, and how — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** adr/0025 names four sources: an ADR with a confirmation line, a specs sync, `specs check` findings and marks. Which are computed by code?

**Options:**

- Code: marks and check findings via `scan`; ADR confirmation extracted by `add --record adr/NNNN`, called by the guide after it writes an ADR; sync via `add --source sync` from the model's comparison (default applied)
- Code: `scan` also sweeps every accepted ADR with a confirmation line

**Answer:** First option — default applied. A sweep would file an item for every long-confirmed ADR (booping's own tier has 27), flooding the index with closed work; only the moment an ADR lands tells new from old, and that moment is the guide's. Recorded as a departure from value/0015 in `index.md`.

## C6 — item format and output content — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** rule/0010 asks the exact content of the item file and the CLI output to be locked now.

**Answer:** Locked in `index.md` `## Architecture` (item file) and `## I/O contract` (every verb's stdout) — default applied. Directions are adr/0025's four (`code-to-spec`, `spec-to-code`, `conflict`, `clarify`); marks and check findings map to `clarify` (the owner settles what is right). Titles truncate at 100 chars with `…`. Duplicate test for `scan`: `(source, record, title)` against items of every status, so a closed item is never refiled.

## C7 — how a plan closes its items — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** "closing the plan closes the item": which edges, and where does the plan link live?

**Answer:** Default applied. The link lives only on the item (`plan:`, vault-relative `plans/{dir}/index.md`) — value/0003, no list on the plan. groom's intake links the items a request names (`open-items plan`). One shared hook script, `playbooks/_scripts/open-items-follow-plan {done|open}`, runs `close --plan` on develop `→ done` and `reopen --plan` on develop `→ fail`, develop `→ cancelled` and groom `→ cancelled`; like the tracker scripts it absorbs the CLI's exit code and warns on stderr, because a hook failing after `status:` is written would abort with the plan advanced. Reconcile by hand with the same CLI.

## C8 — eval coverage — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** "Its evals per the repo's playbook conventions (smoke tier at least)". Which cases?

**Answer:** Default applied: one suite `playbooks/specs/guide/` with three smoke cases — (1) a fixture vault without a project tier: the reply offers init and the alignment guide and writes no record; (2) a fixture with a tier, asked to record a decision with a confirmation: an ADR passing its schema and an `open-items/OI-0001.md` are written, and the reply asks no "which action" question; (3) a fixture with items, asked what is open: the reply carries the index and writes nothing. `regress` tier left for a later optimizer pass.

## C9 — no story record, no seeding — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** Should this plan add a story record for the new surface, and seed booping's own vault with items?

**Answer:** No to both — default applied. Story records are the `docs` playbook's to keep current; a `scan` over booping's tier would commit dozens of items as a side effect of a feature plan. Both stay the owner's call after merge.
