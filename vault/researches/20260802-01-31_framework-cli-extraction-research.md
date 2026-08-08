---
title: Framework CLI extraction — research
status: research
created: 20260802 01:31
---

# Framework CLI extraction — research

Proposal under review: split booping into a **framework CLI** + **core playbooks**, where the CLI handles (0) md-listing with frontmatter tables, (1) jinja rendering with proper context, (2) frontmatter updates with macros, (3) state machines/transitions, (4) layered config incl. macro definitions. Goal: easy authoring of new playbooks on top of the framework; simpler framework.

Verdict up front: **the direction is already half-built and half-decided** — `playbooks/groom/_specs/DECISIONS.md:9` already states *"playbook-specific behavior lives in playbooks; booping core stays a pure playbook framework."* The five proposed capabilities all exist in some form except (0). The real work is not adding capabilities but **evicting the plan domain from core** and **unifying the two parallel state-machine dispatchers**. Below: what exists, what the proposal missed, and the open questions.

## 1. Where the five capabilities stand today

### 0. md listing as frontmatter table — MISSING (only true gap in the list)

No CLI command lists md files. Today listing is done three ways, all ad hoc:

- `/playbook` skill renders `context.playbooks` as a markdown table (LLM-side, from assembled context).
- `render-sprints` renders `context.plans` through `sprints.md.j2` — a hardcoded, plan-only "listing" (`commands/render_sprints.py`, 68 LOC).
- The eval harness discovers suites with `find`-style globs, bypassing booping entirely.

A generic `booping list <glob> [--fields k1,k2] [--where k=v] [--format table|yaml|json]` subsumes all three: playbook listing, run-artifact status boards (`_runs/**/index.md` by `status:`), plan boards, eval-suite inventories. The `frontmatter-update`/`parse_frontmatter` primitives in `context/_yaml.py` (139 LOC, fully generic) already provide the read layer. This also becomes the replacement for `render-sprints`: a listing command + a template equals a sprints report, which `DECISIONS.md:7` already slates as a future `booping sprints-report` outside core.

### 1. Jinja rendering — EXISTS, generic; the *context* is the problem

`rendering.py` (168 LOC), `tools.py` (61 LOC), the `render` command, and `render-playbook`'s `ChoiceLoader` chain (body dir → step dir → playbook dir → roots local→global→core → `src/templates/`) are all plan-free already. What is **not** framework-clean is what the context carries — see §2 "Context assembly".

### 2. Frontmatter updates + macros — EXISTS, with two defects

`frontmatter-update` is generic (any md file, `@now`/`@today`/`@head`, `--remove`, file-target grammar for playbook hooks). Defects:

- `_interpolate` is **duplicated verbatim** in `commands/frontmatter_update.py:37-55` and `commands/transition.py:44-65`. Two copies, three call sites.
- Macros are a hardcoded `if/elif` chain — no registry, no way for a playbook or project to add one.

### 3. State machines — EXISTS, one core, two dispatchers

`context/lifecycle.py` (169 LOC) is already the generic resolver: `resolve_edges`/`resolve_hooks` operate on any `{statuses, superstates, hooks}` dict — `config["plan"]` and playbook `states:` entries deliberately share this shape. What's duplicated between `transition.py` (285 LOC, plan) and `playbook_transition.py` (235 LOC, playbook):

| Concern | plan `transition` | `playbook-transition` |
|---|---|---|
| idempotent re-run | own code | own code (same pattern) |
| bootstrap missing artifact | forbidden (error) | allowed when target = `initial` |
| hook vocabulary | `frontmatter-update`, `render-sprints`, `vault-commit`, `suggest` | `frontmatter-update` (+file-target), `script` |
| report builder | own list-of-lines | own list-of-lines |
| exit-code plumbing | re-raised SystemExit | `_fail()` helper |

Unification = one dispatcher parametrized by (machine dict, artifact path, hook registry, bootstrap policy). `lifecycle.py` already is the shared half; only execution/reporting remains to merge. Then **plan transitions become just another state machine instance** — `plan.statuses` moves out of `src/config.yaml` into a `states:` declaration owned by the plans playbook set.

### 4. Config — EXISTS as core→global→project; the proposed tiers differ

Today: `src/config.yaml` (core) ← `~/.config/booping/config.yaml` (global) ← `{vault}/config.yaml` (project), deep-merge, `agents` shallow, lists replace wholesale (`context/config.py`, 78 LOC + `utils.deep_merge`). Plus a fourth, separate, non-tiered `src/config_files.yaml` (build-only).

The proposal names "core settings" and "playbook settings" but the current stack has **user-global** and **project** tiers the proposal doesn't mention — both are load-bearing (global carries `home_dir`; project carries `cross_review`, agent registrations). And the proposed **playbook-owned tier is genuinely new**: today a playbook cannot ship config defaults. `playbooks/groom/draft-plan` reads `config.get("cross_review")` — a key with **no core default, no schema, no owner** (`_specs/index.md:23-29`). The tier ladder wants to be:

```
framework core → playbook defaults (shipped in playbook dir) → user global → project
```

