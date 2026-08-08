---
title: Idle-aware active time and per-session token accounting
type: feature
status: done
sp: 20
split_from: null
created: 2026-08-08 15:23
planned: null
started: 2026-08-08 18:54
completed: 2026-08-08 20:10
code_reviews: null
sessions:
- 2b2f5f45-99d4-4b69-b1ae-7b9539186bd2
- ea3975e1-c65b-4846-a7ee-aa40d3645450
retro: null
goal: null
summary: "session-stats replaces session-time: wait-on-human excluded from active
  time, token totals, metrics_ frontmatter keys"
commit: 4f5c4fca09d788fd50c050219e09d0fc81e2aad8
reviewed_at: 2026-08-08 18:53
metrics_active_minutes: 147
metrics_models:
- claude-opus-5
metrics_tokens_input: 31030
metrics_tokens_output: 448284
metrics_tokens_cache_creation: 2588613
metrics_tokens_cache_read: 52793431
---

# Idle-aware active time and per-session token accounting

## Context

`booping session-time <plan>` sums turn spans across a plan's stamped sessions, where a turn runs from a real user prompt to the last event before the next one. Every stretch spent waiting on a human lands inside a turn and counts as active work. Because this project's playbooks ask through `AskUserQuestion` — whose answer is a `tool_result`, not a user prompt — an entire interactive groom collapses into one turn: session `19353202` reports 209 minutes, 175 of them a single turn; session `dd8af31c` reports 929, of which one `AskUserQuestion` → `tool_result` gap is 886.5.

Separately, each assistant event carries a `message.usage` object that nothing reads, and metrics can only be addressed one plan path at a time.

After this plan: `booping session-stats` replaces `session-time` as the only metrics surface. It subtracts user-blocking waits from active time, reads token totals (input, output, cache-creation, cache-read) and model ids, is addressed by a directory plus a filename mask, emits one JSON document on stdout whose `totals` object is verbatim what it writes, and stamps `metrics_`-prefixed frontmatter keys that surface as `sprints.md` columns. Migration `006` renames the two keys shipped today and adds the token columns.

## Decisions

- **Wait exclusion, not an idle cap**: active time subtracts the interval between a user-blocking tool call and its `tool_result`, rather than breaking turns on a gap threshold. A threshold misfires on legitimately slow tool calls (a long build, a slow test run); the blocking-call interval is exactly the thing being measured. Evidence: both known outliers are single `AskUserQuestion` spans.
- **Blocking set**: `AskUserQuestion` `tool_use` → its `tool_result` matched by `tool_use_id` (human by definition, keyed by tool name), plus any `user` line carrying `toolDenialKind: "user-rejected"`. `permission-rule`, `automode-blocked` and `automode-unavailable` are system decisions and are never subtracted.
- **Permission-approved waits are an accepted undercount**: an auto-approved tool call and one a human approved after ten minutes are structurally identical in the transcript — no field distinguishes them. The metric under-reports wait rather than guessing, and the limitation is documented.
- **Real-prompt signal**: `origin.kind == "human"` identifies a real user prompt, falling back to the current content-is-a-string heuristic when the field is absent (older transcripts). The heuristic alone misses genuinely human lines such as `[Request interrupted by user for tool use]`.
- **Token semantics**: `input_tokens` excludes both cached forms, so `input + cache_read` does not double-count; `cache_creation`'s `ephemeral_1h_input_tokens` + `ephemeral_5m_input_tokens` sums exactly to `cache_creation_input_tokens`; the per-event `iterations` array mirrors the top-level usage and is never summed. Cache is always reported split, never as one number.
- **Frontmatter keys are flat and `metrics_`-prefixed**: `metrics_active_minutes`, `metrics_models`, `metrics_tokens_input`, `metrics_tokens_output`, `metrics_tokens_cache_creation`, `metrics_tokens_cache_read`. Obsidian Properties and Bases do not support nested YAML mappings — a nested `metrics:` object would not be addressable as a `sprints.md` column, which is the reason the keys exist.
- **Addressing**: one positional path. A directory is walked with `--mask` (default `index.md`); a file path is used directly. Every matching artifact carrying a `sessions:` list is processed.
- **Writes by default**: the command stamps what it computes. `--force` overrides existing values, `--dry-run` emits the identical JSON with nothing written.
- **Output is JSON on stdout**, warnings and errors on stderr, so stdout stays pipeable. The per-artifact `totals` object uses the frontmatter key names verbatim — the printed object is the written object, which is what keeps report and file from drifting.
- **`session-time` is replaced outright**: module, command, tests and fixtures are deleted rather than deprecated. It shipped hours ago, is unreleased, and its only caller is a script hook this plan repoints.
- **No LLM anywhere in the path**: extraction is straight JSON parsing plus timestamp arithmetic, because per-session model calls would be too expensive to run across a vault.

