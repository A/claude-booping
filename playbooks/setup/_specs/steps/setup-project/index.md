---
status: spec-ing
---

# setup-project

[← index](../../index.md)

## Contract

- **Needs** —
  - whether this project is initialized — the project-initialized flag from the run's context
    report (an assumed prerequisite: it does not ship yet, and the step is written against it
    landing in the rendered project-context report)
  - the resolved booping home dir
  - the repo directory name, as the source of project-name candidates
  - whether the repo is under git
  - the project names already present under the home dir
  - on a not-yet-initialized project, asked in-step with `AskUserQuestion`: where the vault
    should live (in the repo or under the home dir), what the project is called, and — skipped
    when the vault itself lives in the repo — whether the repo-root marker is tracked in git,
    hidden from git but visible to the team, or hidden invisibly
  - on an already-initialized project: the change route the user picks, or their choice to
    change nothing

  Every item is read at run time from the context report and from shell calls: the body is
  plain markdown in a playbook that is not `jinja: true` and runs where no project context
  exists, so nothing may be resolved at render time.

- **Value** — the project level settled: a repo wired to a vault it can operate from, scaffolded
  and reachable from the home dir whichever side of the repo boundary it lives on; or, when the
  wiring already exists, an honest report of it plus the routes to change it. Every decision is
  taken in-step via `AskUserQuestion`; nothing is inferred silently, and a run where the user
  changes nothing leaves the repo and the home dir untouched.

- **Output files** —
  - `[CREATED] <vault-dir>/` — the vault tree, materialised by `booping scaffold vault.scaffold
    <vault-dir>`: `plans/`, `retrospectives/`, `_lessons/`, `_booping/`, `notes/` and a
    `.gitignore`. The command takes no `--set` variables; a non-empty destination aborts unless
    `--force` (exit 0 success, 1 user error, 2 OSError). `booping-create-project` carries its
    own hardcoded mkdir and is **not** what this step calls.
  - `[CREATED] <repo-root>/.booping` — the marker: `project_name:` always, plus `vault_path:`
    (resolved against the repo root) when the vault lives in the repo.
  - `[CREATED] <home-dir>/<project-name>` — symlink to the repo-local vault, for a repo-local
    vault only. Step-owned work: scaffold trees declare directories and text files only, never
    symlinks. Just create it — the step carries no failure-branch handling for an occupied path
    or a stale link.
  - `[UPDATED] <repo-root>/.gitignore` **or** `[UPDATED] <repo-root>/.git/info/exclude` — the
    marker's ignore entry, per the visibility answer; neither file is touched when the marker is
    tracked or when the question was skipped.
  - `[CREATED] <vault-dir>/sprints.md` — seeded with `booping render-sprints`, run from the repo
    root so it resolves the marker just written (honouring `vault_path:`). Idempotent.
  - On an already-initialized project: nothing, unless the user takes a change route — then the
    moved or renamed vault directory, the rewritten marker and the re-pointed symlink. A rename
    moves all three together: vault directory, the marker's `project_name`, and the home-dir
    symlink. Move and merge are offered as options, not scripted: the step acts on the user's
    call plus the run's context, with no collision rules and no teardown procedure. There is no
    attach route — a repo is never wired to a pre-existing vault this run did not create.
  - Out of scope: stack detection and `_booping/` extension seeding. The step produces the vault
    tree and its wiring, nothing stack-derived.

- **Harness return** — `## Changed:` listing every path written and empty when nothing was;
  `## Notes:` reporting the resolved project name, vault path and marker visibility.

- **Review gate** —
  - none — vault location, project name, marker visibility and the change route are all settled
    in-step via `AskUserQuestion`

- **Delegation** — inline: the runner performs the step. Model tier recorded for it:
  `opus-5:high`.

## Example artifact

Not-yet-initialized project, vault in the repo at `./booping`, marker hidden invisibly:

```text
booping/
├── .gitignore          # _booping/*.log
├── _booping/
├── _lessons/
├── notes/
├── plans/
├── retrospectives/
└── sprints.md

.booping                # repo root
  project_name: claude-booping
  vault_path: booping

.git/info/exclude       # appended
  .booping

~/Claude/claude-booping -> /home/anton/Dev/@A/claude-booping/booping
```

Vault under the home dir instead — no `vault_path:`, no symlink, and the marker-visibility
question still applies:

```text
~/Claude/claude-booping/
├── .gitignore
├── _booping/
├── _lessons/
├── notes/
├── plans/
├── retrospectives/
└── sprints.md

.booping                # repo root, tracked in git
  project_name: claude-booping
```

Already-initialized project, user changes nothing — the artifact is the report alone:

```text
Project `claude-booping` is already set up.
  vault:  /home/anton/Dev/@A/claude-booping/booping (in the repo)
  marker: .booping — project_name: claude-booping, vault_path: booping
  link:   ~/Claude/claude-booping -> booping/

Routes offered: move the vault · rename the project · merge it into another project.
User changed nothing.
```

## Return Format

Not-yet-initialized project, repo-local vault, marker hidden invisibly:

```markdown
## Changed:
- [CREATED] /home/anton/Dev/@A/claude-booping/booping/
- [CREATED] /home/anton/Dev/@A/claude-booping/.booping
- [CREATED] ~/Claude/claude-booping
- [UPDATED] /home/anton/Dev/@A/claude-booping/.git/info/exclude
- [CREATED] /home/anton/Dev/@A/claude-booping/booping/sprints.md

## Notes:
- project: claude-booping
- vault: /home/anton/Dev/@A/claude-booping/booping (in the repo)
- marker: /home/anton/Dev/@A/claude-booping/.booping — visibility: .git/info/exclude
```

Already-initialized project, user changed nothing:

```markdown
## Changed:

## Notes:
- project: claude-booping
- vault: /home/anton/Dev/@A/claude-booping/booping (in the repo, unchanged)
- marker: /home/anton/Dev/@A/claude-booping/.booping — visibility: .git/info/exclude
```