with framework-level keys reduced to almost nothing (`home_dir`, macro registry, discovery roots) and everything else playbook-owned.

**Macros in config — "can we?"** Yes, with one caveat. Static-format macros (`@now`, `@today`) are pure data: `macros: {now: {format: "%Y%m%d %H:%M", utc: true}}`. Command macros (`@head` = `git rev-parse HEAD`) mean **config-defined shell execution** — but the playbook engine already runs arbitrary `_scripts/` hooks, so a config-defined `@git_commit: {shell: git rev-parse HEAD}` adds no new trust boundary *as long as macros resolve only from playbook/core/global tiers a user consciously installed*. Registry also kills the `_interpolate` duplication. One rule to keep: macro resolution stays **eager and single-pass** (no macro-expanding-macro), or the mutation report stops being deterministic.

## 2. What the proposal missed

Ordered by weight.

### a) The playbook composition engine itself — the biggest framework component isn't in the list

`context/playbook.py` (586 LOC) + `commands/render_playbook.py` (565 LOC) = **31% of the codebase**: discovery across three roots, name-clash rules, graph parsing (steps/subgraphs/waves), `compose()` (metadata-only sections + fetch commands), the STOP/Note in-band problem protocol, the ChoiceLoader chain. It's already plan-free and already *is* the framework. The five listed capabilities are its substrate, not its replacement. Any framework CLI must name this as capability **5: playbook discovery + composed rendering** — otherwise the plan describes the plumbing and forgets the machine.

### b) Context assembly — decide what a "framework context" contains

`Context.assemble()` today loads: `plans`, `retros`, `plan_templates`, `review_templates`, `lessons`, `skills`, `agents`, `extra_instructions` (all domain) alongside `playbooks`, `config`, `project` (framework). The no-vault path already proves the split: without a `.booping` marker, only `skills/agents/playbooks/config` load — the framework surfaces.

For a pure framework, domain collections should not be hardcoded pydantic loaders. Replace with **config-declared collections**:

```yaml
collections:
  plans: {glob: "plans/*.md", schema: optional}
  retros: {glob: "retrospectives/*.md"}
```

Then `context.collections.plans` in jinja, and `booping list plans` for capability 0 — one mechanism serves both. `Plan.load_all`'s hardcoded literal types (`feature|bug|refactoring`), `Retro`, `PlanTemplate`, `ReviewTemplate` all leave core. Bonus: this pre-solves the groom-v3 respec's open problem — *"plan-as-directory breaks `Plan.load_all`'s `plans/*.md` glob"* (`_specs/index.md:140-142`) — because the glob becomes config, not code.

### c) Migration path for the plan lifecycle — the hard part, unstated

"Framework + core playbooks" implies the plan lifecycle (statuses, sprints, vault-commit) becomes playbook-owned. What that concretely means:

