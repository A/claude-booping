---
title: Jinja Playbooks — Composed Step Rendering
type: feature
status: done
sp: 16
split_from: null
created: 2026-07-22 23:47
planned: 20260722 16:05
started: 20260722 16:27
completed: 2026-07-22 16:47
retro: null
goal: null
summary: Playbook body becomes a template; inline_step/reference_step compose 
  steps with directives generated from frontmatter, not authored prose
commit: 2da1080b3e02dcb6cad15adf65e58183479be9bb
sessions:
- 84f5a95b-cb18-4156-99a3-6bead1d78f10
- dd8af31c-0543-4a87-a23a-ad76f962b78d
metrics_active_minutes: 34
metrics_models:
- claude-opus-4-8
metrics_tokens_input: 113662
metrics_tokens_output: 202492
metrics_tokens_cache_creation: 1174988
metrics_tokens_cache_read: 21369541
---

# Jinja Playbooks — Composed Step Rendering

## Context

Today a playbook is `playbook.md` (frontmatter `name,title,summary,trigger,steps`) + `steps/<step>.md` (frontmatter `name,summary,agent,model,effort,review_gate`; body = prompt). The `playbook.md` **body** is free-form prose. All execution logic lives in the `/playbook` skill: it iterates `context.playbooks[].steps`, reads each step file, composes an invocation, spawns the agent or runs inline, and honors `review_gate`.

Two wrinkles:

1. **No composition control.** The author can't compose steps into one procedure document — inlining short steps and referencing long ones. The body is inert prose the LLM reads for orientation only.
2. **Gate ownership sits in prose.** The `review_gate` already lives in step frontmatter, yet playbook bodies **restate** it ("After `current-time`, stop at its review gate") alongside hand-written `## Steps` / `## Gates` sections. This duplicates frontmatter and drifts.

After this plan: the `playbook.md` body is a **Jinja template**. The author writes `{{ inline_step('name') }}` / `{{ reference_step('name') }}` calls; `booping render-playbook <name>` unwraps them into a composed procedure. Each step section carries a per-step **Instructions** block — sub-agent config and review-gate directive — **generated from step frontmatter**, never authored. `inline_step` embeds the step body; `reference_step` emits a lazy `Read [Step](path)` link. The gate stops being author prose and becomes a rendered directive owned by the pipeline; the `/playbook` skill enforces the pause.

## Decisions

- **Playbook body is Jinja**: rendered by a new `booping render-playbook <name>` subcommand, not the generic `render` — the composition functions must be bound to a specific playbook's loaded steps. — Reverses the prior "no Jinja in playbooks" stance for the manifest body only; step files stay plain markdown prompts.
- **Composition functions**: `inline_step('name')` and `reference_step('name')` exposed as Jinja globals inside the manifest render, closured over the target playbook's steps. Unknown step name → render fails with a clear error (author catches typos). — Real Jinja `{{ ... }}`, not a custom `{...}` mini-syntax; reuses the existing Jinja stack.
- **Step-block shape = Instructions list** (locked output contract, see Architecture). Directives are bullets under an `Instructions:` header, emitted **only** when the source frontmatter carries them. — Chosen over blockquote/italic variants.
- **One `agent` field, not three.** Collapse `agent`/`model`/`effort` into a single `agent:` string. Grammar: `null` → run inline in the conversation; `<model>:<effort>` (e.g. `opus:high`, `sonnet:low`) where the left side is a known model tier → spawn a generic sub-agent with that model + effort; any other non-null string → a named sub-agent (`subagent_type=<value>`, colon-safe so `booping:booping-researcher` resolves). — Removes the current dead-weight case (a step with `agent:null` but `model`/`effort` set, which the skill silently ignored on inline). Discriminator: split on first `:`; left ∈ {opus, sonnet, haiku, fable} → model:effort, else the whole value is an agent name.
- **Directives come from frontmatter only**: sub-agent bullet from the resolved `agent` field; review-gate bullet from `review_gate`. If a step has neither, no `Instructions:` block renders — just header + body/reference. — This is the mechanism that moves gate ownership out of author prose (concern 2).
- **Driving intro lives in the `/playbook` skill body**, not in the rendered doc. — The generic "you are running a playbook; honor sub-agents and gates" contract is stable across every playbook; duplicating it into each render violates booping IA (skill owns driving, rendered doc owns per-run content).
- **Drop the `steps:` frontmatter key.** The loader globs `steps/*.md` (skipping `_`-prefixed); the body's `inline_step`/`reference_step` **call order** defines the composed sequence. — Single source of truth: no drift between a frontmatter list and the body calls. A step file present but never called simply does not appear.
- **Reference link uses the step's absolute path.** — The skill (or a spawned agent) can `Read` it regardless of cwd.
- **Un-migrated playbooks degrade, not break**: a body with no composition calls renders its raw prose through. — Lets the two existing playbooks keep working until M4 migrates them.

