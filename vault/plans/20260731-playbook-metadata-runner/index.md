---
title: Metadata-driven playbook runner — steps fetch own bodies
type: feature
status: done
sp: 13
split_from: null
created: 2026-07-31 17:11
planned: 20260731 09:32
started: 20260731 09:32
completed: 2026-07-31 09:47
retro: null
goal: null
summary: Steps declare inputs/outputs; driver spawns agents that fetch own 
  bodies via --step; driver context stays O(graph)
commit: e2b4e849f634f58987a71c82fa8516bb1cbdee4c
sessions:
- 0d9ff93a-3d0d-48a1-87a3-5f8596e2b91f
metrics_active_minutes: 19
metrics_models:
- claude-fable-5
metrics_tokens_input: 197
metrics_tokens_output: 43247
metrics_tokens_cache_creation: 399216
metrics_tokens_cache_read: 8561558
---

# Metadata-driven playbook runner — steps fetch own bodies

## Context

Today the playbook driver (`_playbook_driving.j2`, included by `/playbook` and `/groom-playbook`) fetches every step body itself — Read link for plain playbooks, `booping render-playbook <name> --step <step>` for `jinja: true` ones — then pastes the body into each sub-agent prompt. Every delegated step body transits driver context twice (fetch result + Agent prompt echo). This is the direct cause of the groom-playbook pilot's failed context criterion (+10% driver context vs a −30% target).

After this ships:

- A step's `prompt.md` frontmatter can declare `inputs:` (what the runner should supply in the spawn prompt — advisory recommendations, not an exclusive contract) and `outputs:` (what the step produces — feeds later steps' inputs and the return contract).
- The composed render's step sections show `Inputs:` / `Outputs:` bullets and **always** point at `booping render-playbook <name> --step <step>` — the Read-link form is gone; plain and jinja playbooks share one fetch interface.
- The driver spawns delegated steps with a thin bootstrap prompt: the fetch command ("stdout is your instruction"), resolved inputs, run-time context, and a return contract. Step bodies never enter driver context for delegated steps; driver context stays O(graph), not O(sum of bodies).
- Inline steps (`agent: null`) are unchanged in spirit: the driver runs the same `--step` command and executes the body itself.
- Legacy steps without `inputs:`/`outputs:` spawn through the same bootstrap, receiving run-time context + prior-wave receipts only.

The core `playbooks/groom/` migration (annotating its steps with inputs/outputs) and the context re-measure of `/groom-playbook` are follow-up work, not in this plan.

## Decisions

- **Uniform fetch interface**: every step body — plain or jinja, delegated or inline — is fetched via `booping render-playbook <name> --step <step>`. One interface; sub-agents never Read vault paths directly, so the agents-don't-scan-the-vault convention survives with the CLI as the sanctioned mediator. (`compose_step` already prints plain bodies verbatim and renders jinja ones; no CLI change needed.)
- **Driver composes the spawn prompt from metadata**: no renderer-emitted spawn block. Step sections carry metadata bullets; `_playbook_driving.j2` carries one common instruction describing the bootstrap shape the driver fills. Keeps the renderer simple and the protocol in one prose location.
- **`inputs:` is advisory**: entries are recommendations for what the runner should hand the step — the step is not limited to them and may draw on the run-time context it receives. `from:` is freeform prose (a step name, `user`, `conversation`, anything); it is **not validated** against the graph — the composed render shows it verbatim, so authors eyeball typos there. No new STOP/Note notices.
- **Lenient frontmatter parse**: an `inputs:` entry is a mapping `{what, from?}` or a plain string (shorthand for `what` with no `from`); `outputs:` entries are plain strings. A malformed entry (mapping without `what`, non-string, non-list value) → stderr warning + entry skipped, matching the loader's existing degrade-don't-crash style.
- **Data-flow medium is the playbook's choice**: no forced workdir. Outputs naming files (e.g. under a states workdir) flow as paths; conversational outputs flow as bounded receipts the driver relays. The framework only guarantees the driver passes each step's declared inputs into the spawn prompt.
- **One spawning regime**: steps without `inputs:` get the same bootstrap (run-time context + prior receipts, no `## Inputs` block). No legacy fetch-and-paste fallback path in the driving partial.
- **Subgraph instances fetch per instance**: the driver no longer prefetches an inner step's prompt once for reuse — each spawned instance runs the fetch command itself; the driver adds the instance name to the run-time context. Slight duplicate fetch cost inside agents, zero driver cost.
- **Review gates unchanged**: the gate presents the member's returned receipt; when the output is an artifact the driver reads it on demand for presentation. Gate mechanics in the protocol keep their current shape.