- `plan.statuses`/`superstates`/`hooks.post` move from `src/config.yaml` to a `states:` file in the plans playbook set. `lifecycle.py` consumes it unchanged (already shape-compatible by design).
- `render-sprints` dies as a core command → `booping list` + template, or a playbook `_scripts/` hook. Precedent already exists: `playbooks/groom/_scripts/_plan_status.py` **already re-implements** sprints-render + vault-commit vault-side because playbook machines lack `plan.hooks.post` equivalents — proof that the eviction is possible AND that without framework support it produces duplication (it hardcodes `vault = workdir.parent.parent.parent`).
- `vault-commit` becomes either a generic framework hook (`commit <paths>` — a git side-effect primitive, defensible in core since `@head` already assumes git) or a playbook script. Recommend keeping a generic `git-commit` hook in the framework: three playbook sets will reinvent it otherwise.
- `transition` (the plan command) collapses into unified `playbook-transition` once dispatchers merge.
- The old skills (`/groom` canonical, `/develop`, `/retro`, `/learn`, `/chat`) keep working during migration — they read `config.plan.*`. Either a compat shim (framework re-exports the plans playbook's `states:` under `config.plan`) or a hard cutover per skill. This sequencing question is the most expensive unstated decision in the proposal.

### d) Scaffolding — "easy way to create playbooks" needs a command, not just docs

`bin/booping-create-project` scaffolds vaults, nothing scaffolds playbooks. The `playbook-authoring` playbook exists (vault `_core_playbooks/playbook-authoring`) — it's the *procedure*; a `booping playbook new <name>` (dirs + manifest + one step + optional `states:` stub) is the mechanical half. Also missing: `booping playbook validate <name>` — today validation only happens as in-band STOP notices inside `render-playbook` output; the eval/authoring loop wants a plain exit-code lint.

### e) Playbook distribution — `_dist/` exists, framework has no story

Vault-global root already has `_dist/`, `_lib/` is a **symlink** into the repo (`~/Claude/_playbooks/_lib → repo/playbooks/_lib`), and eval suites live vault-side. If the goal is "others build playbooks on the framework," missing pieces: install/update a playbook from a repo/URL, version pinning, the `_lib/` sharing mechanism formalized (today: symlink by hand). Even a minimal `booping playbook install <git-url>` decision (yes/no/later) belongs in the plan.

### f) The driving protocol stays LLM-side — the CLI cannot absorb it

Worth stating explicitly so the framework doesn't over-reach. Stays in `_playbook_driving.j2` / skills: playbook selection, bootstrap-prompt composition, agent spawning (`detached:` resolution), parallel dispatch discipline, review gates, `Repeat:` instance enumeration, judging prose gates before firing transitions, resume interpretation. Framework CLI = deterministic substrate; driver = judgment. The proposal's frame ("framework = CLI") is right only if the generic driver partial + a thin `/playbook`-style skill are counted as framework deliverables too — they are the other half.

### g) Eval harness contract

Harness needs from the CLI: `--project` (render outside attached project), `--no-lessons` (byte-deterministic output). Notably the harness **bypasses** `render-playbook` for suites (promptfoo reads step files raw, no jinja) — so jinja-converted steps must keep labeled plain-md bodies (`opus-5.md`) testable directly. Framework requirement hiding here: **composed output must stay byte-deterministic under fixed inputs**, i.e. macros/timestamps never leak into `render-playbook` output. Also `booping list` should emit `--format json` so the harness can drive discovery through the CLI instead of globbing.

### h) Conditional edges / optional steps — known missing capability

`_specs/index.md:21`: *"Conditional edges do not exist in the framework, so optional steps always run and record a skip note."* If the framework charter is being rewritten anyway, decide: add conditional/skippable nodes (graph-level `when:` prose judged by driver + a first-class `skipped` outcome), or bless the skip-note workaround as the pattern.

### i) Small but real

- **Logging**: `.booping.log` is vault-coupled (`vault/_booping/`, silent no-op without vault). Framework-only invocations (no project) log nowhere. Decide a projectless log location or drop the feature.
- **Skills/agents/build pipeline**: `skills/`, `agents/`, `src/files/`, `config_files.yaml`, `build` command are Claude-Code-plugin packaging, not framework. In the target world the plugin shrinks to thin driver skills; `config_files.yaml`'s only payload (`effort`) could fold into normal config, killing the fourth config file and possibly the whole build step.
- **`inputs`/`outputs` step frontmatter**: documented in CLAUDE.md, absent from the `Step` model, dropped by the groom respec — delete from the schema during extraction, not after.
- **Doc drift found while researching**: root CLAUDE.md still documents step field `agent:`; code hard-STOPs on it (`legacy_agent_key`, `playbook.py:572`) — current field is `detached:`. Also `debug-template` is a stub (`sys.exit(1)`), and one transient `config-get` crash was observed (`_load_step() takes 3 positional arguments but 4 were given` — not reproducible after; likely stale bytecode, worth one eye during extraction).
- **Naming**: `frontmatter-update`'s positional arg is `plan`; generic CLI wants `file`.

## 3. Target CLI surface (sketch)

| Command | Status |
|---|---|
| `render <template>` | keep (context slimmed to framework + collections) |
| `render-playbook <name> [--step]` | keep — the centerpiece |
| `playbook-state` / `playbook-transition` | keep; `transition` (plan) merges into it |
| `frontmatter-update <file>` | keep; macros from registry |
| `list <collection\|glob>` | **new** — capability 0; replaces `render-sprints` |
| `config-get` | keep; tiers become core → playbook → global → project |
| `playbook new` / `playbook validate` | **new** — authoring loop |
| `transition`, `render-sprints`, `vault-commit` | evicted to plans playbook (vault-commit possibly survives as generic `git-commit` hook) |
| `build`, `debug-template` | plugin-side / drop |

Size check: today 3659 LOC total; playbook engine + lifecycle + rendering + yaml + config ≈ 1900 LOC of it is already the framework. The eviction removes ~700 LOC of plan domain (`transition`, `render_sprints`, `vault_commit`, `plan/retro/template loaders`) and adds back `list` + macro registry + unified dispatcher — net smaller and single-purpose, which matches the "simplify framework" goal.

## 4. Open questions (decide before building)

1. **Migration sequencing**: compat shim for `config.plan.*` so old skills keep working, or per-skill cutover? (Old `/groom` is contractually frozen — the shim looks forced.)
2. **Distribution**: is the framework CLI still plugin-embedded (`uv run --project`) or a published package the plugin depends on? `DECISIONS.md:7` hints published ("a future published booping CLI").
3. **Lessons**: framework feature (stays — it's playbook-scoped and generic) or driver concern? Current implementation is already playbook-native; recommend keep.
4. **`project`/vault concept**: framework keeps workspace discovery (`.booping`, `home_dir`) — it's generic "where do collections/runs live" — but the *name* vault and layout conventions move to playbook docs.
5. **Shell macros in project-tier config**: allow, or restrict command-macros to core/global/playbook tiers? (Project tier is repo-checked-in for local vaults → someone else's repo defines a shell command your transition runs.)

---
Sources: full-codebase catalog + playbook-consumer survey by two research agents (booping-python/src/booping/* with file:line refs; playbooks/*, _specs/, vault-side _playbooks/ eval harness). LOC figures from `wc -l`.