## Architecture

**Load-time inputs**: `Playbook.load_all(vault, home_dir)` → `context.playbooks`. Model changes: `Playbook` gains `body: str` (the manifest body, currently discarded); `Step` gains optional `title: str`, drops `model` and `effort`, and keeps `agent: str | None` now carrying the collapsed grammar above. A small resolver (`resolve_agent(value) -> {"mode": "inline"|"model"|"named", ...}`) parses the field once for both the render partial and the driving skill.

**Render path** (`booping render-playbook <name>`):
1. `Context.assemble()` → find the playbook by `name` in `context.playbooks` (miss → stderr + exit 1, mirroring `config-get`).
2. Build a Jinja `Environment` with a `FileSystemLoader` rooted at `src/templates` (so `_partials/_playbook_step.j2` loads), register `inline_step` / `reference_step` as globals closured over that playbook + a partial-render helper.
3. Render the playbook's manifest `body` via `env.from_string(...)`.
4. Each function resolves the named `Step` and renders `_partials/_playbook_step.j2` with `mode="inline"|"reference"`.

**Locked output contract** — one step section:

```
## <Title>

Instructions:
- Run in a sub-agent — model opus, effort high.
- Review gate: stop after this step — "<review_gate>"; continue only on explicit user confirmation.

<step body>
```

Rules, exact:
- **Title** = `step.title` if set, else the step `name` titleized (`current-time` → `Current Time`).
- **Sub-agent bullet** renders only when `agent` is non-null, resolved per the grammar:
  - `<model>:<effort>` → `Run in a sub-agent — model <model>, effort <effort>.`
  - named agent (`general-purpose`, `booping:booping-researcher`) → `Run in sub-agent: <agent>.`
  - `null` → no bullet (step runs inline).
- **Review-gate bullet** renders only when `review_gate` is non-null. Wording verbatim: `Review gate: stop after this step — "<review_gate>"; continue only on explicit user confirmation.`
- **Neither `agent` nor `review_gate`** → the entire `Instructions:` block is omitted; section is just header + content.
- **Inline mode** → the step body follows the Instructions block.
- **Reference mode** → replaces the body with exactly: `Read [<Title>](<absolute step path>) for content.` (Instructions block still renders above it when present.)

**Drive path** (`/playbook` skill): renders the composed doc via `booping render-playbook <name>`, then walks its `##` sections in order. Per section: an `Instructions` sub-agent bullet → spawn `subagent_type=<agent>` (passing model/effort); no bullet → run inline. A review-gate bullet → STOP after the step, present output + the gate text, continue only on explicit user confirmation. The skill still appends its `## Run-time context` block to each invocation. The generic driving intro moves into the skill body.

## Milestones

### M1: Playbook data model + step partial — 4 SP | done

**Goal**: `Playbook` carries its manifest body, the loader globs step files instead of reading `steps:`, and a `_playbook_step.j2` partial renders one step to the locked contract.