## Architecture

```
{vault}/plans/*/index.md  ──sessions:──▶ booping session-stats {dir} --mask index.md
                                                    │
                        ~/.claude/projects/*/{id}.jsonl ──parse──▶ active time − blocking waits
                                                    │                tokens (in/out/cc/cr), models
                                                    ▼
                              stdout JSON: artifacts[].totals  ═══ same keys ═══▶ frontmatter metrics_*
                                                    │
                                          sprints.md Bases columns
```

- Input sources: the `sessions:` list on each matched artifact; transcripts globbed as `~/.claude/projects/*/{id}.jsonl` (root overridable).
- Output sinks: one JSON document on stdout; `metrics_*` frontmatter via the existing `update_frontmatter` writer, which already round-trips scalar and list values.
- Callers: the `stamp-active-time` script hook on develop's close edges; humans ad hoc. No skill inlines it.

## Milestones

### M1: Extraction engine — wait-aware time, tokens, models — 8 SP | done

**Goal**: a module that turns a session id into active minutes with user-blocking waits subtracted, token totals split four ways, and the distinct model ids.

**Verify**: `just pytest` green, including a fixture whose `AskUserQuestion` span is excluded from the total.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Transcript locator + line classifier: glob `~/.claude/projects/*/{id}.jsonl` (root overridable), stream-parse, classify each line as real-user-prompt (`origin.kind == "human"`, falling back to the content-is-a-string heuristic when the field is absent), assistant event, sidechain, meta, or malformed; yield timestamp, kind, model, tool_use_id, tool name and denial kind | `booping-python/src/booping/session_stats.py`, `booping-python/tests/test_session_stats.py`, `booping-python/tests/fixtures/session_stats/projects/**/*.jsonl` | 3 | done |
| 1.2 | Active time: group events into turns, then subtract every user-blocking interval — an `AskUserQuestion` `tool_use` to its matching `tool_result` by `tool_use_id`, and any span ending in a `toolDenialKind: "user-rejected"` line; `permission-rule` / `automode-blocked` / `automode-unavailable` never subtract; round the total to whole minutes | `booping-python/src/booping/session_stats.py`, `booping-python/tests/test_session_stats.py` | 3 | done |
| 1.3 | Token and model aggregation: sum `input_tokens`, `output_tokens`, `cache_creation_input_tokens`, `cache_read_input_tokens` across non-sidechain assistant events, never reading `iterations`; collect sorted distinct `message.model` values | `booping-python/src/booping/session_stats.py`, `booping-python/tests/test_session_stats.py` | 2 | done |

#### Task 1.1 DoD

- [x] Locator finds a fixture session under a `--projects-root` tree shaped `{root}/{slug}/{id}.jsonl`.
- [x] Missing transcript for a stamped id → stderr warning naming the id, session skipped, exit stays 0.
- [x] Malformed lines and unknown `type` values are skipped and counted, never raised.
- [x] A line with `origin.kind == "human"` and list content (e.g. an interruption notice) classifies as a real user prompt; a `task-notification` origin does not.
- [x] `isSidechain: true` and `isMeta` lines are classified out of real-user-prompt.

#### Task 1.2 DoD

- [x] A fixture with a 60-minute `AskUserQuestion` span inside one turn reports only the working time, not the span.
- [x] A `tool_result` is matched to its `tool_use` by `tool_use_id`, not by position — a fixture interleaving two concurrent tool calls still subtracts the right interval.
- [x] A span ending in `toolDenialKind: "user-rejected"` is subtracted; the same span with `automode-blocked` is not.
- [x] Idle between turns still drops out, and a session ending on an assistant event counts its final turn to the last event.
- [x] Empty / header-only transcript yields 0 minutes without error.
- [x] Regression fixture reproducing session `19353202`'s shape reports well under its unadjusted 209 minutes.

#### Task 1.3 DoD

- [x] Totals sum only top-level `usage` fields; a fixture with a populated `iterations` array yields the same numbers as one without.
- [x] Cache creation and cache read are reported as separate integers, never summed together.
- [x] Sidechain assistant lines contribute neither tokens nor models.
- [x] Two sessions on different models yield both full ids, sorted and deduped.

---

### M2: `session-stats` subcommand and the retirement of `session-time` — 6 SP | done

**Goal**: `booping session-stats {path}` walks a directory by mask, stamps `metrics_*` keys, prints one JSON document, and is the only metrics surface left.

