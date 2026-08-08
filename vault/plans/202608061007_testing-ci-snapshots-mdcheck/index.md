---
title: Testing infrastructure — CI, output snapshots, mdcheck gates
type: feature
status: done
sp: 35
split_from: null
created: 2026-08-06 10:07
planned: null
started: 2026-08-06 11:47
completed: 2026-08-06 13:07
retro: null
goal: null
summary: "Hermetic playbook renders, then just snapshots + just mdcheck + just ci,
  wired into parallel CI jobs"
commit: 92ac86008459ee6f2045dd7d337364a0c654cb5e
reviewed_at: 2026-08-06 11:46
code_review: null
sessions:
- f0d60788-fcf6-4d78-87eb-16bff39d6b98
- e3551b68-b224-4c67-9e02-d132bc6f4500
metrics_active_minutes: 164
metrics_models:
- claude-opus-5
metrics_tokens_input: 801
metrics_tokens_output: 356960
metrics_tokens_cache_creation: 2719746
metrics_tokens_cache_read: 62921628
---

# Testing infrastructure — CI, output snapshots, mdcheck gates

## Context

Automated checking stops at `booping-python/`. `.github/workflows/ci.yml` runs ruff, basedpyright and pytest behind `paths: booping-python/**`; everything the plugin ships — rendered skill and agent artefacts, the composed playbook procedures committed at `playbooks/*/_reports/output.md` — is verified only by a human running `just playbook-reports` and reading `git diff`.

The gap cannot be closed by adding a CI step, because **the committed reports are not reproducible today**. Running `just playbook-reports` on a clean tree dirties `playbooks/develop/_reports/output.md` immediately: the report embeds the repo's live HEAD sha. Two further machine-derived values leak in — absolute plugin paths in the groom report, and the operator's machine-global config tier, which `--project` does not pin even though it already pins playbook and lesson discovery.

After this plan: a render under `--project` depends on nothing outside the plugin root and the named vault; `just snapshots` fails on any drift between a fresh render and the committed bytes; `just mdcheck` fails when a report loses a section or a table; `just ci` runs the whole set; and GitHub Actions runs `ci` on every change rather than on `booping-python/**` alone.

## Decisions

