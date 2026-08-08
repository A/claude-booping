---
title: Playbook State Machines + playbook.yaml
type: feature
status: done
sp: 29
split_from: null
created: 2026-07-30 22:27
planned: 20260730 14:29
started: 20260730 14:42
completed: null
retro: null
goal: null
summary: "playbook.yaml manifests with named state machines, playbook transition/state
  CLI, transition reports, resume protocol"
commit: ff74c1ace2ed0fb3e6fcd253be92a01a4215cdcf
sessions:
- e25f724b-7cd9-48a3-944f-515f110d4733
- 60b0a038-9e51-4d04-bc87-fac93cd7dba0
metrics_active_minutes: 61
metrics_models:
- claude-fable-5
metrics_tokens_input: 381
metrics_tokens_output: 338114
metrics_tokens_cache_creation: 1372945
metrics_tokens_cache_read: 22422948
---

# Playbook State Machines + playbook.yaml

## Context

Playbook runs today live entirely inside one conversation: no persisted run state, no resume, gates enforced only in-chat. playbook-authoring hand-rolls state with `confirmed:` frontmatter flags on its artifacts; the groom playbook preamble hand-rolls resume by mapping plan status to waves. Meanwhile the plan lifecycle already has the right machinery — declarative statuses/transitions with gates and hooks (`src/config.yaml` `plan.*`), a generic resolver (`booping-python/src/booping/context/lifecycle.py`), and a deterministic executor (`booping transition`).

After this ships:

- A playbook declares its graph **and** named state machines in a readable `playbooks/<name>/playbook.yaml` (frontmatter `graph:` stays as a legacy fallback).
- Run state is harness-managed: `booping playbook-transition` owns every artifact mutation; `booping playbook-state` reports the full stop-point picture (outer machine + all subgraph instances) so any session can resume a run.
- `booping transition` (plans) and `booping playbook-transition` both print a structured report of what they changed, so the model no longer re-reads frontmatter to confirm.
- The core `grooming` playbook itself is **not** part of this plan — it will be generated later on the shipped machinery. `playbooks/groom/` and both groom skills stay untouched.

## Decisions

