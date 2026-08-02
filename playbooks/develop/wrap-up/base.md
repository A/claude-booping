# Close the sprint

Verify's report arrives as evidence: which guardrails ran, each verdict, and the plan's own
bookkeeping — every DoD checkbox and every milestone status. Take it as given. Wrap-up starts
only on a green verdict — a red one goes back to the runner for fixes and a verify re-run, never
here. Nothing here re-runs a command, re-reads the plan for completeness, or asks the user
anything: once wrap-up starts it closes without stopping.

The order below is fixed.

## 1. Documentation

Documentation only becomes wrong once the whole sprint has landed, so it is written once, here,
against the finished diff. Scope is the sprint's own diff — what the work made untrue or newly
needed: README sections, `docs/` pages, a CHANGELOG when the project keeps one, the repo's own
`CLAUDE.md` when the sprint changed a convention it states. Never a documentation pass of its
own, never a scope addition. When the sprint invalidated nothing, write nothing and say so in the
report.

## 2. Closing commit

One commit in the attached repo covering the documentation edits, message format
`{{ config.git.commit_message }}`. Skip it when there is nothing to commit — the milestone
commits already landed while the loop ran.

## 3. Transition

Once the closing commit exists (or there was nothing to commit), fire the exit edge:

```bash
booping playbook-transition develop awaiting-retro
```

The plan body is not edited here — no checkbox flipping, no milestone status writing, no new
sections. A replay that finds the plan already at `awaiting-retro` skips this and continues.

## 4. Vault commit

After the transition, so the commit carries the exit status:

```bash
booping vault-commit awaiting-retro {plan-path}
```

## 5. Sprint report

Post in chat: the branch, the milestones shipped, the guardrail verdict as verify reported it, the
documentation touched, the closing commit, the plan's new status. Close on the handoff line
`/retro {plan-path}` — the user runs it, nothing here does.

```markdown
**Sprint done — {plan title} ({total} SP), branch `{branch}`.**

| # | Milestone | SP | Status |
| - | --------- | -- | ------ |
| 1 | {milestone} | {sp} | done |

Guardrails: {verdict as reported} — {commands}; the plan's Final Verification passed alongside them.

Docs: {what was updated and where}; committed as `{message}`.

The plan is at `awaiting-retro`. Next: `/retro {plan-path}`.
```

A sprint that invalidated no documentation closes on the same shape, with the docs line reading
`Docs: nothing invalidated — no documentation changes were needed.` and no closing commit.

## Return format

```markdown
## Changed:

- [UPDATED] {documentation file} — {what changed}
- [UPDATED] plans/{slug}/index.md — in-progress → awaiting-retro
- repo commit: `{closing commit message}`

## Notes:

- docs: {what was updated and why, or that the sprint invalidated none}
- transition: {the transition report verbatim}
- vault-commit: {sha}
- handoff posted: `/retro {plan-path}`

## Questions:
```

The documentation lines are omitted when the sprint invalidated none, and the `repo commit:` line
then reads `repo commit: none — no documentation changes to commit`. The plan line is always
present. `## Questions:` is always empty — the run is over and nothing is open.
