# Clarifications

Autonomous groom run on 2026-10-15: the owner was unavailable, so every question below was settled by the run with the default marked "default applied". Each stays reviewable and amendable before develop starts ([value/0009](../../specs/value/0009-adjustable-control.md), [rule/0002](../../specs/rule/0002-unknown-is-marked.md)).

## C1 — what is left, and what "a manager path" means — answered

**Asked:** 2026-10-15 — intake

**Question:** Parts 1–3 are done (plans 202610151409 and 202610151532); part 4 is the only parked stub. Part 4 says "a manager path honours it", and adr/0028 decides a core `project-manager` playbook. Does this plan build project-manager?

**Options:**

- No — the manager path here is the specs playbook's open-items scenario taking items through groom and develop (adr/0027's own confirmation line); project-manager stays its own request (default applied)
- Yes — build project-manager in this plan

**Answer:** First option — default applied. adr/0028 is a separate, high-complexity decision (item store, computed status, run registry, budget gates) not named in this request's parts; adr/0027's confirmation names only the specs playbook. project-manager will read the same config key when it is groomed.

## C2 — the key — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** Name, placement and validation of the mode key.

**Options:**

- `core.autonomy: supervised | autonomous`, directly under `core`, default `supervised` in `src/config.yaml`; any other value is an in-band STOP on every render surface (default applied)
- `core.autonomous: true | false`

**Answer:** First option — default applied. The request names the two values, so an enum is the honest shape; several playbooks read it (the driving protocol, specs, migrate, later project-manager), so the placement rule puts it directly under `core`. The config merge validates nothing, so a typo (`autonomus`) would silently fall back to supervised — the `core.tracker.driver` precedent makes an unknown name a hard stop instead, reported in band per [rule/0029](../../specs/rule/0029-failures-reported-in-band.md). The project context block shows the resolved mode on every skill load, so a human sees which mode a run started in ([value/0009](../../specs/value/0009-adjustable-control.md)).

## C3 — where gate behaviour switches — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** Each playbook's gate text, or one place?

**Options:**

- One place: the driving protocol `_playbook_driving.j2` renders its gate rule (step 5) and its questions rule from `core.autonomy`; no playbook's `review_gate` changes (default applied)
- A Jinja conditional in every `review_gate` (the migrate `auto_migrate` precedent)

**Answer:** First option — default applied. Every gate and every in-step question already passes through that one partial, so one conditional covers groom, develop, retro, migrate and every user playbook ([value/0003](../../specs/value/0003-single-source.md), [value/0015](../../specs/value/0015-deterministic-where-it-can-be.md) — the branch is chosen by code at render, not by the model). Autonomous: a gate is auto-confirmed — the receipt is still presented, the confirmation is logged as a default and stands for the user's approval any transition gate names (groom's "explicit user approval captured", develop's "the user confirmed the branch name"); a step question is settled with the step's recommended or first option and logged; a question the run would park (groom's `awaiting-clarification`) is settled the same way instead. Two things still stop in autonomous mode: a `**STOP — tell the user:**` notice, and migrate's uncommitted-work question (C6).

## C4 — where defaults are recorded — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** adr/0027 says autonomous runs record their defaults. Where, and written by what?

**Options:**

- A `defaults.md` sidecar beside the run artefact, written only by a new `booping defaults add` — the `booping correction add` precedent minus the transcript lookup (default applied)
- The agent appends to `clarifications.md` (groom) or `{playbook}-defaults.md` (others) by hand, as autonomous runs do today

**Answer:** First option — default applied. Numbering, the timestamp, the file seed and placement are computable, so they are code ([value/0015](../../specs/value/0015-deterministic-where-it-can-be.md)); one sidecar name for every playbook mirrors `corrections.md` and keeps what the agent did without review findable ([value/0009](../../specs/value/0009-adjustable-control.md), [value/0004](../../specs/value/0004-analysable-history.md)). A run with no artefact (specs, setup) does not call it and lists its defaults in its final report instead. `clarifications.md` keeps its one job — questions a supervised run parks.

## C5 — the specs open-items scenario — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** How does the open-items scenario know the mode, and what does autonomous do?

**Options:**

- The specs preamble renders `Autonomy: {mode}` from config; the scenario holds both branches as two short lines keyed on it. Autonomous: the picked ids — or, with none picked, every `open` item — go to `/playbook groom` and then `/playbook develop` on the plan groom readies, in the same session, without stopping; a groom that splits develops the first plan and reports the parked stubs (default applied)
- A Jinja conditional inside `guide/prompt.md`

**Answer:** First option — default applied. The eval harness feeds `prompt.md` to promptfoo raw, so a Jinja branch in the step body could only ever be tested in its supervised arm; a rendered preamble line keeps the value computed by code and lets a smoke fixture state the autonomous one. Supervised behaviour is unchanged: next is `/playbook groom` naming the ids, and that run stops at its plan review (adr/0027's confirmation line).

## C6 — migrate and a dirty branch — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** migrate's survey already asks to commit uncommitted work, but says it "never blocks", and the `core.auto_migrate` notice tells the driver to run migrate "without asking the user". What changes?

**Options:**

- survey names the current branch with the counts and notable paths, and always waits for the answer — neither `core.auto_migrate` nor `core.autonomy` answers it; a decline still proceeds. The auto-migrate notice says the uncommitted-work question is still asked (default applied)
- A hard stop on a dirty tree

**Answer:** First option — default applied. adr/0027: the state is "shown to the user and asked about in either mode" — asked, not refused. The notice is the one place that today licenses skipping it.

## C7 — locked output content — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** Exact text of every new user-facing line ([rule/0010](../../../specs/rule/0010-output-content-locked-in-grooming.md)).

**Answer:** Default applied — locked in `index.md` `## Output contract`: the project-context line, the invalid-mode STOP notice, the amended auto-migrate notice, the specs preamble line, the `defaults.md` entry and the `defaults add` I/O.

## C8 — split — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** Does part 4 fit one plan?

**Answer:** Yes — default applied. 18 SP, under the 35 SP threshold; no split, no parked siblings. `project-manager` (adr/0028) was never part of this request (C1).

## C9 — plan approval — answered

**Asked:** 2026-10-15 — present

**Question:** The plan is ready for development — approve, or say what to change?

**Answer:** Approved — default applied by the autonomous run (owner unavailable). Cross-review's five findings were folded in before present: `--set` validated with the final config (M01), the runner-only snapshot acceptance recorded in `## Risk register`, `--target` confined to the vault and values normalised to one line (M02), `{run artefact}` defined in the driving-protocol contract (M03). 18 SP, no split.
