---
status: awaiting-prompt-confirm
reviewed_at: 20260804 17:46
fixtures_reviewed_at: 20260804 17:46
---

# scope

[← index](../../index.md)

## Contract

- **Needs** —
  - whether this session just delivered a plan, and which — its path, title and `commit:`
    baseline
  - the vault's plans sitting at the configured code-review status
    (`config.skills.code-review.status`, today `awaiting-retro`), with their titles, SP and
    `commit:` baselines
  - the repo's recent commit history, its current branch, and whether the working tree carries
    uncommitted work
  - the user's answer naming the scope — one of the offered candidates, or free text
- **Value** — the target settled before a token is spent on reviewing it. Every candidate rides
  one `AskUserQuestion` call — the plan `develop` just delivered, the latest coherent piece of
  work read off the commit history, the plans queued at the review status, and a free-text
  route — so the user names the right scope outright instead of rejecting a wrong default first.
  What "the latest coherent piece of work" is stays model judgement over `git log --oneline`
  (the latest plan delivery on this branch, a feature's worth of commits, whatever the commits
  actually suggest), never a hardcoded commit count. The answer is then resolved into a concrete
  diff range or file list and surfaced back in the same turn, so a wrong base is caught here and
  not after the detached review has burned on it.
- **Output files** —
  - none — the confirmed scope (a diff range or file list, plus the plan behind it when there is
    one) is carried in conversation
  - nothing is written to the vault or the repo, and no plan-lifecycle status moves in either
    direction
- **Harness return** — none: the step is runner-performed, so it runs in the driving
  conversation and returns no block. What it leaves behind is the scope report in chat and the
  facts `review` reads out of it — the diff range or file list, the branch, and the plan in
  scope with its path when there is one.
- **Review gate** —
  - none — the scope question is asked in-step and the resolved target reported back in the same
    turn
  - a chosen plan carrying no `commit:` baseline yields no diff range: say so and re-ask inside
    the same step — another plan, or an explicit range or file list through the free-text route
- **Delegation** — inline: the runner performs the step in the main context. The reads are cheap
  (`git log --oneline`, `git status`, the plans already in context) and each one feeds a
  judgement the runner has to make itself; nothing here is bulk enough to delegate.

## Example artifact

The single `AskUserQuestion` call, every candidate on it:

```markdown
"What should this review cover?" — single-select, free-text route always on

| Option | Description |
| --- | --- |
| This sprint's plan | `20260803-14-20_playbook-lessons-injection` — delivered by develop earlier in this session; baseline `a1f3c02` |
| Latest work on this branch | 7 commits on `feat/playbook-lessons` since it left `main` — one feature's worth |
| Plan awaiting review | `20260731-09-05_scaffold-subcommand` — `awaiting-retro`, baseline `d40b7e1` |
| Other | free text — a diff range, a file list, or the working tree |
```

Posted in chat once the answer resolves, the `## Review scope` report:

```markdown
## Review scope

`plans/20260803-14-20_playbook-lessons-injection/index.md` — the plan this session's develop run
delivered. Baseline `a1f3c02`.

Diff range `a1f3c02..HEAD` on `feat/playbook-lessons` — 7 commits, 9 files changed, +412/−96.

| Changed file | +/− |
| --- | --- |
| `booping-python/src/booping/context/lesson.py` | +118/−4 |
| `booping-python/src/booping/commands/render_playbook.py` | +64/−12 |
| `src/templates/_partials/_playbook_lessons.j2` | +21/−0 |
| … 6 more |

Working tree is clean — nothing uncommitted sits outside the range.
```

## Return Format

None — the step is runner-performed, so nothing is returned to the harness; the report above is
posted in chat and the run continues in the same conversation.

The baseline-less plan is the one shape worth pinning, posted in place of the report and
followed by a re-ask in the same turn:

```markdown
`plans/20260614-11-30_vault-local-path/index.md` has no `commit:` baseline, so there is no diff
range to review it from. Pick another plan, or give me an explicit range or file list.
```

No scope is fixed until the re-ask lands, and nothing downstream runs before it.