**Verify**: `just test` (loader + model unit tests pass); manually render the partial against a fixture step and eyeball both modes.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Add `body: str = ""` to `Playbook` (capture manifest body in `_load_one`); on `Step` add optional `title`, drop `model`/`effort`, keep `agent: str \| None`; add `resolve_agent(value)` returning `{mode: inline\|model\|named, model?, effort?, name?}` (split on first `:`, left ∈ {opus,sonnet,haiku,fable} → model, else named; null → inline); loader globs `sorted(steps/*.md)` skipping `_`-prefixed, stops reading `steps:` | `booping-python/src/booping/context/playbook.py` | 2 | done |
| 1.2 | Author `_playbook_step.j2`: takes a `step` + `mode` (`inline`\|`reference`); emits `## <Title>`, the conditional `Instructions:` block (sub-agent + review-gate bullets per the locked rules), then body (inline) or `Read [Title](abs path) for content.` (reference) | `src/templates/_partials/_playbook_step.j2` | 2 | done |

#### Task 1.1 DoD

- [x] `Playbook.body` holds the manifest markdown below the frontmatter.
- [x] `Step.title` is optional (defaults `None`); `model`/`effort` fields removed; `agent` holds the collapsed grammar.
- [x] `resolve_agent` covers all three forms + null, with unit tests including the `booping:booping-researcher` (colon, non-model) case.
- [x] Loader discovers steps by globbing `steps/*.md` (sorted, `_`-prefixed skipped); a `steps:` key in frontmatter is neither required nor read.
- [x] Existing fixtures/tests updated for the dropped `steps:` dependency; `just test` green.

#### Task 1.2 DoD

- [x] Inline mode renders header + Instructions (when applicable) + body.
- [x] Reference mode renders header + Instructions (when applicable) + `Read [Title](<abs path>) for content.` and no body.
- [x] Sub-agent bullet omitted when `agent` null; `<model>:<effort>` and named-agent forms each render their locked phrasing.
- [x] Review-gate bullet omitted when `review_gate` null; wording matches the locked contract verbatim.
- [x] A step with neither `agent` nor `review_gate` renders no `Instructions:` block.
- [x] Title falls back to titleized `name` when `title` unset.

---

### M2: `render-playbook` command + composition functions — 5 SP | done

**Goal**: `booping render-playbook <name>` renders a playbook's body with `inline_step`/`reference_step` bound to its steps, producing the composed procedure.

**Verify**: `just test`; `bin/booping render-playbook <fixture>` prints the composed doc; unknown name exits 1.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | New `render_playbook` command: assemble context, find playbook by name (miss → stderr + exit 1), build a `src/templates`-rooted Jinja env, register `inline_step`/`reference_step` globals closured over the playbook's steps (resolve by name, render `_playbook_step.j2`; unknown name raises), render manifest `body` via `from_string`, write stdout/`--output`. Register in `cli.py`. Log the call via `logger.log`. | `booping-python/src/booping/commands/render_playbook.py`, `booping-python/src/booping/cli.py` | 3 | done |
| 2.2 | Tests: fixture playbook (steps covering all three `agent` forms — `model:effort`, named, null-inline — with/without gate; one inline, one referenced); assert inline body present, reference link present + body absent, gate directive sourced from frontmatter, each agent-form directive rendered, neither-directive step bare, call order drives sequence, un-called step absent, unknown-name render raises, missing-playbook exits 1 | `booping-python/tests/test_render_playbook.py`, fixture under `booping-python/tests/` | 2 | done |

#### Task 2.1 DoD

- [x] `bin/booping render-playbook <name>` prints the composed doc for a known playbook.
- [x] Unknown playbook → stderr message + exit 1.
- [x] `inline_step`/`reference_step` resolve steps from the target playbook only; unknown step name raises with a clear message.
- [x] `--output PATH` writes to file; `--output -`/absent writes stdout.
- [x] A `.booping.log` line is written (mirrors `render`).

#### Task 2.2 DoD

