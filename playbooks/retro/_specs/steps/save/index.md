---
status: awaiting-spec-confirm
---

[← index](../../index.md)

# save

## Contract

- **Needs** —
  - the approved retrospective draft, exactly as it was approved — no re-drafting, no new
    findings, no wording the user has not seen
  - the retrospective's frontmatter shape: the plans list, the date, the cross-plan goal
    summary, and the per-plan verdicts
  - the working set and which plan in it is primary
  - where each plan in the working set lives in the vault, as a vault-relative path — both the
    plans list and the per-plan link are written in that form
  - the exit transition the run takes, and which stamps are the command's, which the hook
    script's
  - the handoff the run closes on: `/learn`, offered and never launched
- **Value** — the approved draft becomes the run's one written file and the whole working set
  moves with it. The retrospective lands beside the plan it is about — `retro.md` in the
  primary plan's own directory — and a multi-plan run writes it exactly once: the siblings are
  linked to that one file, never given a copy of it. Everything else the step leaves behind is
  the transition's: the exit edge stamps `reviewed_at` on the approved file, then
  `close-working-set` stamps each plan's retro reference and goal verdict, moves the siblings
  to the status `/learn` claims, re-renders `sprints.md` and commits. No plan frontmatter is
  hand-edited here, and the run ends with a report that says what was written, where every plan
  now sits, and what the user may run next.
- **Output files** —
  - `[CREATED] plans/{primary-slug}/retro.md` — the approved draft verbatim under frontmatter
    carrying `plans:` (always a YAML list, even for a single plan, each entry
    `plans/{slug}/index.md`), `date:` (`YYYY-MM-DD`), `goal_summary:` (the cross-plan one-liner)
    and `goal_verdicts:` (a mapping from those same plan paths to `success` / `partial` /
    `fail`). `reviewed_at:` is not written here — the exit edge's hook stamps it.
  - `[UPDATED] plans/{slug}/index.md`, one per plan in the working set — all of it written by
    `booping playbook-transition retro awaiting-learning`, never by hand: the command sets the
    primary's `status:`, and `close-working-set` then stamps `retro:` and `goal:` on every plan
    in the list and `status: awaiting-learning` on each sibling. The sibling "link" is that
    `retro:` stamp — no line is added to a plan body, since the run edits nothing but the
    retrospective.
  - the vault commit and the re-rendered `sprints.md` — also the script's; the step runs no
    `booping vault-commit` and passes no `--also` of its own.
  - the closing report posted in chat — the retrospective's path, the plans covered and their
    verdicts, each plan's new status, a section per plan tabling the issues reported into the
    retro with their root causes and action items, and the `/learn {primary plan path}` offer
    stated as a command the user may run.
  - order is fixed: write `retro.md`, confirm its `plans:` and `goal_verdicts:` cover the whole
    working set, fire the transition from the workdir, then report. A replay that finds
    `retro.md` already written re-fires nothing it does not need: the plan at `awaiting-retro`
    takes the transition alone, the plan already at `awaiting-learning` is re-reported.
- **Harness return** — none: the step is runner-performed, so it runs in the driving
  conversation and returns no block. What it leaves behind is the written retrospective, the
  transition's own mutation report, and the closing chat report.
- **Review gate** —
  - none — the approval was taken at synthesize and the writes follow it; a cancel there means
    this step never runs
  - the exit edge's first gate (explicit approval of the draft) is a pre-condition the step is
    handed, not one it re-establishes; its second (the `plans:` list covers the working set and
    `goal_verdicts:` carries a verdict for each) is checked against the file just written,
    before the transition is fired, because the hook script reads both
- **Delegation** — inline: the runner performs the step in the main context — the draft is
  already in its context and the remaining work is one write, one command and one report.