**Verify**: `bin/booping session-stats booping-python/tests/fixtures/session_stats/vault --mask index.md --dry-run --projects-root booping-python/tests/fixtures/session_stats/projects | jq -e '.artifacts[0].totals.metrics_active_minutes'` exits 0 and leaves the tree unchanged; `bin/booping session-time` no longer exists.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Subcommand, addressing and JSON output: `session-stats {path} [--mask GLOB] [--force] [--dry-run] [--projects-root PATH]`; a directory walks by mask (default `index.md`), a file path is used directly; artifacts without a `sessions:` key are skipped with a stderr note; the JSON document goes to stdout and every warning to stderr; register in the CLI parser | `booping-python/src/booping/commands/session_stats.py`, `booping-python/src/booping/cli.py`, `booping-python/tests/test_session_stats.py` | 3 | done |
| 2.2 | Write path: stamp the six `metrics_*` keys through `update_frontmatter`; an artifact already carrying any of them is skipped with `written: false` and a skip reason unless `--force`; `--dry-run` emits the identical document and writes nothing | `booping-python/src/booping/commands/session_stats.py`, `booping-python/tests/test_session_stats.py` | 2 | done |
| 2.3 | Retire `session-time`: delete the module, its command, its tests and fixtures, and its CLI registration; repoint `playbooks/_scripts/stamp-active-time` at `session-stats` against the plan's directory; drop the stale `session-time` reference in `stamp-session`'s docstring | `booping-python/src/booping/session_time.py`, `booping-python/src/booping/commands/session_time.py`, `booping-python/src/booping/cli.py`, `booping-python/tests/test_session_time.py`, `booping-python/tests/fixtures/session_time/`, `playbooks/_scripts/stamp-active-time`, `playbooks/_scripts/stamp-session` | 1 | done |

#### Task 2.1 DoD

- [x] A directory path with two matching artifacts produces two entries under `artifacts`, in sorted path order.
- [x] A file path produces exactly one entry, and `--mask` is ignored for it.
- [x] An artifact with no `sessions:` key is skipped with a stderr note, exit stays 0.
- [x] stdout parses as a single JSON document with `jq -e`; no warning text reaches stdout.
- [x] Path that does not exist → stderr message, exit 1; mask matching nothing → stderr message, exit 1.
- [x] `bin/booping session-stats --help` reflects every flag above.

#### Task 2.2 DoD

- [x] A fresh artifact gets all six `metrics_*` keys and reports `written: true`.
- [x] Re-running without `--force` leaves the file byte-identical and reports `written: false` with a skip reason.
- [x] `--force` overwrites existing values.
- [x] `--dry-run` emits the same `totals` as a real run and leaves the tree unchanged.
- [x] Per-session objects and the `totals` object use the frontmatter key names verbatim.

#### Task 2.3 DoD

- [x] `bin/booping session-time` exits non-zero as an unknown subcommand, and no `session_time` module or test remains.
- [x] `stamp-active-time` invokes `session-stats` and still exits 0 when computation fails.
- [x] `rg session-time` over the repo returns only migration and plan history, no live call sites. — closed with task 3.4; the only remaining hit is `migrations/006_metrics_key_prefix/migration.md`.

---

### M3: Frontmatter rename, surfacing, migration 006, docs — 6 SP | done

**Goal**: existing vaults carry the `metrics_`-prefixed keys with token columns visible in `sprints.md`, and the already-stamped plans hold values recomputed under the new rule.

**Verify**: `just ci` green; migration `006` applied twice in a row changes nothing the second time; `sprints.md` lists the six columns.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Config surfacing: replace `active_minutes` and `models` with the six `metrics_*` keys in the sprints.md scaffold Bases `order:` and in `core.groom_playbook.queries.latest_plans.columns` | `src/config.yaml` | 1 | done |
| 3.2 | Migration `006_metrics_key_prefix`: rename `active_minutes` → `metrics_active_minutes` and `models` → `metrics_models` in every `plans/*/index.md` carrying them, and rewrite the `sprints.md` Bases fence `order:` to the six columns; frontmatter `id: 6`; idempotent, following the `005` shape | `migrations/006_metrics_key_prefix/migration.md` | 3 | done |
| 3.3 | Recompute the already-stamped plans under the new algorithm with `bin/booping session-stats {vault}/plans --mask index.md --force`, and record the before/after of the two known outliers in the sprint report | `{vault}/plans/*/index.md` | 1 | done |
| 3.4 | Docs sweep: `session-stats` replaces `session-time` in the project `CLAUDE.md` CLI list; `documentation/vault.md` documents the six keys and the wait-exclusion rule including its permission-approval limitation | `CLAUDE.md`, `documentation/vault.md` | 1 | done |

