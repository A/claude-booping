# Clarifications

Autonomous run: the owner was unavailable, so every question below was settled by the run with a default. Each is `[clarify]` for the owner's later review.

## C1 — one plan or split — answered

**Asked:** 2026-10-14 — intake

**Question:** Should the three items be one plan or split?

**Answer:**

[clarify] One plan, 12 SP — the request asks for one plan, the items are small and independent, well under the 35 SP split threshold.

## C2 — where the shared vault-commit logic lives — answered

**Asked:** 2026-10-14 — draft-plan

**Question:** The four vault-commit hooks need one repo test and one commit routine. Where does it live?

**Options:**

- A stdlib module `playbooks/_scripts/_vault_git.py`, imported by each hook via `sys.path` from its own location
- A new `booping vault-commit` CLI subcommand the hooks call
- Patch each hook in place (four copies)

**Answer:**

[clarify] The stdlib module. The previous fix (4b90729) landed in one copy of four — a single source prevents that drift (value/0003); the hooks are deliberately stdlib-only and do not shell back into `booping`, so a CLI subcommand would break that design.

## C3 — keeping unrelated staged changes out of vault commits — answered

**Asked:** 2026-10-14 — draft-plan

**Question:** In a nested vault, a plain `git commit` would also commit whatever the user has staged elsewhere in the repo. How do the hooks avoid it?

**Answer:**

[clarify] `git add -- {paths}` then `git commit --only -- {paths}` — commits only the hook's vault paths and leaves other staged entries staged (checked on git 2.56). Applied to own-repo vaults too, where it changes nothing in practice.

## C4 — drop-plan in scope — answered

**Asked:** 2026-10-14 — research-codebase

**Question:** The request names groom's and code-review's hooks; retro's `drop-plan` carries the same `.git`-exists gate. Fix it too?

**Answer:**

[clarify] Yes — same defect, same helper; leaving it would be the stale copy the request is about.

## C5 — transition report wording — answered

**Asked:** 2026-10-14 — draft-plan

**Question:** `playbook-transition` prints `script {name}: ok` on any exit 0, even when the hook skipped its commit. Change it?

**Answer:**

[clarify] No — out of scope. The report states the hook's exit status; once the hooks commit, `ok` is truthful for the reported bug. Surfacing hook stdout in the report is a separate change.

## C6 — snapshot acceptance — answered

**Asked:** 2026-10-14 — draft-plan

**Question:** M03 drifts `playbooks/code-review/_reports/output.md`. rule/0013 says a run never accepts baselines. Who accepts?

**Answer:**

[clarify] The develop runner, under the owner's standing permission for this feature (2026-10-14): `just snapshots-accept code-review` only if every drifted hunk is one of the three Baseline cells M03 names, recorded in `develop-defaults.md`; any other drift stops the run.

## C7 — regression test tier for the hooks — answered

**Asked:** 2026-10-14 — draft-plan

**Question:** How are the hook fixes tested?

**Answer:**

[clarify] Pytest subprocess tests in `booping-python/tests/scripts/vault_commit_test.py` with real `git` in `tmp_path`, parametrized over the four hooks × nested / own-repo vault — the txtar corpus has no git-repo fixture, and `close_code_review_test.py` already sets the subprocess shape.
