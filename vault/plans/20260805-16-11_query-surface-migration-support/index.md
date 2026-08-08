---
status: done
title: Query surface — the core capabilities the migrate playbook needs
type: feature
created: 2026-08-05 16:11
sp: 43
split_from: null
planned: null
started: 20260805 10:05
completed: 2026-08-05 10:56
retro: null
goal: null
commit: 2c6513e82ec7f1a9e4af0f7ab30aacb696c78b95
summary: Ordering operator, booping context global, spec glob root, marker 
  setter, migrations dir and the render-time gate
plan_status: ready-for-dev
reviewed_at: 20260805 10:00
sessions:
- a83d3a6a-c4ea-42d1-bb10-8f7658caacc7
- ee9b0a6f-2fec-4066-9cc3-3db73f74e57a
metrics_active_minutes: 126
metrics_models:
- claude-opus-5
metrics_tokens_input: 687
metrics_tokens_output: 385745
metrics_tokens_cache_creation: 955428
metrics_tokens_cache_read: 55875840
---

# Query surface — the core capabilities the migrate playbook needs

## Context

The `migrate` playbook exists at `playbooks/migrate/` (manifest, three step prompts, no eval suites) but cannot run. Its `survey` step body opens on one line that is the whole contract this plan must satisfy:

```jinja
{% set pending = 'migrations.pending' | query(where={'id:gt': booping.latest_migration}) -%}
```

Three pieces of that do not exist, and two more are needed before the playbook can land anything or a user can discover it. Today `booping render-playbook migrate` emits a live STOP: `no query spec at config path: migrations.pending`.

The query surface itself is complete — the plan at `plans/20260805-12-35_frontmatter-query/` shipped M1–M7, giving `query.py` (engine), `commands/query.py` (CLI), and the `query` / `as_table` Jinja filters. Nothing in it is pending. This plan extends it.

After this plan: a vault behind on migrations gets a blocking notice on every render surface telling it to run `/playbook migrate`; that playbook resolves its pending set through the query surface, applies each migration one at a time, advances `latest_migration` in the repo's `.booping` marker, and commits per migration.

## Decisions

