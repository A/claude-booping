# Framing brief

## Request

> 1. So far, let's consider, config shouldn't have any statuses references, except the queryies, hardcode statuses in skills are fine, just don't want to find a solution for it now. Ideally to not have statuses in the playbooks, and instead relay on how playbooks read state machine. I suppose it's enough, instead of inlining statemachine logic into steps. 2. yeah, all to clean up. 3. yep, i think must be hooks (but how to commit from vault and from repo?) smaller notes- consider fixes too. /playbook groom this fixes

Context: the numbered points answer the PR-19 architecture review (core ↔ playbook split, posted at https://github.com/A/claude-booping/pull/19#issuecomment-5193098672) — (1) status-literal duplication, (2) retired-skill fossils, (3) the develop playbook's prose vault-git.

## Task type

`refactoring` — internal structure and prose cleanup with no user-visible behavior change: playbook bodies stop restating state-machine vocabulary, dead references and dead code are removed, and develop's vault snapshots move from prose git to the same `script` hook mechanism its siblings already use. Not `feature`: no new capability is added — every mechanism used (hooks, rendered `## State`, config queries) already exists. Not `bug`: nothing observed diverges from documented behavior; the findings are drift and duplication, not defects (the one behavioral nit, wrap-up's missing `--workdir`, is folded into the hooks migration rather than triaged as a defect).

## Problem

The PR-19 review found the core/playbook split structurally sound but left three families of residue. (1) Status literals are spelled in places that should defer to the machine: retro/learn intake bodies hard-code `awaiting-retro` / `awaiting-learning` while their preambles render `{{ config }}`, and develop/retro/learn closing steps restate `playbook-transition` invocations, gates and sample reports that the rendered `## State` section already carries. (2) Retired-skill fossils survived the skills→playbooks migration: `/retro`+`/learn` handoffs in step prose, a "develop stays canonical" claim the PR made false, `_learn_targets.j2` routing to retired skills, an unshipped authoritative doc reference in playbook-authoring, orphaned docs, and dead engine residue (`Edge.skill`, `DIR_PLAN_NAME`, stale `config["plan"]` docstrings and help-text examples). (3) The develop playbook snapshots the vault via prose `git -C {vault}` commands while groom/retro/learn use `script` hooks on `states:` edges; retro and learn also carry two near-identical ~135-line `close-working-set` scripts. After this refactoring: playbook bodies read state from the rendered machine instead of inlining it, no retired surface is referenced anywhere, and every vault snapshot goes through a hook.

## Clarifications and Decisions

- Goal: clean up bad code while polishing the big skills→playbooks refactor — playbook bodies can't drift from their state machines, zero references to retired surfaces, one predictable commit rule.
- Config may reference statuses **only inside query specs** (`where.status…`); the per-playbook `status` key + query-literal duplication is accepted for now — no reference mechanism is designed in this plan.
- Hardcoded statuses in **skills** (`code-review`) are fine — out of scope.
- Playbook bodies carry **no status literals and no inlined state-machine logic** — they rely on the rendered `## State` section and `playbook-state` instead.
- All retired-skill fossils are cleaned up, engine residue (`Edge.skill`, `DIR_PLAN_NAME`, stale `config["plan]"` docstrings) included.
- `cancelled` becomes a real machine status: added as a terminal to **both** the groom and develop `states:` machines; the `latest_plans` query keeps it.
- Commit rule: a commit tied to a state transition is a `script` hook; a commit not tied to one stays prose under the git guide + `commit_message` config. Develop's mid-loop and wrap-up commits stay prose; wrap-up's transition command gains the missing `--workdir`.
- The near-identical retro/learn `close-working-set` scripts are deduplicated into a shared `playbooks/_scripts/` root (one dir up); the engine's `script` hook resolution learns the fallback.
- Smaller notes all in scope: `specs_dir` in `_playbook_driving.j2` becomes an optional config key (line renders only when set); code-review skill prose points at the delegation table instead of literal agent ids; `when: other` in `git.branches` reworded to a freeform descriptor; stale CLI help examples updated to real config paths. The `migrate` gate exemption stays as-is.
- No post-implementation prose-reshape milestone (lesson 0008 answer: no).
