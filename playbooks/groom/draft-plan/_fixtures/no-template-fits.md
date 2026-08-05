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

Two templates are available. Read the chosen one's `# Plan Body` and `# Quality Checklist` from
its path.

| Name | Description | Read from |
| --- | --- | --- |
| `documentation` | Authoring or restructuring user-facing documentation — multi-page sites, READMEs, cross-linked guides, with optional static-site build pipeline (MkDocs, Jekyll, Docusaurus, etc.). | `docs/plan_templates/documentation.md` |
| `frontend` | Frontend feature work — UI components, state, routing, styling, accessibility. Stack-agnostic (React, Svelte, Leptos, Vue, vanilla). | `docs/plan_templates/frontend.md` |

The project's own `plan_templates/` directory exists and is empty — it overrides nothing and adds
nothing to the two. A template authored there is discovered alongside the core ones; each carries
frontmatter `name` and `description` and the two top-level sections `# Plan Body` and
`# Quality Checklist`.

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
- CRITICAL: the fail-open path on vault resolution is untested — no DoD item or Final Verification
  line asserts what the script does when the workdir ancestry does not resolve and the
  `config-get home_dir` fallback is taken — Milestones
- RISK: a project outside this run's reach that pins `plan.hooks.post` in its own config keeps
  `render-sprints` in the list and fails at load after the hook name is removed; nothing in the
  plan warns such a caller — Out of scope
- NOTE: the I/O contract lists the three environment variables but not their precedence order;
  stating it inline saves a reader a trip through Architecture — I/O contract
```