- **Ordering operator is `id:gt`, a clause-key suffix** — sibling of the existing `:in`, not a symbolic `>`. `parse_where` splits on the first `=` and then inspects the key's suffix; a symbolic form would need a second delimiter and a different tokeniser. `:lt` ships alongside for symmetry — the vocabulary can grow later but cannot shrink, so adding the pair once is cheaper than adding one and returning.
- **The comparison is numeric, not lexical** — `_eq` at `query.py:162-164` is deliberately stringly (`str(value) == str(expected)`), which is exactly wrong for ordering: `"10" < "9"` lexically, and the fresh-vault sentinel `-1` sorts oddly. A `:gt` clause coerces both sides to a number; a side that will not coerce fails the clause, consistent with the existing rule that a row missing the field fails every operator (`query.py:147-148`).
- **Coercion is `float()`, not `int()`** — `int("10.5")` raises, so an `int()` coercion would make `id:gt=10` fail against a row carrying `id: 10.5` for the wrong reason. `float()` accepts `int`, `float`, and the string forms of both; anything else (a `None`, a list, `"abc"`, an empty string) fails the clause. Comparison is then plain `>` / `<` on the two floats. This also settles the operand shapes the Jinja face can produce: `booping.latest_migration` renders as an `int`, but a string `"10"` or a float `10.0` compare identically, and a Jinja undefined fails the clause rather than raising mid-render.
- **Milestone order is M1 → M7, and two edges are hard** — M5's `Verify` invocation exercises `root: core` and `id:gt`, so M5 cannot be verified before M2 and M1 ship; M6's gate needs both the marker read (M3) and a shipped migration to be behind (M5). The milestones are each *executable* from a fresh session with only the plan as context, but they are not *reorderable* — the plan is one sequence, and each milestone below names what it stands on.
- **The operator vocabulary moves into `query.py` and is imported by the command** — `_IN_SUFFIX` / `_NE_SUFFIX` are declared twice today (`query.py:23-24`, `commands/query.py:33-34`). Adding two more suffixes doubles a drift surface that already exists; deduplicating is part of the first milestone rather than a follow-up.
- **Glob root is an explicit `root:` key on the spec, value `core`** — matching booping's config-tier vocabulary (core → global → project) rather than naming an implementation ("plugin"). Rejected: a try-vault-then-fall-back-to-core lookup (ambiguous when both roots match, and it picks one silently), and a path microsyntax inside the glob string (`@core/...`, a syntax the surface does not otherwise have).
- **`root:` resolves inside `run()`, not at either call site** — both faces (`--config` and `| query`) go through `run(spec, vault)` at `query.py:288-299`, so one change covers both. `get_plugin_root()` already exists at `rendering.py:74-78`, memoised.
- **An unknown `root:` value is an error, not a silent fallback** — `QuerySpec` has no `model_config`, so pydantic v2's `extra="ignore"` default means a misspelled `root: plguin` is dropped and the spec silently resolves vault-relative. The model gains `extra="forbid"`, and `root` is validated against the legal set with a custom error naming the value.
- **The context global is `booping.latest_migration`, mirroring the marker key** — not `booping.id`. The template spelling and the file spelling are the same word, so there is no alias to keep in sync across the playbook, the marker and `makemigration`.
- **`latest_migration` is a watermark, not a set of applied ids** — `latest_migration: 7` means everything at or below 7 is done, and a migration numbered 5 merged afterwards never runs. This is what makes `id:gt` express "pending" exactly. Flyway's `outOfOrder` flag exists because the other answer is also defensible; this project is single-author, and the watermark keeps the recorded state one integer.
- **No duplicate-id guard** — two branches each adding `007_*/` merge cleanly, because separate directories never textually conflict, giving a silent duplicate. The known mitigation (a committed pointer file that *does* conflict, per `django-linear-migrations`) is deliberately not adopted: the collision needs two concurrent branches, and this is a single-author project. Recorded in the risk register rather than solved.
- **A migration is trusted on its receipt** — `migration.md` carries no machine-checkable postcondition. Google's and Airbnb's LLM-migration work both conclude the model's self-report is not the receipt, and OpenRewrite defines migration correctness as "re-running produces no change". Neither is adopted here: it would add a field to the format contract `makemigration` must write and a verification runner to the playbook, for a migration set that is currently one entry. Recorded in the risk register.
- **The `.booping` marker gets its own writer — never `_yaml.update_frontmatter`** — the marker is a bare YAML mapping with no `---` delimiters, so `update_frontmatter`'s fallback branch (`context/_yaml.py:118-121`) *prepends* a frontmatter block and produces a two-document stream; the reader then raises `ComposerError: expected a single document in the stream`. Verified empirically during research. The setter round-trips the whole file with ruamel.
- **`ruamel.yaml` is pinned `>= 0.19.1`** — 0.19.0 swapped the C-extension dependency to `clibz` and broke deployments; 0.19.1 dropped both. Module-level `ruamel.yaml.load()` has raised `AttributeError` since 0.18.2, so only instance methods are used.
- **The gate is surface-scoped, consulted at one chokepoint** — Rails' shape: the render surfaces are gated, and the migrate path structurally does not traverse the gate. Rejected: a `--no-migration-check` flag as the primary exemption (dbt's decays into permanent CI boilerplate) and an env var (survives invisibly in shell profiles). Django ticket #35920 is the warning against consulting an exemption in two places.
- **The gate reads a forward-compatible subset of the marker, before any full validation** — it needs `latest_migration` and nothing else. dbt-core#2638 is the cautionary case: `require-dbt-version` was checked after schema validation, so a version-behind user got a schema error instead of "upgrade dbt". Since a future migration may change the marker's schema, a strict parse-then-gate order would leave booping unable to tell the user to run the thing that fixes it.
- **The gate's marker read is independent of `Project`'s** — it does its own minimal read rather than consuming `Project.latest_migration`. `Context.assemble()` runs first and would already have raised on an unreadable marker, which is precisely the case where the user most needs to be told to migrate. The two reads are allowed to disagree: `Project`'s is strict and reports a non-integer as a user error, the gate's treats anything it cannot read as `-1` — behind, therefore gated — so a corrupt marker produces the remedy rather than a stack trace.
- **The migrate exemption keys on the requested playbook name, checked before `Context.assemble()`** — `render-playbook migrate` and `render-playbook migrate --step {step}` are separate process invocations, and the `--step` fetches are issued by spawned sub-agents; both carry the name, so one condition covers every path. Checking the name (not the resolved `Playbook` object) is what makes the exemption survive a vault so behind that assembly itself would fail.
- **Report renders pin `latest_migration` through `--project`** — `--project {path}` already overrides the vault for a reproducible render, but the marker is resolved from cwd, so a report render would otherwise read the developer's own machine state and `just playbook-reports` would churn. `--project` is extended to resolve the marker from the given root as well, and `playbooks/_fixtures/vault/` gains a `.booping` carrying a fixed `latest_migration`. Rejected: extending `--set` to reach context globals (it deep-merges into `config`, and a global is not a config key), and an environment variable (invisible in a diff, the same objection that ruled out an env-var gate escape).
- **The gate emits the existing STOP vocabulary at exit 0** — `render_playbook.py:27-128` already defines `**STOP — tell the user:**` for blocking notices, replacing normal output. The `migrate` playbook's `trigger:` already names this behaviour, and the driver's existing handling then works unchanged.