- **DAG ≠ FSM**: the graph stays a pure execution DAG (waves, parallelism); lifecycle state is a separately **authored** machine. They join only through prose gates ("research-codebase and research-web done") the model judges — no derived wave-FSM, no mechanical coupling. Author decides status granularity; a parallel wave sits inside one status.
- **Named states**: state machines are declared under one top-level `states:` mapping in playbook.yaml, keyed by plain name (`main`, `step`); each graph scope references one by name via a `state:` key (top-level `state: main` for the outer graph, `state:` inside a subgraph node for its inner graph). Reusable across subgraphs. Unresolved ref → STOP notice; a `states:` entry never referenced → Note notice (same in-band channel as graph problems).
- **States-entry shape = plan.statuses shape**: `artifact`, `initial`, `statuses.<key>` with `terminal` and `transitions[{to, when, gates, hooks}]`; optional `superstates` and `hooks.post` accepted with identical semantics (the generalized resolver treats a states entry and `config["plan"]` identically). Moves are addressed by target status, matching `booping transition` — no transition names.
- **Status is harness-managed**: skills/drivers never hand-edit artifact frontmatter status or `confirmed:` flags; only `playbook-transition` mutates run state.
- **Workdir**: states entries' `artifact:` paths are relative to a run workspace. `playbook-transition` and `playbook-state` take `--workdir PATH` (default: cwd). The playbook dir stays read-only source.
- **Instance = dir slug**: `{instance}` in an artifact path is the placeholder; instances are enumerated by globbing it (`{instance}` → `*`) against the workdir. Disk is the registry — no instance list is stored anywhere else.
- **Artifact bootstrap**: when a states entry's artifact file is missing, the only legal move is to `initial`; `playbook-transition <playbook> <initial>` then creates the file with frontmatter `status: <initial>` (creating parent dirs). Any other target on a missing artifact → exit 1.
- **Script hooks**: hook string `script <name>` executes `<playbook-dir>/_scripts/<name>` (must be executable; playbook-dir resolved to an **absolute** path before spawning, since cwd changes) with cwd = workdir and env `BOOPING_ARTIFACT` (absolute artifact path), `BOOPING_INSTANCE` (slug or empty), `BOOPING_WORKDIR`. Non-zero exit → transition fails with exit 2 after printing the script's stderr. Same partial-state caveat as plan transitions (status may already be set when a later hook fails) — documented, not solved here.
- **Idempotent re-run**: current status already equals target → skip the edge entirely (no `frontmatter-update`, no edge `script` hooks — external side effects never run twice); only the states entry's `hooks.post` (if declared) run, mirroring plan transitions. Report: `<to> → <to> (idempotent)` + post-hook lines only.
- **Degenerate artifacts**: artifact file exists but has no frontmatter or no `status:` key → exit 1 with a message naming the artifact and the expected key; never guessed, never auto-repaired.
- **Instance slug extraction**: the slug is the path component at the index where `{instance}` sits in the artifact pattern (path-part indexing, not string parsing of the full match) — pattern `steps/{instance}/index.md` → component 1 of each glob hit relative to workdir.
- **Report over re-read**: both transition commands print a structured report of every mutation (format locked in I/O contract). The "re-read frontmatter to confirm" instruction is removed from `_plan_transitions.j2` and CLAUDE.md.
- **playbook.yaml vs playbook.md**: playbook.yaml owns `graph`, `state`, `states`. playbook.md keeps prose + identity frontmatter (`name, title, summary, trigger, jinja, requires_project`). `graph:` present in both files → STOP notice. playbook.yaml with invalid YAML → STOP notice.
- **Legacy fallback**: no playbook.yaml → frontmatter `graph:` parsed exactly as today, without states (state commands error with "no states declared"; rendering and driving behave as today). The two global playbooks (playbook-authoring, user-stories) live outside this repo and keep working via the fallback; migrating them is vault-side follow-up work, out of this plan.
- **Run workspace convention**: for vault-attached runs the driving convention is workdir = `<vault>/_runs/<playbook>/<run-slug>/`, created by the driver skill (documented in the driving protocol; any workdir works). A playbook's run machine tracks the *procedure*; an artifact with its own lifecycle (e.g. a plan file) keeps that lifecycle — they never share a file.

## Architecture

- `booping-python/src/booping/context/playbook.py` — loader: playbook.yaml discovery, states parse + ref resolution, new problem kinds. `Playbook` model gains `states: dict[str, StateMachine]` and per-scope state refs.
- `booping-python/src/booping/context/lifecycle.py` — resolver generalized to take a machine dict (`statuses`/`superstates`/`hooks`); plan callers pass `config["plan"]`.
- `booping-python/src/booping/commands/transition.py` — plan executor; gains report output; hook dispatch helpers shared with the new command where practical.
- `booping-python/src/booping/commands/playbook_transition.py` (new) — playbook executor: state/artifact resolution, bootstrap, `frontmatter-update` + `script` hooks, report.
- `booping-python/src/booping/commands/playbook_state.py` (new) — read-only state reader, YAML to stdout.
- `booping-python/src/booping/commands/render_playbook.py` + `src/templates/_partials/_playbook_graph.j2` — composed render gains a `## State` section per states entry; state problems join the notice stream.
- `src/templates/_partials/_playbook_driving.j2` — driving protocol gains resume-from-state + fire-transitions rules (live templates, no build step).
- Callers: `/playbook` and `/groom-playbook` skills consume the driving partial; `documentation/playbook.md` and CLAUDE.md document the surface.

### playbook.yaml example (normative — M5.3 docs reuse it)

```yaml
# playbooks/<name>/playbook.yaml
state: main
graph:
  intake: []
  research-codebase: [intake]
  research-web: [intake]
  design: [research-codebase, research-web]
  step-pipeline:
    dependencies: [design]
    state: step
    repeat: once per item the design names
    graph:
      step-spec: []
      step-review: [step-spec]

states:
  main:
    artifact: index.md
    initial: intaking
    statuses:
      intaking:
        transitions:
          - to: researching
            when: intake step complete
            gates: ["request + scope captured in the artifact"]
            hooks: ["frontmatter-update intaken=@now"]
      researching:
        transitions:
          - to: developing-steps
            when: both research steps returned and design confirmed
            gates: ["research-codebase and research-web done, findings recorded"]
            hooks: ["frontmatter-update researched=@now commit=@head", "script check-findings"]
      developing-steps:
        transitions:
          - to: done
            when: every step instance terminal
            gates: ["every steps/*/index.md status: done"]
            hooks: ["frontmatter-update completed=@now"]
      done: {terminal: true}
  step:
    artifact: steps/{instance}/index.md
    initial: spec-ing
    statuses:
      spec-ing:
        transitions:
          - to: reviewing
            when: spec written
            hooks: ["frontmatter-update spec_done=@now"]
      reviewing:
        transitions:
          - to: done
            when: user confirmed the spec
            gates: ["explicit user confirmation captured"]
            hooks: ["frontmatter-update confirmed=@now"]
      done: {terminal: true}
```

