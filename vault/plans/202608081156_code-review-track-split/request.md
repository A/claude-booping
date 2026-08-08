# Framing brief

## Request

> we migrated retro/learn skills as side-playbooks over plan artifact. I want to do same for codereview. Same motivation: codereview isn't always run for each plan, so it should produce it's own artifact. I guess good format is a directory codereviews/{plan filename}/{YYYYMMDDHHmm}.md. Each run is a separate file under same directory, CR linked to plan as list of codereview files. State model is in-codereview -> done, query is plans in done status as table includes list of files with previous CRs. Plannatator presentation stays as a lesson or indirect connection from userland, we don't handle it. Review templates still used and can be both on core/global/project level.

## Task type

`feature` — code-review gains a new user-visible surface: persistent per-run review artifacts under `codereviews/`, an own state machine, plan↔review linking, and a review queue query. Today the run is explicitly ephemeral ("no persistent report"), so this is new capability, not restructure.

- Not `bug`: no divergence between observed and expected behavior — the ephemeral run is by design.
- Not `refactoring`: vault structure, plan frontmatter contract, and playbook lifecycle all change user-visibly; the no-behavior-change DoD test fails.

## Problem

Today the code-review playbook is stateless and ephemeral: findings live only in the conversation, `resolve` ends the run, and the only trace on the plan is the `code_review:` date key stamped into plan frontmatter. Retro/learn already moved to their own artifact track (`retrospectives/{slug}.md` with own statuses, plans stay `done`); code review still has no artifact, no resumability, no history of repeated reviews.

Target: code-review becomes a side-track over the plan artifact, like retro. Each run writes its own artifact `codereviews/{plan-dirname}/{YYYYMMDDHHmm}.md` — one file per run, multiple runs accumulate under the plan's directory. The review artifact owns state `in-codereview → done`. The plan links its reviews as a list of review-file paths. The review queue is a query over plans in `done` status, presented as a table including each plan's existing review files. Plannotator presentation stays userland (lesson or indirect wiring) — out of scope. Review templates remain in use, discoverable at core/global/project level.

## Clarifications and Decisions

- Plan↔review link: new frontmatter key `code_reviews:` (list of review-file paths, null = never reviewed). Old `code_review:` date key is ignored — no migration; legacy plans simply re-enter the queue.
- Queue predicate: `{status: done, code_reviews: null}`.
- Ad-hoc scopes (latest commits, named target) stay supported and also persist: `codereviews/{target-slug}/{YYYYMMDDHHmm}.md`, no plan linking.
- Review artifact state model: `in-codereview → done`.
- Review templates gain the global tier: core + `{home_dir}/review_templates/` + vault `review_templates/`.
- Plannotator presentation stays userland (lesson / indirect wiring) — out of scope.
- No post-implementation reshape milestone expected.