- [x] Every rule in the locked output contract has an asserting test.
- [x] Call order (not glob order) determines section order in the output.
- [x] `just test` green.

---

### M3: `/playbook` skill — render-then-drive — 3 SP | done

**Goal**: the skill renders the composed playbook and drives it, owning the driving intro and gate-pause; step iteration by hand-reading files is gone.

**Verify**: `bin/booping render src/templates/skills/playbook.md.j2` (clean output); `just build`; `git diff -- skills/playbook/` shows the rebuilt shell body only where expected.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Rewrite the skill Execute flow: `booping render-playbook <name>` → walk `##` sections; sub-agent bullet → spawn `subagent_type=<agent>` (model/effort from the bullet), else inline; review-gate bullet → STOP, present output + gate text, resume only on explicit confirmation; keep appending `## Run-time context`. Move the generic driving intro into the skill body. Drop the old "read each step file / iterate `context.playbooks[].steps`" logic. | `src/templates/skills/playbook.md.j2` | 3 | done |

#### Task 3.1 DoD

- [x] Rendered skill body drives from `render-playbook` output, not per-step file reads.
- [x] Driving intro + gate-enforcement contract live in the skill body (from frontmatter-derived directives), not restated per playbook.
- [x] `## Run-time context` still appended to each invocation.
- [x] No prose that re-describes step ordering or gates the rendered doc already carries.
- [x] `bin/booping render src/templates/skills/playbook.md.j2` renders with no `{{placeholder}}` leaks; `just build` clean.

---

### M4: Migrate existing playbooks — 2 SP | done

**Goal**: `test` and `build-user-stories` playbook bodies use `inline_step`/`reference_step` and single-`agent` step frontmatter; their hand-written `## Steps` / `## Gates` prose and `steps:` key are removed.

**Note**: vault-side edits (`<home_dir>/_playbooks/`) — the orchestrator applies them directly during develop. Limited, mechanical; not a heavyweight handoff.

**Verify**: `bin/booping render-playbook test` and `... build-user-stories` produce composed docs whose gate directives come from step frontmatter (no gate prose in the bodies).

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Rewrite `test/playbook.md` body to `inline_step` calls (short steps); migrate step `agent`/`model`/`effort` → single `agent`; delete `steps:` key and the gate/summary prose | `<home_dir>/_playbooks/test/playbook.md`, `test/steps/*.md` (vault) | 1 | done |
| 4.2 | Rewrite `build-user-stories/playbook.md` body: inline short steps, `reference_step` the long ones; migrate step frontmatter to single `agent` (e.g. reshake `sonnet`+`high` → `agent: sonnet:high`); delete `## Steps`/`## Gates` prose and `steps:` key | `<home_dir>/_playbooks/build-user-stories/playbook.md`, `build-user-stories/steps/*.md` (vault) | 1 | done |

#### Task 4.1 DoD

- [x] `test/playbook.md` body is composition calls only; no `steps:` key; no gate prose.
- [x] `render-playbook test` shows the `current-time` review-gate directive sourced from that step's frontmatter.

#### Task 4.2 DoD

- [x] `build-user-stories/playbook.md` body is composition calls; long steps referenced, short inlined; no `steps:` key; no `## Steps`/`## Gates` prose.
- [x] `render-playbook build-user-stories` shows both steps' gates from frontmatter.

---

### M5: Docs + CLAUDE.md — 2 SP | done

**Goal**: every reference to the old playbook model is updated; the new `render-playbook` command and Jinja-body contract are documented.

**Verify**: grep for stale claims (`no Jinja`, `steps` frontmatter key, prose gates) returns only intended hits; `just docs` builds.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | CLAUDE.md: update the Playbooks bullet (drop "Plain markdown, no Jinja"; manifest frontmatter `name,title,summary,trigger` — no `steps`; step frontmatter `name,summary,agent,review_gate` — `model`/`effort` collapsed into `agent`; body carries `inline_step`/`reference_step` calls; gate owned by render from frontmatter); add `render-playbook` to the `## CLI` list | `CLAUDE.md` | 1 | done |
| 5.2 | Rewrite `documentation/playbooks.md`: manifest + step frontmatter contract (drop `steps:`, `model`, `effort`; document the single-`agent` grammar), body-as-template + composition functions, the Instructions-block contract, gate-from-frontmatter, `render-playbook`; update the worked example | `documentation/playbooks.md` | 1 | done |

