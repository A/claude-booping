---
reviewed_at: 20260801 05:30
---

# design — 20260801-12-02_justfile-eval-filtering

## Approach

One new script, `bin/eval-run.sh`, owns selector parsing, suite resolution and the per-suite loop;
all four eval recipes in `justfile` become one-liners that delegate to it. This is the split the
repo already uses at `justfile:35-36` → `bin/eval-md.sh` (a recipe stays a one-liner; branching
lives in a `bin/*.sh` the repo can run directly), and it is the only shape that survives the two
hard constraints the research found: promptfoo's `combineConfigs` merges a multi-`-c` invocation
into a single cross-product eval, so a multi-suite selector must become N sequential processes;
and a non-shebang `just` recipe runs line-by-line, so the loop cannot live in the recipe body
without giving each of the four recipes its own shebang and a copy of the same shell.

**Resolution is enumerate-then-filter, with one match rule.** The script resolves the repo root
from its own location (`here=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)`, then `cd` to its
parent — the `bin/booping` precedent) and enumerates *every* suite first:
`playbooks/*/*/promptfooconfig.yaml` under `shopt -s nullglob`, so an unmatched pattern yields an
empty list instead of its own literal text (equivalent to `find playbooks -mindepth 3 -maxdepth 3
-name promptfooconfig.yaml`; the glob is chosen because the `_`-exclusion is two `case` tests
rather than `find` prune predicates). A path component starting with `_` is never a playbook or a
step: `playbooks/_lib`, `playbooks/groom/_scripts/`, `playbooks/groom/_specs/` and any
`<step>/_fixtures/` are excluded by the same rule the playbook loader applies, not by glob depth. A
step directory without a `promptfooconfig.yaml` is not a suite and is skipped. Discovery is over
the core repo `playbooks/` tree only — 8 suites under `playbooks/groom/` today; no vault root is
consulted. Nothing inside a `promptfooconfig.yaml` is read: a suite is fully identified by its
directory path.

