---
{}
---

[← index](../../index.md)

# interview — Tests

## Fixtures

| Fixture              | Requirements                                                                       |
| -------------------- | ---------------------------------------------------------------------------------- |
| complete-description | prose description of a release-notes playbook; slug, goal, done-state, home stated |

## Tests

| Fixture              | Tier    | Title          | Check logic                                                                                           |
| -------------------- | ------- | -------------- | ----------------------------------------------------------------------------------------------------- |
| complete-description | smoke   | SECTIONS       | Goal, Success result, Artifact home present; Wishes optional                                          |
| complete-description | smoke   | ONE-PARA       | Goal and Success result are exactly one paragraph each                                                |
| complete-description | smoke   | HOME-PATH-ONLY | Artifact home body is a single path, nothing else                                                     |
| complete-description | smoke   | WISHES-LIST    | Wishes, when present, is a bullet list only                                                           |
| complete-description | smoke   | SLUG-PATH      | brief written at `release-notes/_specs/brief.md` — the slug the description names                     |
| complete-description | smoke   | HOME-VALUE     | Artifact home is `releases/_work/` — the path the description names                                   |
| complete-description | smoke   | NO-QUESTIONS   | the return's Questions section is empty — the input answers everything                                |
| complete-description | regress | GOAL-REFLECTS  | Goal restates the description's ask (draft release notes from merged PRs); no scope absent from input |
| complete-description | regress | WISHES-COVER   | Wishes include sign-off-before-commit and house-style, both stated in the description                 |
