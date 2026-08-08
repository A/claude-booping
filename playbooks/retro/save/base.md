# Save the retrospective

The approved draft arrives from `synthesize` exactly as the user approved it, together with the working set, its primary plan, and the per-plan goal verdicts. Write it as approved — no re-drafting, no new findings, no wording the user has not seen.

The order below is fixed: write the file, check its frontmatter covers the working set, advance the run, report.

## 1. Write the retrospective

{% from "_partials/timestamps.md" import slug_ts, human_ts -%}
One file per run, whatever the size of the working set: `retrospectives/{{ slug_ts }}_{kebab-title}.md` under the vault root, which is the run workdir. The title is the run's own, kebab-cased. Plans are never given a copy — they are linked by the `retro:` stamp the exit hook applies.

The approved draft goes in verbatim, under frontmatter carrying exactly these keys:

- `plan:` — the primary plan's vault-relative path.
- `plans:` — always a YAML list, even for a single plan; every entry a vault-relative path, the primary included.
- `title:` — the retrospective's title, the same one the slug is built from.
- `created:` — `{{ human_ts }}`.
- `goal_verdicts:` — those same plan paths mapped to the verdict the user gave at triage.

No `status:` and no `reviewed_at:` are written by hand: the exit transition bootstraps the one and stamps the other.

```yaml
---
plan: plans/20260728-09-15_playbook-run-state/index.md
plans:
  - plans/20260728-09-15_playbook-run-state/index.md
  - plans/20260729-11-40_playbook-reports/index.md
title: Playbook run state and reports
created: 2026-08-02 14:10
goal_verdicts:
  plans/20260728-09-15_playbook-run-state/index.md: success
  plans/20260729-11-40_playbook-reports/index.md: partial
---
```

## 2. Check the frontmatter against the working set

Before firing anything: every plan in the working set appears in `plans:`, and every entry in `plans:` has a verdict in `goal_verdicts:`. This is the exit edge's second gate, and it is checked against the file just written because the hook script reads both keys and aborts the transition on either gap.

## 3. Transition

Once the file is on disk, advance the run per the `## State` section — from the vault root, passing `--target retrospectives/{slug}.md` for the file just written. The exit edge's hooks stamp the `retro:` back-link and the goal verdict on every plan in the working set and commit the vault; nothing here hand-edits plan frontmatter.

## 4. Closing report

Post in chat: the retrospective's path, the plans covered with their verdicts, then a section per plan tabling the issues reported into the retro — each with its root cause and its action items — the issue and action-item counts, and the `/playbook learn` offer stated as a command the user may run. Offer it; never launch it.

```markdown
**Retrospective saved** — `retrospectives/202608021410_playbook-run-state.md`.

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

Next, if you want the lessons absorbed: `/playbook learn retrospectives/202608021410_playbook-run-state.md`
```

## Replay

A replay that finds the retrospective already written re-fires nothing it does not need: a run still at the entry status takes the transition alone, a run already past it is only re-reported, with the transition line reading `already at {status} — no transition taken`.
