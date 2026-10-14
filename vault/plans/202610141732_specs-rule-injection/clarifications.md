# Clarifications

Autonomous groom run on 2026-10-14: the owner was unavailable, so every question below was settled by the run with the default marked "default applied". Each stays reviewable and amendable before develop starts ([value/0009](../../specs/value/0009-adjustable-control.md), [rule/0002](../../specs/rule/0002-unknown-is-marked.md)). The parent plan's C11–C13 bind this plan and are not repeated.

## C1 — injected rule line content — answered

**Asked:** 2026-10-14 — draft-plan

**Question:** Rule/0010 wants the exact content of a user-facing output locked in grooming. Shape of the injected section on every surface: an H2 `## Rules`, then the count sentence `The following {n} rule(s) apply to this {playbook|step|agent|skill}. Never silently violate one{; conflict → stop and flag — playbook surface only}. Read a rule's record when its brief is not enough.`, then one bullet per rule `- **{title}** — {brief} [{ref}]({link})`, the brief's whitespace collapsed to one line and never Jinja-rendered. Confirm or amend.

**Options:**

- Shape as written (default applied)
- A `### {ref} — {title}` heading per rule, like lessons

**Answer:** Shape as written — default applied. One line per rule keeps the section compact ([value/0002](../../specs/value/0002-minimal-effective-context.md)); the count sentence mirrors the lessons section so both read alike.

## C2 — link and ref form per tier — answered

**Asked:** 2026-10-14 — draft-plan

**Question:** `{ref}` is namespaced as specs refs are: core `booping:rule/NNNN`, global `{namespace}:rule/NNNN`, project `rule/NNNN`. `{link}` is core `${CLAUDE_PLUGIN_ROOT}/{path from plugin root}` (the review-template precedent, reproducible across machines), global the absolute path, project the path relative to the repo root. Right forms?

**Options:**

- As written (default applied)
- Absolute paths for every tier

**Answer:** As written — default applied. Hermetic renders keep core and project and drop global, so only the two machine-independent forms ever reach a committed report ([rule/0027](../../specs/rule/0027-renders-reproducible.md)).

## C3 — core and project tier on one directory — answered

**Asked:** 2026-10-14 — draft-plan

**Question:** In booping's own repo the core and project tiers both resolve to `vault/specs/`. Records are deduplicated by the record file's realpath, the first tier in core → global → project order winning, so a rule injects once with its `booping:` ref. A dev checkout whose plugin root is a different directory from the repo (an installed plugin next to a worktree) still injects both copies. Acceptable?

**Options:**

- Realpath dedupe, first tier wins (default applied)
- Dedupe by ref number across tiers

**Answer:** Realpath dedupe, first tier wins — default applied. Number-based dedupe would silently drop a different tier's own rule that happens to share a number.

## C4 — placement — answered

**Asked:** 2026-10-14 — draft-plan

**Question:** On every surface the `## Rules` section sits immediately before the `## Lessons` section, at the position lessons take when there are none. Agree?

**Options:**

- Directly before Lessons (default applied)
- Directly after Lessons

**Answer:** Directly before Lessons — default applied.

## C5 — opt-out flag — answered

**Asked:** 2026-10-14 — draft-plan

**Question:** `render-playbook` gets a separate `--no-rules` flag, symmetric to `--no-lessons`; `--no-lessons` stays as it is. Nothing in the repo passes `--no-lessons` today. Agree, or should one flag cover both?

**Options:**

- Separate `--no-rules` (default applied)
- `--no-lessons` strips rules too

**Answer:** Separate `--no-rules` — default applied. The request keeps lessons unchanged.

## C6 — notices for rules — answered

**Asked:** 2026-10-14 — draft-plan

**Question:** On the `render-playbook` surfaces, a rule that cannot be injected (frontmatter error, `targets:` without `brief:` or an unparseable target) and a rule targeting a step the rendered playbook does not have each become a non-blocking `**Note — tell the user:**` naming the record path and pointing at `booping specs check`. An untargeted rule is legitimate and raises nothing. Agent and skill surfaces stay silent, as they do for lessons. Agree?

**Options:**

- As written (default applied)
- No notices for rules

**Answer:** As written — default applied ([rule/0029](../../specs/rule/0029-failures-reported-in-band.md)).

## C7 — size against the stub's estimate — answered

**Asked:** 2026-10-14 — draft-plan

**Question:** The stub estimated ~11 SP; the plan as drafted is 23 SP across four milestones, mostly e2e cases for each surface and the docs pass. Still under the 35 SP threshold, so no split. Agree?

**Options:**

- One plan at 23 SP (default applied)
- Trim scope — name what

**Answer:** One plan at 23 SP — default applied.

## C8 — rule/0001 and lessons in parallel — answered

**Asked:** 2026-10-14 — draft-plan

**Question:** Rule/0001 (targeted at `learn`) says a taken lesson is written as a rule, never as a lesson file, while `learn` still writes lessons. Once this plan ships, rule/0001's brief reaches `learn` and contradicts its step bodies. Change `learn` here, or leave it to the lessons migration?

**Options:**

- Leave learn to the lessons migration (default applied)
- Retarget rule/0001 off `learn` until then

**Answer:** Leave learn to the lessons migration — default applied. Parent C11 keeps rule/0001 targeted on purpose and C12 accepts the overlap until that migration; the conflict note of the playbook surface ("conflict → stop and flag") makes the contradiction visible instead of silent. [clarify] Retargeting rule/0001 is a one-line change if the owner prefers learn quiet until the migration.

## C9 — baselines this plan moves — answered

**Asked:** 2026-10-14 — draft-plan

**Question:** Core rules inject into the hermetic renders (parent C13), so the committed reports of `groom`, `develop` and `learn` drift, and any e2e case rendering a core playbook may too. Workers rebaseline the e2e cases they move with `--txtar-update` and list them; the committed `_reports/` are never written by a run — the runner shows `just snapshots` drift to the owner, who accepts it ([rule/0013](../../specs/rule/0013-snapshot-baselines-accepted-by-user.md)). Agree?

**Options:**

- As written (default applied)

**Answer:** As written — default applied.
