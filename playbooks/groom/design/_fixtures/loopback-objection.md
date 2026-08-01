Playbook `groom`, target step `design`, loopback re-entry — a confirmed design already exists for
this run and the user has objected to exactly one call in it.

Run-time context:

- project: `claude-booping` (the booping plugin repo)
- run slug: `20260801-09-15_sprints-report-script`
- run workdir: `_runs/groom/20260801-09-15_sprints-report-script/`
- plan file: `plans/20260801-09-15_sprints-report-script.md` — identity frontmatter only, not yet
  drafted

The upstream artifacts, the design as it stands on disk, and the user's objection follow.

## Confirmed framing — `_runs/groom/20260801-09-15_sprints-report-script/intake.md`

```markdown
---
reviewed_at: 20260801 09:32
---
# Intake — sprints report as a playbook script

## Request

> sprints.md should stop being a booping built-in. The groom playbook should render it from its
> own `_scripts/` hook on the transition edges, and booping's `render-sprints` — the subcommand
> and the automatic post hook — should go away.

## Restated problem

Today the vault snapshot is a framework concern: `render-sprints` is a `booping` subcommand and
an entry in `plan.hooks.post`, so every `booping transition` re-renders `sprints.md` whatever
workflow the move belongs to. The report describes one workflow's shape, not the framework's, and
the direction is that playbook-specific behaviour lives in the playbook. The request is to move
the render into a groom-playbook-local script fired as a `script` hook on the machine's edges,
then retire the core surface it replaces.

## Task type

`feature` — a new capability (a playbook-owned reporting script with its own invocation contract)
plus the retirement of the built-in it replaces. Not a bug: nothing diverges from expected
behaviour. Not a refactoring: the invocation surface users depend on changes, not just its
structure.

## Scope boundaries

**In scope**

- the playbook-local script, its hook wiring on the machine's edges, and how it resolves the vault
- the sprints template's new home under the playbook
- removing `render-sprints` from `plan.hooks.post` and from the CLI, and every in-repo caller of
  it (`/chat`'s orient refresh included)

**Out of scope**

- the snapshot's column set and sort order — the rendered table stays byte-comparable
- back-filling or re-rendering historical vaults
- moving any other post hook (`vault-commit` stays where it is)

## Scope challenge

- [x] Should `booping render-sprints` be removed outright, or kept as a deprecated alias for a
      release? — **Answered:** removed outright; every caller is in this repo and moves in the
      same change.
- [x] Does the script render the whole vault's plans, or only the plans this run touched? —
      **Answered:** the whole vault. The file is a snapshot, exactly as today.
- [x] Any dependency or config surface this must not pull in? — **Answered:** nothing added to
      `booping-python`, and no new config key beyond what the retirement removes.
```

## Blast radius — `_runs/groom/20260801-09-15_sprints-report-script/research-codebase.md`

