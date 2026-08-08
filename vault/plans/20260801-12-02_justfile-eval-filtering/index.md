---
title: Justfile eval filtering
type: feature
status: cancelled
sp: 17
split_from: null
created: 2026-08-01 12:02
planned: null
started: null
completed: null
retro: null
goal: null
summary: "Pick which promptfoo eval suites run by passing a path substring to just
  eval/eval-md/smoke/regress"
commit: null
sessions:
- e3071baa-bf3a-4eaf-ba28-a57d06dac1e6
metrics_active_minutes: 40
metrics_models:
- claude-fable-5
metrics_tokens_input: 243
metrics_tokens_output: 65361
metrics_tokens_cache_creation: 479698
metrics_tokens_cache_read: 11320110
---

# Justfile eval filtering

## Context

The four eval recipes in `justfile` — `eval`, `eval-md`, `smoke`, `regress` (lines 28–46) — each
forward every argument to one `npx promptfoo@latest eval` process. Choosing which of the eight
suites under `playbooks/groom/*/promptfooconfig.yaml` runs means spelling the config path by hand
(`just smoke -c playbooks/groom/intake/promptfooconfig.yaml`, the form the comment block at
`justfile:24-26` documents). There is no way to run every suite of one playbook, or every suite in
the repo, in one invocation — and a bare `just regress` today errors, because with no `-c` promptfoo
falls back to a `./promptfooconfig.yaml` that does not exist at the repo root.

After this work every eval recipe takes an optional selector: any substring of a suite's directory
path relative to the repo root. `just regress groom/decompose` runs the `decompose-work` suite,
`just regress groom/` runs all eight suites of the playbook, `just regress` runs every suite in the
repo, and `just regress --dry-run groom` lists what would run without invoking promptfoo. A selector
that matches nothing prints nothing and exits 0. The explicit `-c` form keeps working exactly as the
justfile documents it today.

## Decisions

- **Where the logic lives**: one new script, `bin/eval-run.sh`, owns selector parsing, suite
  resolution and the per-suite loop; all four recipes become one-line delegations — the split the
  repo already uses at `justfile:35-36` → `bin/eval-md.sh`, and the only shape that avoids copying
  the same shell into four recipe bodies, since a non-shebang `just` recipe runs line-by-line and
  cannot hold a loop.
- **Multi-suite execution**: N sequential `promptfoo eval` processes, one per resolved suite — not
  one process with repeated `-c` — because promptfoo's `combineConfigs` merges multiple configs into
  a single eval, cross-producting each step's prompt and provider against every other step's tests.
- **Suite resolution**: enumerate-then-filter. Every `playbooks/*/*/promptfooconfig.yaml` is
  enumerated first under `shopt -s nullglob`, any path component starting with `_` is dropped, and
  the selector filters what remains — one code path serves the selector, the bare invocation and the
  `_`-exclusion rule.
- **Selector semantics**: a single plain case-sensitive substring matched against the suite's
  directory path (`playbooks/<playbook>/<step>`), with only a trailing `/` stripped — no grammar, no
  segments, no parse. One comparison covers `groom`, `groom/`, `playbooks/groom`, `groom/decompose`,
  `decompose-work` and `design` alike. Matching the directory rather than the config path keeps
  `config`, `promptfoo` and `yaml` from selecting everything.
- **Multi-hit is not an error**: the runner is N-ary by construction, so `groom/` matching eight
  suites is the same operation as `groom/de` matching two — and treating it as an error would
  contradict the zero-match no-op.
- **Zero match**: short-circuits before any promptfoo invocation — no output, exit 0. This is the
  confirmed policy and it also avoids promptfoo's non-existent-`./promptfooconfig.yaml` fallback.
- **Selector vs pass-through args**: recipes keep a single `*args` variadic and gain
  `[positional-arguments]`; the script takes the selector to be the first post-flag argument only
  when it does not start with `-`. A recipe parameter (`sel="" *args:`) was rejected because a
  leading optional positional binds `-c` as the selector on just 1.57.0, breaking the documented
  pass-through form.