## Architecture

```
                      ┌─────────────────────────────────────┐
  .booping (repo)     │  booping render / render-playbook   │
  ├ project_name      │  ─────────────────────────────────  │
  ├ vault_path        │  1. Context.assemble()              │
  └ latest_migration ─┼─▶ 2. migration gate  ◀── migrations/*/migration.md
        │             │       behind? → STOP, exit 0        │      (id: in frontmatter)
        │             │       exempt: the migrate playbook  │
        │             │  3. render                          │
        │             └─────────────────────────────────────┘
        │
        │  read                                    write
        ▼                                            ▲
  booping global                            booping marker-set
  {{ booping.latest_migration }}            latest_migration={id}
        │                                            │
        │                                            └── apply-migration step
        ▼
  'migrations.pending' | query(where={'id:gt': booping.latest_migration})
        │
        ▼
  query.run(spec, vault)
    root: core → get_plugin_root()   ← new
    glob: migrations/*/migration.md
    sort: id
```

Input sources: the repo `.booping` marker (one key), the plugin root's `migrations/` tree, the merged config. Output sinks: stdout (rendered body, or the STOP notice), stderr (diagnostics), the marker file (setter only). Callers: every `skills/{name}/SKILL.md` body is a `` !`booping render …` `` line, so the gate surfaces at skill load; `/playbook migrate` drives `render-playbook migrate` and must not be gated by it.

## Milestones

### M1: Ordering operator — `:gt` / `:lt`, numeric — 7 SP | done

**Goal**: `--where id:gt=3` and `where={'id:gt': 3}` select rows whose field is numerically greater than the operand.

**Verify**: `bin/booping query --config migrations.pending --where id:gt=-1 --output paths` lists every shipped migration, and `just test` passes.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Move the operator-suffix vocabulary into `query.py` as the single declaration and import it in the command; no behaviour change | `booping-python/src/booping/query.py`, `booping-python/src/booping/commands/query.py` | 2 | done |
| 1.2 | Add `:gt` / `:lt` branches to `matches` with a numeric coercion helper beside `_eq`; a non-coercible side fails the clause | `booping-python/src/booping/query.py`, `booping-python/tests/query_test.py` | 3 | done |
| 1.3 | Accept `:gt` / `:lt` in `parse_where`, update `--where` help text and the malformed-clause error | `booping-python/src/booping/commands/query.py`, `booping-python/tests/commands/query_test.py` | 2 | done |