- **git HEAD becomes a macro, not a `Context` field**: `core.macros.git_commit` replaces `Project.git_commit` — because a macro is already the one render-time value `--stub-macro` and config-declared `macro_stubs` can pin, and HEAD is exactly the shape of value that needs pinning. A second bespoke pinning mechanism for git would duplicate what macros do.
- **Macros gain an optional `cwd:`, and the argv key is named `command:`**: a macro node may be a mapping `{command: [...], cwd: ...}` alongside today's bare list — `cwd` is `repo` or `vault`, because `git rev-parse HEAD` must resolve against the repo while a macro during a playbook transition runs with cwd set to the run workdir. The bare-list form stays valid and means "process cwd".
- **`@head` retires**: `frontmatter-update`'s `@head` token exists only because a macro could not target the repo directory (`booping-python/src/booping/commands/frontmatter_update.py:68-70` says so in a comment). `cwd: repo` removes that reason, and one way to reach HEAD beats two.
- **`--project` is hermetic**: under `--project`, the machine-global config tier is skipped, matching the discovery pinning already at `booping-python/src/booping/context/__init__.py:95-99`. No new flag — `--project` already means "resolve against this vault, not this machine".
- **Stubs move from flags to the fixture config**: `playbooks/_fixtures/vault/config.yaml` declares a top-level `macro_stubs:` mapping and the justfile drops its four `--stub-macro` flags. Verified working against the current build with no code change — `macro_stubs` is already read from the merged config (`booping-python/src/booping/macros.py:117-123`), so this is a config edit, not a feature.
- **Template paths render relative to the plugin root**: `PlanTemplate.path` / `ReviewTemplate.path` are absolute (`booping-python/src/booping/context/plan_template.py:19-31`) and reach the groom report as five `/home/anton/...` rows. A repo-relative string is both reproducible and more useful to a reader than a path from someone else's machine.
- **The committed reports are the snapshots**: `playbooks/*/_reports/output.md` serves both roles — human-readable report and snapshot baseline. No parallel snapshot file, because two committed copies of the same bytes would drift against each other.
- **Verbs follow insta, not Jest**: `snapshots` validates and `snapshots-accept` takes the new output as the truth. `accept` names the decision being made; `update` reads as maintenance of the tooling. The interactive `review` sibling is not built.
- **`snapshots` never writes; `snapshots-accept` is the only writer**: the check renders into a temp directory and diffs, so it passes or fails identically on a dirty tree and cannot be satisfied by an accidental regeneration. The loop is: edit → `just snapshots` fails with a diff → `just snapshots-accept` → commit.
- **One render worker, `snapshots-render [--fixture] [target]`**: both snapshot recipes and the debug render delegate to it, replacing today's near-duplicate `playbook-reports` / `playbook-reports-live` pair. `--fixture` selects the fixture vault (hermetic, stub-pinned); without it the worker renders the attached project's own vault with macros executed for real. `target` names what to render — every playbook today, and the name deliberately says nothing about playbooks so the snapshot set can grow to skills and agents without a rename.
- **No snapshot library**: `pytest-snapshot` is declared in `booping-python/pyproject.toml:23-27`, unused, and last released in 2022; `syrupy` and `inline-snapshot` are alive but solve a problem this repo does not have, since the baselines are fixed-path committed files. `pytest-snapshot` is dropped rather than adopted.
- **mdcheck rules stay shallow — structure only**: presence and order of sections, and presence plus column headers of the tables inside them. The failures it must catch are "the agents table is gone", "a section disappeared", "a table lost a column". Content assertions belong to the snapshot check, which already catches every byte.
- **mdcheck rules are two-tier**: rule files are YAML `{doc, rules[]}` parsed with `deny_unknown_fields` and support **no** `include:`/`extends:` (`~/Dev/@A/markdown-checker/src/rules.rs:332-340`). One self-contained file per playbook would duplicate the shared shape nine times, so a shared `playbooks/_lib/report.rules.yaml` runs over every report, and an optional per-playbook `playbooks/{name}/_reports/rules.yaml` sits beside the report it checks and names that playbook's own sections and tables.
- **The installed crate is `markdown-checker`, not `mdcheck`**: crates.io `markdown-checker` 0.1.1 points at `github.com/A/markdown-checker`; the crate literally named `mdcheck` is an unrelated package from a different author (`github.com/fibnas/mdcheck`). `mdcheck` is only the binary name. Installing the wrong one is a silent, plausible failure, so the install line is pinned in the recipe's error text.
- **`just mdcheck` hard-fails when the binary is absent**, printing `cargo install markdown-checker`. Local green must mean CI green.
- **Recipe names carry no prefix**: `lint`, `typecheck`, `pytest`, `snapshots`, `snapshots-accept`, `snapshots-render`, `mdcheck`, `ci` — each named for what it checks.
- **CI splits into parallel jobs**: `python`, `snapshots`, `mdcheck` run concurrently for failure attribution; `just ci` remains the single local equivalent.
- **The docs build stays out**: `mkdocs build --strict` remains in `docs.yml` and is not folded into `ci`. mdcheck is scoped to rendered reports and gets no rules over `docs/` or `documentation/`.

## Architecture

Three layers, each depending on the one below.

**Hermeticity (M1–M2).** A render under `--project {vault}` reads only: the plugin root, that vault, and macro stubs declared in that vault's config. Everything machine-derived is either removed (global config tier), made relative (template paths), or routed through the macro mechanism where a stub can pin it (git HEAD). The `cwd:` field is what lets a repo-targeting command be a macro at all.