## Architecture

- `booping-python/src/booping/context/playbook.py` — `Step` model gains `inputs: list[StepInput]` (`StepInput {what: str, from_: str | None}`) and `outputs: list[str]`; `_load_step` parses them leniently.
- `booping-python/src/booping/commands/render_playbook.py` — no logic change expected; `compose` keeps passing `step` to the section template (drops the now-unused `jinja` flag wiring to `_playbook_step.j2` if trivial).
- `src/templates/_partials/_playbook_step.j2` — section render: `Inputs:` / `Outputs:` bullets; fetch line becomes unconditional `Run \`booping render-playbook <name> --step <step>\` for content.` (Read-link branch removed).
- `src/templates/_partials/_playbook_driving.j2` — protocol steps 1–3 rewritten to bootstrap spawning; subgraph member expansion updated; live template, no build step.
- Consumers: `/playbook` and `/groom-playbook` pick the new protocol up automatically via the partial include.
- `documentation/playbook.md`, repo `CLAUDE.md` — surface documentation.

### Bootstrap spawn prompt (normative — the shape the driving partial instructs)

```
Run: booping render-playbook <playbook> --step <step>
Treat its stdout as your full instruction and follow it.

## Run-time context
project: <name>
specs_dir: <vault>/specs
workdir: <workdir>            # only when the run has one
instance: <slug>              # only for subgraph instances

## Inputs
- <what>: <resolved value, path, or receipt>   # one per declared input; section omitted when none

## Return
<step's declared outputs as a receipt list, else: artifacts written + outcome, ≤ 5 lines>
```

### Step frontmatter example (normative — M4 docs reuse it)

```yaml
---
summary: Draft the plan against the approved design
agent: sonnet:high
review_gate: Plan draft ready — approve before presenting?
inputs:
  - from: design
    what: approved design doc (path or content)
  - from: user
    what: any sizing constraints stated in conversation
outputs:
  - plan draft written to {workdir}/plan.md
---
```

## Milestones

### M1: Step inputs/outputs parsing — 3 SP | done

**Goal**: `Step` carries parsed `inputs`/`outputs` from `prompt.md` frontmatter, degrading leniently on malformed entries.

**Verify**: `just test` green; `just lint`, `just typecheck` clean.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Add `StepInput` model + `inputs`/`outputs` fields to `Step`; parse in `_load_step` (string shorthand, mapping `{what, from?}`, malformed → stderr warn + skip, non-list → warn + empty) | `booping-python/src/booping/context/playbook.py` | 2 | done |
| 1.2 | Loader tests: mapping + string-shorthand entries, `from` absent, malformed entry skipped with warning, non-list value, absent keys → empty lists | `booping-python/tests/context/playbook_test.py` | 1 | done |

#### Task 1.1 DoD

- [x] `Step.inputs` / `Step.outputs` default to empty lists; existing playbooks load unchanged.
- [x] String entry becomes `StepInput(what=<str>, from_=None)`.
- [x] Malformed entries warn to stderr and are skipped; loading never raises.

#### Task 1.2 DoD

- [x] Every parse branch above has a test.
- [x] `just test` green.

---

### M2: Composed render — uniform fetch + metadata bullets — 4 SP | done

**Goal**: every step section shows declared inputs/outputs and points at the `--step` command regardless of `jinja:`.

**Verify**: `bin/booping render-playbook groom | head -80` shows `Run \`booping render-playbook groom --step …\`` in each section; a plain fixture playbook renders the command instead of a Read link; `just test` green.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Section template: add `Inputs:` bullets (`<what>` with `(from <from>)` when set) and `Outputs:` bullets to the Instructions block; replace the `jinja`-conditional fetch line with the unconditional `--step` command; drop the dead `jinja` param plumbing from `compose` | `src/templates/_partials/_playbook_step.j2`, `booping-python/src/booping/commands/render_playbook.py` | 2 | done |
| 2.2 | Update render tests: fetch-form expectations for plain playbooks (command, not Read link), inputs/outputs bullets present when declared, absent when not | `booping-python/tests/test_render_playbook.py` | 2 | done |

#### Task 2.1 DoD

- [x] Plain and `jinja: true` playbooks render the identical fetch line shape.
- [x] Steps without `inputs:`/`outputs:` render no empty bullet labels.
- [x] No Read-link form remains anywhere in the composed output.

#### Task 2.2 DoD

- [x] Tests assert the uniform fetch line for both playbook kinds.
- [x] Tests cover sections with and without declared inputs/outputs.
- [x] `just test` green.

