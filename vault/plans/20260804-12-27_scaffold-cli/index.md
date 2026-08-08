---
title: Scaffold CLI — booping scaffold {config-path} {dest}
type: feature
status: done
plan_status: ready-for-dev
sp: 15
split_from: null
created: 2026-08-04 12:27
planned: null
started: 20260804 07:49
completed: 2026-08-04 08:07
retro: null
goal: null
summary: "booping scaffold materialises a config-declared file/dir tree into a destination,
  with Jinja-seeded file content"
commit: f7cbe60f4e5b935e99f061c9026995d399b62def
reviewed_at: 20260804 07:43
sessions:
- bc34a56e-7ede-4ca4-a139-62c3770456c8
- 6a379acd-5cdc-48e1-8235-87427ea2d67e
metrics_active_minutes: 34
metrics_models:
- claude-opus-5
metrics_tokens_input: 256
metrics_tokens_output: 152827
metrics_tokens_cache_creation: 923822
metrics_tokens_cache_read: 11663144
---

# Scaffold CLI — booping scaffold {config-path} {dest}

## Context

booping has exactly one scaffolding path today: `bin/booping-create-project`, a standalone uv script that hardcodes the vault layout as `mkdir -p "$ROOT"/{plans,retrospectives,lessons,_booping,notes}`. Every other directory tree a user needs — a playbook skeleton, a step directory, a plan-template stub — is created by hand or written file-by-file by a skill. There is no declarative way to say "this name means these directories and these seed files", and no way for global or project config to contribute its own trees.

After this ships, `booping scaffold {config-path} {dest}` reads a tree declared anywhere in the merged config and materialises it into a destination directory, creating the structure and seeding files whose content the tree declares inline. Because trees ride the existing core → global → project merge, a project or a machine-global config can add its own trees or override leaves of a core one without restating anything.

**Assumed goal — to be confirmed at approval.** The first tree reached for is a playbook skeleton: `booping scaffold playbook.scaffold ./playbooks/{name}` replaces the hand-creation of `playbook.md` + `playbook.yaml` + `_references/` that `playbook-authoring` currently walks an author through. The saving is that a new tree becomes a config edit rather than a code change or a manual sequence. The user has not yet stated the goal in their own terms; this assumption stands in until they do, and confirming it is part of the approval gate.

## Decisions

- **Addressing — dotted config path, not a registry**: the first positional argument is a dot-separated path traversed through the merged config (`booping scaffold playbook.scaffold ./playbooks/x`, `booping scaffold skills.install.project_scaffold ~/Claude/new`). Trees colocate with the config they serve rather than living in one `scaffold:` namespace. Consequences accepted: no registry, therefore no no-args listing; the config path is the user-facing name; a path resolving to a non-tree value is a runtime error the loader reports against the offending path.
- **No wrapper keys**: a template's value **is** its directory contents. No `tree:`, no `description:`. This makes every level of the structure obey one rule — a mapping of names to nodes is a directory's children — with no special case at the top.
- **Tree encoding — hybrid**: a string value is a file's content; a mapping without the reserved key `type` is a directory's children; a mapping carrying `type` is an explicit node descriptor. Shallow trees cost one line per level; the explicit form exists for nodes needing more than content. `type` is a reserved filename inside a tree.
- **Tier extensibility comes from `deep_merge`, not from addressing**: `utils.deep_merge` already recurses into mappings and shallow-merges only `agents`, so nested trees merge per-leaf across tiers for free. Project always wins on collision; core trees are deliberately not un-overridable, matching every other booping surface.
- **Existing destination is an error**: a non-empty destination aborts with exit 1 unless `--force` is passed. `--force` overwrites files the template names and leaves every other file in the destination untouched — it never deletes a directory. This keeps a mistyped path from destroying work while still allowing a tree to be seeded into an existing directory.
- **Seed content is Jinja-rendered** through `rendering.build_source_env`, the existing ad-hoc-source environment, with a plain `Environment` and no `SandboxedEnvironment`. Config is the same trust level as every other booping template, and Jinja's own docs state the sandbox "is no solution for perfect security".
- **`--set` exposes bare variables**: `--set name=x` makes `{{ name }}` resolve directly in seed content. This diverges from `render` / `render-playbook`, where `--set` merges into `config` and is read as `{{ config.name }}`. Accepted for readability of the common case; the divergence is documented in the CLI section of `CLAUDE.md`.
- **Pre-flight, then write**: the whole tree is parsed, validated, and rendered into memory before any path is touched, so a malformed node or a Jinja error leaves the filesystem untouched. Partial writes occur only on an OS-level failure mid-write.
- **`mode:` deferred**: explicit nodes support `type` and `content` only. The reserved `type` key keeps the escape hatch open, so file permissions land later without a breaking change.

