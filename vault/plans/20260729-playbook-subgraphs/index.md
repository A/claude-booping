---
title: Playbook Subgraphs with Repeat
type: feature
status: done
sp: 19
split_from: null
created: 2026-07-29 22:35
planned: 20260729 12:14
started: 20260729 15:12
completed: null
retro: null
goal: null
summary: "Nested subgraph nodes in playbook graphs: dependencies + prose repeat +
  inner graph; drop body embedding"
commit: 072f5af8e3b8e569fddeaac53edb269290200501
sessions:
- eb1cde4d-1ee3-4823-965b-c51497570a98
- 3f3ac793-6fef-4805-b0a6-c28513710c15
metrics_active_minutes: 32
metrics_models:
- claude-fable-5
metrics_tokens_input: 291
metrics_tokens_output: 198383
metrics_tokens_cache_creation: 535745
metrics_tokens_cache_read: 12465717
---

# Playbook Subgraphs with Repeat

## Context

The playbook `graph:` frontmatter is a flat mapping `step → [deps]`. Long procedures (e.g. a playbook-authoring pipeline where `step-spec → fixtures → llm-tests → step-prompt → step-suite → smoke-optimizer → regress-optimizer` should run once per decomposed step) cannot express grouping or repetition. After this ships:

- A graph node may be a **subgraph**: a mapping with `dependencies:` (list, outer-scope names), optional `repeat:` (prose, LLM-driver-judged), and `graph:` (inner mapping, same rules as top level). One nesting level only.
- A subgraph without `repeat` is pure grouping and runs once.
- `render-playbook` renders the subgraph as a cluster in the mermaid chart, a nested entry in the wave list, and an intro section followed by inner step sections; the driving protocol tells the driver how to expand `repeat` instances at runtime.
- **No step body is ever embedded** in the composed output (today wave-1 bodies are). Every step section carries a fetch form (Read link, or `--step` command for jinja playbooks). Rationale: embedded bodies leak whole step prompts into the harness context of the driving skill.

## Decisions

- **Node discrimination**: graph node value list → plain step (deps inline, unchanged). Value mapping → subgraph node; requires `dependencies` (list) + `graph` (non-empty mapping); optional `repeat` (string). Any other key, wrong type, or a mapping value inside an inner graph (nesting) → blocking STOP notice.
- **`repeat` is prose, not an expression** — mirrors the config `gates` (verifiable) vs `when` (prose) split. Step outputs carry no schema, so nothing mechanical could evaluate a `foreach`; the driver enumerates instances by judgment from upstream output.
- **Scope rule**: inner graph deps reference inner names only; a subgraph's `dependencies` reference outer-scope names only (plain steps or other subgraph nodes). Cross-scope reference → `unknown_dep` STOP notice naming the scope.
- **Step addressing stays flat**: step dirs remain flat subdirectories of the playbook dir, so names are globally unique and `--step <name>` needs no namespacing. Each step name may appear at most once across the outer graph and all inner graphs; a duplicate → STOP notice.
- **One nesting level** — subgraph inside a subgraph is a STOP notice. Lift later if needed.
- **No embedding, anywhere**: `compose()` never inlines a step body; the `embed` branch is removed. For `jinja: true` playbooks, step bodies are no longer pre-rendered at compose time — a body's Jinja error now surfaces at `--step` fetch time (as the existing in-band STOP text from `compose_step`), not at compose time. Preamble rendering is unchanged.
- **Gates per instance**: a `review_gate` on a step inside a repeated subgraph fires on every instance. Authors control noise by omitting gates.
- **Inline steps in repeated subgraphs are allowed**: static inline-parallel check applies per inner wave (within one instance). Instance-level parallelism is driver judgment: instances may run in parallel only when every inner step has a non-null `agent`; otherwise sequential.
- **Model shape**: `Playbook.graph` stays `dict[str, list[str]]` for the outer scope (subgraph node key → its `dependencies`); new `Playbook.subgraphs: dict[str, SubgraphNode]` carries `repeat` + inner graph. `resolve_waves` is unchanged and is called once per scope.

## Architecture

`booping render-playbook <name>` composition pipeline, loader→renderer→driver:

1. **Loader** (`booping-python/src/booping/context/playbook.py`): `_load_one` parses the discriminated graph into outer `graph` + `subgraphs`, collecting shape problems as new `GraphProblem` kinds (`bad_node`, `nested_subgraph`, `duplicate_step`). Wave resolution runs per scope.
2. **Renderer** (`booping-python/src/booping/commands/render_playbook.py` + `src/templates/_partials/_playbook_graph.j2`, `_playbook_step.j2`): notices for the new problem kinds; mermaid `subgraph … end` cluster; nested wave list; subgraph intro section; `Part of:` chrome on inner steps; all step sections fetch-form.
3. **Driver** (`src/templates/_partials/_playbook_driving.j2`, included by `/playbook` and `/groom-playbook`): fetch-only wording plus the repeat-expansion rule.

