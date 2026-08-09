---
title: Scaffold-seeded plan creation and a scaffold receipt contract
type: feature
status: in-progress
sp: 24
related_to: null
created: 2026-08-09 13:10
planned: null
started: 2026-08-09 13:46
completed: null
code_reviews: []
sessions:
- b1cf1fe7-f86c-4335-9434-c95e92d29a8c
- b74396a9-b99a-442d-9be4-9c58e6c11d5c
retro: null
agents:
  cross-review: ad3c866791222e82b
summary: groom seeds index.md via booping scaffold; scaffold and 
  frontmatter-update both answer with a unified diff
commit: 1bcc6229c7e8e013baec69c28747135663eb23e0
reviewed_at: 2026-08-09 13:44
---

# Scaffold-seeded plan creation and a scaffold receipt contract

## Context

`booping scaffold` materialises a config-declared file tree, rendering each file through the full context environment — so `macro('core.macros.git_commit')` and `core.macros.date` already work inside a tree. `setup` and `playbook-authoring` create their artifacts this way. The plan track does not: `groom/intake` shows the model a literal frontmatter block and asks it to write `index.md` in that shape, transcribing every value by hand.

After this plan: `groom/intake` creates the plan directory with one `booping scaffold` call, and `booping scaffold` reports each write as a unified diff so the caller knows what landed without reading the file back. `commit:` carries the repo HEAD from the moment the plan is created instead of staying `null` until a sprint starts, and the frontmatter shape lives in exactly one place — the config tree — instead of three.

## Decisions

- **Receipt format**: plain unified diff per touched file, `/dev/null` as the from-side for a new file — because the created-versus-updated distinction is already readable from the `---` line, so a separate verb header would restate it. `difflib.unified_diff` from the stdlib, not `git diff --no-index`, because scaffold's primary caller (`setup`) targets a vault that is not a git repository yet.
- **Silence on no-op**: a file whose rendered content matches what is on disk produces no output — the report carries changes, not an inventory.
- **Existing files are skipped, not errors**: without `--force` an existing target is left alone and reported; the caller decides what to do. This replaces the current dest-is-not-empty hard error, which cannot distinguish a stale directory from a plan directory that legitimately already exists.
- **`--force` keeps its meaning**: overwrite the files the tree names, reported as a normal diff.
- **Tree covers `index.md` plus an empty `request.md`**: the brief is free prose with no macro-valued keys, so only its path is seeded.
- **`_partials/plan_frontmatter.md` is deleted, not moved**: `booping frontmatter-update {plan} sp=… summary="…"` already renders its values as Jinja with the `macro` global, so draft-plan writes its two keys through the CLI and needs no literal block to copy.
- **`frontmatter-update` gets the same receipt**: it prints a key list to stderr today, which tells the caller what was set but not what the file now says. Both writers share one diff helper and one silence rule, so a prompt body never needs to know which command produced a receipt.
- **`frontmatter-update` types its scalars**: it stores every value as a string today, so `sp=23` lands as `sp: '23'` while every existing plan carries an integer. Handing draft-plan a writer that quotes numbers would corrupt the key it is being handed, so the coercion is a prerequisite rather than a follow-up. Found by writing this plan's own `sp` through the command.
- **`_partials/plan_structure.md` collapses into `_partials/plan_templates.md`**: once the frontmatter block and the H1 rule are gone — the tree seeds both — what remains is the template mechanics, and draft-plan already includes the two partials back to back.
- **Slug prefixing stays with the model**: the groom preamble already renders `Plan dir: plans/{YYYYMMDDHHmm}_{kebab-title}/`, so no flag and no config dest pattern is added.

## Architecture

`booping scaffold <config-path> <dest>` is invoked from a rendered prompt body and its stdout is read by the model that invoked it. That makes stdout a prompt-facing contract, not a human log: it must be complete enough to skip a read-back and quiet enough not to flood context.

The write path already separates planning from application — `_plan()` builds a list of `_Write(path, content)` before anything touches disk, so the previous content of every target is readable at that point and a diff needs no restructuring. Only `_apply()` changes: it compares against what is on disk, decides write-versus-skip, and emits the receipt.

Callers: `groom/intake` (new), `setup/setup-project`, `playbook-authoring/scaffold`. All three see the new report; only groom's prompt is rewritten in this sprint.

`booping frontmatter-update` is the second half of the same surface: scaffold creates a file, `frontmatter-update` amends one, and after this plan both answer with the same diff. Between them they cover every write groom makes to a plan's frontmatter, which is what lets the shape live only in the config tree.

