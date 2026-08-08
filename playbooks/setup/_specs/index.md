---
status: building-steps
reviewed_at: 20260804 08:43
playbook_yaml_reviewed_at: 20260804 08:47
---
# setup — Decomposition

Take a repo from any starting state to a working booping project in one driven conversation.
There is no discovery step: the `/playbook` skill's context report already tells the run whether
booping itself is initialized and whether this project is, and the two steps read those flags.
**setup-booping** settles the machine level — the booping config and its `home_dir` — and
**setup-project** settles the project level: scaffolding the vault tree, marker and symlink when
the project is new, or, when everything is already in place, reporting that and offering the
change routes (move the vault, rename the project, merge it into another). Every decision is
taken inside the step with `AskUserQuestion`; there are no review gates. The run is ephemeral —
no run directory, no persisted state, nothing to resume — and a cancelled run leaves the machine
and the repo untouched.

## Graph

```yaml
graph:
  setup-booping: []
  setup-project: [setup-booping]
```

## Steps

| Step          | Summary                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | Inputs                                                                                                                                                                                                                                                                                             | Artifact                                                                                                                                | Gate | Delegation | Model           | Spec                                 |
| ------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- | ---- | ---------- | --------------- | ------------------------------------ |
| setup-booping | machine level: when booping is not yet initialized, ask the preferred home dir (default `~/Claude/`) and create the config; when it is, report the resolved home dir and change nothing                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | the booping-initialized flag from the run's context report; the machine's configured home dir when there is one; the user's preferred home dir                                                                                                                                                     | the machine booping config, created only when absent                                                                                    | none | inline     | sonnet-5:medium | [spec](steps/setup-booping/index.md) |
| setup-project | project level: when the project is not initialized, ask vault location (in the repo or under the home dir), project name from repo-name candidates, and marker visibility — add to git, hide in `.gitignore`, or hide in the untracked exclude file (skipped when the vault itself lives in the repo) — then scaffold the vault tree, write the marker, symlink a repo-local vault into the home dir and seed the sprints snapshot; when the project is already initialized, report the state and offer the change routes: move the vault, rename the project (vault directory, marker project name and home-dir symlink move with it), merge it into another project | the project-initialized flag from the run's context report; the resolved home dir; the repo directory name as name candidates; whether the repo is under git; the project names already under the home dir; the user's location, name and marker-visibility answers, or the change route they pick | the scaffolded vault tree, the repo marker, a home-dir symlink for a repo-local vault, an ignore entry when asked, the sprints snapshot | none | inline     | opus-5:high     | [spec](steps/setup-project/index.md) |

## Assumptions and constraints

- **`booping scaffold` has shipped** — `booping scaffold <dotted-config-path> <dest> [--force]
  [--set KEY=VALUE]`: the dotted path points into the merged config, where a string node is
  Jinja-rendered file content and a mapping is a directory; `--set` values are exposed as **bare**
  template variables (`{{ name }}`, not `{{ config.name }}` — a deliberate divergence from
  `render` / `render-playbook`); a non-empty destination without `--force` exits 1 (0 success,
  1 user error, 2 OSError). `setup-project` scaffolds the vault through it.
- **The `vault.scaffold` core tree has landed** — `booping scaffold vault.scaffold <vault-dir>`
  creates `plans/`, `retrospectives/`, `_lessons/`, `_booping/`, `notes/` and a `.gitignore`.
  It takes no `--set` variables. `booping-create-project` still carries its own hardcoded
  `mkdir -p` and does not route through the tree.
- **Every prerequisite has landed** — the last one, the `booping_initialized` /
  `project_initialized` flags, now opens the yaml block of `_partials/_project_context.j2`
  on both branches, carried by `Context.booping_initialized` (a global config tier exists)
  and by whether a `.booping` marker resolved.
- Scaffold trees declare directories and text files only — **no symlinks** — so the repo-local
  vault → home-dir symlink is step-owned work that `setup-project` performs itself.
- **Bootstrap constraint on the manifest** — the run starts on a machine that may have no
  booping config and no attached project, so the playbook MUST declare `requires_project: false`.
  `jinja: true` is fine: the `_NO_CONTEXT` STOP in `commands/render_playbook.py` fires only when
  the assembled `Context` is `None`, and the CLI always assembles one (with `project: None`
  outside a project). Bodies must simply not dereference `context.project`. Verified this run:
  `booping render-playbook setup` renders clean outside any project with an empty global config.
- **Step bodies follow the core pattern** — `prompt.md` carries the frontmatter and a single
  `{% include "<model>.md" %}`; the body lives in the model-named sibling (`setup-booping/sonnet-5.md`,
  `setup-project/opus-5.md`), matching `groom` and `playbook-authoring`.
- Stack detection and `_booping/` extension seeding are **out of scope** — `setup-project` seeds
  the project directory structure only, nothing stack-derived.
- There is no attach route: a repo is never wired to a pre-existing vault the run did not create.
- The change routes are **offered, not scripted**: the step presents move / rename / merge and
  acts on the user's call plus the run's context. No collision rules, no teardown procedure.