- **Explicit `-c`**: when the pass-through args already carry `-c` / `--config` / `--config=…` and
  no selector was given, resolution is skipped entirely and the args go to one promptfoo process
  unchanged. A selector *and* an explicit `-c` together are a usage error (exit 2), because handing
  both to one process is precisely the silent cross-product `combineConfigs` produces.
- **Failure policy**: `set -uo pipefail` without `set -e`, so a red suite does not abort the sweep —
  an aggregate is the point. A suite that produces no `--output` JSON at all is a config- or
  provider-level error rather than a test failure, and aborts the loop instead of repeating a
  doomed, judge-billed run across the remaining suites.
- **Cost visibility**: every run that resolves at least one suite prints a one-line announce naming
  the resolved suites before the first invocation, and never prompts. `--dry-run` prints the
  resolved config paths and exits 0. A `y/N` confirmation was rejected — it makes four recipes
  interactive and then needs a `--yes` flag and a non-TTY bypass.
- **Aggregation**: per-suite stats are read back from each `--output` JSON with `jq` and summed into
  one `TOTAL` line printed when two or more suites ran; single-suite runs stay byte-similar to
  today. `jq` absent degrades to per-suite output plus an aggregated exit code rather than failing
  the run.
- **Markdown reports**: `bin/eval-md.sh` is folded into `bin/eval-run.sh` behind a `--md` flag and
  deleted, rather than kept beside it — two scripts would each need the same selector parser and it
  would drift. `bin/report-md.jq` stays per-suite and is called once per suite.
- **Dependency footprint**: `npx` and `jq` (already required by the report path) plus `glow` on the
  `--md` path only; no new dependency is introduced.

## Architecture

`bin/eval-run.sh` sits between the justfile and promptfoo. It resolves the repo root from its own
location — `here=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)`, then its parent, the
`bin/booping` precedent — so behaviour does not depend on the caller's cwd.

Input sources: its own argument vector, and the `playbooks/` directory tree. It reads no environment
variable and parses nothing inside a `promptfooconfig.yaml` — a suite is fully identified by its
directory path, which is what makes resolution a path operation.

Output sinks: each suite's promptfoo output streams straight to the terminal under a per-suite
header; the announce line and the `TOTAL` line are the script's own stdout additions; warnings and
usage errors go to stderr. On the `--md` path each suite's `--output` JSON is rendered through the
unchanged `bin/report-md.jq` and appended to one combined markdown file — each suite's rendered
`# <description>` first line already acts as its section heading — which a single
`glow -w "$(tput cols)"` shows at the end.

Side effects: one `mktemp -t promptfoo-eval-XXXXXX.json` per suite, deleted after stats extraction
in plain mode and kept (with paths echoed) in `--md` mode.

Callers: the four `justfile` recipes, each a one-liner that prepends its own fixed flags — `--md`
for `eval-md`, `--tier smoke` for `smoke`, `--tier regress` for `regress`, none for `eval` — and
forwards `"$@"`. Nothing else in the repo invokes it; `just test` is pytest over `booping-python/`
and CI never invokes promptfoo, so `--dry-run` is the verification handle.

Unchanged by this work: every `playbooks/groom/*/promptfooconfig.yaml`, every `tests.yaml` and its
`metadata: {playbook, step, tier}`, the `--filter-metadata tier=` axis, and `bin/report-md.jq`.

## Milestones

### M1: Suite resolution and `--dry-run` — 5 SP | pending

**Goal**: `bin/eval-run.sh` resolves a selector to a list of suite config paths and can print that
list without invoking promptfoo.