## Architecture

The command is a new `booping` subcommand, following the module shape every other command uses: a `commands/scaffold.py` exposing `add_parser(subparsers)` and `_run(args)` with `p.set_defaults(func=_run)`, registered by one line in `cli.py`.

Tree parsing lives in `context/scaffold.py`, following `context/lifecycle.py` — pure logic over a sub-dict of the merged config, with no disk reads of its own. This keeps the command module to argument handling, filesystem side effects, and reporting.

Input sources: the merged config via `Context.assemble()`, which resolves core → global → project, plus `--set` pairs. Output sinks: the destination directory, a plain-text report on stdout, diagnostics on stderr, and one line in `_booping/.booping.log` via `logger.log`. No other tool consumes this command's stdout — it is not inlined into a skill via `` !`command` `` — so the report format is for humans and is free to change.

Node semantics, resolved by `context/scaffold.py`:

| Config value | Meaning |
|---|---|
| string | File; the string is its content, Jinja-rendered |
| mapping without `type` | Directory; entries are its children |
| mapping with `type: file` | File; optional `content` (absent → empty file) |
| mapping with `type: dir` | Directory; optional `children` (absent → empty dir) |
| `null` | Error — message names both fixes (`""` for an empty file, `{}` for an empty dir) |
| list, int, bool, any other scalar | Error, reported against the node's path |

Name validation applies to every mapping key used as a filename: a key containing `/`, or equal to `.` or `..`, is rejected before any write. This closes path traversal out of the destination, which matters because config is merged from a machine-global tier that a project does not control.

## Milestones

### M1: Tree model and loader — 5 SP | done

**Goal**: the merged config at a dotted path parses into a validated node tree, with every malformed shape reported against its path.

**Verify**: `cd booping-python && uv run pytest tests/context/scaffold_test.py -q`

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Node model + recursive parse of a config sub-tree into file/dir nodes, covering all four valid shapes in the Architecture table | `booping-python/src/booping/context/scaffold.py`, `booping-python/tests/context/scaffold_test.py` | 3 | done |
| 1.2 | Validation: dotted-path traversal miss, non-tree value at path, `null` node, non-str/mapping node, and unsafe filename keys — each raising a typed error carrying the offending dotted path | `booping-python/src/booping/context/scaffold.py`, `booping-python/tests/context/scaffold_test.py` | 2 | done |

#### Task 1.1 DoD

- [x] A string value parses to a file node whose content is that string.
- [x] A mapping with no `type` key parses to a dir node; each key of that mapping becomes one child node, named by the key.
- [x] `{type: file}` parses to an empty file node; `{type: file, content: "x"}` carries the content.
- [x] `{type: dir}` parses to an empty dir node; `{type: dir, children: {...}}` carries the children.
- [x] Nesting to at least three levels round-trips to the expected node tree.
- [x] `uv run basedpyright` passes on the new module with no new `# type: ignore` beyond the `dict[str, Any]` narrowing the codebase already accepts.

#### Task 1.2 DoD

