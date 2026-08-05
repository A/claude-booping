Playbook `groom`, target step `draft-plan`. The design is confirmed and the plan file exists with
identity frontmatter only — no body has been written yet.

Run-time context:

- project: `claude-booping` (the booping plugin repo)
- run slug: `20260801-sprints-report-script`
- run workdir: the plan directory `plans/20260801-sprints-report-script/`
- plan file: `plans/20260801-sprints-report-script/plan.md` — created by intake, identity
  frontmatter only

The confirmed framing, the blast-radius map, the confirmed design, the plan file as it stands, the
plan-template catalogue, the plan frontmatter shape, the sizing scale and the project's
cross-review configuration follow.

## Confirmed framing — the `## Framing` section of `plans/20260801-sprints-report-script/index.md`

```markdown
## Framing

### Request

> sprints.md should stop being a booping built-in. The groom playbook should render it from its
> own `_scripts/` hook on the transition edges, and booping's `render-sprints` — the subcommand
> and the automatic post hook — should go away.

### Restated problem

Today the vault snapshot is a framework concern: `render-sprints` is a `booping` subcommand and
an entry in `plan.hooks.post`, so every `booping transition` re-renders `sprints.md` whatever
workflow the move belongs to. The report describes one workflow's shape, not the framework's, and
the direction is that playbook-specific behaviour lives in the playbook. The request is to move
the render into a groom-playbook-local script fired as a `script` hook on the machine's edges,
then retire the core surface it replaces.

### Task type

`feature` — a new capability (a playbook-owned reporting script with its own invocation contract)
plus the retirement of the built-in it replaces. Not a bug: nothing diverges from expected
behaviour. Not a refactoring: the invocation surface users depend on changes, not just its
structure.

### Scope boundaries

**In scope**

- the playbook-local script, its hook wiring on the machine's edges, and how it resolves the vault
- the sprints template's new home under the playbook
- removing `render-sprints` from `plan.hooks.post` and from the CLI, and every in-repo caller of
  it (`/chat`'s orient refresh included)

**Out of scope**

- the snapshot's column set and sort order — the rendered table stays byte-comparable
- back-filling or re-rendering historical vaults
- moving any other post hook (`vault-commit` stays where it is)

### Web research

Requested — the user asked for current practice on how a hook-fired standalone script is
built before the design is settled.

### Scope challenge

- [x] Should `booping render-sprints` be removed outright, or kept as a deprecated alias for a
      release? — **Answered:** removed outright; every caller is in this repo and moves in the
      same change.
- [x] Does the script render the whole vault's plans, or only the plans this run touched? —
      **Answered:** the whole vault. The file is a snapshot, exactly as today.
- [x] Any dependency or config surface this must not pull in? — **Answered:** nothing added to
      `booping-python`, and no new config key beyond what the retirement removes.
```

## Blast radius — the `## Blast radius` section of `plans/20260801-sprints-report-script/index.md`

