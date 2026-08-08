# research-web — 20260801-12-02_justfile-eval-filtering

## Verdict

Researched — the central design call, how a multi-suite selector (`groom/`, or bare `just regress`) reaches promptfoo, turns on promptfoo's documented multi-config semantics and on just's parameter/shell grammar, neither of which has precedent anywhere in this repository; the obvious answer (expand the selector into repeated `-c` paths) is documented upstream as producing a *single combined* eval rather than one run per suite.

## Approaches

### A. Fan-in — one promptfoo invocation, repeated `-c` / glob

The selector expands to a list of `playbooks/<name>/<step>/promptfooconfig.yaml` paths interpolated into the existing single-line recipe: `npx promptfoo@latest eval --filter-metadata tier=regress -c <path>...`. promptfoo documents both forms — `promptfoo eval -c config1.yaml -c config2.yaml -c config3.yaml` and `promptfoo eval -c my_configs/*`.

- Fits: the recipe stays one line, today's `--filter-metadata tier=` flag and the remaining pass-through args are untouched, and one invocation yields one result set the existing `bin/eval-md.sh` report path can consume unchanged.
- Costs: promptfoo states multiple configs "combine them into a single eval" — the per-step suites' distinct prompts, providers and tests merge into one matrix, so `groom/` and bare `just regress` stop being "run each suite" and become "run one cross-product"; correct only for the single-suite selector `groom/decompose`.
- Retire cost: low — the recipe body reverts to its current single line.

### B. Fan-out — one `promptfoo eval` per resolved suite, looped in the recipe

The selector resolves to a path list and the recipe iterates, invoking promptfoo once per suite. Because non-shebang just recipes are "evaluated and run line-by-line", the loop must be a `#!/usr/bin/env bash` shebang recipe (or a single backslash-continued line).

- Fits: preserves per-suite isolation, which is what "regress groom/" means here — each `promptfoo eval` sees exactly one config, so prompts/providers/tier metadata stay scoped to their own step, and it matches upstream's position (the request for native separate-eval runs, issue #1098, is still open with no built-in mode).
- Costs: N invocations produce N result sets with no aggregate view, and the recipe must author its own exit-status aggregation — with `set -e` in a shebang recipe the first failing suite aborts the remaining ones, so "run all playbooks" needs an explicit fail-fast-vs-run-all decision.
- Retire cost: medium — the two recipes each grow a shebang body, and reverting means deleting shell logic rather than one flag.

### C. Fan-out behind a resolver script (`bin/eval-select.sh`)

The recipes stay one-liners delegating to a bash script that owns selector parsing, path resolution and the per-suite loop — the pattern `eval-md` already uses via `bin/eval-md.sh`.

- Fits: gives the selector grammar room the justfile does not have — prefix/substring step matching (`decompose` → `decompose-work`), the silent no-op on no match, and separating the selector from remaining pass-through args — while keeping both recipes' bodies as short as they are today; `[positional-arguments]` (just 1.29.0+, available on the installed 1.57.0) can hand `$1`/`$@` to the script without interpolation quoting.
- Costs: a new file outside the justfile, where the selector grammar is less discoverable than in the recipe that documents it, and the in-scope surface grows from two recipe lines to a script that itself wants a smoke test.
- Retire cost: low — delete one script and revert two recipe lines.

## Pitfalls

- **Multiple configs merge, they do not fan out.** promptfoo's own guide is explicit: "You can run multiple configs at the same time, which will combine them into a single eval", and issue #1098 reports the same for glob form (`-c configs/*`). This forces the fan-in vs fan-out call up front: the `groom/` and bare-invocation cases cannot be served by widening the `-c` list, only by looping.
- **A leading optional positional swallows a leading flag.** With `regress sel="" *args:`, invoking `just regress -c playbooks/groom/intake/promptfooconfig.yaml` binds `-c` to `sel` and `playbooks/...` to `args` (verified locally on just 1.57.0: `sel=[-c] args=[foo.yaml]`) — flags after a recipe name are passed to the recipe, not to just. That is precisely the invocation the justfile header currently documents, so the design must either reject/ignore a selector beginning with `-` and push it back into `args`, or accept that the documented pass-through form breaks.
- **A `for` loop cannot be written plainly in a just recipe.** Recipes without a shebang are "evaluated and run line-by-line, which means that multi-line constructs probably won't do what you want" (a multi-line loop also trips just's leading-whitespace check outright). This forces approach B or C: shebang recipe, backslash-continued one-liner, or external script — there is no plain-recipe middle ground.
- **Shebang recipes get no error handling for free.** just recommends `set -euxo pipefail` for bash shebang recipes precisely because it makes them "behave more like normal, shell `just` recipes"; `set -e` "makes bash exit if a command fails". On a loop over every playbook's suites this decides whether one red suite ends the run or the loop completes and reports an aggregate — a call the design must make, not inherit.
- **"Silent no-op on no match" is not what a bare glob does.** An unmatched pattern is left as its literal self unless `nullglob` is set — "If no matching filenames are found, and the shell option `nullglob` is disabled, the word is left unchanged" (verified locally: `/nonexistent/*.yaml` expands to itself under `sh`). Interpolating a raw glob therefore hands promptfoo a nonexistent config path and produces a loud error, the opposite of the confirmed scope boundary; resolution must go through an explicit existence test (`find`, or `shopt -s nullglob` inside a bash shebang) rather than shell expansion at the call site.
- **The tier filter is orthogonal and survives either approach.** `--filter-metadata` is "Only run tests whose metadata matches the key=value pair. Can be specified multiple times for AND logic" — it filters *tests within* a config, never selects configs, so it cannot substitute for suite selection and does not need to change. Confirms the intake's open question: selectors map to config paths, not to metadata filters.

## Sources

| Source | Backs | Checked |
| --- | --- | --- |
| https://www.promptfoo.dev/docs/configuration/guide/ | Multiple configs combine into a single eval; both `-c a.yaml -c b.yaml` and `-c my_configs/*` are documented forms | 20260801 |
| https://github.com/promptfoo/promptfoo/issues/1098 | No native per-config separate-eval mode; explicit lists and globs both combine; request still open | 20260801 |
| https://www.promptfoo.dev/docs/usage/command-line/ | `-c, --config <paths...>` takes multiple paths; `--filter-metadata key=value` is repeatable and filters tests, not configs; `--filter-pattern` matches test descriptions | 20260801 |
| https://just.systems/man/en/recipe-parameters.html | Parameters may have default values and be omitted; `*name` variadic takes zero or more args and must be last; interpolations need quoting when they may contain spaces | 20260801 |
| https://raw.githubusercontent.com/casey/just/master/README.md | Non-shebang recipes run line-by-line so multi-line constructs need `\` continuation or a shebang; flags after a recipe name go to the recipe | 20260801 |
| https://just.systems/man/en/safer-bash-shebang-recipes.html | `set -euxo pipefail` is the recommended shebang-recipe preamble; `set -e` exits on the first failing command | 20260801 |
| https://just.systems/man/en/attributes.html | `[positional-arguments]` (introduced in just 1.29.0) exposes recipe parameters as `$1`/`$@` in the body | 20260801 |
| https://www.gnu.org/software/bash/manual/html_node/Filename-Expansion.html | An unmatched glob is left unchanged unless `nullglob` is set; `failglob` errors instead | 20260801 |
