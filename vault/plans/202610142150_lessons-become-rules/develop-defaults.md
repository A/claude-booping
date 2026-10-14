# Develop defaults

Autonomous develop run on 2026-10-14: the owner was unavailable, so every point below was settled by the run. Each stays reviewable ([value/0009](../../specs/value/0009-adjustable-control.md)).

## D1 — branch

The owner fixed the branch for this run: `feat/specs`, the worktree's current branch, reused as is. No branch created, no `AskUserQuestion` (provision's branch gate auto-confirmed by the owner's instruction).

## D2 — milestone groups

Group ceiling is 1 → seven briefings, one per milestone, in id order (M01 … M07).

## D3 — snapshot acceptance overrides rule/0013 for this run

[rule/0013](../../specs/rule/0013-snapshot-baselines-accepted-by-user.md) and lesson 0013 forbid `just snapshots-accept` from inside a run. The owner's standing permission for this feature (2026-10-14) overrides it for this run only: accept only when every drifted hunk is a change the plan describes; any other drift stops the run. Accepted reports are listed under `## Accepted reports` at the end.

## D4 — commit message format

The develop playbook's `<agent>: <plan title> <message>` contradicts [rule/0022](../../specs/rule/0022-conventional-commits-with-scope.md) (conventional commits with scope) and every non-run commit on this branch. Milestone commits use `type(scope): …`, the building worker named in the body.

## D5 — M01 touched `justfile`

The M01 Verify `just e2e -k "specs and init"` could not run: the recipe interpolated `{{ args }}` unquoted, splitting the `-k` expression. The worker switched the recipe to `[positional-arguments]` + `"$@"`. Outside the contract's file list but required for its own Verify; kept, committed with M01.

## D6 — M02 DoD 2.2 read as scoped to M02's files

DoD 2.2 asks the full `render-playbook learn` to name no `_lessons/` destination, but the remaining mentions sit in the Dedup Sweep and Write bodies that M03 and M04 rewrite. Closed M02 on its own files (preamble, `## Targets`, Extract Candidates clean); the whole-render assertion is carried by the plan's Final Verification after M04.

## D7 — rule/0001 commits with the code

`vault/specs/` is this repo's project specs tier, which [adr/0001](../../specs/adr/0001-specs-tiers.md) puts in the same commit as the code it governs. M04's rule/0001 edit is committed in the milestone commit, not the vault bookkeeping commit.

## D8 — C5's plain-text source contradicts the rule schema

C5 writes `## Follows from` as plain text `retrospectives/{slug}.md` when the vault is outside the repo, but `src/specs/schemas/rule.yaml` requires a link in every item, so such a record fails `booping specs check`. The check is not weakened. Default: vault outside the repo → link a project-tier value when one fits; otherwise one item opening with `[clarify]`, naming the retrospective in plain text and linking the tier README, so the owner settles the source. [clarify] the owner may prefer a schema change (allow an unlinked source item) instead.

