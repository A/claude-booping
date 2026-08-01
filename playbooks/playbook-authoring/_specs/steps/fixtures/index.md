---
status: spec-ing
---

# fixtures

[← index](../../index.md)

## Contract

- **Needs** — the target step name; the target step's confirmed contract and example; the
  step's confirmed test plan; answers to any previously returned questions.
- **Value** — the ground every check stands on: real files materializing exactly what the
  confirmed tests file describes — its `## Fixtures` table says what each contains, its test
  rows say what each is for; no fixture a test doesn't use, no test naming a fixture that
  doesn't exist. A wrong corpus makes every check either vacuous or flaky.
- **Output files** — `[CREATED|UPDATED] <name>/<step>/_fixtures/*` — one file per fixture the
  rows name. A fixture set mirrors the artifacts the step would actually receive from its
  upstream steps — separate compact files, together one realistic input state. A trap fixture
  carries exactly the flaw its row provokes, nothing else.
- **Harness return** — `## Changed:` list and `## Questions:` — only when a row's fixture is
  ambiguous to materialize (which flaw, how realistic, what scale); empty otherwise.
- **Review gate** — the user reads the fixture files themselves and confirms the set.

## Example artifact

For a step whose task is "write the user story for the auth feature", the success set is the
upstream artifacts it would really receive — the confirmed features index plus the side doc
that exists about that feature:

`_fixtures/features-index.md`

```markdown
# Features

| # | Feature                    | Priority |
| - | -------------------------- | -------- |
| 1 | Auth — email + OAuth login | P0       |
| 2 | Billing — subscriptions    | P1       |
| 3 | Search — full-text         | P2       |
```

`_fixtures/auth-notes.md`

```markdown
# Auth — working notes

OAuth via Google only for v1; magic links instead of passwords.
Sessions live 30 days, silent refresh.
Enterprise SSO explicitly out of scope until Q3.
```

## Return Format

```markdown
## Changed:
- [CREATED] user-stories/story/_fixtures/features-index.md
- [CREATED] user-stories/story/_fixtures/auth-notes.md

## Questions:
1. Row "conflicting sources" — should the index contradict the notes on the OAuth provider,
   or on the session length? Pick one, the trap stays single-flaw.
```
