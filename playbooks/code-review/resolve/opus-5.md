# Act on the verdict and close the run

The user's verdict is already recorded in the run's artifact under `## Verdict`, together with the findings as they were classified and the scope the run opened on. Act on it; the findings are never re-presented, re-grouped or re-classified here, and the verdict is never asked for again or re-litigated.

The order below is fixed: apply the dispositions, write `## Resolution`, close the run, report.

## Each finding's disposition

- **Approved, trivial** — a rename, a stale comment, a small local edit the proposed fix already spells out: apply it yourself with `Edit`.
- **Approved, non-trivial** — everything else, whatever its severity: delegate it. Never apply it yourself.
- **Rejected** — drop it. No argument, no counter-proposal, no reworked version of it.
- **Corrected** — where the user described a fix different from the proposed one, their words win: carry theirs into the edit or the briefing in place of the proposed fix.

Where the verdict genuinely leaves a finding's disposition open, ask in `## Questions:` rather than guess.

## Delegating a non-trivial fix

The step stays yours; only the code change goes out. Brief the worker agent the **Available Agents** table names for applying approved non-trivial fixes — one briefing per fix, or one per file when several land in the same file. Each briefing carries the finding with its anchor, severity and offending snippet, the fix to apply (the user's correction where they gave one), the files it touches, and the project's conventions the change must follow. Take back which files it changed and what it did, and fold that into the report — do not re-read the diff to verify it.

## Write the resolution

Once every disposition is applied, append `## Resolution` to the artifact — the ledger of what this step did, grouped the same way the closing report groups it, one line per finding with the files it touched and who applied it:

```markdown
## Resolution

**Applied here (2)**
- `src/auth/session.py:88` — NIT · `tmp` renamed to `refreshed_at`
- `src/auth/session.py:141` — NIT · stale comment above `_rotate()` dropped

**Delegated to `booping-developer` (2)**
- `src/auth/refresh.py:52` — BLOCKER · now `secrets.compare_digest` (lesson `0007_constant_time_compare`)
- `src/api/routes.py:210` — SUGGESTION · duplicated 401 branch extracted into `_unauthorized()`

**Dropped on the user's call (1)**
- `src/api/routes.py:33` — SUGGESTION · wider error envelope — the current shape stays
```

A group with no entries is left out.

## Close the run

From the vault root, passing the run's `--target`:

```
booping playbook-transition code-review done --target codereviews/{dir}/{ts}.md --workdir {vault}
```

The exit edge's hooks stamp `reviewed_at:`, append the artifact's path to the linked plan's `code_reviews:` list, and commit the vault. Nothing here hand-edits plan frontmatter, and nothing here commits — the repo's own changes stay uncommitted for the user.

## The closing report

Post it in chat, once, as the last thing the step does — the whole ledger, so the user sees what landed without re-reading the diff. Name the artifact, group by disposition, count each group, name the agent the delegated fixes went to, and close on the standing line that nothing in the repo was committed or pushed:

```markdown
## Review closed — `abc1234..HEAD` (plan `202608031402_token-refresh`)

Recorded in `codereviews/202608031402_token-refresh/202608041530.md`; the plan's `code_reviews:` list now points at it.
    ← second clause omitted when the run had no plan in scope

**Applied here (2 nits)**
- `src/auth/session.py:88` — NIT · `tmp` renamed to `refreshed_at` (checklist `python:naming`)
- `src/auth/session.py:141` — NIT · stale comment above `_rotate()` dropped

**Delegated to `booping-developer` (1 blocker, 1 suggestion)**
- `src/auth/refresh.py:52` — BLOCKER · token compared with `==`; now `secrets.compare_digest` (lesson `0007_constant_time_compare`)
- `src/api/routes.py:210` — SUGGESTION · duplicated 401 branch extracted into `_unauthorized()`

**Dropped on your call (1)**
- `src/api/routes.py:33` — SUGGESTION · wider error envelope — you kept the current shape
```

A group with no entries is left out. The run ends here: no plan status moves, and a second look after these fixes is a new run against the same plan, with its own artifact.

## Return format

One `[UPDATED]` line per repo file edited, annotated with the finding it closes and who applied it, plus the artifact; the ledger counts and the standing no-commit line in `## Notes:`; `## Questions:` only when an approved fix cannot be applied.

```markdown
## Changed:

- [UPDATED] src/auth/session.py — NIT `session.py:88` rename, `:141` comment (runner)
- [UPDATED] src/auth/refresh.py — BLOCKER `refresh.py:52` constant-time compare (booping-developer)
- [UPDATED] src/api/routes.py — SUGGESTION `routes.py:210` 401 branch extracted (booping-developer)
- [UPDATED] codereviews/202608031402_token-refresh/202608041530.md — `## Resolution`, closed at `done`

## Notes:

- 2 applied by the runner, 2 delegated to `booping-developer`, 1 dropped on the user's call
- the vault commit is the exit hook's; nothing in the repo was committed or pushed

## Questions:
```

## Replay

A replay that finds `## Resolution` already written re-fires nothing it does not need: a run still at `human-review` takes the transition alone, a run already at `done` is only re-reported, with the transition line reading `already at done — no transition taken`.