#### Task 1.1 DoD

- [x] `_IN_SUFFIX` / `_NE_SUFFIX` are declared exactly once, in `query.py`.
- [x] `commands/query.py` imports them rather than redeclaring.
- [x] `just test` passes with no test changes — this task is behaviour-preserving.

#### Task 1.2 DoD

- [x] `matches` returns True for `{'id:gt': 3}` against a row with `id: 10`, and False against `id: 3`.
- [x] `{'id:gt': -1}` matches a row with `id: 1` — the fresh-vault sentinel case.
- [x] Coercion is `float()`: `id: 10`, `id: 10.5`, `id: "10"` and operand `10` / `"10"` / `10.0` all compare numerically.
- [x] A row whose field is `"abc"`, `None`, empty or a list — or an operand of the same — fails the clause rather than raising.
- [x] A Jinja undefined as the operand fails the clause rather than raising mid-render.
- [x] Suffix dispatch tries `:in`, `:gt`, `:lt`, then `!`, then the bare key, so a field literally named `x:gt` cannot shadow the operator.
- [x] Tests cover `:lt` symmetrically.

#### Task 1.3 DoD

- [x] `--where id:gt=3` parses and reaches `matches` with the suffix intact on the clause key.
- [x] `--where id:gt=` (empty value) exits 1 with a stderr message naming the clause.
- [x] `--help` enumerates `k=v`, `k!=v`, `k:in=a,b`, `k:gt=n`, `k:lt=n`.

---

### M2: Glob root — `root: core` on a query spec — 8 SP | done

**Goal**: a spec declaring `root: core` globs the plugin root; a spec omitting `root:` keeps today's vault-relative behaviour unchanged.

**Verify**: `bin/booping query --config migrations.pending --output paths` lists `migrations/001_plans_to_dirs/migration.md` from outside any project, and `bin/booping query --config plans --output paths` still resolves vault-relative.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Add `root` to `QuerySpec` and resolve it inside `run()`; `path` and `slug` computed relative to the resolved base | `booping-python/src/booping/query.py`, `booping-python/tests/query_test.py` | 3 | done |
| 2.2 | Set `extra="forbid"` on `QuerySpec` and validate `root` against the legal set with a custom error naming the value | `booping-python/src/booping/query.py`, `booping-python/tests/query_test.py` | 2 | done |
| 2.3 | Move the no-vault guard after root resolution in both faces, so a `root: core` spec is queryable outside a project | `booping-python/src/booping/commands/query.py`, `booping-python/src/booping/rendering.py`, `booping-python/tests/commands/query_test.py` | 3 | done |

#### Task 2.1 DoD

- [x] `run(spec, vault)` globs `get_plugin_root()` when `root` is `core`, else `vault`.
- [x] A `core` row's `path` column reads `migrations/001_plans_to_dirs/migration.md`, relative to the plugin root.
- [x] An existing spec with no `root` produces byte-identical output to before the change.

#### Task 2.2 DoD

- [x] `root: plguin` raises `QueryError` naming the bad value and the legal set, exit 1.
- [x] An unknown key in a spec raises rather than being silently dropped.
- [x] The custom error on the literal field uses `mode="before"` — with `mode="after"` the literal check fires first and the custom error is unreachable.

#### Task 2.3 DoD

- [x] `bin/booping query --config migrations.pending` succeeds with cwd outside any booping project.
- [x] A vault-relative spec with no project still exits 2 with the existing message.
- [x] The Jinja face raises the same way for a vault-relative spec with no vault.

---

### M3: The `booping` context global — 6 SP | done

**Goal**: `{{ booping.latest_migration }}` renders the recorded id in every rendering surface, `-1` when nothing has been applied.