**Verify**: `bin/eval-run.sh --dry-run` prints the eight
`playbooks/groom/<step>/promptfooconfig.yaml` paths one per line and exits 0;
`bin/eval-run.sh --dry-run groom/decompose` prints exactly
`playbooks/groom/decompose-work/promptfooconfig.yaml`; `bin/eval-run.sh --dry-run nosuchstep`
prints nothing and exits 0; `bin/eval-run.sh --dry-run groom -c x.yaml; echo $?` prints `2`.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Create the script: `#!/usr/bin/env bash`, `set -uo pipefail`, `shopt -s nullglob`, mode `755`, repo-root resolution from `${BASH_SOURCE[0]}`. Parse recipe flags from the front — `--tier <smoke\|regress>`, `--md`, `--dry-run` — in any order, stopping at the first unrecognised token; take the selector as the first post-flag argument when it does not start with `-`; pass every remaining argument through in order. Detect `-c` / `--config` / `--config=…` among the pass-through args. Validate the `--tier` value at parse time — before any resolution and before the `--dry-run` short-circuit — and emit the exit-2 usage errors there. | `bin/eval-run.sh` | 3 | pending |
| 1.2 | Enumerate `playbooks/*/*/promptfooconfig.yaml`, drop any entry whose playbook or step component starts with `_`, strip a trailing `/` from the selector, and keep the entries whose directory path relative to the repo root contains it as a case-sensitive substring; no selector keeps all. Zero matches exit 0 with no output. Warn once on stderr when `playbooks/_lib` does not resolve. Implement `--dry-run`: print the resolved config paths one per line, exit 0. | `bin/eval-run.sh` | 2 | pending |

#### Task 1.1 DoD

- [ ] `test -x bin/eval-run.sh` succeeds and `head -1 bin/eval-run.sh` is `#!/usr/bin/env bash`.
- [ ] `bin/eval-run.sh --dry-run` invoked from `/tmp` by absolute path prints paths under
      `playbooks/`, proving cwd-independence.
- [ ] `bin/eval-run.sh --tier bogus --dry-run; echo $?` prints `2` and a message on stderr, and
      prints no config paths — the value is rejected before resolution.
- [ ] `bin/eval-run.sh --dry-run groom -c playbooks/groom/intake/promptfooconfig.yaml; echo $?`
      prints `2` and a message on stderr.
- [ ] `bin/eval-run.sh --dry-run -c playbooks/groom/intake/promptfooconfig.yaml` (no selector)
      does not exit 2 — the legacy path is not rejected.
- [ ] `bin/eval-run.sh --md --dry-run` and `bin/eval-run.sh --dry-run --md` both exit 0, showing
      recipe flags are order-independent.

#### Task 1.2 DoD

- [ ] `bin/eval-run.sh --dry-run | wc -l` prints `8`.
- [ ] `bin/eval-run.sh --dry-run groom/` and `bin/eval-run.sh --dry-run playbooks/groom` each print
      the same eight lines as the bare invocation.
- [ ] `bin/eval-run.sh --dry-run groom/decompose` prints exactly
      `playbooks/groom/decompose-work/promptfooconfig.yaml`.
- [ ] `bin/eval-run.sh --dry-run groom/de` prints the `decompose-work` and `design` paths and
      nothing else.
- [ ] `bin/eval-run.sh --dry-run _lib`, `bin/eval-run.sh --dry-run _fixtures` and
      `bin/eval-run.sh --dry-run promptfoo` each print nothing and exit 0.
- [ ] `bin/eval-run.sh --dry-run desgin; echo $?` prints nothing and then `0`.
- [ ] With `playbooks/_lib` renamed away, a run prints one warning line on stderr and stdout is
      unchanged.

---

### M2: Sequential execution, aggregation and `--md` — 7 SP | pending

**Goal**: a resolved selector runs one promptfoo process per suite, announces the set up front, and
reports one rolled-up total — with `--md` producing a single combined markdown report.

