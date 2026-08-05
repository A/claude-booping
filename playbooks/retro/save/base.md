# Save the retrospective

The approved draft arrives from `synthesize` exactly as the user approved it, together with the
working set and its primary plan, and the per-plan goal verdicts. Write it as approved — no
re-drafting, no new findings, no wording the user has not seen.

The order below is fixed: write the file, check its frontmatter covers the working set, fire the
transition from the workdir, report.

## 1. Write `retro.md`

One file per run, whatever the size of the working set: `retro.md` in the primary plan's own
directory, which is the run workdir. Siblings are never given a copy — they are linked by the
`retro:` stamp the exit hook applies.

The approved draft goes in verbatim, under frontmatter carrying the plans list, the date, the
cross-plan goal summary and the per-plan verdicts. `plans:` is always a YAML list, even for a
single plan, and every entry is a vault-relative path; `goal_verdicts:` maps those same paths to
the verdict the user gave at triage. `reviewed_at:` is not written here — the exit edge stamps it.

```yaml
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
```

## 2. Check the frontmatter against the working set

Before firing anything: every plan in the working set appears in `plans:`, and every entry in
`plans:` has a verdict in `goal_verdicts:`. This is the exit edge's second gate, and it is checked
against the file just written because the hook script reads both keys and aborts the transition on
either gap.

## 3. Transition

Fired from the workdir, once `retro.md` is on disk:

```bash
booping playbook-transition retro awaiting-learning
```

The command writes the primary plan's `status:`, stamps `reviewed_at` on `retro.md`, then runs
`close-working-set`, which stamps `retro:` and `goal:` on every plan in the list, moves each
sibling to `awaiting-learning` and commits. Nothing here hand-edits plan frontmatter, runs
`booping vault-commit`, or passes an `--also` of its own.

```
awaiting-retro → awaiting-learning
frontmatter retro.md: reviewed_at="20260802 15:40"
script close-working-set: ok
```

That report is authoritative — do not re-read the plans to verify the moves.

## 4. Closing report

Post in chat: the retrospective's path, the plans covered with their verdicts and new statuses,
then a section per plan tabling the issues reported into the retro — each with its root cause and
its action items — the issue and action-item counts, and the `/learn` offer stated as a command
the user may run. Offer it; never launch it.

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

## Replay

A replay that finds `retro.md` already written re-fires nothing it does not need: a plan still at
`awaiting-retro` takes the transition alone, a plan already at `awaiting-learning` is only
re-reported, with the transition line reading `already at awaiting-learning — no transition taken`.