**Check recipes (M3–M4).** `snapshots-render` is the worker: it renders a target set to a destination, hermetically under `--fixture` and against the live vault without it. `snapshots` points it at a temp directory and diffs the result against the committed baselines; `snapshots-accept` points it at the committed paths. The target set is every playbook today, and the worker's contract is written so adding skills or agents to it later is a new target, not a new recipe. Both inherit the existing `**STOP` guard. `mdcheck` runs the shared rule file once over every report, then each per-playbook `rules.yaml` against its sibling. `just ci` = `lint typecheck pytest snapshots mdcheck`.

**CI (M5).** Three jobs. `python` keeps today's uv path (bumped to `setup-uv@v9` with `enable-cache: true`). `snapshots` needs uv + just. `mdcheck` needs a Rust toolchain, `Swatinem/rust-cache@v2` and `cargo install markdown-checker` — the crate publishes no prebuilt binaries, so `taiki-e/install-action` and `cargo-binstall` would both fall back to source compilation anyway, making plain `cargo install` plus a cache the honest choice.

Callers affected outside the CLI: `playbooks/develop/intake/base.md` and `src/templates/_partials/_project_context.j2` read `context.project.git_commit`; `playbooks/develop/playbook.yaml:31` uses `@head`. All three move to the macro.

## Milestones

### M1: Macro `command:` / `cwd:` and git HEAD as a macro — 8 SP | done

**Goal**: `git rev-parse HEAD` reaches templates and transition hooks through `core.macros.git_commit`, resolving against the repo regardless of process cwd; `Project.git_commit` and the `@head` token are gone.

**Verify**:
```
cd booping-python && uv run pytest && uv run ruff check . && uv run basedpyright
cd /tmp && /home/anton/Dev/@A/claude-booping/bin/booping render-playbook develop --project /home/anton/Dev/@A/claude-booping/playbooks/_fixtures/vault | grep 'current HEAD'
```
The second command prints the same sha as `git -C /home/anton/Dev/@A/claude-booping rev-parse HEAD`, despite cwd being `/tmp`.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Macro node accepts a mapping form with keys `command` and `cwd` beside the bare list; `cwd` is `repo` or `vault` and resolves to that directory, defaulting to process cwd; cache key includes the resolved cwd | `booping-python/src/booping/macros.py`, `booping-python/tests/macros_test.py` | 3 | done |
| 1.2 | Thread repo and vault directories into `make_macro` at all three call sites | `booping-python/src/booping/macros.py`, `booping-python/src/booping/rendering.py`, `booping-python/src/booping/commands/render_playbook.py`, `booping-python/src/booping/commands/frontmatter_update.py` | 2 | done |
| 1.3 | Declare `core.macros.git_commit`; move both render surfaces onto it; delete `Project.git_commit` and `_resolve_git_commit` | `src/config.yaml`, `playbooks/develop/intake/base.md`, `src/templates/_partials/_project_context.j2`, `booping-python/src/booping/context/project.py`, `booping-python/tests/context/project_test.py` | 2 | done |
| 1.4 | Retire `@head`: hook line uses the macro, token and its branch removed from `frontmatter-update` | `booping-python/src/booping/commands/frontmatter_update.py`, `playbooks/develop/playbook.yaml`, `playbooks/develop/_specs/states.md`, `booping-python/tests/commands/frontmatter_update_test.py` | 1 | done |

#### Task 1.1 DoD

- [x] A macro declared as a bare list behaves exactly as before — existing tests pass unmodified.
- [x] A macro declared with `command: [git, rev-parse, HEAD]` and `cwd: repo` runs with cwd set to the repo directory, asserted from a test whose process cwd is elsewhere.
- [x] `cwd: vault` resolves to the vault directory; an unknown `cwd:` value raises `MacroError` naming the offending value and the legal set.
- [x] A mapping node missing `command`, or carrying an unknown key, raises `MacroError` naming the config path.
- [x] Two calls to the same macro with the same arguments but different resolved cwd are cached separately.

#### Task 1.2 DoD

- [x] `make_macro` accepts the repo and vault directories; all three call sites pass what they have.
- [x] A call site with neither available still works — `cwd: repo` with no repo known raises `MacroError` naming the macro, rather than silently running in process cwd.
- [x] `basedpyright` clean.

