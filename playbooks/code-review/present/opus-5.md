# Record the findings and collect the verdict

Put the findings `review` returned in front of the user and collect their verdict on them.

## What you receive

- the severity-classified findings — each with its file and line anchor, its severity, the offending snippet, the proposed fix, and the checklist item or lesson id it cites
- the confirmed review scope and the run's artifact path under `codereviews/`

Take the findings as they stand. Do not re-read the code, re-derive a finding, re-word a fix, or move a finding between severities — a lesson violation stays a `BLOCKER`. Nothing is judged here.

The order below is fixed: write the findings, advance the run, ask, record the verdict.

## 1. Write the findings

Append `## Findings` to the artifact, grouped by severity — `BLOCKER`, then `SUGGESTION`, then `NIT` — each group headed with its count, an empty group dropped entirely. One entry per finding: file and line, the offending snippet, the proposed fix, and the item or lesson it cites. This block is written once and posted verbatim in step 3 — the artifact and the chat post never diverge.

```markdown
## Findings

**BLOCKER (1)**
- `src/auth/refresh.py:52` — token compared with `==`: `if token == stored:` → `if secrets.compare_digest(token, stored):` — lesson `0007_constant_time_compare`

**SUGGESTION (2)**
- `src/api/routes.py:210` — the 401 branch is duplicated in three handlers; extract `_unauthorized()` — checklist `python:dry`
- `src/api/routes.py:33` — error envelope drops the request id — checklist `api:errors`

**NIT (2)**
- `src/auth/session.py:88` — `tmp` → `refreshed_at` — checklist `python:naming`
- `src/auth/session.py:141` — comment above `_rotate()` no longer matches the code
```

When `review` returned no findings, the section is written as `_No findings._`.

## 2. Advance the run — before the user is asked

Once `## Findings` is on disk, transition per the `## State` section, from the vault root, passing the run's `--target`. The verdict is asked for at `human-review`, never at `in-agent-review`.

## 3. Post and ask

Post the block from step 1 in chat, headed with the scope:

```markdown
## Review findings — `a1f3c02..HEAD` (plan `202608031402_token-refresh`)
```

Close on the ask — which of these should be applied — in prose, in the same message, never through `AskUserQuestion`. Then stop and wait. With no findings, say so and say there is nothing to rule on; the run still passes through here.

Where the project has registered an agent for presenting a review, hand the findings to that agent instead of posting them yourself and take the verdict back from it — what it does with them is carried by its own description, not by this step.

## 4. Record the verdict

Read the reply as chat text and carry it forward as the user gave it. Do not argue a rejection, do not re-open a finding they settled, and do not start fixing anything — `resolve` owns that. Ask a follow-up only where the reply leaves a finding genuinely unanswered.

Append `## Verdict` to the artifact — one line per finding, its disposition in the user's own terms, their correction quoted where they gave one:

```markdown
## Verdict

- `src/auth/refresh.py:52` — BLOCKER · approved
- `src/api/routes.py:210` — SUGGESTION · approved, "extract it but keep the log line"
- `src/api/routes.py:33` — SUGGESTION · dropped — the current envelope shape stays
- `src/auth/session.py:88` — NIT · approved
- `src/auth/session.py:141` — NIT · dropped
```

`resolve` acts on this section; nothing else in the artifact is touched here, and no plan frontmatter moves.
