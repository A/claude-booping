---
status: awaiting-spec-confirm
---

[← index](../../index.md)

# save

## Contract

- **Needs** —
  - the approved retrospective draft, exactly as it was approved — no re-drafting, no new
    findings, no wording the user has not seen
  - the retrospective's frontmatter shape: the primary plan, the plans list, the title, the
    date, and the per-plan verdicts
  - the working set and which plan in it is primary
  - where each plan in the working set lives in the vault, as a vault-relative path — both the
    plans list and the per-plan link are written in that form
  - the exit transition the run takes, and which stamps are the command's, which the hook
    script's
  - the handoff the run closes on: `/learn`, offered and never launched
- **Value** — the approved draft becomes the run's one written file and the whole working set
  is stamped against it. The retrospective is standalone —
  `retrospectives/{YYYYMMDDHHMM}_{kebab-title}.md` in the vault — and a multi-plan run writes it
  exactly once: every covered plan points at that one file, never at a copy. Everything else the
  step leaves behind is the transition's: the exit edge stamps `reviewed_at` on the approved
  file, then `close-working-set` stamps each plan's retro reference and goal verdict and commits.
  No plan `status:` moves and no plan frontmatter is hand-edited here; the run ends with a report
  that says what was written, what verdict each plan carries, and what the user may run next.
- **Output files** —
  - `[CREATED] retrospectives/{YYYYMMDDHHMM}_{kebab-title}.md` — the approved draft verbatim
    under frontmatter carrying `plan:` (the primary, `plans/{slug}/index.md`), `plans:` (always a
    YAML list, even for a single plan, same entry form), `title:`, `created:` (`YYYY-MM-DD`) and
    `goal_verdicts:` (a mapping from those same plan paths to `success` / `partial` / `fail`).
    Neither `status:` nor `reviewed_at:` is written here — `playbook-transition` writes the first
    and the exit edge's hook the second.
  - `[UPDATED] plans/{slug}/index.md`, one per plan in the working set — all of it written by
    `booping playbook-transition retro awaiting-learning --target retrospectives/{slug}.md`,
    never by hand: the command sets the **retrospective's** `status:`, and `close-working-set`
    then stamps `retro:` and `goal:` on every plan in the list. No plan `status:` is touched —
    they are already `done`. The "link" is that `retro:` stamp; no line is added to a plan body,
    since the run edits nothing but the retrospective.
  - the vault commit — also the script's; the step runs no commit of its own.
  - the closing report posted in chat — the retrospective's path, the plans covered and their
    verdicts, a section per plan tabling the issues reported into the retro with their root
    causes and action items, and the `/playbook learn {retrospective path}` offer stated as a
    command the user may run.
  - order is fixed: write the retrospective, confirm its `plans:` and `goal_verdicts:` cover the
    whole working set, fire the transition from the vault root, then report. A replay that finds
    the file already written re-fires nothing it does not need: a run at `awaiting-retro` takes
    the transition alone, a run already at `awaiting-learning` is only re-reported.
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

The hook script the exit edge names is the **shared** `playbooks/_scripts/close-working-set`,
which `learn` fires too; the per-playbook difference lives in the hook line's argv
(`--verdicts --prefix retro --stage retrospectives`). Its contract, restated from
[states](../../states.md) — executable, self-contained, standard library only, no shelling back
into `booping` (the vault carries no `.booping` marker), like groom's `_scripts/commit-plan`.
`booping playbook-transition` runs it with cwd and `BOOPING_WORKDIR` set to the vault root and
`BOOPING_ARTIFACT` set to the resolved retrospective. It reads `plans:` and `goal_verdicts:` out
of the artifact; under `--verdicts`, for every plan in `plans:` it stamps
`retro: retrospectives/{slug}.md` (the vault-relative artifact path) and `goal:` from that plan's
verdict. Retro passes no `--status`, so no plan status moves. It then commits the artifact and
every touched plan. A missing plan file, a plan missing from `goal_verdicts:`, or an artifact
without either key is an error, not a silent skip: it exits non-zero and the transition aborts.

## Example artifact

`retrospectives/202608021540_playbook-run-state.md`, as written (body abridged — it is the
approved draft, following the retrospective template's sections):

````markdown
---
title: Playbook run state & reports
plan: plans/20260728-09-15_playbook-run-state/index.md
plans:
  - plans/20260728-09-15_playbook-run-state/index.md
  - plans/20260729-11-40_playbook-reports/index.md
created: 2026-08-02
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

The transition, fired from the vault root once the file is on disk, and its report:

```
booping playbook-transition retro awaiting-learning --target retrospectives/202608021540_playbook-run-state.md

awaiting-retro → awaiting-learning
frontmatter: reviewed_at="20260802 15:40"
script close-working-set: retro/goal stamped on 2 plans; vault-commit: 7c4e910
```

The closing report posted in chat:

```markdown
**Retrospective saved** — `retrospectives/202608021540_playbook-run-state.md`.

| Plan | Verdict |
| ---- | ------- |
| `plans/20260728-09-15_playbook-run-state/index.md` | success |
| `plans/20260729-11-40_playbook-reports/index.md` | partial |

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

Next, if you want the lessons absorbed: `/playbook learn retrospectives/202608021540_playbook-run-state.md`
```

## Return Format

None — the step is runner-performed, so nothing is returned to the harness; the retrospective is
on disk, the transition report is the authoritative record of the stamps applied, and the closing
report above ends the run in the driving conversation.

A replay that finds the work already done posts the same report with the transition line reading
`already at awaiting-learning — no transition taken`.