## Milestones

### M1: Scaffold receipt and per-file write semantics — 8 SP | done

**Goal**: `booping scaffold` prints a unified diff for every file it writes, skips and reports files that already exist, and says nothing about files whose content is unchanged.

**Verify**: `cd booping-python && uv run pytest tests/commands/scaffold_test.py -q`

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Add the shared receipt helper — `difflib.unified_diff` over previous content (empty for a new file) versus new content, `/dev/null` as the from-file when the target did not exist, the path as the to-file, and the empty string for identical content — and emit it per written file from scaffold | `booping-python/src/booping/utils.py`, `booping-python/src/booping/commands/scaffold.py` | 3 | done |
| 1.2 | Per-file existence semantics — an existing target is skipped and reported without a write, `--force` overwrites and reports the diff, and the dest-is-not-empty precondition is removed in favour of the per-file rule | `booping-python/src/booping/commands/scaffold.py` | 3 | done |
| 1.3 | Cover both in tests — new file diff shape, overwrite diff shape, unchanged file silence, skipped existing file, `--force` overwrite, and a non-empty destination no longer erroring | `booping-python/tests/commands/scaffold_test.py` | 2 | done |

#### Task 1.1 DoD

- [x] A newly created file prints `--- /dev/null`, `+++ {path}`, and one all-additions hunk.
- [x] An overwritten file prints a diff of the change alone, with standard context lines.
- [x] A file whose rendered content equals its on-disk content prints nothing.
- [x] Directory creation is still reported, and the trailing count line still summarises the run.
- [x] No new dependency is added to `booping-python/pyproject.toml`.

#### Task 1.2 DoD

- [x] An existing target without `--force` is not written and is reported as existing.
- [x] An existing target with `--force` is overwritten and reported as a diff.
- [x] `booping scaffold` against a non-empty destination exits 0 instead of erroring.
- [x] Exit code 2 is still reserved for write failures, and 1 for user errors (bad config path, malformed `--set`).

#### Task 1.3 DoD

- [x] Each of the six behaviours above has its own test.
- [x] The three report strings asserted at `tests/commands/scaffold_test.py:208-212` are replaced, not deleted, by assertions on the new shapes.
- [x] `uv run pytest tests/commands/scaffold_test.py -q` passes.

---

### M2: The same receipt from `frontmatter-update` — 5 SP | pending

**Goal**: `booping frontmatter-update` prints the diff of the change it made, in the same shape scaffold prints, on stdout.

**Verify**: `bin/booping frontmatter-update {a plan}/index.md summary="probe" && bin/booping frontmatter-update {a plan}/index.md summary="probe"` — the first prints a one-hunk diff, the second prints nothing.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Print the file's before/after diff through the shared helper on stdout, keeping the existing `updated {path}: {keys}` summary on stderr | `booping-python/src/booping/commands/frontmatter_update.py` | 2 | pending |
| 2.2 | Write scalar values with their YAML type — an integer, float, boolean or null value lands unquoted, everything else stays a string | `booping-python/src/booping/commands/frontmatter_update.py` | 2 | pending |
| 2.3 | Cover the diff, the no-op silence, the scalar typing and the `--remove` / `--append` paths in tests | `booping-python/tests/commands/frontmatter_update_test.py` | 1 | pending |

#### Task 2.1 DoD

- [ ] A key set to a new value prints a unified diff of the frontmatter lines that changed, and nothing else.
- [ ] Setting a key to the value it already holds prints nothing on stdout.
- [ ] An `--append` of an already-present value prints nothing on stdout.
- [ ] The summary line stays on stderr, so a hook's captured output is unchanged.
- [ ] Exit codes are unchanged: `1` for a missing plan or a malformed pair, `2` for a write failure.

#### Task 2.2 DoD

- [ ] The rule is round-trip, not de-quoting: the value is parsed into the Python type its plain YAML form would load as, and the emitter is left to decide quoting. No quote-stripping pass, and no value that reloads as a different type than the one it was written with.
- [ ] `sp=23` writes `sp: 23`, not `sp: '23'`, matching how every existing plan stores it.
- [ ] `retro=null` writes a YAML null, and a boolean value writes unquoted.
- [ ] A value that only looks numeric in part (`summary=23 things`) stays a string.
- [ ] A string whose plain form would reload as another type keeps its quotes — `summary=yes` writes `'yes'`, since bare `yes` reloads as a boolean under the YAML 1.1 resolver ruamel uses.
- [ ] A string needing quotes for syntax keeps them: a leading `@`, `*`, `&`, `!`, `%` or backtick, a colon-space inside the value, or leading or trailing whitespace.
- [ ] A macro-rendered value (`completed="{{ macro('core.macros.date', '+%Y-%m-%d %H:%M') }}"`) still writes as a string, so the date keys hooks stamp are unaffected.