#### Task 5.1 DoD

- [x] CLAUDE.md Playbooks bullet reflects the Jinja body, dropped `steps:` key, and frontmatter-owned gates.
- [x] `render-playbook` appears in the `## CLI` list with a one-line description.
- [x] No "no Jinja, no build step" claim remains for playbook bodies.

#### Task 5.2 DoD

- [x] `documentation/playbooks.md` frontmatter contract, authoring section, and worked example match the new model.
- [x] The "no Jinja" line and "list your steps in order under `steps:`" instruction are gone.
- [x] `just docs` builds without error.

---

## Final Verification

- [x] `just lint`, `just typecheck`, `just test` green.
- [x] `just build` renders cleanly; `git diff -- skills/ agents/` shows only the intended `skills/playbook/SKILL.md` change (if any).
- [x] `bin/booping render src/templates/skills/playbook.md.j2` — no stale step-iteration prose, no `{{placeholder}}` leaks.
- [x] `bin/booping render-playbook test` and `... build-user-stories` produce composed docs with frontmatter-sourced gate directives.
- [x] Project-local extension point (`_booping/skill_playbook.md`) still inlines.

## Out of scope

- Cross-session playbook resume (still one-conversation only).
- Eval suites / run harness under `<home_dir>/_playbooks/` (`_lib`, `_smoke`, `evals/`, `run.sh`, `justfile`) — vault-side, not this repo.
- Step-file format: `steps/<step>.md` stays a plain-markdown prompt; no Jinja in step bodies.
- Nested/conditional composition (loops, `if` around steps) beyond straight `inline_step`/`reference_step` calls.

## CLAUDE.md impact

Update the **Playbooks** bullet (frontmatter contract, Jinja body, dropped `steps:`, gate ownership) and add `render-playbook` to the **CLI** list — owned by Task 5.1.

---

# Quality Checklist

## Frontmatter

- [x] Frontmatter matches the plan frontmatter template.
- [x] `sp` (16) equals the sum of per-task SP (4 + 5 + 3 + 2 + 2).

## Content

- [x] Context names the behavior change (composed render + frontmatter-owned gates), not "refactor internals".
- [x] DoD bullets verifiable by reading rendered output or a diff.
- [x] Every task lists exact template / partial / config / source paths.
- [x] Every task DoD uses checkboxes.
- [x] Every milestone has a `Verify` step including a rebuild/test.
- [x] Each milestone executable from a fresh session with only the plan.

## Skill-design hygiene

- [x] No structured facts duplicated in prose — directives render from step frontmatter.
- [x] Single-consumer driving intro lives in the skill body, not config.
- [x] No stack-specific details in the skill body.
- [x] No restated flow — rendered composition is the contract.

## Anti-patterns (must be absent)

- [x] No "TBD"/"TODO"/"implement later".
- [x] No task spanning unrelated concerns (data model, renderer, skill, docs each isolated per milestone).
- [x] No prose section duplicating a rendered artifact.

## External references validated

- [x] `booping-python/src/booping/context/playbook.py`, `cli.py`, `src/templates/skills/playbook.md.j2`, `documentation/playbooks.md`, `CLAUDE.md` all exist.
- [x] `render-sprints` command pattern (cli.py registration) confirmed as the mirror for `render-playbook`.
- [x] Vault playbooks `test/` and `build-user-stories/` exist at the resolved `<home_dir>/_playbooks/`.

## CLAUDE.md impact

- [x] Config/render-artifact/CLI changes reflected in CLAUDE.md via Task 5.1.