Hook vocabulary in `hooks:` — `frontmatter-update <key>=<val>...` (against the entry's artifact; `@now`/`@today`/`@head` interpolation, same as plan transitions) and `script <name>` (from `_scripts/`, per Decisions). Statuses here deliberately don't mirror graph nodes one-to-one — the author chooses granularity.

## Milestones

### M1: playbook.yaml manifest + named states in loader — 6 SP | done

**Goal**: `Playbook.load_all` reads graph + states from `playbooks/<name>/playbook.yaml` when present, with validated `state:` refs; frontmatter `graph:` remains the fallback.

**Verify**: `cd booping-python && uv run pytest tests/context/playbook_test.py` green; a fixture playbook with playbook.yaml loads graph + states; a fixture with both `graph:` sources yields the STOP-level problem.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | playbook.yaml discovery + graph relocation: parse `graph:` from playbook.yaml when the file exists; frontmatter fallback unchanged; `graph:` in both → new problem kind `graph_in_both`; unparseable playbook.yaml → problem kind `bad_manifest`. Subgraph nodes accept a `state` key (`_SUBGRAPH_KEYS`). | `booping-python/src/booping/context/playbook.py`, `booping-python/tests/context/playbook_test.py`, fixtures under `booping-python/tests/__fixtures__/` | 3 | done |
| 1.2 | `StateMachine` model + ref resolution: parse the top-level `states:` mapping + `state:` refs into `StateMachine` entries (`artifact: str`, `initial: str`, `statuses: dict`, raw dict preserved for the resolver); validate initial ∈ statuses, artifact non-empty, `{instance}` allowed only in subgraph-referenced entries; `state:` ref to a missing entry → problem `unknown_state`; `states:` entry never referenced → non-blocking problem `orphan_state`. `Playbook` gains `states` + `state_refs` (scope → states name). | `booping-python/src/booping/context/playbook.py`, `booping-python/tests/context/playbook_test.py`, fixtures | 3 | done |

#### Task 1.1 DoD

- [x] Fixture playbook with playbook.yaml (graph only) resolves identical waves to its frontmatter twin.
- [x] `graph:` in both files produces `graph_in_both`; invalid YAML produces `bad_manifest`; both carried in `graph_problems`.
- [x] Legacy playbooks (frontmatter graph, no playbook.yaml) load byte-identically to today (existing tests untouched and green).

#### Task 1.2 DoD

- [x] States entries parse with artifact/initial/statuses; raw dict round-trips to the resolver unchanged.
- [x] `state:` ref to a missing entry → `unknown_state`; `states:` entry never referenced → `orphan_state`.
- [x] A playbook.yaml without `states:` (graph only) is valid — states are optional.

---

### M2: lifecycle generalization + transition report — 5 SP | done

**Goal**: the resolver works on any machine dict; `booping transition` prints a structured report of every mutation and the re-read instruction is gone.

**Verify**: `cd booping-python && uv run pytest tests/context/lifecycle_test.py tests/commands/transition_test.py` green; a manual `booping transition` run prints the report shape from the I/O contract.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Generalize resolver: `resolve_edges(status, machine)` / `resolve_hooks(from_status, to_status, machine)` take the machine dict (keys `statuses`, `superstates`, `hooks`) instead of digging `config["plan"]`; update all call sites to pass `config["plan"]`. | `booping-python/src/booping/context/lifecycle.py`, `booping-python/src/booping/commands/transition.py`, `booping-python/tests/context/lifecycle_test.py` | 2 | done |
| 2.2 | Transition report: after hooks run, print to stdout — line 1 `<from> → <to>`, then one line per executed hook: `frontmatter: k=v ...` (resolved values, quoted when containing spaces), `render-sprints: <n> plans → <path>`, `vault-commit: <short-sha>` (or `vault-commit: nothing to commit`). Idempotent re-run prints `<to> → <to> (idempotent)` + post-hook lines. | `booping-python/src/booping/commands/transition.py`, `booping-python/src/booping/commands/vault_commit.py` (return sha), `booping-python/tests/commands/transition_test.py` | 2 | done |
| 2.3 | Drop re-read: `_plan_transitions.j2` replaces "re-read the plan frontmatter to confirm" with "the report is authoritative — do not re-read to verify"; same fix to the CLAUDE.md "Plan lifecycle" bullet. | `src/templates/_partials/_plan_transitions.j2`, `CLAUDE.md` | 1 | done |

#### Task 2.1 DoD

- [x] Existing lifecycle tests pass with machine-dict arguments; no behavior change for plans.
- [x] No remaining call site passes the full config to the resolver.

#### Task 2.2 DoD

- [x] Report lines match the I/O contract for happy path, `--also`, and idempotent re-run.
- [x] stdout carries only the report; diagnostics stay on stderr.

#### Task 2.3 DoD

- [x] `bin/booping render src/templates/skills/groom.md.j2` output contains the new wording and no re-read instruction.
- [x] CLAUDE.md no longer instructs post-transition re-read.

---

### M3: `booping playbook-transition` executor — 5 SP | done

**Goal**: one command moves a playbook run artifact through its machine, running `frontmatter-update` and `script` hooks deterministically, printing the report.

**Verify**: `cd booping-python && uv run pytest tests/commands/playbook_transition_test.py` green; manual run against a fixture playbook moves the artifact and prints the report.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Subcommand `playbook-transition <playbook> <to> [--state <name>] [--instance SLUG] [--workdir PATH]`: resolve playbook from context (respect `--workdir` default cwd); default `--state` = the outer graph's ref; `--instance` required iff the states entry's artifact path contains `{instance}` (missing/extra → exit 1); read current status from artifact frontmatter (file exists but no frontmatter / no `status:` key → exit 1 per Decisions); missing artifact → only `<to> == initial` legal, creates the file with `status: <initial>`; idempotent re-run per Decisions; illegal edge → exit 1 listing allowed targets. | `booping-python/src/booping/commands/playbook_transition.py` (new), `booping-python/src/booping/cli.py`, `booping-python/tests/commands/playbook_transition_test.py` (new), fixtures | 3 | done |
| 3.2 | Hook dispatch + report: `frontmatter-update` against the artifact with `@now/@today/@head` interpolation (reuse transition.py helpers); `script <name>` runs `<playbook-dir>/_scripts/<name>` per the Decisions contract (absolute playbook-dir, cwd=workdir, env vars); unknown hook → exit 2; report format per I/O contract. Log line to `.booping.log` in the standard format: `<iso8601-utc>: [playbook-transition] <playbook> <state>[/<instance>] <from>→<to>`. | `booping-python/src/booping/commands/playbook_transition.py`, `booping-python/tests/commands/playbook_transition_test.py` | 2 | done |

#### Task 3.1 DoD

- [x] Bootstrap: missing artifact + target=initial creates file (with parent dirs) and reports it; missing artifact + other target exits 1.
- [x] `--instance` validation both directions; `{instance}` interpolated into the artifact path.
- [x] Illegal edge exits 1 with allowed targets on stderr.
- [x] Idempotent re-run: edge hooks skipped, only `hooks.post` run, report says `(idempotent)` (test).
- [x] Degenerate artifact (no frontmatter / no `status:`) exits 1 naming the artifact (test).
- [x] `--workdir` omitted → artifact resolved against cwd (test).

#### Task 3.2 DoD

- [x] Script hook receives `BOOPING_ARTIFACT`/`BOOPING_INSTANCE`/`BOOPING_WORKDIR`, runs with cwd=workdir; non-zero exit → command exit 2 with script stderr relayed.
- [x] Report shows `frontmatter:` line and `script <name>: ok` per executed hook.

---

### M4: `booping playbook-state` reader + full-run integration test — 4 SP | done

**Goal**: one read-only command reports the full run state — outer status, valid next edges, and every subgraph instance — as YAML on stdout; an end-to-end test proves the resume story.

**Verify**: `cd booping-python && uv run pytest tests/commands/playbook_state_test.py` green; manual run against a mid-run fixture workdir prints outer + instance statuses.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Subcommand `playbook-state <playbook> [--workdir PATH]`: for each states entry (outer first, then subgraph ones) report status (`not-started` when the artifact is missing; degenerate artifact → exit 1 per Decisions) and `next` edges (`to`, `when`, `gates`) from the resolver; enumerate instances by globbing `{instance}` → `*` and extracting the slug via path-part indexing per Decisions, sorted; playbook without states → exit 1 "no states declared"; unknown playbook → exit 1. YAML shape per I/O contract. | `booping-python/src/booping/commands/playbook_state.py` (new), `booping-python/src/booping/cli.py`, `booping-python/tests/commands/playbook_state_test.py` (new), fixtures | 3 | done |
| 4.2 | Full-run integration test: a fixture playbook with an outer states entry + one `{instance}` subgraph entry walked end-to-end in a tmp workdir — bootstrap outer, advance to the subgraph-covering status, bootstrap two instances, advance one to terminal, assert `playbook-state` mid-run snapshot matches (statuses + next edges + both instances), advance everything to terminal, assert final snapshot. Exercises transition + state through the CLI entry points, not internals. | `booping-python/tests/commands/playbook_run_integration_test.py` (new), fixtures | 1 | done |

#### Task 4.1 DoD

- [x] Output is valid YAML matching the I/O contract; instances keyed by dir slug, sorted.
- [x] Missing outer artifact → `status: not-started`, `next` = the initial-bootstrap edge only.
- [x] Degenerate artifact exits 1 (test, mirroring playbook-transition).
- [x] Read-only: no file writes, no log side effects beyond the standard `.booping.log` line.

#### Task 4.2 DoD

- [x] Integration test runs both CLI entry points end-to-end in a tmp workdir and passes.
- [x] Mid-run and final `playbook-state` snapshots asserted structurally (parsed YAML, not string match).

---

### M5: renderer, driving protocol, docs — 8 SP | done

**Goal**: composed renders surface states, the shared driving protocol gains resume + harness-managed transitions, and all reference docs describe the new surface.

**Verify**: renderer tests cover the `## State` section on a states-bearing fixture; `bin/booping render-playbook groom` still composes unchanged (legacy path); `bin/booping render src/templates/skills/playbook.md.j2` renders the updated protocol; `just lint typecheck test` green.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | Renderer: `## State` section after `## Execution graph` — per states entry a table (status → to / when / gates / hooks) + artifact path + the exact `playbook-transition` / `playbook-state` invocations; state problems (`unknown_state`, `graph_in_both`, `bad_manifest` as STOP; `orphan_state` as Note) join the notice stream. | `booping-python/src/booping/commands/render_playbook.py`, `src/templates/_partials/_playbook_graph.j2`, `booping-python/tests/test_render_playbook.py` | 3 | done |
| 5.2 | Driving protocol: `_playbook_driving.j2` — on entry to a states-bearing playbook run `playbook-state --workdir <run workdir>` and resume from the reported frontier; when a step outcome matches a transition's `when`, judge `gates` then fire `playbook-transition` and trust its report; never hand-edit artifact status. Playbooks without states keep today's in-conversation protocol verbatim. | `src/templates/_partials/_playbook_driving.j2` | 3 | done |
| 5.3 | Docs: rewrite `documentation/playbook.md` (playbook.yaml, named states, state/transition/state commands, `_scripts/`, resume); update CLAUDE.md playbook paragraph + `## CLI` section; update `skills/playbook` thin-shell `allowed-tools` if new booping subcommands need it (then `just build`). | `documentation/playbook.md`, `CLAUDE.md`, `src/files/skills/playbook/SKILL.md.j2` (if needed) | 2 | done |

#### Task 5.1 DoD

- [x] Fixture playbook with states renders the `## State` section; fixture without states renders no such section.
- [x] Each new problem kind appears in-band with the correct STOP/Note level (test per kind).

#### Task 5.2 DoD

- [x] Rendered protocol instructs: state read on entry, transition on trigger, report trusted, no manual status edits.
- [x] `/playbook` and `/groom-playbook` render clean (`bin/booping render` on both skill templates).

#### Task 5.3 DoD

- [x] documentation/playbook.md examples parse (yaml snippets lint-clean) and match implemented CLI flags.
- [x] CLAUDE.md CLI section lists both new subcommands with one-line contracts.
- [x] No stale references to frontmatter-only graphs remain in documentation/ or CLAUDE.md.

---

### M6: rendered-output reshape pause — 1 SP | pending

**Goal**: hand the rendered artifacts back to the user for prose shaping before the sprint closes.

**Verify**: user has reviewed and either confirmed or requested reshapes; requested reshapes applied.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 6.1 | Pause: present to the user — a states-bearing fixture's composed `render-playbook` output, rendered `/playbook` + `/groom-playbook` skill bodies, `documentation/playbook.md` — and apply requested IA/prose reshapes (lesson 0004 four-check pass). | rendered outputs of M5 files | 1 | pending |

#### Task 6.1 DoD

- [ ] User explicitly confirmed the rendered shapes (or reshapes applied and re-confirmed).

---

## I/O contract

**`booping playbook-transition <playbook> <to> [--state <name>] [--instance SLUG] [--workdir PATH]`**

- stdout (report; the authoritative record — consumers must not re-read to verify):

  ```
  intaking → researching
  frontmatter: status=researching researched="20260730 14:02"
  script check-findings: ok
  ```

  Bootstrap adds `created <artifact-path>` as line 1. Idempotent re-run: `researching → researching (idempotent)`.
- stderr: diagnostics, script stderr relay, errors.
- Exit codes: `0` success; `1` user error (unknown playbook/state, illegal edge, instance mismatch, missing artifact with non-initial target, degenerate artifact without frontmatter `status:`); `2` internal/hook failure (script non-zero, unknown hook, unwritable artifact).

**`booping playbook-state <playbook> [--workdir PATH]`**

- stdout (YAML):

  ```yaml
  playbook: grooming
  workdir: /abs/path
  states:
    main:
      artifact: index.md
      status: researching
      next:
        - to: designing
          when: both research steps returned
          gates: ["research-codebase and research-web done, findings recorded"]
    step:
      artifact: steps/{instance}/index.md
      instances:
        step-spec-intake: {status: done}
        step-spec-design: {status: llm-tests, next: [{to: fixtures, when: tests confirmed}]}
  ```

- Exit codes: `0` success; `1` unknown playbook or no states declared.

**`booping transition`** (changed surface only): stdout gains the report lines shown in Task 2.2; exit codes unchanged.

## Final Verification

- [ ] `just lint`, `just typecheck`, `just test` green.
- [ ] `--help` for both new subcommands reflects the documented flags.
- [ ] Happy path + one failure path verified by invocation for `playbook-transition`, `playbook-state`, and the `transition` report.
- [ ] `bin/booping render-playbook groom` (legacy path) and both driver skill templates render cleanly (consumer-skill check).

## Out of scope

- Authoring the core `grooming` playbook — deferred; generated later on the shipped machinery (follow-up plan). `playbooks/groom/` and `/groom-playbook` stay as-is on the legacy fallback.
- Migrating the two global playbooks (`playbook-authoring`, `user-stories`) to playbook.yaml + states — vault-side, kept working by the legacy fallback.
- Changing the canonical `/groom` skill, template, or artifacts in any way.
- Concurrency control for parallel instance transitions (last-writer-wins on distinct files is acceptable; instances never share an artifact).
- Rollback/undo of partially-applied hook lists (matches existing plan-transition behavior).
- Plan-lifecycle migration into a `states:`-style block — `config["plan"]` stays where it is; only the resolver call shape changes.

## CLAUDE.md impact

- `## CLI`: add `playbook-transition` and `playbook-state`; note the transition report contract.
- Layout: rewrite the Playbooks bullet (playbook.yaml, named states, `_scripts/`, resume); core-playbook bullet unchanged (`playbooks/groom/` stays).
- Plan lifecycle: replace the post-transition re-read bullet with the report contract.