**Verify**: `bin/eval-run.sh --tier smoke groom/de` prints
`→ 2 suite(s): groom/decompose-work, groom/design`, then a `── groom/decompose-work ──` and a
`── groom/design ──` section, then one `TOTAL  smoke · 2 suite(s) · …` line, and exits 0 when both
suites pass; `bin/eval-run.sh --md --tier smoke groom/de` additionally opens one glow view covering
both suites and echoes the report and JSON paths.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Print the announce line `→ N suite(s): <playbook>/<step>, …` when N ≥ 1, then loop the resolved suites sequentially: `npx promptfoo@latest eval -c <config> [--filter-metadata tier=<tier>] <pass-through args…> --output <tmp>.json`, each preceded by a `── <playbook>/<step> ──` header. Abort the loop when a suite produces no `--output` JSON — a config- or provider-level error — with a stderr message and exit 1, leaving the remaining suites uninvoked. Route the no-selector-with-`-c` case to a single unresolved invocation whose own exit status is passed through. | `bin/eval-run.sh` | 3 | pending |
| 2.2 | Read each suite's `--output` JSON with `jq`, sum passed / failed / errored, and print `TOTAL  <tier\|both> · N suite(s) · P passed, F failed, E errored` when N ≥ 2. Exit 1 when any suite exits non-zero or reports failures or errors, else 0. Skip the totals line and fall back to the aggregated promptfoo exit codes when `jq` is unavailable. Delete each temp JSON after stats extraction in plain mode. | `bin/eval-run.sh` | 2 | pending |
| 2.3 | Implement `--md`: render each suite's `--output` JSON through `bin/report-md.jq` and append to one combined markdown file, show it with `glow -w "$(tput cols)"` after the last suite, echo the report path and each JSON path, and keep the temp JSONs. | `bin/eval-run.sh` | 2 | pending |

#### Task 2.1 DoD

- [ ] `bin/eval-run.sh --tier smoke groom/design` prints `→ 1 suite(s): groom/design` before any
      promptfoo output.
- [ ] `bin/eval-run.sh --tier smoke groom/de` prints two `── <playbook>/<step> ──` headers and two
      distinct suite outputs.
- [ ] `bin/eval-run.sh --tier smoke groom/design --filter-pattern nomatch` reaches promptfoo with
      the extra flag — visible as zero tests selected — proving pass-through args survive
      resolution.
- [ ] `bin/eval-run.sh -c playbooks/groom/intake/promptfooconfig.yaml` runs exactly one promptfoo
      process with no announce line and no resolution.
- [ ] With one suite's config temporarily made invalid so no `--output` JSON is written, a two-suite
      run stops after that suite, does not invoke promptfoo again, prints a message on stderr, and
      exits `1`.
- [ ] `bin/eval-run.sh --tier smoke groom/` prints one announce line naming all eight
      `<playbook>/<step>` pairs, comma-separated, untruncated.

#### Task 2.2 DoD

- [ ] `bin/eval-run.sh --tier smoke groom/de` ends with one
      `TOTAL  smoke · 2 suite(s) · <P> passed, <F> failed, <E> errored` line whose counts equal the
      sum of the two per-suite summaries.
- [ ] `bin/eval-run.sh --tier smoke groom/design` prints no `TOTAL` line.
- [ ] `bin/eval-run.sh --tier smoke groom/design; echo $?` prints `0` when the suite passes and `1`
      when at least one of its cases fails.
- [ ] Running with `jq` shadowed by a stub that exits non-zero prints no `TOTAL` line, still prints
      both suites' output, and exits with the aggregated promptfoo status.
- [ ] After a plain-mode run, no `promptfoo-eval-*.json` file created by that run remains in
      `${TMPDIR:-/tmp}`.

#### Task 2.3 DoD

- [ ] `bin/eval-run.sh --md --tier smoke groom/de` writes one markdown file containing two
      `# <description>` headings, one per suite.
- [ ] The same run echoes a `report md:` line and one `results json:` line per suite, and those
      JSON files still exist afterwards.
- [ ] The milestone's diff touches `bin/eval-run.sh` only — `git status --porcelain` lists no
      change to `bin/report-md.jq`, which is invoked with `jq -r -f bin/report-md.jq <json>` once
      per suite.
- [ ] `bin/eval-run.sh --md --tier smoke groom/design` produces the same report content as
      `bin/eval-md.sh --filter-metadata tier=smoke -c playbooks/groom/design/promptfooconfig.yaml`
      produces before that script is removed in M3.

---

### M3: Recipe delegation, `bin/eval-md.sh` retirement and docs — 5 SP | pending

**Goal**: the four eval recipes drive `bin/eval-run.sh`, the superseded script is gone, and the
justfile comment block and `CLAUDE.md` describe the selector instead of the `-c`-by-hand form.

