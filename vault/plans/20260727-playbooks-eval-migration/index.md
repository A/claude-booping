---
title: Playbooks Eval Infrastructure Migration
type: refactoring
status: cancelled
sp: 0
split_from: null
created: 2026-07-27 00:00
planned: 20260727 15:08
started: null
completed: 2026-07-27 18:44
retro: null
goal: null
summary: Migrate vault _playbooks to dir-form + rebuild eval harness on 
  render-playbook --step; ungroomed
commit: be1fbb3151de5968651c94a15905ae49208f291c
sessions:
- 1d9285d4-1faa-4d8c-971e-039057ad94d8
- 23ee2d99-ea09-4cec-8334-c3aa0d716a07
metrics_active_minutes: 60
metrics_models:
- claude-fable-5
metrics_tokens_input: 374
metrics_tokens_output: 270109
metrics_tokens_cache_creation: 1292370
metrics_tokens_cache_read: 17744545
---

# Playbooks Eval Infrastructure Migration

Parked until M3 of `plans/20260727-groom-as-playbook-pilot.md` lands (`--step` + `--project`). Vault-side work under `~/Claude/_playbooks/`; needs its own grooming pass — `sp: 0` is a placeholder, not an estimate.

## Scope (from plan-review session, 2026-07-27)

1. Migrate `build-user-stories` to dir form (`<step>/prompt.md`); introduce `_references/`, `_fixtures/`; rename `dist/` → `_dist/` and `test/` → `_test/` — both currently produce loader noise / a live phantom playbook. (The pilot's M2 may have already landed the minimal dir-form move; this item finishes the restructure.)
2. Split each suite's `tests.yaml` into `tests.smoke.yaml` (deterministic gates) + `tests.regress.yaml` (rubrics only, not a superset — no anchor duplication) (D8); `promptfooconfig.yaml` lists both.
3. Ladder → one `red.md` RED control per step; delete rungs.
4. Prompt loader (`_lib/prompt_loader.py`): shell `booping render-playbook --step` + append target/input block. Provider drops `entry:`; `consumer_prompt.txt` drops `<<INPUT>>`/`<<ATOM>>` substitution (D7).
5. Fixture trees + dynamic-var loader composing `<file path="…">` blocks, so chain corpora exist once.
6. Groom eval suite — only possible after item 4 + `--project`.