```markdown
## Blast radius

### Touched surfaces

| Surface | Where | Why it moves | Risk |
| --- | --- | --- | --- |
| `render-sprints` hook | `booping-python/src/booping/hooks.py` | retired once the playbook owns the render | medium — every `transition` edge fires it today |
| `render-sprints` subcommand | `booping-python/src/booping/commands/render_sprints.py` | removed with the hook | medium — a caller outside this repo breaks silently |
| subcommand registration | `booping-python/src/booping/cli.py` | the argument parser still exposes the retired name | low |
| subcommand tests | `booping-python/tests/commands/render_sprints_test.py` | a removed subcommand takes its tests with it | low |
| `bin/booping` | `bin/booping` | the wrapper's documented subcommand list names `render-sprints` | low |
| `/chat` orient refresh | `src/templates/skills/chat.md.j2` | the only other in-repo caller — inlines `booping render-sprints` at skill-load time | medium — a stale call renders as an error inside the skill body |
| sprints template | `src/templates/sprints.md.j2` | moves under the playbook's `_scripts/` | low — self-contained, reads `context.plans` only |
| post-hook list | `src/config.yaml` (`plan.hooks.post`) | drops `render-sprints`, leaving `vault-commit` | medium — a project config that pins the list keeps the dead name |
| new script home | `playbooks/groom/_scripts/` | the playbook-local script and the moved template land here | low — the dir does not exist yet |
| hook wiring | `playbooks/groom/playbook.yaml` | the run machine's edges gain the `script` hooks | medium — a wrong edge renders the snapshot at the wrong moment |
| CLI docs | `CLAUDE.md`, `documentation/cli.md` | the retired subcommand is documented in both | low |

### Prior art

- `_scripts/` hooks already run with `BOOPING_WORKDIR`, `BOOPING_ARTIFACT` and `BOOPING_INSTANCE`
  in the environment and cwd set to the run workdir; a non-zero exit aborts the transition. This
  is the working precedent for a playbook-local side effect.
- `bin/booping-create-project` is the reference shape for a standalone uv inline script — PEP 723
  header, no place inside `booping-python`.
- `bin/booping config-get {dotted.key}` is the supported way a shell-side caller reads a resolved
  config value; `bin/booping-create-project` already uses it for `home_dir`.

### Conventions in play

- `skills/` and `agents/` are build artefacts — edit `src/files/**.j2`, then `just build`.
- Structured data lives in `src/config.yaml`; a skill body never restates it as prose.
- Playbook-specific behaviour lives in the playbook; booping core stays a pure playbook framework.
- Every change under `booping-python/` clears `just lint`, `just typecheck`, `just test`; a
  removed subcommand takes its tests with it.

### Unknowns for design

- Whether a script deriving the vault from `BOOPING_WORKDIR` holds for a repo-local vault. The
  default workdir is the plan directory `{vault}/plans/{slug}/`, so the vault is `../..` — but
  a repo-local
  vault named by the `.booping` `vault_path:` marker can sit anywhere in the tree, and the script
  has no assembled context to ask.
```

## Confirmed design — the `## Design` section of `plans/20260801-sprints-report-script/index.md`

```markdown
## Design

### Approach

A standalone uv inline script at `playbooks/groom/_scripts/render-sprints`, fired as a
`script render-sprints` hook on the run machine's edges. It reads `BOOPING_WORKDIR`, resolves the
vault from it, loads every `plans/*.md` frontmatter, and renders the template — moved from
`src/templates/sprints.md.j2` to `playbooks/groom/_scripts/sprints.md.j2` — to `{vault}/sprints.md`.
Chosen over shelling back into the framework CLI because the retirement is the point: with the
render owned by the playbook, `render-sprints` leaves `booping-python/src/booping/hooks.py`, its
subcommand module and registration go with it, and `plan.hooks.post` in `src/config.yaml` drops to
`vault-commit` alone. The script's only framework dependency is `bin/booping config-get`, and only
on the fallback path.

### Surface changes

- **CLI** — `booping render-sprints` removed, together with
  `booping-python/src/booping/commands/render_sprints.py`, its registration in
  `booping-python/src/booping/cli.py` and `booping-python/tests/commands/render_sprints_test.py`.
  `/chat`'s orient refresh in `src/templates/skills/chat.md.j2` drops the call and reads
  `sprints.md` as it stands; `bin/booping`'s documented subcommand list drops the name.
- **Config** — `plan.hooks.post` in `src/config.yaml` becomes `[vault-commit]`; the
  `render-sprints` hook name is removed from `hooks.py`, so a project config still pinning it
  fails loudly at load rather than silently doing nothing. The `vault-commit` post hook itself is
  untouched — it stays on `booping transition`, which this playbook never calls.
- **Script** — `playbooks/groom/_scripts/render-sprints`, PEP 723 header, deps `jinja2` +
  `pyyaml`. Reads `BOOPING_WORKDIR` (required — absent is a usage error, exit 1), `BOOPING_VAULT`
  (optional explicit override), and falls back to `booping config-get home_dir` only when the
  workdir ancestry does not resolve. Refuses to write when the resolved directory has no `plans/`
  beside it. Writes `{vault}/sprints.md`.
- **Hook wiring** — `playbooks/groom/playbook.yaml` gains `script render-sprints` on every edge of
  the run machine, and `script commit-run` on the single edge into `ready-for-dev`.
- **Commit** — one commit per run, fired on the last edge only, staging `plans/{slug}.md` and
  `sprints.md` together with message `groom({slug}): ready-for-dev`. `BOOPING_NO_COMMIT=1` renders
  without committing, for dry runs.
- **Template** — `sprints.md.j2` moves under `_scripts/`; columns, sort order and the
  do-not-hand-edit header are unchanged, so the rendered file stays byte-comparable.

### Alternatives

- **Thin shell script calling `booping render` on a playbook-local template** — rejected: the
  report would still need the framework to resolve a project context, so the surface the request
  retires stays alive under another name.
- **Keeping the render as a `booping` subcommand** — rejected: that is the status quo, and the
  request is precisely to move one workflow's report out of the framework.

### Trade-offs

- **Vault resolution: derive from `BOOPING_WORKDIR`, or always ask `booping config-get home_dir`**
  — deriving (`../../..` from the run workdir) needs no framework call and works for the default
  layout, but silently produces a wrong path if a run workdir is ever placed elsewhere; asking
  `config-get` is authoritative for the default layout but cannot see a `.booping` `vault_path:`
  override from outside a project. — **Settled:** derive from `BOOPING_WORKDIR`, with
  `BOOPING_VAULT` as an explicit override and `config-get home_dir` as the last fallback. The
  repo-local vault is the open end of this call and is deliberately left unspecified here: a
  `vault_path:` marker can point anywhere in the tree, the script has no assembled context to ask,
  and which of the three resolution paths actually holds has to be probed against a real
  repo-local vault before the chain can be written. Whoever implements it clarifies and
  decomposes it on contact — this design settles the shape, not the steps.
- **Render failure policy: abort the transition, or warn and continue** — aborting keeps the
  snapshot and the run status in lockstep but turns a template typo into a stuck run, since the
  status write has already landed when hooks fire; warning leaves a stale `sprints.md` that the
  next transition refreshes. — **Settled:** warn on stderr and exit 0; a stale snapshot is
  cheaper than a stranded run.
- **Vault commit granularity: one commit per transition, or one commit at the end of the run** —
  per transition keeps every state move independently revertible and matches what
  `booping transition` does today; one commit at the end gives the vault history one meaningful
  diff per groom run but loses the intermediate points. — **Settled by the user:** one commit at
  the end of the run, covering the plan and the snapshot together. The user's words: "Six vault
  commits per groom run, one per transition, and the diff of any single one says nothing. I want
  a run to land as one commit at the end, covering the plan and the snapshot together."

### Risks

- A vault whose `.booping` marker points somewhere unusual resolves to the wrong directory and the
  snapshot is written outside the vault — mitigated by the `BOOPING_VAULT` override and by
  refusing to write when the resolved directory has no `plans/` beside it.
- `uv run` pays a cold resolve on the first hook after any environment change, on a path that
  fires on every transition — mitigated by pinning the two dependencies in the PEP 723 header so
  the cached environment is reused.
- A run that ends anywhere but `ready-for-dev` leaves the vault uncommitted, since the commit
  rides the last edge only — mitigated by the render still firing on every edge, so the working
  tree is always current even when nothing has been committed yet.
- The retired subcommand is documented in `CLAUDE.md` and `documentation/cli.md`; a missed
  reference leaves users calling a command that no longer exists — mitigated by grepping both
  trees for `render-sprints` as a task in the plan.
```

## Already on disk — `plans/20260801-sprints-report-script/plan.md`

```markdown
---
title: Sprints report as a playbook script
type: feature
status: in-spec
sp: null
split_from: null
created: 2026-08-01
planned: null
started: null
completed: null
retro: null
goal: null
summary: ""
commit: null
---
```

## Plan-template catalogue

Five templates are available. Read the chosen one's `# Plan Body` and `# Quality Checklist` from
its path.

| Name | Description | Read from |
| --- | --- | --- |
| `backend` | Backend feature work — APIs, data models, services, migrations, background jobs, protocols. Stack-agnostic. | `docs/plan_templates/backend.md` |
| `claude-skill` | Authoring or refactoring a Claude Code skill — skill bodies, partials, config schema, rendered outputs, skill-level agents. | `docs/plan_templates/claude_skill.md` |
| `cli` | CLI tool work — argument parsing, subcommands, I/O, error handling, exit codes. Standalone scripts or larger CLI suites. | `docs/plan_templates/cli.md` |
| `documentation` | Authoring or restructuring user-facing documentation — multi-page sites, READMEs, cross-linked guides, with optional static-site build pipeline (MkDocs, Jekyll, Docusaurus, etc.). | `docs/plan_templates/documentation.md` |
| `frontend` | Frontend feature work — UI components, state, routing, styling, accessibility. Stack-agnostic (React, Svelte, Leptos, Vue, vanilla). | `docs/plan_templates/frontend.md` |

The project's own `plan_templates/` directory is empty — nothing overrides or adds to the five.

The five template files, on disk in the run tree:

<file path="docs/plan_templates/backend.md">
---
name: backend
description: Backend feature work — APIs, data models, services, migrations, background jobs, protocols. Stack-agnostic.
---

# Plan Body

## Context

Why this work now. Cover three beats:
- **Current state** — what exists today, what's missing or broken.
- **Motivation** — why this change is needed.
- **Scope** — what this plan covers, and explicitly what it does NOT.

## Decisions

Non-obvious design choices. One bullet per decision: **topic**, the decision, and a one-sentence justification.

- **{Topic}**: {decision} — {why}

## Architecture

How this change fits the existing system. Integration points. Reference concrete files and functions. One diagram when the flow is non-trivial.

## Milestones

### M1: {Milestone name} — {SP} SP | pending

**Goal**: one sentence — what changes after this milestone.

**Verify**: exact commands (or observable outcomes) to confirm this milestone is done.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | ... | `path/to/file.ext` | 2 | pending |
| 1.2 | ... | `path/to/other.ext` | 1 | pending |

#### Task 1.1 DoD

- [ ] Specific, verifiable criterion.
- [ ] Test / verification command passes.

#### Task 1.1 Code sketch *(only when the shape is non-obvious)*

```
class NewThing:
    def method(self):
        ...  # interface only — implementers flesh out
```

---

### M2: ...

---

## Implementation Order *(when milestones have dependencies)*

```
M1 ──┐
     ├── M3
M2 ──┘
        ↓
     M4
```

Note which milestones may run in parallel.

## Key Files Reference

Files that span multiple milestones or orient a reader.

| File | Role |
|------|------|
| `path/to/file.ext` | why it matters for this plan |

## Final Verification

- [ ] End-to-end acceptance criterion.
- [ ] Test command — all tests pass.
- [ ] Lint / typecheck command — clean.
- [ ] Any project-specific final checks.

## Testing Strategy *(required when correctness is statistical, subjective, or emergent — LLM pipelines, search/ranking, ML, heuristics, ETL over real data, performance-critical paths)*

Answer three questions:

1. **Business-goal acceptance** — how does a human confirm the feature does its job beyond "tests pass"? Name the concrete criterion.
2. **Fast debug loop** — which dataset + command lets a developer iterate on quality in seconds, not minutes? Include dataset path, command, expected runtime.
3. **User-facing validation** — which preview / dry-run / comparison view lets a non-engineer confirm output quality before ship?

For pure-deterministic work (CRUD, refactor), a single line stating "N/A — deterministic" is sufficient.

## Deployment / config impact *(when new env vars, external services, or infra changes)*

| Env var / config | docker-compose / deploy | terraform / infra | CI workflow |
|------------------|-------------------------|-------------------|-------------|
| `NEW_VAR_NAME` | present | present | present |

## Authorization / data access *(when touching endpoints, querysets, or tenant-scoped data)*

- [ ] Every queryset / query scopes to the authenticated actor (or is documented as public).
- [ ] Authorization is verified across the full API surface in scope, not just per-endpoint.
- [ ] No endpoint exposes data from other users / tenants.

## Out of scope

Explicit list of things intentionally not done in this sprint. At least one bullet; prevents "anything goes" interpretation.

## CLAUDE.md impact

Either name specific sections to update with an owning task, or state "No CLAUDE.md changes required — {one-line justification}".

| Section | Change | Owning task |
|---------|--------|-------------|
| `## {section}` | {what to add/change} | M{n}.{task} |

---

# Quality Checklist

Verify before leaving `in-spec`. Every item must be satisfiable by reading the plan file alone.

## Frontmatter

- [ ] Frontmatter matches [plan frontmatter](${CLAUDE_PLUGIN_ROOT}/docs/template_plan_frontmatter.md) — every required field present and shaped correctly.
- [ ] `sp` equals the sum of per-task SP across milestones.
- [ ] `summary` is set (non-empty, single line, ≤ ~120 chars) for `feature` and `refactoring` plans.

## Content

- [ ] Context explains "why now", not just "what".
- [ ] For features and refactorings: `summary` is phrased as the user/internal-visible outcome, not engineering output.
- [ ] Definition of Done bullets are testable (verifiable by command or inspectable output).
- [ ] Decisions table lists real alternatives — no empty "Alternative considered" rows.
- [ ] Every milestone has a `Verify` command or verifiable outcome.
- [ ] Every task lists exact file paths, not "related files" or "somewhere in X".
- [ ] Every task DoD uses checkboxes, not prose.
- [ ] Code sketches use `...` in method bodies — agents implement from interfaces, not by copying literal code.

## Anti-patterns (must be absent)

- [ ] No "TBD", "TODO", "implement later", "details to follow".
- [ ] No "Similar to Task N" without specifying what's similar.
- [ ] No "handle edge cases", "add error handling", "clean up" as standalone tasks.
- [ ] No "either X or Y" unresolved — pick one, justify in Decisions.
- [ ] No task spanning unrelated concerns (model + API + frontend in one row).
- [ ] No milestone that requires reading more than the plan file to execute.

## External references validated

- [ ] Package / image / crate versions confirmed against official registries.
- [ ] Third-party API endpoints and flags validated against current docs.
- [ ] No assumed external reference without a verification note.

## Out of scope + coverage

- [ ] Out-of-scope section present; at least one excluded concern named.
- [ ] Every requirement in the user's request maps to at least one task, or is explicitly deferred in Out of scope with justification.

## Consistency

- [ ] Function / class names used in one task match their definition in another.
- [ ] File paths are consistent across tasks.
- [ ] Data structures (schemas, models) match between producer and consumer tasks.

## Backend-specific

- [ ] New data persistence (migration, schema change, new index) is called out explicitly and paired with a rollback note.
- [ ] Authorization / data-access checks section filled in if endpoints are touched, or marked N/A with justification.
- [ ] Deployment / config impact section filled in if env vars / infra change, or marked N/A.
- [ ] Testing Strategy answered if the work is quality-dependent, or marked N/A for pure deterministic work.

## CLAUDE.md impact

- [ ] Either names the specific sections/bullets to update (with an owning task) or explicitly states "No CLAUDE.md changes required" with justification.
- [ ] If the sprint introduces a registry / builder / harness, changes a public data shape, or relocates a "how to add X" procedure, there is a concrete task for the CLAUDE.md update — not deferred to retro.
</file>
<file path="docs/plan_templates/claude_skill.md">
---
name: claude-skill
description: Authoring or refactoring a Claude Code skill — skill bodies, partials, config schema, rendered outputs, skill-level agents.
---

# Plan Body

## Context

What skill (or skill family) this plan affects. Current behavior, the gap or wrinkle, what changes after.

## Decisions

- **{Topic}**: {decision} — {why}

Typical topics: what moves to config vs stays in skill body, which partials to extract, what the skill's phases / craft become, what lazy-loads vs embeds.

## Architecture

How the skill interacts with other skills via shared config (statuses, agents, task types). Diagram the skill's load-time inputs (config, partials, `!`commands``, lazy docs) if non-trivial.

## Milestones

### M1: {Milestone name} — {SP} SP | pending

**Goal**: one sentence — the observable change in the rendered skill or shared config.

**Verify**: render and sanity check (e.g. `bin/booping render src/templates/skills/<name>.md.j2` and review output).

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | ... | `src/templates/skills/<name>.md.j2`, `src/config.yaml` | 2 | pending |

#### Task 1.1 DoD

- [ ] Rendered skill diff matches intended shape.
- [ ] No hardcoded values that duplicate config.
- [ ] Lazy-load links resolve.

---

## Final Verification

- [ ] `just build` renders cleanly (for skill/agent thin-shell changes via `src/files/`) and `bin/booping render src/templates/skills/<name>.md.j2` produces clean output (for skill/agent body changes).
- [ ] Rendered skill body reviewed (no stale state names, no prose that duplicates rendered tables, no `{{placeholder}}` leaks).
- [ ] Project-local extension points (`_booping/skill_<name>.md`) still inline correctly.

## Out of scope

Explicit exclusions — e.g. "groom skill only; develop/retro/learn unchanged", "no plan-template changes".

## CLAUDE.md impact

Name sections to update, or state "No CLAUDE.md changes required — {justification}".

---

# Quality Checklist

## Frontmatter

- [ ] Frontmatter matches [plan frontmatter](${CLAUDE_PLUGIN_ROOT}/docs/template_plan_frontmatter.md).
- [ ] `sp` equals the sum of per-task SP across milestones.

## Content

- [ ] Context names the behavior change visible in rendered skills, not "refactor internals".
- [ ] DoD bullets are verifiable by reading the rendered output or a diff.
- [ ] Every task lists exact template / partial / config paths.
- [ ] Every task DoD uses checkboxes, not prose.
- [ ] Every milestone has a `Verify` step that includes a rebuild.
- [ ] Each milestone executable from a fresh session with only the plan as context.

## Skill-design hygiene

- [ ] Structured facts (statuses, transitions, task types, agents) go in `src/config.yaml`, not prose.
- [ ] Single-consumer content lives in the skill body, not config.
- [ ] Long-form reference content (> a paragraph) is a lazy-load doc under `docs/`, not inlined.
- [ ] `!`commands`` are used for dynamic content (project context, lessons, extra instructions), not baked facts.
- [ ] No restated flow / state descriptions — the rendered transitions table is the contract.
- [ ] No stack-specific details in the skill body (Django, React, etc.) — project specifics belong in `~/Claude/{project}/_booping/`.

## Anti-patterns (must be absent)

- [ ] No "TBD", "TODO", "implement later", "details to follow".
- [ ] No task spanning unrelated concerns (config schema + renderer + multiple skills in one row).
- [ ] No prose section that duplicates a rendered table or partial.
- [ ] No "Phase 1..N" numbered workflow when the transitions table already carries the flow.
- [ ] No stale state names (e.g. references to removed/orphaned statuses).

## External references validated

- [ ] Template paths reference files that exist.
- [ ] Lazy-load doc links resolve from the rendered skill's location.

## CLAUDE.md impact

- [ ] Any change to config schema, partial API, or rendered-artifact paths is reflected in `CLAUDE.md` via an owning task.
</file>
<file path="docs/plan_templates/cli.md">
---
name: cli
description: CLI tool work — argument parsing, subcommands, I/O, error handling, exit codes. Standalone scripts or larger CLI suites.
---

# Plan Body

## Context

What CLI (or subcommand) this plan affects. Current behavior, gap, change after.

## Decisions

- **{Topic}**: {decision} — {why}

Typical topics: argument shape, subcommand layout, I/O format (JSON vs text), exit-code contract, config-file vs flags, dependency footprint.

## Architecture

How the CLI fits the surrounding toolchain. Input sources, output sinks, side effects. If invoked by other tools or skills (e.g. inlined via `!`command``), name the callers and their expected output shape.

## Milestones

### M1: {Milestone name} — {SP} SP | pending

**Goal**: one sentence — the observable change in CLI behavior.

**Verify**: exact invocation + expected output (e.g. `./bin/mytool --flag arg 2>&1 | diff - tests/fixtures/expected.txt`).

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | ... | `bin/mytool`, `tests/fixtures/*.txt` | 2 | pending |

#### Task 1.1 DoD

- [ ] Happy-path invocation produces expected output.
- [ ] `--help` reflects the new surface.
- [ ] Exit code matches the contract (0 on success, ≠0 on defined failure modes).

---

## I/O contract

Document the CLI's input/output surface explicitly.

- **Arguments / flags**: `tool [--flag VALUE] <positional>` — what each controls.
- **stdin**: what's read (format, when optional).
- **stdout**: format + shape (plain text? JSON? markdown for skill inlining?).
- **stderr**: diagnostics, warnings, errors.
- **Exit codes**: `0 = success`, `1 = user error`, `2 = internal error`, etc.

## Final Verification

- [ ] Help text updated and accurate.
- [ ] Happy-path + at least one failure-path invocation verified.
- [ ] Exit codes match the documented contract.
- [ ] If inlined via `!`command``: the consumer skill renders cleanly.

## Out of scope

Explicit exclusions — e.g. "no new config-file format", "sync-only; async variant later".

## CLAUDE.md impact

Name sections to update (new CLI in the `CLI` section, new inlining point in a skill), or state "No CLAUDE.md changes required — {justification}".

---

# Quality Checklist

## Frontmatter

- [ ] Frontmatter matches [plan frontmatter](${CLAUDE_PLUGIN_ROOT}/docs/template_plan_frontmatter.md).
- [ ] `sp` equals the sum of per-task SP across milestones.

## Content

- [ ] Context names the user-visible CLI behavior change.
- [ ] DoD bullets are verifiable by invocation + output diff.
- [ ] Every task lists exact files.
- [ ] Every task DoD uses checkboxes, not prose.
- [ ] Every milestone has a `Verify` invocation.
- [ ] Each milestone executable from a fresh session with only the plan as context.

## I/O contract

- [ ] Argument / flag shape is enumerated, not "add some flags".
- [ ] Output format for stdout is specified (plain / JSON / markdown).
- [ ] Exit codes are defined for every failure mode the CLI distinguishes.

## Anti-patterns (must be absent)

- [ ] No "TBD", "TODO", "implement later", "handle error cases later".
- [ ] No task spanning unrelated concerns (parser + subcommand + I/O format in one row).
- [ ] No "add a command for X" without specifying argument shape + output.
- [ ] No silent failures — every error path has an exit code and stderr message.
- [ ] No CLI that prints to stdout and stderr the same content (makes piping ambiguous).

## External references validated

- [ ] Dependency versions (PyPI, cargo, npm) confirmed against current registry.
- [ ] Any OS command the CLI shells out to is verified to exist on supported platforms.

## CLAUDE.md impact

- [ ] `## CLI` section (or equivalent) updated with the new tool / subcommand, or explicitly states "No CLAUDE.md changes required".
</file>
<file path="docs/plan_templates/documentation.md">
---
name: documentation
description: Authoring or restructuring user-facing documentation — multi-page sites, READMEs, cross-linked guides, with optional static-site build pipeline (MkDocs, Jekyll, Docusaurus, etc.).
---

# Plan Body

## Context

Who the docs are for (end users vs contributors), what they cover, what gap motivates the work. Note any existing documentation that overlaps and how the new content relates to it (replaces / supplements / cross-links).

## Decisions

- **{Topic}**: {decision} — {why}

Typical topics: site generator (MkDocs / Jekyll / Docusaurus / plain markdown), theme, where source files live, how the published site is built and hosted (GitHub Pages branch, Netlify, etc.), per-page vs single-page split, what stays in README vs moves to the docs site, lazy-loading from skills if applicable.

## Information architecture

Sketch the page tree with a one-line purpose per page. Call out cross-links between pages and back-links from existing surfaces (README, skill bodies, lazy-load `docs/` fragments).

```
documentation/
├── index.md          # purpose
├── ...
```

## Milestones

Order pages so each milestone produces something reviewable in isolation. A typical shape:

1. **Scaffold** — site generator config, directory layout, build/deploy CI, local-serve target. No content yet.
2. **Foundation pages** — landing/index, walkthrough, primary entry-point pages.
3. **Reference pages** — one milestone per logical group (per-skill, per-command, per-feature).
4. **Cross-references and stale-reference cleanup** — README link, skill lazy-load wiring, project-conventions doc updates.
5. **Reshape** — pause for user IA review against the rendered site; apply prose/structure changes uncovered by reading the built output.

### M1: {Milestone name} — {SP} SP | pending

**Goal**: one sentence — what page(s) or pipeline component lands.

**Verify**: build/serve the site locally and load the affected pages in a browser; check cross-links resolve; on CI changes, push a branch and confirm the workflow runs green.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | ... | `documentation/<page>.md`, `mkdocs.yml` | 2 | pending |

#### Task 1.1 DoD

- [ ] Page renders in the local build with no broken links.
- [ ] Cross-links to/from sibling pages resolve.
- [ ] Code blocks lint cleanly (correct language tags, runnable where applicable).
- [ ] No prose that duplicates content already covered by another page — link instead.

---

## Final Verification

- [ ] Local build succeeds with no warnings (`mkdocs build --strict` or equivalent).
- [ ] CI workflow runs green on the sprint branch and the published preview (if any) renders.
- [ ] Every internal cross-link resolves; every external link (package, API, doc) verified against current source.
- [ ] All references invalidated by this work are updated in the same sprint (README links, lazy-load paths, skill bodies, `CLAUDE.md` mentions). No "follow-up sweep" deferred.

## Out of scope

Explicit exclusions — e.g. "no skill-body rewrites", "no new commands documented", "no translation".

## CLAUDE.md impact

Name sections to update (e.g. add `documentation/` to the layout section, distinguish it from `docs/`), or state "No CLAUDE.md changes required — {justification}".

---

# Quality Checklist

## Frontmatter

- [ ] Frontmatter matches [plan frontmatter](${CLAUDE_PLUGIN_ROOT}/docs/template_plan_frontmatter.md).
- [ ] `sp` equals the sum of per-task SP across milestones.

## Content

- [ ] Context names the audience (end users vs contributors) and the gap being closed.
- [ ] Information architecture sketch is present and shows every page with a one-line purpose.
- [ ] Each page is a milestone task or grouped with siblings under one milestone — no orphan pages.
- [ ] DoD bullets are verifiable by loading the rendered page or running the build.
- [ ] Every task lists exact file paths.
- [ ] Every milestone has a `Verify` step that includes a build or local-serve check.
- [ ] Each milestone executable from a fresh session with only the plan as context.

## Documentation hygiene

- [ ] No prose duplicated across pages — extracted to a single source and linked.
- [ ] Per-page `What it does` / purpose line near the top so the page is skimmable.
- [ ] Code blocks tagged with the correct language; commands runnable as written.
- [ ] No screenshots of text where copy-able text would do.
- [ ] No "coming soon" placeholders in pages that ship.

## Cross-references

- [ ] Every existing surface that should link to the new docs (README, skill bodies, lazy-load fragments) is updated in the same sprint, not deferred.
- [ ] Every existing surface invalidated by the new docs (now-redundant README sections, removed lazy-load files) is cleaned up in the same sprint.
- [ ] `CLAUDE.md` updated to describe the new `documentation/` layout and its relationship to other doc surfaces.

## Reshape milestone

- [ ] A reshape milestone is included if rendered output is likely to expose IA issues only post-build (typical for multi-page sites and cross-linked content).
- [ ] The reshape milestone has explicit DoD: user reads the rendered site, files prose/structure feedback as a list, feedback is applied before the plan transitions out of `in-progress`.

## Anti-patterns (must be absent)

- [ ] No "TBD", "TODO", "details to follow" in pages that ship.
- [ ] No mixed audiences in one page (end-user content and contributor content interleaved).
- [ ] No giant single-page dump where multi-page split was the call — and vice versa.
- [ ] No content that restates the schema/code source of truth in prose where a link would do.

## External references validated

- [ ] Every package version, theme name, plugin, image tag, CLI flag, and config option named in the docs is checked against current upstream docs.
- [ ] All cross-links resolve from the rendered site (not just from raw markdown).

## CLAUDE.md impact

- [ ] Any change to top-level layout (new `documentation/` directory, new build target, new CI workflow) is reflected in `CLAUDE.md` via an owning task.
</file>
<file path="docs/plan_templates/frontend.md">
---
name: frontend
description: Frontend feature work — UI components, state, routing, styling, accessibility. Stack-agnostic (React, Svelte, Leptos, Vue, vanilla).
---

# Plan Body

## Context

Why this work now. Current UI state, user-visible gap or bug, scope of this plan.

## Decisions

Non-obvious design choices: component decomposition, state location, styling approach, routing shape.

- **{Topic}**: {decision} — {why}

## Architecture

How the new UI fits the component tree, state flow, and data-loading boundaries. Integration points with backend APIs. Reference concrete files.

## Milestones

### M1: {Milestone name} — {SP} SP | pending

**Goal**: one sentence — what changes in the UI after this milestone.

**Verify**: exact commands (typecheck, tests, visual check) or observable outcomes.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | ... | `src/components/Foo.tsx` | 2 | pending |

#### Task 1.1 DoD

- [ ] Component renders with all documented props.
- [ ] States: loading / empty / error / success covered.
- [ ] Typecheck + test commands pass.

---

## Final Verification

- [ ] End-to-end user flow reproduces expected behavior in the browser / device.
- [ ] Typecheck clean.
- [ ] Unit / component tests pass.
- [ ] Visual regression / accessibility spot check if applicable.

## Accessibility & interaction *(when adding interactive UI)*

- [ ] Keyboard navigation paths enumerated.
- [ ] Screen-reader labels / roles specified where they differ from defaults.
- [ ] Focus management for dialogs / transitions called out.
- [ ] Reduced-motion / high-contrast considerations if relevant.

## Responsive & cross-browser *(when visual layout changes)*

- [ ] Breakpoint behavior specified.
- [ ] Browser / device matrix the change is verified against.

## Out of scope

Explicit exclusions — e.g. "no design-system-wide token changes", "desktop only for now".

## CLAUDE.md impact

Name sections to update, or state "No CLAUDE.md changes required — {justification}".

---

# Quality Checklist

## Frontmatter

- [ ] Frontmatter matches [plan frontmatter](${CLAUDE_PLUGIN_ROOT}/docs/template_plan_frontmatter.md).
- [ ] `sp` equals the sum of per-task SP across milestones.

## Content

- [ ] Context names the user-visible outcome, not "implement X component".
- [ ] DoD bullets are observable in the browser or a test runner.
- [ ] Every task lists exact files.
- [ ] Every task DoD uses checkboxes, not prose.
- [ ] Every milestone has a `Verify` step.
- [ ] Each milestone executable from a fresh session with only the plan as context.

## Anti-patterns (must be absent)

- [ ] No "TBD", "TODO", "implement later", "styling TBD", "handle states later".
- [ ] No task spanning unrelated concerns (component + API + state store in one row).
- [ ] No task that adds a component without also specifying its props, states, and where it mounts.
- [ ] No "match the design" without linking the source of truth (Figma, mockup, existing component).

## External references validated

- [ ] Package / library versions confirmed against registry.
- [ ] API endpoints the UI consumes are verified to exist (or the backend task creating them is a dependency).

## Frontend-specific

- [ ] Accessibility section filled in for interactive UI, or marked N/A.
- [ ] Responsive / cross-browser section filled in for layout changes, or marked N/A.
- [ ] State placement decision (local / shared / URL) is explicit for any new stateful behavior.

## CLAUDE.md impact

- [ ] Names sections to update with an owning task, or explicitly states "No CLAUDE.md changes required".
</file>

## Plan frontmatter shape

```yaml
title: {Descriptive Title}        # string
type: feature | bug | refactoring
status: in-spec                   # active groom runs write directly here
sp: {total}                       # integer — the sprint total
split_from: null                  # string path; sibling stubs only
created: YYYY-MM-DD               # date this file was first written
planned: null                     # set on in-spec → awaiting-plan-review
started: null                     # set on ready-for-dev → in-progress
completed: null                   # set on terminal transition
retro: null                       # path to retrospective file
goal: null                        # success | partial | fail
summary: ""                       # one-line plan intent (≤ ~120 chars)
commit: null                      # repo HEAD when the draft was finalised
```

## Sizing

Story-point scale:

| SP | Meaning |
| --- | --- |
| 1 | Simple text/config change, no risk |
| 2 | Simple task, predictable, no risk |
| 3 | Medium task, minor risks but predictable overall |
| 4 | Complex task, medium risk, may need small research but clear enough |
| 5 | Research task — developer needs to clarify and decompose further before proceeding |

- `redecompose_threshold: 5`
- `max_milestones_per_agent: 1` — a development run bundles one milestone into one agent briefing,
  so a milestone is the largest unit a single agent ever holds.

## Project config — cross-review

```yaml
core:
  cross_review_agent: codex
```

## Cross-review return — supplied inline

The harness spawns no sub-agent in this run. The reviewer named above ran over the finished draft
and returned exactly the following, verbatim; treat these lines as the return of the cross-review
pass:

```
- CRITICAL: the commit must not ride on the hook — a render hook that also writes git history
  couples two side effects with different failure modes, and staging the whole run on the single
  edge into `ready-for-dev` means an abandoned run commits nothing at all; commit per transition
  as `booping transition` already does, and drop `commit-run` — Architecture
- NOTE: the I/O contract lists the three environment variables but not their precedence order;
  stating it inline saves a reader a trip through Architecture — I/O contract
```