**Verify**: `just --list` succeeds; `just smoke --dry-run groom/decompose` prints the
`decompose-work` config path; `just regress --dry-run` lists all eight;
`just smoke -c playbooks/groom/intake/promptfooconfig.yaml` still runs that single suite;
`test ! -e bin/eval-md.sh`.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Replace the four eval recipe bodies with delegations — `eval` → `@bin/eval-run.sh "$@"`, `eval-md` → `@bin/eval-run.sh --md "$@"`, `smoke` → `@bin/eval-run.sh --tier smoke "$@"`, `regress` → `@bin/eval-run.sh --tier regress "$@"` — each keeping `[no-exit-message]` and gaining `[positional-arguments]`. Delete `bin/eval-md.sh` in the same change. | `justfile`, `bin/eval-md.sh` | 2 | pending |
| 3.2 | Rewrite the eval comment block at `justfile:24-26`: the one match rule (the argument is a substring of `playbooks/<playbook>/<step>`; no argument runs every suite; recipe flags precede the selector) plus the canonical invocations `just regress groom/decompose`, `just regress groom/`, `just regress`, `just regress --dry-run groom`, and the note that an explicit `-c` still runs one suite unresolved. | `justfile` | 1 | pending |
| 3.3 | Correct `CLAUDE.md` line 36 — the per-step suites under `playbooks/<name>/<step>/` and the run harness (`bin/eval-run.sh`, `bin/report-md.jq`) are committed in this repo, not vault-side — and add a `bin/eval-run.sh` entry to the `## CLI` section giving the invocation shape, the substring match rule and the exit codes. | `CLAUDE.md` | 2 | pending |

#### Task 3.1 DoD

- [ ] `just --list` succeeds and shows `eval`, `eval-md`, `smoke`, `regress`.
- [ ] `just smoke --dry-run groom/decompose` prints
      `playbooks/groom/decompose-work/promptfooconfig.yaml`.
- [ ] `just regress --dry-run | wc -l` prints `8`.
- [ ] `just smoke -c playbooks/groom/intake/promptfooconfig.yaml; echo $?` runs exactly that suite
      and prints `0` when it passes.
- [ ] `just eval --dry-run groom/design` prints one path, and the corresponding real run applies no
      `--filter-metadata tier=` filter.
- [ ] `just smoke --dry-run` with no further arguments lists all eight suites rather than failing on
      an empty argument list.
- [ ] A failing `just smoke groom/design` prints no `just`-generated error banner, on all four
      recipes.
- [ ] `test ! -e bin/eval-md.sh`, and `grep -rn "eval-md.sh" justfile bin` returns no match.

#### Task 3.2 DoD

- [ ] The comment block no longer contains the string `pass one with -c` and no longer presents
      `-c` as the way to pick a suite.