**Verify**: `bin/booping render` on a scratch template containing `{{ booping.latest_migration }}` prints the marker's value; `bin/booping debug-context` shows it.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Read `latest_migration` from the marker in `Project.load_cwd` as a forward-compatible subset read; expose it as a `Project` field defaulting to `-1` | `booping-python/src/booping/context/project.py`, `booping-python/tests/context/project_test.py` | 3 | done |
| 3.2 | Thread `context` into `_build_env` and set the `booping` global there, wrapped in the existing `Row` so attribute access is safe | `booping-python/src/booping/rendering.py`, `booping-python/tests/rendering_test.py` | 3 | done |

#### Task 3.1 DoD

- [x] A marker with no `latest_migration` key loads with `-1`, not an error.
- [x] A marker carrying unknown keys still loads — the read takes only the key it needs.
- [x] A non-integer `latest_migration` is reported as a user error naming the file, not a crash mid-render.

#### Task 3.2 DoD

- [x] `{{ booping.latest_migration }}` resolves in `render`, `render-playbook` and `scaffold` seed content.
- [x] The global is set in exactly one place.
- [x] The no-context branch of `render_playbook.build_env` (lesson rendering) is documented as having neither the `booping` global nor the `query` filter — both render as undefined rather than raising — with a test asserting it, so a lesson author does not expect either to work.

---

### M4: `latest_migration` setter — 6 SP | done

**Goal**: `booping marker-set latest_migration={id}` writes the marker, preserving its comments, quoting and key order.

**Verify**: `bin/booping marker-set latest_migration=3 && bin/booping debug-context | grep latest_migration` reports 3, and `git diff .booping` shows exactly one changed line.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | A ruamel round-trip marker writer — whole-file load, mutate one top-level scalar, dump; `preserve_quotes` on, `width` wide | `booping-python/src/booping/context/_yaml.py`, `booping-python/tests/context/yaml_test.py` | 3 | done |
| 4.2 | The `marker-set` subcommand: argument shape, exit codes, stderr report, `.booping.log` entry | `booping-python/src/booping/commands/marker_set.py`, `booping-python/src/booping/cli.py`, `booping-python/tests/commands/marker_set_test.py` | 3 | done |

#### Task 4.1 DoD

- [x] Round-tripping a marker with comments and mixed quoting changes only the target line.
- [x] `width` is set high enough that untouched long lines are not re-wrapped.
- [x] The writer is used for `.booping` only; `update_frontmatter` is untouched and still owns `---`-delimited files.
- [x] A regression test asserts the marker remains a single YAML document after a write.

#### Task 4.2 DoD

- [x] `marker-set latest_migration=3` exits 0 and prints one authoritative line to stderr; stdout stays empty.
- [x] A malformed pair (no `=`) exits 1 with a stderr message.
- [x] No marker resolvable exits 2.
- [x] The value is set absolutely, never incremented — ids may skip.
- [x] The invocation is logged to `.booping.log` in the existing format.

---

### M5: `migrations/` and the first migration — 4 SP | done

**Stands on**: M1 and M2 — the `Verify` invocation below exercises both `root: core` and `id:gt`, so this milestone cannot be verified before they ship.

**Goal**: the plugin ships `migrations/001_plans_to_dirs/migration.md`, and `migrations.pending` resolves it.

**Verify**: `bin/booping query --config migrations.pending --where id:gt=-1 --output table` renders one row with id 1.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | Declare the `migrations.pending` spec as a top-level config key beside `plans`; create `migrations/` | `src/config.yaml` | 1 | done |
| 5.2 | Write `001_plans_to_dirs/migration.md` — frontmatter `id`, title, summary; prompt plus commands converting flat `plans/{slug}.md` into `plans/{slug}/index.md` | `migrations/001_plans_to_dirs/migration.md` | 3 | done |

#### Task 5.1 DoD