#### Task 1.3 DoD

- [x] `booping config-get core.macros.git_commit` prints the mapping.
- [x] `playbooks/develop/intake/base.md` and `_project_context.j2` render the sha via `macro('core.macros.git_commit')`.
- [x] `grep -rn "git_commit" booping-python/src` returns no `Project` field and no resolver function.
- [x] `bin/booping debug-context` no longer lists `git_commit` under `project` and does not error.
- [x] Rendering a skill body outside a git repo yields the macro's error path, not a traceback.

#### Task 1.4 DoD

- [x] `playbooks/develop/playbook.yaml` hook reads `frontmatter-update commit="{{ macro('core.macros.git_commit') }}"`.
- [x] `frontmatter-update {plan} commit=@head` no longer resolves specially — `@head` is written through as a literal.
- [x] `--help` text no longer mentions `@head`.
- [x] A develop transition onto `in-progress` stamps the same sha as `git rev-parse HEAD`, exercised by the existing transition test.

---

### M2: Hermetic `--project` renders — 7 SP | done

**Goal**: a report rendered under `--project` is byte-identical across machines, checkouts and working directories.

**Verify**:
```
just snapshots-accept && git diff --exit-code -- playbooks/
cd /tmp && HOME=/tmp/fakehome XDG_CONFIG_HOME=/tmp/fakehome/.config /home/anton/Dev/@A/claude-booping/bin/booping render-playbook groom --project /home/anton/Dev/@A/claude-booping/playbooks/_fixtures/vault | diff - /home/anton/Dev/@A/claude-booping/playbooks/groom/_reports/output.md
```
Both exit 0. Until M3 lands, the first command is `just playbook-reports`.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | `--project` skips the machine-global config tier | `booping-python/src/booping/context/__init__.py`, `booping-python/tests/context/context_test.py` | 2 | done |
| 2.2 | `PlanTemplate.path` / `ReviewTemplate.path` render relative to the plugin root | `booping-python/src/booping/context/plan_template.py`, `booping-python/src/booping/context/review_template.py`, `playbooks/_partials/plan_templates.md`, `booping-python/tests/context/plan_template_test.py` | 2 | done |
| 2.3 | Fixture vault declares `macro_stubs:`; justfile drops its `--stub-macro` flags | `playbooks/_fixtures/vault/config.yaml`, `justfile` | 1 | done |
| 2.4 | Regenerate every report; confirm byte-stability under a foreign `HOME`, `XDG_CONFIG_HOME` and cwd | `playbooks/*/_reports/output.md` | 2 | done |

#### Task 2.1 DoD

- [x] With `--project`, `Config.load` receives only the vault override path — no global tier.
- [x] Without `--project`, the global tier still merges; a regression test asserts both branches.
- [x] A value set only in the machine-global config is absent from a `--project` render, asserted by a test writing a global config into the isolated `XDG_CONFIG_HOME` from `booping-python/tests/conftest.py:9-32`.

#### Task 2.2 DoD

- [x] The `Read from` column of the groom report carries repo-relative paths, with no leading `/`.
- [x] `grep -rn "/home/" playbooks/*/_reports/output.md` matches only the static example prose in the `setup` and `migrate` reports — no derived path.
- [x] Any other consumer of `.path` still resolves the file, or is updated in the same task.

#### Task 2.3 DoD

- [x] `playbooks/_fixtures/vault/config.yaml` declares a top-level `macro_stubs:` covering every macro call shape the shipped playbooks make, `core.macros.git_commit` included.
- [x] The fixture render invocation passes only `--project` and `--output`.
- [x] The live render path still executes macros for real — stubs must not leak into it.

#### Task 2.4 DoD

- [x] Regenerating every report leaves `git diff --exit-code -- playbooks/` clean.
- [x] The same holds after committing an unrelated file — HEAD moving does not dirty a report.
- [x] Rendering from a different cwd with a foreign `HOME` and `XDG_CONFIG_HOME` produces byte-identical output.

---