#### Task 2.3 DoD

- [ ] Each of the behaviours in 2.1 and 2.2 has its own test.
- [ ] The tests assert the diff's shape, not just that output is non-empty.
- [ ] A regression test pins `sp` round-tripping as an integer.

---

### M3: The groom scaffold tree and intake wiring — 4 SP | pending

**Goal**: `groom/intake` creates the plan directory with one `booping scaffold` call, and the created `index.md` carries a real `created` and a real `commit`.

**Verify**: `bin/booping scaffold core.groom_playbook.scaffold /tmp/plan-tree-check --set title="Check" --set type=feature` then read the printed diff — no file is read back.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Add `core.groom_playbook.scaffold` — `index.md` carrying the identity frontmatter with `title`/`type` from `--set`, `created` from `core.macros.date`, `commit` from `core.macros.git_commit`, every other key at its documented empty value, plus the H1; and an empty `request.md` | `src/config.yaml` | 2 | pending |
| 3.2 | Rewrite intake's plan-creation section to invoke the tree and act on the printed receipt, dropping the frontmatter block and its include | `playbooks/groom/intake/fable-5.md` | 2 | pending |

#### Task 3.1 DoD

- [ ] The tree renders with `--set title=` and `--set type=` and no other variables.
- [ ] `created` and `commit` come from macros; neither is a placeholder.
- [ ] `status:` is present as `framing`, keeping `playbook-transition`'s initial-status bootstrap satisfied.
- [ ] `retro:` is `null`, since the retro candidates query filters on it.
- [ ] `sp`, `related_to`, `planned`, `started`, `completed` are `null`; `code_reviews` and `sessions` are `[]`.
- [ ] A title containing a colon or a quote renders as valid YAML — the tree is raw text templating with no emitter to lean on, so the value is quoted at the template level (`{{ title | tojson }}`).

#### Task 3.2 DoD

- [ ] The step body names the exact invocation, with the plan directory assembled from the preamble's rendered `Plan dir:` line.
- [ ] The body states that the printed receipt is the confirmation and the created file is not read back.
- [ ] A target reported as already existing is handled by the step's own judgement, with no branch prescribed in the prompt.
- [ ] The `{% include "_partials/plan_frontmatter.md" %}` line is gone.

---

### M4: Retire the frontmatter duplicates — 5 SP | pending

**Goal**: the plan frontmatter shape exists only in `core.groom_playbook.scaffold`, and draft-plan writes its keys through `booping frontmatter-update`.

**Verify**: `grep -rn "plan_frontmatter\|template_plan_frontmatter\|plan_structure" playbooks/ docs/ src/ | grep -v "_reports/\|_specs/"` returns nothing.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Delete `_partials/plan_frontmatter.md` and `_partials/plan_structure.md`, folding the surviving template mechanics — the two top-level template sections, and authoring a new template when none fits — into `_partials/plan_templates.md`, which also names the `frontmatter-update` invocation that writes the drafter's keys | `playbooks/_partials/plan_frontmatter.md`, `playbooks/_partials/plan_structure.md`, `playbooks/_partials/plan_templates.md`, `playbooks/groom/draft-plan/opus-5.md` | 3 | pending |
| 4.2 | Delete `docs/template_plan_frontmatter.md` and repoint the Quality Checklist line in all five plan templates at the observable property instead of the deleted file | `docs/template_plan_frontmatter.md`, `docs/plan_templates/backend.md`, `docs/plan_templates/cli.md`, `docs/plan_templates/claude_skill.md`, `docs/plan_templates/documentation.md`, `docs/plan_templates/frontend.md` | 2 | pending |

#### Task 4.1 DoD

