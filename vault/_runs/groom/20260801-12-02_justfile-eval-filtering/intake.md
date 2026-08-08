---
reviewed_at: 20260801 05:11
---

# Intake — Justfile eval filtering

## Request

> I want to update justfile regress/smoke to support filtering, for example i can say just regress groom/decompose - regress for decompose-work step, just regress groom/ - regress groom playbook and `just regress` - regress for all playbooks.

## Restated problem

Today `just smoke` and `just regress` run promptfoo with a tier filter (`--filter-metadata tier=smoke|regress`) and pass every other argument straight through; selecting a suite requires spelling the full config path by hand (`just smoke -c playbooks/groom/intake/promptfooconfig.yaml`), and there is no way to run all suites of one playbook, or all playbooks, in one invocation. The recipes must instead accept an optional path-style selector: `<playbook>/<step>` runs that one step's suite (`just regress groom/decompose` → the `decompose-work` step), `<playbook>/` runs every suite under that playbook, and no selector runs every suite of every playbook.

## Task type

`feature` — the recipes gain a new capability (selector-driven suite resolution) that changes what an invocation does and how the developer drives evals. Not `bug`: current behaviour matches its documentation — nothing observed diverges from expected. Not `refactoring`: the defining test is "no behaviour change", and here the visible behaviour of `just regress`/`just smoke` is exactly what changes.

## Scope boundaries

**In scope**

- The `smoke` and `regress` recipes in the repo `justfile` accepting an optional selector argument: `<playbook>/<step>`, `<playbook>/`, or absent (all playbooks).
- Resolving a selector to the matching `playbooks/<name>/<step>/promptfooconfig.yaml` suite path(s) and passing them to promptfoo.
- The `just regress groom/decompose` example resolving to the `decompose-work` step — i.e. the selector's step segment matching the step it names.
- Keeping remaining arguments pass-through to promptfoo alongside a selector.

**Out of scope**

- The promptfoo suites themselves — no change to any `promptfooconfig.yaml`, test cases, or the smoke/regress tier metadata.
- The `eval` / `eval-md` recipes and `bin/eval-md.sh` / `bin/report-md.jq` report rendering.
- `booping render-playbook` and the playbook framework — no CLI or loader change.
- New eval tiers, CI wiring, or eval-result storage.

## Scope challenge

- [ ] `groom/decompose` names step `decompose-work` — should the step segment prefix-match (any unique prefix wins), or is this a one-off alias and only exact step names are accepted?
- [ ] Should the same selector also work for `just eval` / `just eval-md`, or do only `smoke` and `regress` change?
- [ ] Do selectors resolve only against core `playbooks/` in this repo, or also against the vault-side roots (`<home_dir>/_playbooks/`, local `_playbooks/`) where other suites may live?
- [ ] When a selector matches nothing (typo, step without a suite), should the recipe fail loudly listing available suites, or silently run nothing?
- [ ] Bare `groom` without a trailing slash — treat it the same as `groom/`, or reject it to keep the grammar strict?