### M3: Snapshot recipes and the `ci` aggregate — 7 SP | done

**Goal**: `just snapshots` fails on report drift without touching the tree, `just snapshots-accept` is the only writer, and `just ci` runs every check CI runs.

**Verify**:
```
just ci
printf '\ndrift\n' >> playbooks/groom/_reports/output.md && ! just snapshots && just snapshots-accept && git diff --stat -- playbooks/; git checkout -- playbooks/
```
The first exits 0. The second shows `snapshots` failing on injected drift, `snapshots-accept` restoring the rendered bytes, and the tree ending clean.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | `snapshots-render [--fixture] [target]` worker recipe, replacing `playbook-reports` and `playbook-reports-live` | `justfile` | 3 | done |
| 3.2 | `snapshots` (render to a temp dir, diff, no writes) and `snapshots-accept` (write the committed reports), both delegating to the worker | `justfile` | 2 | done |
| 3.3 | Rename `test` → `pytest`; add the `ci` recipe chaining lint, typecheck, pytest, snapshots, mdcheck | `justfile` | 1 | done |
| 3.4 | Drop the unused `pytest-snapshot` dev dependency | `booping-python/pyproject.toml`, `booping-python/uv.lock` | 1 | done |

#### Task 3.1 DoD

- [x] `snapshots-render --fixture` renders against `playbooks/_fixtures/vault` and writes the committed `_reports/output.md` paths.
- [x] Without `--fixture` it renders the attached project's own vault with macros executed for real, writing the gitignored `_reports/local.md`.
- [x] An optional trailing argument narrows the run to one playbook, as `playbook-reports groom` does today.
- [x] The destination directory is overridable so `snapshots` can target a temp dir.
- [x] A `**STOP` notice in any fixture render fails the recipe, naming every affected playbook — today's `justfile:39-42` behaviour, preserved.
- [x] `playbook-reports` and `playbook-reports-live` no longer exist.

#### Task 3.2 DoD

- [x] `just snapshots` writes nothing under `playbooks/` — asserted by running it on a dirty tree and confirming the dirt is unchanged.
- [x] It exits non-zero and prints a unified diff naming each drifted report.
- [x] `just snapshots-accept` writes exactly the committed report paths and nothing else.
- [x] `just snapshots` exits 0 immediately after `just snapshots-accept` on a clean checkout.

#### Task 3.3 DoD

- [x] `just --list` shows `pytest`, `snapshots`, `snapshots-accept`, `snapshots-render`, `mdcheck`, `ci`; no bare `test`.
- [x] `just ci` runs all five stages in order and stops at the first failure.
- [x] `ci` calls `snapshots`, never `snapshots-accept` — CI must never rewrite a baseline.
- [x] The recipe is the single definition of the check set — the workflow names jobs, never stage lists.

#### Task 3.4 DoD

- [x] `pytest-snapshot` is absent from `pyproject.toml` and the lockfile.
- [x] `uv sync && uv run pytest` passes.

---

### M4: mdcheck structural rules — 6 SP | done

**Goal**: a report that loses a section, or a table inside a section, fails with a file, line and rule id.

**Verify**:
```
just mdcheck
sed -i '/^## Available Agents/,/^## Shared instructions/d' playbooks/groom/_reports/output.md && ! just mdcheck; git checkout -- playbooks/
```
The first exits 0; the second confirms a deleted section and its table are caught.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Shared rule file over the framework-guaranteed structure | `playbooks/_lib/report.rules.yaml` | 2 | done |
| 4.2 | Per-playbook rule files naming each playbook's own sections and tables | `playbooks/{name}/_reports/rules.yaml` | 2 | done |
| 4.3 | `mdcheck` recipe: PATH check with install hint, shared run plus a per-playbook loop, failure aggregation | `justfile` | 2 | done |

#### Task 4.1 DoD

