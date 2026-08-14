---
id: "04"
title: "Fixed mutation set and kill-rate scoring"
sp: 3
status: done
plan: "vault/plans/202608141156_benchmark-scoring/index.md"
---

# M04: Fixed mutation set and kill-rate scoring

A frozen, hand-authored mutation set for the reference benchmark exists, every mutation is killed by the opus etalon corpus, and `bench-score mutations` computes a branch's kill rate.

**Scope**: `vault/benchmarks/mutations/frontmatter-update-e2e/` (new: `NN_{slug}.patch` files + `manifest.md`), `vault/benchmarks/_scripts/bench-score` (new subcommand). Mutation target: `booping-python/src/booping/commands/frontmatter_update.py` as it stands at baseline `e0d1796` — patches are written against that blob and never regenerated, so every model's corpus faces the identical set. A baseline change is a new benchmark: the set is frozen per benchmark id, and a future baseline gets its own registry entry with its own mutation dir — no in-place regeneration.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Author 10–15 patches, each one behavior break the migration's tests exist to catch — bool/int/float coercion dropped, append idempotency removed, append-creates-list-on-null broken, exit 1 ↔ 2 swapped, summary moved stderr→stdout, diff suppressed on change, remove-key made a no-op, macro value left unrendered, YAML `yes`-quirk quoting dropped, log line dropped when vault attached, and similar — each `NN_{slug}.patch` produced by `git diff` of a hand-edit on an `e0d1796` worktree. `manifest.md`: one row per patch — name, the behavior broken, the etalon case(s) expected to kill it. | `vault/benchmarks/mutations/frontmatter-update-e2e/*.patch`, `…/manifest.md` | 2 | done |
| 4.2 | `mutations` subcommand: in the branch worktree, per patch — `git apply` the patch, run the branch's frontmatter-update corpus, record killed (≥1 case fails) / survived, revert (`git apply -R` or checkout), next; never two patches applied at once; a patch that fails to apply on the branch (model touched `src/` — a scope red flag already) is reported `not-applicable`, excluded from the denominator, and flagged. JSON: per-patch verdict + kill rate n/N. | `vault/benchmarks/_scripts/bench-score` | 1 | done |

Tests (lesson 0016): set validity is itself a test — the opus etalon corpus (repo HEAD) must kill 15/15; that run is the fixture. Kill-rate parsing asserted on the deepseek branch's real result.

## Definition of Done

### Task 4.1
- [x] 10–15 patches; each applies clean on a fresh `e0d1796` worktree (`git apply --check`).
- [x] Manifest maps every patch to the behavior broken and the expected killer case(s) from the etalon list; no TODO rows.
- [x] Mutations touch only `frontmatter_update.py` — no test files, no plugin code.

### Task 4.2
- [x] Etalon validation: every patch killed by the opus corpus at HEAD (kill rate N/N) — a surviving patch is fixed or replaced before the milestone closes, and the validation run is recorded in the manifest.
- [x] Deepseek branch kill rate computed and recorded in the milestone's Verify output; worktree left clean (`git status --short` empty) after the sweep.
- [x] Verdicts are per-patch in the JSON with the failing case names as kill evidence.

## Verify

- `vault/benchmarks/_scripts/bench-score mutations --benchmark frontmatter-update-e2e --branch bench/deepseek-deepseek-v4-pro-0813 | jq .kill_rate` prints n/N with N = patch count.
- Same command against a worktree of repo HEAD's corpus (etalon) → N/N.
- `for p in vault/benchmarks/mutations/frontmatter-update-e2e/*.patch; do git -C {baseline-worktree} apply --check "$p"; done` — all clean.