The hook script the exit edge names, `_scripts/close-working-set`, does not exist yet: shipping
it belongs to this step's prompt and wrapper work. Its contract, restated from
[states](../../states.md) — executable, self-contained, standard library only, no shelling back
into `booping` (the vault carries no `.booping` marker), like groom's `_scripts/_plan_status.py`.
`booping playbook-transition` runs it with cwd and `BOOPING_WORKDIR` set to
`{vault}/plans/{primary-slug}`, from which it derives the primary slug (the workdir's name) and
the vault (two levels up). It reads `plans:` and `goal_verdicts:` out of the workdir's
`retro.md`; for every plan in `plans:` it stamps `retro: plans/{primary-slug}/retro.md` and
`goal:` from that plan's verdict; for every plan *other than* the primary it also sets
`status: awaiting-learning` — the primary's own `status:` is already written by the command
before the hooks run. It then re-renders the vault's `sprints.md` from plan frontmatter and
commits the touched plans plus `sprints.md`. A missing plan file, a plan missing from
`goal_verdicts:`, or a `retro.md` without either key is an error, not a silent skip: it exits
non-zero and the transition aborts.

## Example artifact

`plans/20260728-09-15_playbook-run-state/retro.md`, as written (body abridged — it is the
approved draft, following the retrospective template's sections):

````markdown
---
plans:
  - plans/20260728-09-15_playbook-run-state/index.md
  - plans/20260729-11-40_playbook-reports/index.md
date: 2026-08-02
goal_summary: Run state shipped and resumable; the reports recipe landed but drifted from the
  fixture vault it renders against.
goal_verdicts:
  plans/20260728-09-15_playbook-run-state/index.md: success
  plans/20260729-11-40_playbook-reports/index.md: partial
---

# Retrospective — Playbook run state & reports

## What went well

- `playbook-transition` was made the only writer of run state before any step consumed it, so
  the frontier never had two sources.
- ...

## What went wrong

### The migration landed in the same commit as the model change

**What happened**: M2 shipped the model change and its migration together; the failing
`just test` in session 3 was the first signal.

**Root cause**: the plan's task list never asked for a migration task, so the lesson that
covers this had nothing to fire against.

**Impact**: one rework cycle mid-sprint and a rewritten M2 task list.

## Lesson gaps

- `lessons/0007_migrations-before-code.md` — the rule is right, but it is written for the
  execution stage and this failed at planning.

## Action items & takeaways

| # | Type | Item | Owner | Status |
|---|------|------|-------|--------|
| 1 | Heuristic | When a plan touches a model, the plan must carry its own migration task | standing | Planned |
````

The transition, fired from the workdir once the file is on disk, and its report:

```
booping playbook-transition retro awaiting-learning

awaiting-retro → awaiting-learning
frontmatter retro.md: reviewed_at="20260802 15:40"
script close-working-set: retro/goal stamped on 2 plans; plans/20260729-11-40_playbook-reports/index.md → awaiting-learning; sprints.md: 14 plans; vault-commit: 7c4e910
```

The closing report posted in chat:

```markdown
**Retrospective saved** — `plans/20260728-09-15_playbook-run-state/retro.md`.

| Plan | Verdict | Status |
| ---- | ------- | ------ |
| `plans/20260728-09-15_playbook-run-state/index.md` | success | `awaiting-learning` |
| `plans/20260729-11-40_playbook-reports/index.md` | partial | `awaiting-learning` |

### `plans/20260728-09-15_playbook-run-state/index.md`

| # | Issue | Root cause | Action items |
| - | ----- | ---------- | ------------ |
| 1 | Migrations shipped with the code they support | Lesson filed execution-stage; nothing reads it while a plan is drafted | Re-file the lesson as planning-stage |
| 2 | Verify commands ran only at sprint end | Plan put Verify at sprint level, not per milestone | Heuristic: every milestone carries its own Verify lines |

### `plans/20260729-11-40_playbook-reports/index.md`

| # | Issue | Root cause | Action items |
| - | ----- | ---------- | ------------ |
| 3 | Reports drifted from the fixture vault | Recipe renders against a vault no test pins | Task: pin the fixture vault in CI |

3 issues carried, 2 action items. Both plans link to the one shared retrospective.

Next, if you want the lessons absorbed: `/learn plans/20260728-09-15_playbook-run-state/retro.md`
```

## Return Format

None — the step is runner-performed, so nothing is returned to the harness; the retrospective is
on disk, the transition report is the authoritative record of the plan moves, and the closing
report above ends the run in the driving conversation.

A replay that finds the work already done posts the same report with the transition line reading
`already at awaiting-learning — no transition taken`.