- [x] Asserts a `## Playbook Steps` section exists, holding a table whose columns are exactly `Step`, `Dependencies`, `Summary`, `Review gate`.
- [x] Asserts that when a `## State` section exists it holds a table with columns exactly `Status`, `To`, `When`, `Gates` — expressed with a rule-level `optional:` so a stateless playbook passes.
- [x] Asserts section order with `ordered:`, marking `## Lessons`, `## State` and `## Subgraph: …` optional with a trailing `?`.
- [x] Asserts at least one `## Step:` section per report, and that no line begins `**STOP — tell the user:**`.
- [x] No assertion reaches into section prose — structure only.
- [x] Passes against all nine committed reports unmodified.

#### Task 4.2 DoD

- [x] Each playbook whose preamble renders a table gets a rule requiring that section and that table's columns — `## Available Agents` with `agent` / `good for` / `bad for` is the case that motivated this.
- [x] `groom` requires `## State`; `migrate` requires `## Subgraph: apply`; `playbook-authoring` requires `## Subgraph: step-pipeline` and `## State`.
- [x] Each file names that playbook's own step sections, so a dropped step fails.
- [x] A playbook with no local `rules.yaml` is skipped silently, not reported as an error.

#### Task 4.3 DoD

- [x] Missing `mdcheck` on PATH → exit non-zero, with stderr naming `cargo install markdown-checker` verbatim.
- [x] The shared file runs once over `playbooks/*/_reports/output.md`; each local `rules.yaml` runs against its sibling `output.md`.
- [x] Every failing report is reported, not just the first, and the recipe exits non-zero once at the end.
- [x] mdcheck exit 2 or 3 (rule-file or internal error) is surfaced distinctly from exit 1 (findings).

---

### M5: CI workflow — 5 SP | done

**Goal**: every push and pull request runs the full check set as three parallel jobs.

**Verify**: push the branch and confirm all three jobs pass; `gh workflow view ci` lists jobs `python`, `snapshots`, `mdcheck`.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | Restructure `ci.yml`: drop path filters, three parallel jobs, `setup-uv@v9` with `enable-cache: true`, `extractions/setup-just@v4` | `.github/workflows/ci.yml` | 3 | done |
| 5.2 | `mdcheck` job: Rust toolchain, `Swatinem/rust-cache@v2`, `cargo install markdown-checker` pinned to a version | `.github/workflows/ci.yml` | 2 | done |

#### Task 5.1 DoD

- [x] No `paths:` filter — the workflow fires on every push to `master` and every pull request.
- [x] Jobs `python`, `snapshots` and `mdcheck` run in parallel, each calling one `just` recipe.
- [x] The `snapshots` job calls `just snapshots`, never `just snapshots-accept`.
- [x] `defaults.run.working-directory: booping-python` no longer applies to jobs running repo-root recipes.
- [x] `setup-uv@v9` with `enable-cache: true`.
- [x] `just` is installed via `extractions/setup-just@v4` — it is not preinstalled on `ubuntu-latest`.

#### Task 5.2 DoD

- [x] `cargo install markdown-checker --version 0.1.1 --locked` — pinned, and not the unrelated `mdcheck` crate.
- [x] `Swatinem/rust-cache@v2` present so a warm run does not recompile.
- [x] The job fails if `mdcheck --version` is not on PATH after the install step.

---

### M6: Documentation — 2 SP | done

**Goal**: `CLAUDE.md` describes the macro `command:` / `cwd:` node, the hermetic `--project` guarantee and the new recipe set, and no longer carries the retired `@head` or the wrong default-branch name.

**Verify**: `grep -n '@head\|playbook-reports\|deploy.*on push to .main' CLAUDE.md` returns nothing.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 6.1 | Update the CLI, Layout, Config schema and Editing conventions sections; fix the `main` → `master` error | `CLAUDE.md` | 2 | done |

#### Task 6.1 DoD