**Blocked (1/2)**: migration `006`'s plan-frontmatter rename substituted `active_minutes:` → `metrics_active_minutes:` without checking whether the prefixed key was already present, so a plan carrying both — the state a `session-stats --force` run before migrating produces — would gain duplicate YAML keys; re-briefed the worker to drop the old key when the target already exists, matching what the fence script already does.

#### Task 3.1 DoD

- [x] `order:` and `latest_plans.columns` list the six `metrics_*` keys and neither old name.

#### Task 3.2 DoD

- [x] Migration matches the shipped `migrations/NNN_slug/migration.md` shape with `id: 6`.
- [x] A plan already carrying `metrics_active_minutes` is left unchanged; a plan carrying the old names is renamed with its values preserved. A plan carrying both keys at once — the state a `session-stats --force` run before migrating produces — drops the old key and keeps the prefixed value, rather than writing a duplicate.
- [x] A fence already listing the six columns is left unchanged.
- [x] A second consecutive run reports nothing to do and writes nothing.

#### Task 3.3 DoD

- [x] Every plan that carried `active_minutes` carries recomputed `metrics_*` values. — 37 artifacts stamped, 36 skipped for having no `sessions:` key.
- [x] Sessions `19353202` and `dd8af31c` report materially lower active minutes than 209 and 929, and the sprint report names both numbers. — `19353202`: 209 → 50 minutes; `dd8af31c`: 929 → 23 minutes.

#### Task 3.4 DoD

- [x] `CLAUDE.md` names `session-stats` and no longer names `session-time`.
- [x] `documentation/vault.md` documents all six keys and states the permission-approval undercount.

## I/O contract

- **Arguments / flags**: `booping session-stats {path} [--mask GLOB] [--force] [--dry-run] [--projects-root PATH]` — `{path}` is a directory (walked by `--mask`, default `index.md`) or a single file; `--force` overwrites existing metric values; `--dry-run` computes and prints without writing; `--projects-root` overrides `~/.claude/projects`.
- **stdin**: none.
- **stdout**: one JSON document, nothing else:

```json
{
  "artifacts": [
    {
      "path": "plans/202608081156_code-review-track-split/index.md",
      "written": true,
      "sessions": [
        {
          "session": "046bbec9-0000-0000-0000-000000000000",
          "metrics_active_minutes": 61,
          "metrics_models": ["claude-fable-5"],
          "metrics_tokens_input": 8801,
          "metrics_tokens_output": 121004,
          "metrics_tokens_cache_creation": 2100553,
          "metrics_tokens_cache_read": 60218844
        }
      ],
      "totals": {
        "metrics_active_minutes": 105,
        "metrics_models": ["claude-fable-5"],
        "metrics_tokens_input": 13921,
        "metrics_tokens_output": 209214,
        "metrics_tokens_cache_creation": 3980773,
        "metrics_tokens_cache_read": 104319756
      }
    },
    {
      "path": "plans/20260804-18-27_booperiser-cli/index.md",
      "written": false,
      "skipped": "already stamped; --force to override",
      "sessions": [],
      "totals": {}
    }
  ]
}
```

- **stderr**: warnings (missing transcript naming the id, malformed-line count, artifact without a `sessions:` key) and errors.
- **Exit codes**: `0` success, including runs that warned; `1` user error (path missing, mask matched nothing, unreadable artifact); `2` internal error.

## Final Verification

- [x] `just ci` green (lint, typecheck, pytest, snapshots, mdcheck). — exit 0; 799 passed, zero snapshot drift.
- [x] `bin/booping session-stats --help` matches the I/O contract.
- [x] Happy path, `--dry-run`, a `--force` re-run and the missing-transcript path all verified by invocation.
- [x] Exit codes match the contract. — missing path 1, empty mask 1, happy run 0.
- [x] `bin/booping session-time` is gone and nothing in the repo calls it. — the only remaining mention is migration `006` itself.
- [x] End-to-end: migration `006` on the live vault, then a `--force` recompute, leaves every previously stamped plan carrying six `metrics_*` keys. — 37 plans, six keys each, no old keys and no duplicates.

## Out of scope

- A text or table output format — JSON is the only stdout shape; humanising minutes or token counts stays a view concern.
- Cost estimation in currency, and per-model token attribution.
- The `cache_creation` TTL breakdown (`ephemeral_1h` / `ephemeral_5m`) as separate fields.
- Stamping `sessions:` onto retrospectives or code reviews — only plans carry the list today; the directory-plus-mask addressing merely leaves room for it.
- Detecting permission-approval waits, which no transcript field distinguishes.
- Parsing sidechain `subagents/*.jsonl` files.
- Re-deriving session attribution — the heuristic backfill already run is not repeated or improved here.

## CLAUDE.md impact

`## Commands` — replace `session-time` with `session-stats` in the `bin/booping` subcommand list (task 3.4). No other sections.