- [x] `migrations.pending` declares `root: core`, `glob: migrations/*/migration.md`, `sort: id`.
- [x] The spec-schema comment block in `src/config.yaml` documents `root` and the `:gt` / `:lt` operators.

#### Task 5.2 DoD

- [x] Frontmatter carries `id: 1`, a title and a one-line summary — the three columns `survey` renders.
- [x] The prompt states the transformation in terms a fresh agent can act on with no other context.
- [x] The prompt touches the vault only and never mentions git or `.booping` — the playbook owns the commit and the id advance.
- [x] Re-running against an already-converted vault is a no-op, not an error.

---

### M6: The render-time gate — 10 SP | done

**Stands on**: M3 (the marker read) and M5 (a shipped migration, without which no vault is ever behind and the gate cannot be exercised).

**Goal**: a vault behind on migrations gets a STOP notice naming `/playbook migrate` instead of rendered output; the migrate path itself is never gated.

**Verify**: with `latest_migration: -1` in the marker, `bin/booping render src/templates/skills/chat.md.j2` prints the STOP and exits 0, while `bin/booping render-playbook migrate` renders normally.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 6.1 | A shared gate helper: subset marker read, highest shipped id, notice text; no dependency on full config validation | `booping-python/src/booping/migrations.py`, `booping-python/tests/migrations_test.py` | 3 | done |
| 6.2 | Call the gate from both render entry points immediately after `Context.assemble()`, consulted at one chokepoint, with the migrate playbook structurally exempt | `booping-python/src/booping/commands/render.py`, `booping-python/src/booping/commands/render_playbook.py`, `booping-python/tests/commands/render_test.py` | 3 | done |
| 6.3 | Extend `--project` to resolve the marker from the given root, add a fixture `.booping` with a fixed `latest_migration`, and regenerate the reports | `booping-python/src/booping/commands/render_playbook.py`, `playbooks/_fixtures/vault/.booping`, `playbooks/migrate/_reports/output.md` | 4 | done |

#### Task 6.1 DoD

- [x] The helper reads only `latest_migration` and tolerates unknown keys — a marker whose schema a future migration changed still yields a usable notice.
- [x] The read is the helper's own, not `Project.latest_migration`; an unreadable or non-integer value is treated as `-1` (behind, therefore gated), so a corrupt marker produces the remedy and never a stack trace.
- [x] The highest shipped id comes from migration frontmatter, never from the directory-name prefix.
- [x] No migrations shipped, or the vault current, returns no notice.
- [x] The notice names the exact remedy command and stands alone with no surrounding chrome — it is read at skill load and in CI logs.

#### Task 6.2 DoD

- [x] `booping render` and `booping render-playbook` both emit the notice and exit 0 when behind.
- [x] The notice replaces normal output rather than preceding it.
- [x] The exemption condition is the requested playbook name equalling `migrate`, evaluated before `Context.assemble()` — so it holds even when assembly itself would fail — and consulted in exactly one place.
- [x] `bin/booping render-playbook migrate` and `bin/booping render-playbook migrate --step {step}` both render normally with the vault behind; the `--step` case is a separate process issued by a spawned sub-agent and must be covered by its own test.
- [x] A test asserts the exemption, so it cannot rot unnoticed.

#### Task 6.3 DoD

- [x] `--project {path}` resolves the `.booping` marker from that root, not from cwd.
- [x] `just playbook-reports` produces byte-identical output across two consecutive runs with the developer's own marker set to different values in between.
- [x] `playbooks/migrate/_reports/output.md` renders clean — the STOP it carries today is gone.
- [x] The pinning mechanism is documented in `CLAUDE.md` beside `--stub-macro`.

---

### M7: Documentation — 2 SP | done

**Goal**: `CLAUDE.md` and the public docs describe the new CLI surface and config keys.

**Verify**: `just docs` builds, and `CLAUDE.md` mentions `marker-set`.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 7.1 | Update the CLI section, the config-schema section, and the two public-doc mentions of `booping query` | `CLAUDE.md`, `documentation/vault.md`, `documentation/quick_start.md` | 2 | done |