- [ ] Every invocation the block names is executed once and behaves as the block claims.
- [ ] The block states that recipe flags (`--dry-run`, and the recipes' own `--md` / `--tier`)
      precede the selector.

#### Task 3.3 DoD

- [ ] `grep -n "not in this repo" CLAUDE.md` returns no match on the playbooks bullet.
- [ ] `grep -n "bin/eval-run.sh" CLAUDE.md` matches inside the `## CLI` section.
- [ ] The new CLI entry names the invocation shape, the substring match rule, and exit codes 0 / 1
      / 2.
- [ ] The playbooks bullet names `bin/eval-run.sh` and `bin/report-md.jq` as committed in this repo.

---

## I/O contract

**Arguments / flags** —
`bin/eval-run.sh [--tier smoke|regress] [--md] [--dry-run] [<selector>] [promptfoo args…]`

- `--tier smoke|regress` — appends `--filter-metadata tier=<tier>` to every invocation. Any other
  value is a usage error.
- `--md` — render each suite's results through `bin/report-md.jq` into one combined markdown report
  and show it in `glow`.
- `--dry-run` — print the resolved config paths, one per line, and exit without invoking promptfoo.
- Recipe flags are consumed from the front in any order; the first unrecognised token ends flag
  parsing.
- `<selector>` — the first post-flag argument, taken as a selector only when it does not start with
  `-`. A trailing `/` is stripped; the remainder is matched as a plain case-sensitive substring
  against each suite's directory path relative to the repo root (`playbooks/<playbook>/<step>`).
  Absent selector = every suite.
- Everything from the first unrecognised token onward — minus the selector — passes through to
  promptfoo in order.

**stdin** — nothing is read.

**stdout** — plain text. The script's own additions, interleaved with promptfoo's unmodified output:

- `→ N suite(s): groom/design, groom/draft-plan, …` once before the first invocation, whenever
  N ≥ 1. Every resolved `<playbook>/<step>` is listed, comma-separated, on that one line — never
  truncated or elided, however many resolved.
- `── <playbook>/<step> ──` before each suite's output.
- `TOTAL  <tier|both> · N suite(s) · P passed, F failed, E errored` after the last suite, when
  N ≥ 2. `<tier>` is the `--tier` value; `both` when no tier was given.
- Under `--dry-run`: the resolved config paths only, one per line.
- Under `--md`: a `report md: <path>` line and one `results json: <path>` line per suite.

**stderr** — diagnostics only: the unresolved-`playbooks/_lib` warning, usage-error messages, and
promptfoo's own diagnostics. No content is duplicated between stdout and stderr.

**Exit codes**

- `0` — every resolved suite passed, or nothing resolved, or `--dry-run`.
- `1` — at least one suite exited non-zero, or reported failures or errors, or produced no
  `--output` JSON at all (the config- or provider-level error that aborts the loop). On the
  unresolved explicit-`-c` path, the single promptfoo process's own status is passed through.
- `2` — usage error: unknown `--tier` value, a selector combined with an explicit
  `-c` / `--config` / `--config=…`, or `playbooks/` unreadable.

**Environment** — none read. Temp files are `mktemp -t promptfoo-eval-XXXXXX.json`, one per suite,
deleted after stats extraction in plain mode and kept in `--md` mode.

## Final Verification

- [ ] The `justfile` comment block and the `CLAUDE.md` CLI entry both describe the substring rule
      and are accurate against the shipped script.
- [ ] Happy path verified: `just smoke groom/design` (one suite), `just regress --dry-run groom/`
      (eight suites, no spend), `just regress --dry-run` (every suite).
- [ ] Failure paths verified: `just smoke --dry-run groom -c x.yaml` exits 2;
      `just smoke --dry-run nosuchstep` prints nothing and exits 0; a failing suite exits 1.
- [ ] Exit codes match the documented contract on each of those invocations.
- [ ] `just smoke -c playbooks/groom/intake/promptfooconfig.yaml` — the form the justfile documented
      before this work — still runs exactly that suite.
- [ ] `just lint`, `just typecheck` and `just test` pass (unchanged — no `booping-python/` code is
      touched).
- [ ] `git status` shows no drift under `skills/` or `agents/`; the justfile is outside the
      `src/files/` build pipeline, so no `just build` is triggered.

## Out of scope

- The promptfoo suites themselves — no change to any `playbooks/groom/*/promptfooconfig.yaml`, to
  any `tests.yaml`, or to the `metadata: {playbook, step, tier}` axis.
- `bin/report-md.jq` — it stays per-suite and is not given a multi-run shape.
- `booping render-playbook` and the playbook loader — no CLI or loader change.
- Vault-side playbook roots (`<home_dir>/_playbooks/`, `{vault}/_playbooks/`) — discovery is over
  the core repo `playbooks/` tree only.
- New eval tiers, CI wiring, or eval-result storage.
- An anchored or two-segment selector grammar, and any interactive confirmation prompt — both
  rejected in `## Decisions`.
- Automated test coverage for `bin/eval-run.sh`; the repo has no shell test harness and `just test`
  is pytest over `booping-python/` only. `--dry-run` is the verification handle.

## CLAUDE.md impact

- **Playbooks bullet (line 36)** — the closing sentence "Eval suites + run harness live vault-side
  (`~/Claude/_playbooks/`) with their own README — not in this repo" is corrected: the per-step
  suites under `playbooks/<name>/<step>/` and the run harness (`bin/eval-run.sh`,
  `bin/report-md.jq`) are committed in this repo.
- **`## CLI` section** — gains a `bin/eval-run.sh` entry: invocation shape, the substring match rule,
  the four recipes that delegate to it, and the exit-code contract. The section omits the eval
  recipes entirely today.