- [x] `core.macros.{name}` documents the mapping node — keys `command` and `cwd`, both legal `cwd` values — alongside the surviving bare-list form.
- [x] `render-playbook --project` documents that it pins the config tiers as well as discovery.
- [x] `frontmatter-update` no longer documents `@head`.
- [x] The justfile recipe list names `pytest`, `snapshots`, `snapshots-accept`, `snapshots-render`, `mdcheck` and `ci`, and no longer names `playbook-reports` or `playbook-reports-live`.
- [x] Editing conventions describe the snapshot loop — edit, `just snapshots`, `just snapshots-accept`, commit — and name `just ci` as the full drift check.
- [x] Both "push to `main`" claims (lines 37 and 238) read `master`.
- [x] The mdcheck dependency is documented with the exact crate name and the reason the binary name differs.

---

## I/O contract

The CLI surface is unchanged except where named below.

- **`core.macros.{name}`** — accepts either today's bare list, or a mapping with `command:` (the argv list) and optional `cwd:` (`repo` or `vault`). `cwd` omitted → process cwd, as today.
- **`booping render-playbook --project {path}`** — now additionally skips the machine-global config tier. Same arguments, same stdout shape.
- **`booping frontmatter-update`** — loses the `@head` token; `@head` becomes an ordinary literal value. `--help` updated.
- **`just pytest`** — stdout and exit code are pytest's.
- **`just snapshots`** — renders to a temp directory and diffs. stdout: a unified diff per drifted report, or nothing. Exit `0` clean, `1` on drift or a `**STOP` notice. Writes nothing under `playbooks/`.
- **`just snapshots-accept`** — rewrites `playbooks/*/_reports/output.md`. stdout: the paths written. Exit `0`, or `1` on a `**STOP` notice.
- **`just snapshots-render [--fixture] [target]`** — the worker. `--fixture` renders hermetically against the fixture vault; without it, the attached project's vault with macros executed. `target` defaults to every playbook and narrows to one by name; the argument is what a future skills or agents snapshot set plugs into.
- **`just mdcheck`** — stdout: mdcheck findings (`file:line  check  message`). Exit `0` clean, `1` on findings; non-zero with an install hint on stderr when the binary is missing.
- **`just ci`** — stdout: each stage's. Exit: the first non-zero stage's.

Error surfaces: a malformed macro node, an unknown `cwd:` value, or `cwd: repo` with no repo resolvable all raise `MacroError` naming the config path, exiting non-zero with the message on stderr.

## Final Verification

- [ ] `just ci` exits 0 on a clean tree.
- [ ] Injected drift in any report fails `just snapshots`; a deleted section or table fails `just mdcheck`.
- [ ] `just snapshots` leaves the working tree untouched, verified on a dirty tree.
- [ ] A render under `--project` is byte-identical with a foreign `HOME`, `XDG_CONFIG_HOME` and cwd.
- [ ] Committing an unrelated file does not dirty any report.
- [ ] All three CI jobs pass on the pushed branch.
- [ ] `just build` produces no drift in `skills/` or `agents/`.

## Out of scope

- **Build-artefact snapshots** — no gate over `skills/` or `agents/` drift from `just build`.
- **Per-step render snapshots** — only composed reports are snapshotted.
- **Python-side render snapshot tests** — no `syrupy` / `inline-snapshot` adoption; `pytest-snapshot` is removed, not replaced.
- **mdcheck content assertions** — structure only; no rules over prose inside a section.
- **mdcheck over anything but rendered reports** — no rules for playbook sources, `docs/` templates, `documentation/`, or vault artefacts.
- **`mkdocs build --strict` in `ci`** — it stays in `docs.yml`.
- **Publishing work in the `markdown-checker` repo** — already published as `markdown-checker` 0.1.1.
- **Eval suites** — `just eval` / `smoke` / `regress` stay out of `ci`; they cost model calls.
- **`documentation/` pages describing the check pipeline** — `CLAUDE.md` only.

## CLAUDE.md impact

Updated in M6:

- `## CLI` — `render-playbook --project` config-tier pinning; `frontmatter-update` losing `@head`.
- `## Config schema` → `core.macros.{name}` — the `command:` / `cwd:` mapping node.
- `## Layout` — the justfile recipe list.
- `## Editing conventions` — the snapshot loop and `just ci` as the drift check; the two wrong `main` references.