- [ ] `playbooks/_partials/plan_frontmatter.md` and `playbooks/_partials/plan_structure.md` are deleted, and `draft-plan/opus-5.md` includes only `_partials/plan_templates.md`.
- [ ] `plan_templates.md` carries the `# Plan Body` / `# Quality Checklist` mechanics and the author-a-new-template rule, unchanged in substance.
- [ ] `plan_templates.md` states that `sp` and `summary` are the drafter's and are written with `booping frontmatter-update {plan}/index.md sp=… summary="…"`.
- [ ] No partial contains a frontmatter yaml block or an H1-matching-title rule.
- [ ] `bin/booping render-playbook groom` exits 0 and its Draft Plan section renders without a template error.

#### Task 4.2 DoD

- [ ] `docs/template_plan_frontmatter.md` is deleted.
- [ ] No file references `template_plan_frontmatter`.
- [ ] Each plan template's frontmatter checklist item asserts a property that can be checked against the plan itself.

---

### M5: Documentation — 2 SP | pending

**Goal**: the scaffold documentation describes three trees and the stdout contract both writers now share.

**Verify**: `just docs`

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | Update the scaffold section — the third tree and its `--set` variables, the unified-diff stdout contract shared with `frontmatter-update`, the per-file skip rule and what `--force` now means — and correct the "two scaffold trees" count | `documentation/project_config.md` | 2 | pending |

#### Task 5.1 DoD

- [ ] `core.groom_playbook.scaffold` is listed beside the other two trees with its `--set` variables.
- [ ] The stdout contract is documented as a unified diff per changed file, silent on unchanged files.
- [ ] The skip-existing rule and `--force`'s meaning are stated.
- [ ] The sentence counting "the two scaffold trees" reads three.
- [ ] `just docs` builds without a broken-link warning on the edited page.

---

## I/O contract

- **Arguments / flags**: unchanged — `booping scaffold <config-path> <dest> [--force] [--set KEY=VALUE]... [--stub-macro DOTTED.PATH=LITERAL]...`.
- **stdin**: not read.
- **stdout**: for each file the run wrote, a unified diff — `--- /dev/null` or `--- {path}`, `+++ {path}`, then hunks. Created directories keep their existing one-line report. The run ends with the existing count line. A file whose content did not change, and a file skipped because it exists, contribute no diff; a skipped file is named on one line.
- **stderr**: unchanged — `error: {message}` for user errors and write failures.
- **Exit codes**: `0` success, including a destination that already holds some of the tree's files; `1` user error (unknown config path, malformed `--set` or `--stub-macro`, destination exists as a non-directory); `2` write failure.

`booping frontmatter-update` adopts the same stdout contract — a unified diff of the change it made, nothing when the file did not change — while keeping its `updated {path}: {keys}` summary and its error messages on stderr. Its arguments, flags and exit codes are unchanged.

## Final Verification

- [ ] `just ci` passes.
- [ ] `just snapshots` is run and its diff reported verbatim; `just snapshots-accept` is never run, since accepting the baseline is the user's call.
- [ ] `bin/booping scaffold --help` reflects the unchanged flag surface.
- [ ] A scaffold into a fresh directory and a second scaffold into the same directory are both exercised, and the second writes nothing.
- [ ] `bin/booping render-playbook groom` exits 0 with no STOP notice.
- [ ] A real groom run creates a plan whose `commit:` equals `git rev-parse HEAD`.
- [ ] `bin/booping frontmatter-update` on an unchanged value prints nothing on stdout and still exits 0.

## Out of scope

- `develop/intake`'s missing `commit: null` branch and its equality comparison of plan `commit` against HEAD. Plans created before this change keep the `null..HEAD` behaviour.
- The `goal:` key reconciliation between retro's `close-working-set` stamp and `gather-feedback`'s read.
- Converting `setup` and `playbook-authoring` prompt bodies to consume the new receipt. Their stdout changes with the CLI, but their bodies are not rewritten here.
- Any change to slug construction — no flag, no config dest pattern.

## Risk register

- **Dropping the dest-is-not-empty precondition changes `setup` and `playbook-authoring`.** Both currently refuse a half-built destination and will instead fill the gaps, with `--force` still the only way to overwrite. Accepted deliberately: the per-file rule is strictly more informative, and refusing was what blocked a plan directory that legitimately already exists.
- **The receipt is prompt-facing, so its size is a context cost.** Mitigated by the silence rules rather than a cap: only changed files appear, and a diff carries only its hunks.

## CLAUDE.md impact

- `## Config` — the scaffold-tree bullet gains the groom tree; the existing wording generalises, so confirm rather than assume no edit is needed.
- No change to `## Layout`, `## Playbooks` or `## Lifecycle`: no file moves between roots and no status vocabulary changes.