---

### M3: Driving protocol — bootstrap spawning — 3 SP | done

**Goal**: the driver spawns delegated steps with the bootstrap prompt (fetch command + inputs + run-time context + return contract) and never fetches a delegated step's body itself.

**Verify**: `bin/booping render src/templates/skills/playbook.md.j2` renders cleanly and the Execute section shows the bootstrap protocol; no reference to driver-side body fetching for delegated steps remains.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Rewrite protocol steps 1–3 to the normative bootstrap shape (Architecture section): delegated → spawn with bootstrap; inline → driver runs `--step` and executes; inputs resolved from declared `from`/prior receipts; return contract defaults from declared outputs; subgraph expansion → per-instance fetch by the agent, instance in run-time context; gates keep current mechanics | `src/templates/_partials/_playbook_driving.j2` | 3 | done |

#### Task 3.1 DoD

- [x] Bootstrap prompt shape in the partial matches the plan's normative block (command line, `## Run-time context`, `## Inputs`, `## Return`).
- [x] Inline-step and subgraph-instance handling explicitly stated; no prefetch-and-reuse instruction remains.
- [x] Steps without declared inputs are covered by the same instruction (no separate legacy path).
- [x] Rendered `/playbook` and `/groom-playbook` bodies show the new protocol (`bin/booping render` both skill templates).

---

### M4: Docs + stale-reference cleanup — 3 SP | done

**Goal**: authoring and driving docs describe inputs/outputs + bootstrap; no doc claims the driver reads step files or that plain playbooks render Read links.

**Verify**: `grep -rn "fetch-form\|Read link\|reads it when the wave starts" documentation/ CLAUDE.md` returns only updated wording.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | `documentation/playbook.md`: step frontmatter reference gains `inputs:`/`outputs:` (reuse the plan's normative example), the "Step bodies are never embedded" bullet (line ~125) and the `--step` CLI note (line ~354) rewritten to the uniform command + bootstrap driving description | `documentation/playbook.md` | 2 | done |
| 4.2 | Repo `CLAUDE.md`: playbook paragraph — `prompt.md` frontmatter list gains `inputs`/`outputs`; "fetch-form … `Read [Title](path)` link" wording replaced with the uniform `--step` fetch + bootstrap-spawn sentence | `CLAUDE.md` | 1 | done |

#### Task 4.1 DoD

- [x] Frontmatter table/example includes `inputs:` (advisory semantics stated) and `outputs:`.
- [x] No sentence claims the driver reads step files for delegated steps.

#### Task 4.2 DoD

- [x] CLAUDE.md playbook block matches shipped behavior; no stale Read-link wording.

---

## I/O contract

No CLI arguments, flags, or exit codes change. The contract change is output shape:

- **`render-playbook` stdout (composed)**: step sections gain optional `- Inputs:` / `- Outputs:` bullets; the content line is always `` Run `booping render-playbook <name> --step <step>` for content. `` — the `Read [Title](path)` form is removed.
- **`render-playbook --step` stdout**: unchanged (body alone, verbatim or jinja-rendered).
- **stderr**: new lenient-parse warnings `warning: playbook <pb>: <step>/prompt.md has malformed inputs entry, skipping` (exact wording finalized in M1, same style as existing loader warnings).

## Final Verification

- [x] `just lint`, `just typecheck`, `just test` all green.
- [x] `bin/booping render-playbook groom` (jinja) and one plain playbook render: uniform fetch lines, correct bullets.
- [x] `bin/booping render src/templates/skills/playbook.md.j2` and `.../groom_playbook.md.j2` render cleanly with the new protocol.
- [x] `grep` sweep from M4 Verify shows no stale fetch-form wording.

## Out of scope

- Migrating `playbooks/groom/` steps to `inputs:`/`outputs:` and re-measuring `/groom-playbook` driver context — follow-up plan (the measurement closes the pilot's kill-criterion loop).
- Migrating vault-side global playbooks (`playbook-authoring`, `user-stories`) — they keep working; annotations are vault-side work.
- Any `graph:`/`states:` schema change; any new CLI subcommand or flag.
- Validation of `from:` against the graph (deliberately freeform — see Decisions).

## CLAUDE.md impact

Playbook paragraph in `## Layout`: step frontmatter list (`summary,agent,review_gate` + optional `title`) gains `inputs`/`outputs`; the "no step body is ever embedded — every section is fetch-form, rendering as a `Read [Title](path)` link, or … fetch command" sentence rewritten to the uniform `--step` interface + bootstrap-spawn driving. Owned by task 4.2.