```markdown
# Blast radius — sprints report as a playbook script

## Touched surfaces

| Surface | Where | Why it moves | Risk |
| --- | --- | --- | --- |
| `render-sprints` hook | `booping-python/src/booping/hooks.py` | retired once the playbook owns the render | medium — every `transition` edge fires it today |
| `render-sprints` subcommand | `booping-python/src/booping/commands/render_sprints.py` | removed with the hook; `/chat`'s orient refresh is its only other caller | medium — a caller outside this repo breaks silently |
| sprints template | `src/templates/sprints.md.j2` | moves under the playbook's `_scripts/` | low — self-contained, reads `context.plans` only |
| post-hook list | `src/config.yaml` (`plan.hooks.post`) | drops `render-sprints`, leaving `vault-commit` | medium — a project config that pins the list keeps the dead name |
| CLI docs | `CLAUDE.md`, `documentation/cli.md` | the retired subcommand is documented in both | low |

## Prior art

- `_scripts/` hooks already run with `BOOPING_WORKDIR`, `BOOPING_ARTIFACT` and `BOOPING_INSTANCE`
  in the environment and cwd set to the run workdir; a non-zero exit aborts the transition. This
  is the working precedent for a playbook-local side effect.
- `bin/booping-create-project` is the reference shape for a standalone uv inline script — PEP 723
  header, no place inside `booping-python`.
- `bin/booping config-get {dotted.key}` is the supported way a shell-side caller reads a resolved
  config value; `bin/booping-create-project` already uses it for `home_dir`.

## Conventions in play

- `skills/` and `agents/` are build artefacts — edit `src/files/**.j2`, then `just build`.
- Structured data lives in `src/config.yaml`; a skill body never restates it as prose.
- Playbook-specific behaviour lives in the playbook; booping core stays a pure playbook framework.
- Every change under `booping-python/` clears `just lint`, `just typecheck`, `just test`; a
  removed subcommand takes its tests with it.

## Unknowns for design

- Whether a script deriving the vault from `BOOPING_WORKDIR` holds for a repo-local vault. The
  default workdir is `{vault}/_runs/groom/{slug}/`, so the vault is `../../..` — but a repo-local
  vault named by the `.booping` `vault_path:` marker can sit anywhere in the tree, and the script
  has no assembled context to ask.
```

## External practice — `_runs/groom/20260801-09-15_sprints-report-script/research-web.md`

```markdown
# research-web — 20260801-09-15_sprints-report-script

## Verdict

Researched — the render leaves the framework's Python process and becomes a standalone program
fired by a hook; how such a script gets its dependencies, its inputs and its failure policy has no
precedent in this repository.

## Approaches

### Standalone uv inline script under the playbook's `_scripts/`

A PEP 723 header declares the dependencies; `uv run` resolves them per invocation against a cached
environment.

- Fits: matches `bin/booping-create-project`, the shape this repo already ships; the playbook dir
  stays self-contained and the script travels with the playbook to any discovery root.
- Costs: the script re-implements plan loading that `booping-python` already owns, and a cold
  resolve is paid on the hook path.
- Retire cost: low — deleting one file removes the behaviour.

### Thin shell script that shells back into the framework CLI

A few lines calling a general-purpose `booping render` over a template that lives under the
playbook dir.

- Fits: no dependency management at all; plan loading, the config merge and vault resolution stay
  in the framework where they are already tested.
- Costs: the retirement is only partial — `render-sprints` goes, but the report still depends on
  the framework resolving a project context for the playbook's own template.

### Keep the render inside `booping-python` as a subcommand

- Fits: nothing changes mechanically; the code stays typed and tested with the rest of the package.
- Costs: the status quo under another name — one workflow's report stays a framework concern,
  which is exactly what the request retires.

## Pitfalls

- A hook script that resolves paths from its own location or from cwd breaks the moment the run
  workdir moves. Hook contracts pass the workdir in the environment; reading `BOOPING_WORKDIR`
  rather than guessing is the difference between a portable script and one pinned to one layout.
- A non-zero exit from a hook aborts the transition *after* the status write has already landed,
  leaving the artifact ahead of its side effects. A render failure — missing template, unparsable
  plan frontmatter — must not be able to strand a state move.
- Per-invocation dependency resolution is the standing cost of standalone scripts: with a cold
  cache the first run after any environment change pays seconds, on a path that fires on every
  transition.

## Sources

| Source | Backs | Checked |
| --- | --- | --- |
| https://peps.python.org/pep-0723/ | inline metadata for a standalone dependency-declaring script | 20260801 |
| https://docs.astral.sh/uv/guides/scripts/ | `uv run` resolution and caching per script invocation | 20260801 |
| https://jinja.palletsprojects.com/en/stable/api/ | `Environment` + `FileSystemLoader` for rendering a template from a directory outside the package | 20260801 |
```

## The design on disk — `_runs/groom/20260801-09-15_sprints-report-script/design.md`

```markdown
---
reviewed_at: 20260801 10:40
---
# design — 20260801-09-15_sprints-report-script

## Approach

A standalone uv inline script at `playbooks/groom/_scripts/render-sprints`, fired as a
`script render-sprints` hook on the machine's edges. It reads `BOOPING_WORKDIR`, resolves the
vault from it, loads every `plans/*.md` frontmatter, and renders the template — moved from
`src/templates/sprints.md.j2` to `playbooks/groom/_scripts/sprints.md.j2` — to `{vault}/sprints.md`.
Chosen over shelling back into the framework CLI because the retirement is the point: with the
render owned by the playbook, `render-sprints` leaves `booping-python/src/booping/hooks.py`, its
subcommand module goes with it, and `plan.hooks.post` in `src/config.yaml` drops to `vault-commit`
alone. The script's only framework dependency is `bin/booping config-get`, and only on the
fallback path.

## Surface changes

- **CLI** — `booping render-sprints` removed, together with
  `booping-python/src/booping/commands/render_sprints.py` and its tests. `/chat`'s orient refresh
  drops the call and reads `sprints.md` as it stands.
- **Config** — `plan.hooks.post` in `src/config.yaml` becomes `[vault-commit]`; the
  `render-sprints` hook name is removed from `hooks.py`, so a project config still pinning it
  fails loudly at load rather than silently doing nothing.
- **Script** — `playbooks/groom/_scripts/render-sprints`, PEP 723 header, deps `jinja2` +
  `pyyaml`. Reads `BOOPING_WORKDIR` (required — absent is a usage error), `BOOPING_VAULT`
  (optional explicit override), and falls back to `booping config-get home_dir` only when the
  workdir ancestry does not resolve. Writes `{vault}/sprints.md`.
- **Commit** — the same script stages `plans/{slug}.md` and `sprints.md` and commits them in the
  vault repo on every edge it runs on, message `groom({slug}): {to-status}`. `BOOPING_NO_COMMIT=1`
  renders without committing, for dry runs.
- **Template** — `sprints.md.j2` moves under `_scripts/`; columns, sort order and the
  do-not-hand-edit header are unchanged, so the rendered file stays byte-comparable.

## Alternatives

- **Thin shell script calling `booping render` on a playbook-local template** — rejected: the
  report would still need the framework to resolve a project context, so the surface the request
  retires stays alive under another name.
- **Keeping the render as a `booping` subcommand** — rejected: that is the status quo, and the
  request is precisely to move one workflow's report out of the framework.

## Trade-offs

- **Vault resolution: derive from `BOOPING_WORKDIR`, or always ask `booping config-get home_dir`**
  — deriving (`../../..` from the run workdir) needs no framework call and works for a repo-local
  vault, but silently produces a wrong path if a run workdir is ever placed elsewhere; asking
  `config-get` is authoritative for the default layout but cannot see a `.booping`
  `vault_path:` override from outside a project. — **Settled:** derive from `BOOPING_WORKDIR`,
  with `BOOPING_VAULT` as an explicit override and `config-get home_dir` as the last fallback.
- **Render failure policy: abort the transition, or warn and continue** — aborting keeps the
  snapshot and the run status in lockstep but turns a template typo into a stuck run, since the
  status write has already landed when hooks fire; warning leaves a stale `sprints.md` that the
  next transition refreshes. — **Settled:** warn on stderr and exit 0; a stale snapshot is
  cheaper than a stranded run.
- **Vault commit granularity: one commit per transition, or one commit at the end of the run** —
  per transition keeps every state move independently revertible and matches what
  `booping transition` does today; one commit at the end gives the vault history one meaningful
  diff per groom run but loses the intermediate points. — **Settled:** one commit per transition,
  unchanged from the current behaviour.

## Risks

- A vault whose `.booping` marker points somewhere unusual resolves to the wrong directory and the
  snapshot is written outside the vault — mitigated by the `BOOPING_VAULT` override and by
  refusing to write when the resolved directory has no `plans/` beside it.
- `uv run` pays a cold resolve on the first hook after any environment change, on a path that
  fires on every transition — mitigated by pinning the two dependencies in the PEP 723 header so
  the cached environment is reused.
- The retired subcommand is documented in `CLAUDE.md` and `documentation/cli.md`; a missed
  reference leaves users calling a command that no longer exists — mitigated by grepping both
  trees for `render-sprints` as a task in the plan.
```

## The user's objection — this pass's input

> Six vault commits per groom run, one per transition, and the diff of any single one says
> nothing. I want a run to land as one commit at the end, covering the plan and the snapshot
> together. Rewrite that call; everything else in the design stands as confirmed.