**The selector is a plain substring filter over that list — there is no grammar.** Each enumerated
suite is reduced to its directory path relative to the repo root (`playbooks/groom/design`,
`playbooks/groom/decompose-work`, …); a suite is selected when that path contains the selector as a
case-sensitive substring. One rule covers every form the request named and several it did not:
`groom`, `groom/`, `playbooks/groom` and `playbooks/groom/` all match the whole playbook;
`groom/decompose`, `decompose`, `decompose-work` and `compose` all match the one step;
`design` matches that step in any playbook. The only normalisation is stripping trailing `/` from
the selector (so a tab-completed `groom/design/` still matches — `sweep.sh`'s `${1%/}` precedent).
Matching is against the suite *directory*, not the config path, so `config`, `promptfoo` or `yaml`
select nothing rather than everything. A multi-hit selector is not an error — the runner is already
N-ary, and `groom/` matching eight suites is the same operation as `groom/de` matching two. Because
the filter runs after `_`-exclusion, a selector naming an excluded directory (`_lib`, `_fixtures`)
matches nothing. Zero matches short-circuit before any promptfoo invocation: nothing is printed,
exit 0 (the confirmed no-op), which also avoids promptfoo's fallback of auto-loading a
non-existent `./promptfooconfig.yaml`.

**Selector vs pass-through args.** The recipes keep their single `*args` variadic — no
`sel=""` parameter — so a leading flag cannot be bound to a selector by `just`. The script takes
the selector to be its first non-recipe-flag argument only when that argument does not start with
`-`; every remaining argument passes through to promptfoo in order. This is `sweep.sh`'s rule
(`[ "${1#-}" = "$1" ]`) and it keeps `just smoke -c playbooks/groom/intake/promptfooconfig.yaml`
working exactly as the justfile documents today.

**Explicit `-c` decides whether resolution happens at all.** An absent selector means *all
suites*, except when the pass-through args already carry `-c` / `--config` / `--config=…`: then no
resolution runs and the args go to one promptfoo process unchanged (the legacy form). A selector
*and* an explicit `-c` together are rejected with exit 2, because passing both to one process is
precisely the silent cross-product `combineConfigs` produces.

**Execution and aggregation.** One `npx promptfoo@latest eval -c <config> [--filter-metadata
tier=<tier>] <args…> --output <tmp>.json` per resolved suite, sequential, `set -uo pipefail`
without `set -e` so a red suite does not abort the sweep. Each suite's promptfoo output streams to
the terminal under a one-line `── <playbook>/<step> ──` header. Per-suite stats are read back from
the `--output` JSON with `jq` and summed into a single `TOTAL` line printed when two or more
suites ran (single-suite runs stay byte-similar to today). The run's exit code is 1 if any suite
exits non-zero or reports failures/errors, else 0. If `jq` is unavailable the totals line is
skipped and the exit code falls back to the aggregated promptfoo exit codes.

**Cost guards.** Every run that resolves at least one suite announces what it is about to do —
`→ 3 suite(s): groom/design, groom/draft-plan, groom/decompose-work` — on one line before the
first invocation, and never prompts. With a single substring rule the set a selector reaches is
wider than a two-segment grammar's, so the announce line is doing more work here than it was: it is
the moment an over-broad `groom/de` or a bare judged sweep of all eight suites becomes visible, and
it stays safe in CI and non-interactive shells. A suite that produces no `--output` JSON at all is
a config- or provider-level error rather than a test failure; the loop aborts there instead of
repeating a doomed, judge-billed run across the remaining seven suites. `--dry-run` prints the
resolved config paths, one per line, and exits 0 without invoking promptfoo — the way to check a
selector before a judged sweep, and the only automated-verification handle a new `bin/*.sh` gets in
a repo whose `just test` is pytest over `booping-python/` only. If `playbooks/_lib` does not
resolve (it is a symlink to an out-of-repo vault directory, so a fresh clone has none), one stderr
warning is printed before the first run.

**Markdown reports.** `bin/eval-md.sh` is folded into `bin/eval-run.sh` behind a `--md` flag
rather than kept beside it — two scripts would each need the same selector parser. In `--md` mode
each suite's `--output` JSON is rendered through the unchanged `bin/report-md.jq` and appended to
one combined markdown file, whose per-suite `# <description>` first line already acts as a section
heading; a single `glow -w "$(tput cols)"` shows the combined document at the end, and the report
plus JSON paths are echoed as today. `bin/report-md.jq` stays per-suite and is not given a
multi-run shape.

**Documentation.** The justfile comment block at `justfile:24-26` currently teaches the `-c`-by-hand
form the selector replaces and is rewritten to the one match rule; `CLAUDE.md:36` ("Eval suites +
run harness live vault-side … not in this repo") is corrected, and the recipe contract is added to
CLAUDE.md's CLI section, which omits the eval recipes entirely today.

## Surface changes

**New: `bin/eval-run.sh`** (mode `755`, `#!/usr/bin/env bash`, `set -uo pipefail`,
`shopt -s nullglob`)

```
bin/eval-run.sh [--tier smoke|regress] [--md] [--dry-run] [<selector>] [promptfoo args…]
```

- Recipe flags are consumed from the front in any order until the first unrecognised token:
  `--tier <smoke|regress>` appends `--filter-metadata tier=<tier>` to every invocation; `--md`
  switches on report rendering; `--dry-run` prints resolved paths and exits. Any other `-`-leading
  token ends flag parsing and passes through.
- Selector: any single substring, taken only if it is the first post-flag argument and does not
  start with `-`; trailing `/` stripped; matched case-sensitively against each suite's directory
  path relative to the repo root (`playbooks/<playbook>/<step>`).
- Resolution: enumerate `playbooks/*/*/promptfooconfig.yaml` with any `_`-prefixed playbook or step
  component excluded, then keep the entries whose directory path contains the selector; no selector
  keeps all of them.
- Exit codes: `0` all resolved suites passed, or nothing resolved, or `--dry-run`; `1` at least
  one suite failed or errored; `2` usage error — unknown `--tier` value, selector combined with an
  explicit `-c`/`--config`, or `playbooks/` unreadable.
- Env: none read; `--output` temp files are `mktemp -t promptfoo-eval-XXXXXX.json`, deleted after
  stats extraction in plain mode and kept (with paths echoed) in `--md` mode.
- Stdout additions: `→ N suite(s): groom/design, groom/draft-plan, …` before the first suite
  whenever N ≥ 1; `── <playbook>/<step> ──` before each suite; `TOTAL  <tier|both> · N suite(s) ·
  P passed, F failed, E errored` after the last suite when N ≥ 2.

**Changed: `justfile`** — the four eval recipes become delegations, each keeping
`[no-exit-message]` and gaining `[positional-arguments]` so the body can use `"$@"` instead of
`{{ args }}` interpolation (available on the installed just 1.57.0; the attribute landed in 1.29.0):

```just
[no-exit-message]
[positional-arguments]
eval *args:
    @bin/eval-run.sh "$@"

[no-exit-message]
[positional-arguments]
eval-md *args:
    @bin/eval-run.sh --md "$@"

[no-exit-message]
[positional-arguments]
smoke *args:
    @bin/eval-run.sh --tier smoke "$@"

[no-exit-message]
[positional-arguments]
regress *args:
    @bin/eval-run.sh --tier regress "$@"
```

**Changed: `justfile:24-26` comment block** — replaced with the one match rule ("the argument is a
substring of `playbooks/<playbook>/<step>`; no argument runs every suite") and the canonical
invocations: `just regress groom/decompose` (one step), `just regress groom/` (one playbook),
`just regress` (every suite), `just regress groom --dry-run` (resolution only), plus the note that
an explicit `-c` still runs a single suite unresolved.

**Deleted: `bin/eval-md.sh`** — its body (temp JSON, `report-md.jq` render, `glow`, echoed paths,
promptfoo exit code passthrough) moves into `bin/eval-run.sh`'s `--md` path.

**Unchanged:** `bin/report-md.jq`, every `playbooks/groom/*/promptfooconfig.yaml`, every
`tests.yaml` and its `metadata: {playbook, step, tier}`, and the `--filter-metadata tier=` axis.

**Changed: `CLAUDE.md`** — line 36's "Eval suites + run harness live vault-side … not in this repo"
corrected to state that the per-step suites under `playbooks/<name>/<step>/` and the run harness
(`bin/eval-run.sh`, `bin/report-md.jq`) are committed here; a `bin/eval-run.sh` entry added to the
CLI section listing the substring match rule and the exit codes.

## Alternatives

- **A two-segment selector grammar, `<playbook>[/[<step-substring>]]`, with the playbook segment
  matched exactly and only the step segment matched as a substring.** Lost because it needs a parse,
  a split rule and an error class of its own (a `_`-prefixed or unknown playbook segment) to reach
  the same suites a single substring filter reaches with one comparison — and the precision it buys
  over the flat filter is precision the announce line and `--dry-run` already supply.
- **Matching the selector against the full config path (`…/promptfooconfig.yaml`) rather than the
  suite directory.** Lost because `config`, `promptfoo` and `yaml` would then select every suite.
- **A `y/N` confirmation above a resolved-count threshold.** Lost because it makes four recipes
  interactive, which then needs a `--yes` flag and a non-TTY bypass; the announce line plus
  `--dry-run` cover the same cost risk without either.
- **Fan-in: expand the selector into repeated `-c` paths on one promptfoo process.** Lost because
  promptfoo documents multiple configs as combining "into a single eval" — each step's tests would
  be graded against every other step's prompt and provider.
- **Fan-out looped inside `just` shebang recipes.** Lost because it puts the same loop, the same
  `set -euo pipefail` preamble and the same resolution logic into four recipe bodies, against the
  repo's one-liner-recipe convention.
- **A recipe parameter `sel="" *args:` to capture the selector in `just` itself.** Lost because a
  leading optional positional binds `-c` as the selector (verified on just 1.57.0), breaking the
  pass-through form the justfile currently documents.
- **`--filter-metadata step=<step>` instead of path resolution.** Lost because `--filter-metadata`
  filters tests *within* a config and cannot select configs, so it still needs a `-c` and cannot
  express `groom/` at all.
- **Porting the vault harness `~/Claude/_playbooks/_scripts/sweep.sh` wholesale.** Lost because it
  brings a per-suite `report.jq`, a `SWEEP_PROGRESS_FILE` ticker coupled to the out-of-repo
  provider, and log-file redirection into the repo — far more surface than resolution plus a loop.
- **A path-emitting resolver (`bin/eval-select.sh`) that the recipes consume.** Lost because the
  caller of a path list still has to loop, which puts the loop back in the recipes.
- **Keeping `bin/eval-md.sh` and giving it its own selector handling.** Lost because the selector
  parser would exist twice and drift.

## Trade-offs

No call is left for the user: the one cost question this work raised — what a bare `just regress`
does before it starts spending on 8 suites of opus-judged cases — is settled in `## Approach` as
announce-then-run (one line naming the resolved suites, never a prompt), with `--dry-run` as the
see-without-running path; the alternatives it displaces are recorded above.

## Risks

- **One flat substring rule matches more than a user means.** A short selector reaches far
  (`o` matches five of today's eight steps, `e` nearly all), a playbook name is no longer anchored
  to the playbook segment, so a future `groom-lite` or `regroom` playbook silently joins every
  `just regress groom` run, and a step name shared across playbooks (`design`, `intake`) selects
  all of its copies. This is the cost the user accepted for one rule instead of two, and it grows
  as the `playbooks/` tree grows. Mitigation: the announce line prints the resolved suite names
  before any invocation, `--dry-run` shows them without spending, and the `TOTAL` line names the
  count that actually ran — an unintended match is visible within one line of scrollback, not after
  the bill. If the tree ever makes this bite, an anchored form (`^`-prefixed or exact-path
  selector) is an additive filter tweak on the same enumerate-then-filter shape.
- **A typo resolves to nothing and exits 0 silently** — the confirmed policy, so a mistyped
  `just regress groom/desgin` looks like a clean pass. Mitigation: exit 0 with no output is
  deliberate; `--dry-run` is the check, and the announce line's absence is the tell — with the
  announce line printed on every non-empty resolution, "no line, no output" is now the single
  unambiguous signature of a zero match. Residual risk accepted by the confirmed scope.
- **A broken `playbooks/_lib` symlink makes every suite fail identically.** It is untracked and
  points outside the repo, so a fresh clone has zero working suites. Mitigation: one stderr warning
  when it does not resolve, plus the abort-on-no-results rule, which stops the sweep at the first
  suite instead of erroring through all eight.
- **An unmatched glob would otherwise be handed to promptfoo as a literal path.** Mitigation:
  `shopt -s nullglob` plus an explicit count check before the loop, so zero matches never reach an
  invocation.
- **Run-all instead of fail-fast can spend judge calls after the first red suite.** Mitigation:
  test failures continue by design (an aggregate is the point), while a suite producing no results
  at all — a config or provider error — aborts the run.
- **`bin/eval-run.sh` ships with no automated coverage**; `just test` is pytest over
  `booping-python/` and CI never invokes promptfoo. Mitigation: `--dry-run` makes resolution
  verifiable without cost, and the selector cases (`groom/decompose`, `groom/`, bare, `_`-skipping,
  zero-match, selector + `-c`) are checkable by hand from it.
- **Plain-mode totals add a `jq` dependency to `eval`/`smoke`/`regress`**, which previously needed
  only `npx`. Mitigation: `jq` is already required by the report path, and its absence degrades to
  per-suite output plus an aggregated exit code rather than failing the run.
- **Temp JSON accumulation in `$TMPDIR`** grows by one file per suite in `--md` mode. Mitigation:
  plain mode deletes its temp JSON after reading stats; `--md` keeps them deliberately and echoes
  the paths, as `bin/eval-md.sh` does today.