Composed-output contract for a subgraph (locked here; exact strings in tasks):

```
## Subgraph: step-pipeline

Instructions:
- After: manifest
- Repeat: once per step produced by decompose; instances may run in parallel
- Inner waves: 1. `step-spec` 2. `fixtures` …

## Step Spec

Instructions:
- Part of: step-pipeline (repeated)
- …existing bullets…

Run `booping render-playbook <name> --step step-spec` for content.
```

Wave list: the subgraph appears in its outer wave as `` `step-pipeline` *(subgraph)* ``; its inner waves render as an indented numbered sub-list under that line. Mermaid: `subgraph step-pipeline["step-pipeline (repeat)"] … end` cluster with `dependencies` drawn as edges into the cluster.

Existing playbooks (`playbooks/groom/`) contain no subgraphs and keep rendering — but lose wave-1 embedding like everything else; the driving protocol covers the fetch in step 1 already.

## Milestones

### M1: Loader — subgraph parse, validation, per-scope waves — 5 SP | done

**Goal**: `Playbook` loads the discriminated graph into `graph` + `subgraphs` with all shape/scope problems collected as `GraphProblem`s, never raised.

**Verify**: `cd booping-python && uv run pytest tests/context/playbook_test.py -q` — green, including new subgraph cases.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | `SubgraphNode` model (`name`, `dependencies: list[str]`, `repeat: str \| None`, `graph: dict[str, list[str]]`); `name` is auto-populated from the graph key by `_load_one` (same pattern as `Step.name` from the dir name); parse discriminated node forms in `_load_one`; new `GraphProblem` kinds `bad_node` (missing/extra/mistyped keys), `nested_subgraph`, `duplicate_step` (same step name in two scopes) | `booping-python/src/booping/context/playbook.py`, `booping-python/tests/context/playbook_test.py` | 3 | done |
| 1.2 | Per-scope wave resolution: `resolve_waves` on the outer graph (subgraph node = one node) and once per inner graph; new `Playbook.executable_step_names` property returning `list[str]` — outer plain-step keys + all inner keys, excluding subgraph keys — consumed by the missing/orphan checks in M3 | `booping-python/src/booping/context/playbook.py`, `booping-python/tests/context/playbook_test.py` | 2 | done |

#### Task 1.1 DoD

- [x] List node → plain step; mapping node → `SubgraphNode`; parse never raises on malformed frontmatter.
- [x] Mapping without `dependencies` or `graph`, with an unknown key, with a non-list `dependencies`, or with a non-mapping `graph` → `bad_node` problem naming the node.
- [x] Mapping value inside an inner graph → `nested_subgraph` problem.
- [x] Same step name in outer scope and an inner graph (or two inner graphs) → `duplicate_step` problem.
- [x] Subgraph without `repeat` loads with `repeat is None` (grouping-only).
- [x] Existing flat-graph playbooks load byte-identical to before (regression cases pass untouched).

#### Task 1.2 DoD

- [x] Outer waves place a subgraph node by its `dependencies` exactly like a plain step.
- [x] Inner graphs resolve to their own waves; inner `unknown_dep`/`cycle` problems carry the subgraph name (scope) for the notice.
- [x] Inner dep naming an outer step → `unknown_dep`; subgraph `dependencies` naming an inner step → `unknown_dep`.
- [x] `Playbook.executable_step_names` excludes subgraph keys and includes all inner keys.

---

### M2: Renderer — drop body embedding entirely — 2 SP | done

**Goal**: no composed output ever contains a step body; every step section is fetch-form.

**Verify**: `cd booping-python && uv run pytest tests/test_render_playbook.py -q` green; `bin/booping render-playbook groom | grep -c 'render-playbook groom --step'` equals the number of graph steps.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Remove the `embed` branch: `compose()` in `booping-python/src/booping/commands/render_playbook.py` stops pre-rendering wave-1 bodies (the `for name in waves[0] …` loop and `bodies` dict go away; jinja playbooks: preamble still rendered; body errors now surface at `--step` time) and drops `embed=` from the `step_tmpl.render(...)` kwargs; `_playbook_step.j2` drops the `embed` input and always emits the fetch form (Read link for plain, `--step` command for jinja); update all affected tests/fixtures | `booping-python/src/booping/commands/render_playbook.py`, `src/templates/_partials/_playbook_step.j2`, `booping-python/tests/test_render_playbook.py` | 2 | done |

