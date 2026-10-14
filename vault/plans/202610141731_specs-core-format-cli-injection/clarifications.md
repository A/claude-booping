# Clarifications

## C1 — plan split — answered

**Asked:** 2026-10-14 — draft-plan

**Question:** The full request estimated ~42 SP, past the 35 SP threshold. Keep the split — this plan ships the format, `core.specs` tier config and `booping specs check|ls|next` (34 SP); rule injection is parked as the sibling stub `plans/202610141732_specs-rule-injection/`?

**Options:**

- Split as drafted (default applied)
- One plan, all four items (~42 SP)

**Answer:** Split as drafted.

## C2 — workers editing vault/specs — answered

**Asked:** 2026-10-14 — draft-plan

**Question:** M01 has a worker move `vault/specs/schemas/` and the format half of `vault/specs/README.md` into `src/specs/`. Rule/0019 keeps workers out of the vault; the plan treats `vault/specs/` as booping's shipped core tier, i.e. plugin content. Is that exception right, or should the runner do M01's vault edits?

**Options:**

- Worker edits vault/specs as plugin content (default applied)
- Runner performs the vault/specs edits itself

**Answer:** Worker edits vault/specs as plugin content — the records are repo files; run state, plans and lessons stay the runner's.

## C3 — project tier namespace — answered

**Asked:** 2026-10-14 — draft-plan

**Question:** The project tier carries no namespace — no upper tier references a project record, and project refs are always un-namespaced. Should a project tier have a namespace of its own (e.g. the project name)?

**Options:**

- No project namespace (default applied)
- Project namespace = project name

**Answer:** No project namespace.

## C4 — sources base — answered

**Asked:** 2026-10-14 — draft-plan

**Question:** `sources` entries resolve against the tier's anchor: core → plugin root, global → `home_dir`, project → repo root; entries containing `://` are skipped. Booping's own records write `sources` repo-relative (`vault/…`, `playbooks/…`). Right base?

**Options:**

- Tier anchor as listed (default applied)
- Relative to the record's own directory, like body links

**Answer:** Tier anchor as listed.

## C5 — CLI output content — answered

**Asked:** 2026-10-14 — draft-plan

**Question:** Rule/0010 wants output content locked with the owner. The run locked it alone: `ls` = `{type}/{NNNN}  {status}  {summary}` (status `-` when absent, no padding); `next` = `{type}/{NNNN}`; `check` = `{path}:{line}  {level}  {check}  {message}` on stdout plus the stderr trailer `{n} record(s) checked: {e} error(s), {w} warning(s)`; message table and exit codes 0/1/2 in index.md's I/O contract. Confirm or amend.

**Answer:** Accepted as drafted; the owner may amend after the sprint (decided by the orchestrator on the owner's behalf).

## C6 — checks not ported — answered

**Asked:** 2026-10-14 — draft-plan

**Question:** Not ported from shatterlings in this plan: heading-anchor checks, ADR alternatives table ↔ `###` correspondence, conflict `resolved` ↔ `## Resolution`, `[clarify]`/`[unknown]` marker counts in `ls` and a `review` verb, `check {paths}`, `--format json`, tags, `stamp`, the PreToolUse hook. Any of these needed in this plan rather than as follow-ups?

**Options:**

- All follow-ups (default applied)
- Pull some into this plan — name which

**Answer:** All follow-ups.

## C7 — default tier — answered

**Asked:** 2026-10-14 — draft-plan

**Question:** Every verb takes `--tier core|global|project`, default `project`. In booping's own repo the project tier is `vault/specs/`, the same directory as the core tier. OK?

**Options:**

- Default project (default applied)
- Default: all tiers at once

**Answer:** Default project. Core stays booping's own vault/specs (dogfood, adr/0001); booping-repo-only rules carry no targets, so they never inject (see C11).

## C8 — missing global tier is a warning — answered

**Asked:** 2026-10-14 — draft-plan

**Question:** Besides an unknown namespace, a namespace whose tier directory does not exist on this machine (CI, a collaborator without the home dir) is also a `namespace` warning, not a `ref` error. Agree?

**Options:**

- Warning (default applied)
- Error

**Answer:** Warning.

## C9 — own record findings — answered

**Asked:** 2026-10-14 — draft-plan

**Question:** Booping's own `vault/specs/` records were never checked for links, refs or `sources`. The plan has the runner fix any such finding as vault work in Final Verification, never by weakening a check. Agree, or should failing records be listed for you to fix?

**Options:**

- Runner fixes them (default applied)
- Runner lists them, owner fixes

**Answer:** Runner fixes them.

## C10 — mdcheck version — answered

**Asked:** 2026-10-14 — research-web

**Question:** Local `mdcheck` is 0.1.0, crates.io's latest `markdown-checker` is 0.1.1 (shatterlings pins 0.1.1). The plan pins nothing and uses whatever `cargo install markdown-checker` yields. Pin 0.1.1 in docs/CI?

**Options:**

- No pin (default applied)
- Pin 0.1.1

**Answer:** Pin 0.1.1 in docs and CI, matching shatterlings.

## C11 — booping-specific rules in core (sibling plan) — answered

**Asked:** 2026-10-14 — draft-plan

**Question:** For the parked rule-injection plan: core-tier rules 0013 (snapshot baselines) and 0015 (review covers code only) are booping-repo specifics with `targets:`; once injection ships they reach every user's runs. Retarget, retire or move them to booping's project-only records before that plan lands?

**Answer:** Settled now: rule/0013 and rule/0015 lost their targets/brief (booping-repo practice, documented but never injected); rule/0012 is retired and lost them too. Remaining targeted core rules (0001, 0004, 0006-0010) describe how booping's core playbooks behave for every user and are meant to inject.

## C12 — lesson/rule duplicates (sibling plan) — answered

**Asked:** 2026-10-14 — draft-plan

**Question:** For the parked rule-injection plan: `vault/specs/rule/` 0006–0010, 0013, 0015 restate `vault/_lessons/` 0004–0007, 0010, 0013, 0015; with lessons kept in parallel both inject into booping's own runs. Accept the duplicate until the lessons migration, or drop the overlapping lessons when injection ships?

**Options:**

- Accept duplicates until the migration
- Drop overlapping lessons in the injection plan

**Answer:** Accept duplicates until the lessons migration.

## C13 — snapshot drift (sibling plan) — answered

**Asked:** 2026-10-14 — draft-plan

**Question:** For the parked rule-injection plan: hermetic renders keep the core tier, so core rules targeting core playbooks will appear in the committed reports and every rule edit drifts them. Accept that, or exclude the core tier from fixture renders?

**Options:**

- Accept the drift
- Exclude core rules from fixture renders

**Answer:** Accept the drift — the committed reports show what users get.