#### Task 7.1 DoD

- [x] The CLI section documents `marker-set` with its argument shape and exit codes.
- [x] The config-schema section documents `migrations.pending`, `root`, and the `:gt` / `:lt` operators.
- [x] `documentation/vault.md` and `documentation/quick_start.md` reflect the extended `--where` vocabulary.

## I/O contract

**`booping query`** — extended, not changed.

- **Arguments**: `--where {clause}` gains `k:gt=n` and `k:lt=n` alongside `k=v`, `k!=v`, `k:in=a,b`. Repeatable, unchanged semantics.
- **stdin**: not read.
- **stdout**: unchanged — `table` (GFM), `json`, `yaml` or `paths`.
- **stderr**: unchanged — `error: ` prefixed diagnostics.
- **Exit codes**: unchanged — 0 success, 1 user error (malformed clause, unknown config path, unknown `root` value), 2 environment (no vault resolvable for a vault-relative spec).

**`booping marker-set`** — new.

- **Arguments**: `booping marker-set {key}={value}`, one pair. Only `latest_migration` is meaningful today; the command takes a key so the marker stays writable as it grows.
- **stdin**: not read.
- **stdout**: empty.
- **stderr**: one authoritative line — `marker: latest_migration=3`.
- **Exit codes**: 0 success; 1 user error (malformed pair, non-integer id); 2 environment (no marker resolvable, OSError mid-write).

**The migration gate** — affects `booping render` and `booping render-playbook`.

- **stdout**: on a behind vault, `**STOP — tell the user:** …` replacing all normal output.
- **stderr**: nothing — the notice is in-band.
- **Exit code**: 0, matching the existing playbook-notice convention.

## Final Verification

- [x] Help text updated for `--where` and for `marker-set`.
- [x] Happy-path and at least one failure-path invocation verified for every new surface.
- [x] Exit codes match the documented contract.
- [x] `bin/booping render-playbook migrate` renders with no STOP notice.
- [x] `just lint`, `just typecheck`, `just test` all pass.
- [x] `just playbook-reports` leaves no diff on a second consecutive run.

## Risk register

- **Duplicate migration ids under concurrent authorship** — two branches each adding `NNN_*/` merge cleanly with no textual conflict, producing a silent duplicate and a broken watermark. Deferred deliberately: single-author project. The mitigation if it ever bites is a committed pointer file that conflicts on merge, plus a CI assertion that ids are unique and contiguous.
- **A migration that half-applies still advances the watermark** — migrations are trusted on their receipt, with no machine-checkable postcondition. Deferred deliberately for a one-entry migration set. The mitigation is a `verify` frontmatter key the CLI runs after the model reports done, which would also become part of the format contract `makemigration` writes.
- **The gate fires in CI far from whoever caused it** — the documented failure mode of every hard-blocking version gate. Mitigated only by the notice carrying the exact remedy command; accepted otherwise.

## Out of scope

- The `migrate` playbook itself — authored at `playbooks/migrate/`, unchanged by this plan beyond being unblocked by it.
- The `makemigration` playbook — a separate authoring run. It writes migration directories in the format M5 establishes.
- Migration rollback or a `down` direction. Migrations are one-shot forward mutations; reverting the per-migration commit is the recovery path.
- Any change to the existing `--where` operators or to `plans.glob` behaviour.
- The unrelated `src/config.yaml` modification currently in the working tree from the sprints/Bases work.

## CLAUDE.md impact

- `## CLI` section: add `booping marker-set`, and extend the `booping query` entry with the `:gt` / `:lt` operators.
- `## Config schema (src/config.yaml)` section: add the top-level `migrations` key and document `root` on a query spec.
- `## Layout` section: add `migrations/` as a plugin-root directory.
- The report-pinning mechanism chosen in Task 6.3, documented beside `--stub-macro`.