#### Task 2.1 DoD

- [x] No step body text appears in `compose()` output for any playbook (plain or jinja), any wave.
- [x] Jinja playbooks: compose no longer fails on a broken step body; the error surfaces from `compose_step` at fetch time as the existing in-band STOP text.
- [x] `_playbook_step.j2` has no `embed` input; `compose()` passes none.
- [x] All existing render tests updated to the fetch-form expectation; no test asserts an embedded body.

---

### M3: Renderer — subgraph composition — 7 SP | done

**Goal**: a playbook with a subgraph renders the locked contract: notices for new problem kinds, mermaid cluster, nested wave list, subgraph intro section, inner step sections with `Part of:` chrome.

**Verify**: `cd booping-python && uv run pytest tests/test_render_playbook.py -q` green (subgraph fixtures are built with the existing tmp-path playbook builders in `booping-python/tests/helpers.py` / test-local factories — no committed fixture dir); for the eyeball pass, scaffold a throwaway subgraph playbook under the session scratch dir and render it with `bin/booping render-playbook <name> --project <scratch-vault>`.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | STOP notices for `bad_node`, `nested_subgraph`, `duplicate_step`; inner-scope `unknown_dep`/`cycle` notices prefixed with the subgraph name; `_MISSING`/orphan checks driven by the executable-step-names helper; inline-parallel check applied per inner wave | `booping-python/src/booping/commands/render_playbook.py`, `booping-python/tests/test_render_playbook.py` | 2 | done |
| 3.2 | `_playbook_graph.j2`: mermaid `subgraph <name>["<name> (repeat)"] … end` cluster (inner edges inside, `dependencies` as edges into the cluster); wave list renders the subgraph as `` `<name>` *(subgraph)* `` with an indented inner-wave sub-list | `src/templates/_partials/_playbook_graph.j2`, `booping-python/tests/test_render_playbook.py` | 2 | done |
| 3.3 | Compose walk: subgraph intro section (`## Subgraph: <name>` with `After:`, `Repeat:` when set, `Inner waves:` bullets) emitted at the subgraph's outer-wave position, then inner step sections in inner wave order with a `Part of: <name>[ (repeated)]` bullet; `_playbook_step.j2` gains the `Part of:` input | `booping-python/src/booping/commands/render_playbook.py`, `src/templates/_partials/_playbook_step.j2`, `booping-python/tests/test_render_playbook.py` | 3 | done |

#### Task 3.1 DoD

- [x] Each new problem kind renders one `**STOP — tell the user:**` notice naming the node and, for inner-scope problems, the subgraph.
- [x] A graph key with neither a step dir nor a subgraph entry still yields `_MISSING`; subgraph keys themselves never yield `_MISSING`.
- [x] A step dir wired only into an inner graph is not an orphan; an unwired dir still is.
- [x] Two inline steps sharing an inner wave → `_INLINE_PARALLEL`.
- [x] Any blocking notice suppresses the execution graph and step sections (existing contract holds).

#### Task 3.2 DoD

- [x] Mermaid output for a fixture with one subgraph parses (fenced block well-formed) and contains exactly one `subgraph … end` cluster.
- [x] Cluster title carries `(repeat)` only when `repeat` is set.
- [x] Wave list shows the subgraph once, in its resolved outer wave, with all inner waves as an indented numbered sub-list.
- [x] Flat playbooks render the graph section byte-identical to before.

#### Task 3.3 DoD

- [x] Section order: outer wave order; at the subgraph's slot — intro section, then inner sections in inner wave order.
- [x] `Repeat:` bullet appears in the intro iff `repeat` is set, verbatim prose.
- [x] Inner step sections carry `Part of: <name>` (` (repeated)` suffix iff `repeat` set) and are fetch-form (M2 rule).
- [x] `--step <inner-step>` returns the body with no chrome, unchanged from plain steps.

---

### M4: Driving protocol + reference docs — 4 SP | done

**Goal**: the driver knows how to run subgraphs (repeat expansion, per-instance gates, instance parallelism) and every reference that claims wave-1 embedding or a flat-only graph is updated.

