---
type: runbook
title: Run the eval suites and read the PR comment
summary: Evals run locally on subscription auth via just smoke/regress/eval; results land as one sticky advisory PR comment, never a gate.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: live
sources: [justfile, scripts/eval-run.sh, scripts/eval-pr-comment.sh, scripts/report-pr.jq, playbooks/_lib/claude_provider.py, .github/workflows/ci.yml]
---

## When

A change touches a playbook step that has an eval suite (`promptfooconfig.yaml` beside
its `prompt.md`), or a PR wants evidence of how the steps behave. CI never runs evals.

## Before you start

- Claude Code is logged in on a subscription: the provider runs `claude -p` and strips
  `ANTHROPIC_API_KEY` from its environment so nothing is billed to an API key.
- `npx` and `gh` are on the path, and the branch has an open PR if the result should be
  posted; without one the report prints to stdout.

## Steps

1. List the suites with `just suites`.
2. Run the deterministic tier first: `just smoke <playbook>/<step>`, or `just smoke all`.
   It makes no judge calls.
3. Run the judged tier when the smoke tier is clean: `just regress <playbook>/<step>`. It
   costs judge calls; `just eval` runs both tiers, `just eval-md` also renders a local
   markdown report.
4. To keep a run off the PR, prefix it with `EVAL_PR=0`.
5. Read the PR comment: one fenced block whose header names the tier, branch, head SHA
   and recipe, then the tally, then one section per suite — failing suites first — with a
   `PASS`/`FAIL` line per case and each failing check nested under it, named by its
   `MDCHECK:` / `FILES:` / `RETURN:` tag or assertion type.
6. Treat a judged-tier failure as a lead, not a verdict: the suites judge freshly
   generated artefacts, so a full run lands on a different red set each time. Re-run the
   one suite before acting on a single red case.

## Check

- The PR has one comment starting with `<!-- booping-eval -->`, and its
  `<!-- sha: … -->` line matches the head commit; a later push makes it stale, and a
  re-run edits the same comment in place.
- [unknown] `scripts/eval-pr-comment.sh` says an `evals` CI gate greps the marker line,
  but `.github/workflows/ci.yml` has no eval job and the justfile calls the comment
  advisory; which is meant is not confirmed.