- [x] A dotted path with no match raises an error naming the full path and the first missing segment.
- [x] A path resolving to a string, list, int or bool raises an error naming the path and the found type.
- [x] A `null` node raises an error whose message names both `""` and `{}` as the fixes.
- [x] A key containing `/`, or equal to `.` or `..`, raises an error naming the key and its parent path.
- [x] Every error carries the dotted config path of the offending node, not just a message.

---

### M2: The `scaffold` subcommand — 7 SP | done

**Goal**: `booping scaffold {config-path} {dest}` materialises a tree on disk, renders seed content, honours `--force`, and reports what it did.

**Verify**: `cd booping-python && uv run pytest tests/commands/scaffold_test.py -q`

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Command module + `cli.py` registration: positional `config-path` and `dest`, `--force`, `--set`; destination existence check and `--force` overwrite semantics | `booping-python/src/booping/commands/scaffold.py`, `booping-python/src/booping/cli.py`, `booping-python/tests/commands/scaffold_test.py` | 3 | done |
| 2.2 | Seed-content rendering via `build_source_env`, with `--set` pairs exposed as bare template variables; pre-flight render of the whole tree before any write | `booping-python/src/booping/commands/scaffold.py`, `booping-python/tests/commands/scaffold_test.py` | 2 | done |
| 2.3 | stdout report, stderr diagnostics, exit-code contract, and the `logger.log` call | `booping-python/src/booping/commands/scaffold.py`, `booping-python/tests/commands/scaffold_test.py` | 2 | done |

#### Task 2.1 DoD

- [x] `booping scaffold --help` lists both positionals, `--force` and `--set` with their descriptions.
- [x] A missing destination is created, parents included.
- [x] An existing empty destination is written into without `--force`.
- [x] An existing non-empty destination exits 1 with nothing written, and stderr names the destination.
- [x] With `--force`, a file the template names is overwritten and a file it does not name is left byte-identical.
- [x] `--force` never removes a directory.

#### Task 2.2 DoD

- [x] A seed string containing `{{ name }}` renders the value passed as `--set name=...`.
- [x] A seed string with no Jinja syntax is written byte-identical, trailing newline preserved.
- [x] Seed content can reference the `config` and `context` globals, matching what `build_source_env` binds.
- [x] A Jinja error in any node aborts before the first write; the destination is unchanged.
- [x] A malformed `--set` pair (no `=`) exits 1 with the offending pair on stderr, matching `render`'s message.

#### Task 2.3 DoD

- [x] stdout carries one line per path, tagged created or overwritten, plus a trailing summary count.
- [x] stdout and stderr never carry the same content.
- [x] Exit 0 on success; exit 1 on unknown config path, non-tree value, invalid node, unsafe filename, existing destination without `--force`, malformed `--set`, or Jinja error; exit 2 on `OSError` during write.
- [x] Every non-zero exit writes a message to stderr naming the cause.
- [x] `_booping/.booping.log` gains one `[scaffold]` line per invocation when a project is attached.

---

### M3: Core tree and documentation — 3 SP | done

**Goal**: a working core tree ships as the dogfood case, and the CLI surface is documented.

**Verify**: `bin/booping scaffold playbook.scaffold /tmp/scaffold-check --set name=demo && find /tmp/scaffold-check | sort`

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Core `playbook.scaffold` tree producing a playbook skeleton: `playbook.md` with identity frontmatter, `playbook.yaml` with an empty `graph:`, and an empty `_references/` | `src/config.yaml`, `booping-python/tests/commands/scaffold_test.py` | 2 | done |
| 3.2 | Document the subcommand in the `## CLI` section and the config surface in `## Config schema`, including the `--set` divergence from `render` | `CLAUDE.md`, `documentation/` | 1 | done |

#### Task 3.1 DoD