**Verify**: `bin/booping render src/templates/skills/playbook.md.j2 | grep -i subgraph` shows the new protocol; `grep -rn "embedded" CLAUDE.md documentation/playbook.md` shows no stale wave-1-embedding claim.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | `_playbook_driving.j2`: step 1 reworded to fetch-only (no embedded bodies); new subgraph rule — on a `## Subgraph:` section, enumerate instances by judgment from the `repeat` prose and upstream output (one instance when no `repeat`), walk inner waves per instance, honor gates per instance, run instances in parallel only when every inner step has a non-null agent (else sequentially), report per-instance completion. Context/concurrency bounds: fetch each inner step body **once** and reuse it across instances; spawn at most 4 instance sub-agent batches per message; per-step bounded return contracts (existing protocol step 2) apply per instance. Run the lesson-0004 four-check IA pass on the updated partial before saving | `src/templates/_partials/_playbook_driving.j2` | 2 | done |
| 4.2 | `documentation/playbook.md`: new "Subgraphs" section (schema, scope rule, repeat semantics, one-level limit) + update graph/embedding claims; CLAUDE.md Playbooks bullet: embedding sentence and graph description updated to the new contract | `documentation/playbook.md`, `CLAUDE.md` | 2 | done |

#### Task 4.1 DoD

- [x] Protocol contains no mention of embedded wave-1 bodies.
- [x] Subgraph rule covers: instance enumeration (prose-judged), per-instance inner-wave walk, per-instance gates, agent-gated instance parallelism, per-instance failure reporting.
- [x] Bounds present: fetch-once-reuse for inner bodies, ≤ 4 parallel instance spawns per message.
- [x] Four-check IA pass (lesson 0004) applied to the partial; result noted in the milestone report.
- [x] Rendered `/playbook` and `/groom-playbook` skills include the updated protocol (`bin/booping render` spot-check).

#### Task 4.2 DoD

- [x] `documentation/playbook.md` documents the subgraph node schema with a YAML example and the STOP conditions.
- [x] No document in the repo still claims wave-1 bodies are embedded (grep for "embed" across `CLAUDE.md`, `documentation/`, `docs/`).
- [x] CLAUDE.md Playbooks bullet reflects: discriminated node forms, one nesting level, fetch-only sections.

---

### M5: Prose reshape pause — 1 SP | pending

**Goal**: user shapes the rendered surfaces before the plan leaves execution.

**Verify**: user has reviewed and either edited or explicitly accepted each surface.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | /develop pauses and hands back for shaping: (a) composed output of the M3 throwaway subgraph playbook (scratch dir, rendered via `--project`), (b) the updated `_playbook_driving.j2` as rendered inside `/playbook`, (c) the new `documentation/playbook.md` section. Apply the user's prose edits; no logic changes | `src/templates/_partials/_playbook_driving.j2`, `src/templates/_partials/_playbook_step.j2`, `src/templates/_partials/_playbook_graph.j2`, `documentation/playbook.md` | 1 | pending |

#### Task 5.1 DoD

- [ ] All three rendered surfaces presented to the user.
- [ ] User edits applied or explicit "no changes" captured.
- [ ] Tests still green after prose edits (`just test`).

---

## I/O contract

`booping render-playbook` surface is unchanged in shape; content contract changes:

- **Arguments / flags**: `booping render-playbook <name> [--step NAME] [--project PATH] [--output PATH]` — no new flags. `--step` addresses any step dir, inner or outer, by flat name.
- **stdout**: composed markdown — notices → preamble → `## Execution graph` (mermaid + nested wave list) → sections in outer wave order, subgraph intro + inner sections at the subgraph's slot. **No step bodies anywhere** — fetch forms only. `--step` prints the bare body (unchanged).
- **stderr**: unknown playbook / unknown step (unchanged).
- **Exit codes**: unchanged — `0` incl. in-band STOP notices; `1` unknown playbook/step; `2` internal.

## Final Verification

- [ ] `just lint && just typecheck && just test` green.
- [ ] `bin/booping render-playbook groom` renders with zero embedded bodies and no notices.
- [ ] Fixture subgraph playbook renders all four surfaces per the locked contract.
- [ ] Malformed-subgraph fixtures produce their STOP notices, exit 0.
- [ ] `bin/booping render src/templates/skills/playbook.md.j2` renders cleanly with the updated protocol.

## Out of scope

- Nesting beyond one level.
- Mechanical `foreach` expressions or structured step-output channels.
- Sub-playbook composition (`use:` referencing another playbook).
- Changes to `/groom`, the groom core playbook's graph, or eval suites.
- Persisting instance state across sessions (driving stays in-conversation).

## CLAUDE.md impact

The Playbooks bullet in the Layout section: graph description gains the subgraph node form (`dependencies` + optional `repeat` + inner `graph`, one level), and the "wave-1 step bodies are embedded" sentence is replaced by the fetch-only contract. Handled in Task 4.2.