- [x] `bin/booping scaffold playbook.scaffold {tmpdir} --set name=demo` produces `playbook.md`, `playbook.yaml`, and `_references/`.
- [x] The generated `playbook.md` frontmatter carries the name passed via `--set name=...`.
- [x] `bin/booping render-playbook` run against the generated skeleton reports its missing-graph STOP rather than crashing.
- [x] A test asserts the generated tree against a fixture listing.

#### Task 3.2 DoD

- [x] `CLAUDE.md` `## CLI` gains a `bin/booping scaffold` entry stating both positionals, both flags, and the exit codes.
- [x] `CLAUDE.md` `## Config schema` documents the node encoding table and the `type` reserved key.
- [x] The `--set` bare-variable divergence from `render` is stated explicitly in both places it could be looked up.
- [x] `CLAUDE.md` `## Layout` gains `scaffold` in the subcommand list on the `bin/booping` line.
- [x] `CLAUDE.md` `## Layout` gains `scaffold` in the subcommand list on the `booping-python/` line.
- [x] No stale claim that `booping-create-project` is the only scaffolding path.

---

## I/O contract

- **Arguments / flags**: `booping scaffold <config-path> <dest> [--force] [--set KEY=VALUE]...`
  - `<config-path>` — dot-separated path into the merged config, e.g. `playbook.scaffold`. Required.
  - `<dest>` — destination directory. Created if missing, parents included. Required.
  - `--force` — overwrite files the tree names when the destination is non-empty. Never deletes directories.
  - `--set KEY=VALUE` — repeatable, later pairs win, values stay strings. Exposed to seed content as a bare variable.
- **stdin**: not read.
- **stdout**: plain text. One line per materialised path — `created dir {path}`, `created file {path}`, `overwrote file {path}` — followed by a summary line with the totals.
- **stderr**: all diagnostics and errors. Never duplicates stdout content.
- **Exit codes**: `0` = success. `1` = user error — unknown config path, value at path is not a tree, invalid node shape, `null` node, unsafe filename key, destination non-empty without `--force`, malformed `--set`, Jinja error in seed content. `2` = internal error — `OSError` while creating a directory or writing a file.

## Final Verification

- [ ] `booping scaffold --help` is accurate for both positionals and both flags.
- [ ] Happy path verified: a nested tree materialises with correct content.
- [ ] Failure paths verified: unknown config path, non-empty destination without `--force`, malformed `--set`, unsafe filename key.
- [ ] Exit codes match the documented contract on every path above.
- [ ] `just lint`, `just typecheck`, `just test` all pass.
- [ ] Not inlined via `` !`command` `` in any skill, so no consumer-render check applies.

## Out of scope

- **Template updates.** Unlike Copier's `copier update`, a scaffolded directory is a one-shot copy: no answers file is written, and there is no later re-merge when the config tree changes. A permanent non-goal of this design, not a deferral.
- **Interactive prompting.** Copier and Cookiecutter both ask questions at generation time; `--set` is the non-interactive equivalent here. A prompting layer is a possible later sprint.
- **`--dry-run`.** Excluded to keep the flag surface minimal; `--force`'s non-deleting semantics make a preview less necessary.
- **File permissions (`mode:`).** Deferred; the reserved `type` key keeps the escape hatch open.
- **No-args listing of available trees.** Impossible under dotted-path addressing, which has no registry to enumerate. Accepted as a consequence of that choice.
- **`bin/booping-create-project`.** Untouched. Its `home_dir` ladder, `.booping` marker writing and `--local` handling are not tree-shaped work, and the vault layout is not re-expressed as a scaffold tree in this sprint.
- **Symlinks and binary file content.** Trees declare directories and text files only.

## CLAUDE.md impact

- `## CLI` — add the `bin/booping scaffold` entry (arguments, flags, exit codes, the `--set` divergence from `render`).
- `## Config schema (src/config.yaml)` — document the tree node encoding and the reserved `type` key.
- `## Layout` — the `bin/booping` line and the `booping-python/` line both enumerate subcommands and must gain `scaffold`.
