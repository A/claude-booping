# Framing brief

## Request

> plan next config update: i want all core settings to be namespaced in config.core. Logic is next: if a field belongs to a specific playbook it goes into config.core.{name}_playbook, if it belongs to core development loop or it's cross playbooks - it goes to config.core. core - is playbook set delivered togehter, and it becomes an example of namespacing in config for user playbooks.

## Task type

`refactoring`.

Test: does the change add a capability a user can invoke, or only relocate existing declarations? Only relocation — every rendered surface must read the same after the move.

- Not `feature`: no new user-facing capability. `core.{name}_playbook` is a placement convention for keys that already exist, not a new mechanism — the engine already resolves any dotted path.
- Not `bug`: nothing diverges from expected behaviour. Today's flat layout is a design that outgrew itself, not a defect.

## Problem

`src/config.yaml` today mixes three unrelated ownership levels at the top level with no convention distinguishing them:

- **Engine keys** — `home_dir`, `macros`, `migrations`, `plan`, `git`, `playbook.scaffold`, `vault.scaffold`.
- **Cross-playbook keys** — `research_agent`, `core.sprint`, `core.task_types`, `core.plans`.
- **Single-playbook keys** — `core.groom_playbook.*`, plus `skills.develop`, `skills.code-review`, `skills.retro`, `skills.learn` still keyed under `skills.` although the skills were retired and the consumers are playbooks.

Namespacing was started (`core.sprint`, `core.task_types`, `core.plans`, `core.groom_playbook`) and stopped mid-way, so both conventions are live at once. A user authoring their own playbook has no worked example of where a playbook's own config belongs, and `skills.{name}` remains as a false lead pointing at a retired surface.

What must change: every setting the core playbook set owns sits under `config.core`, with a playbook's own settings under `config.core.{name}_playbook` and shared/loop-wide settings directly under `config.core`. `core` becomes the reference example a user's playbook namespace copies. Engine-level keys that are not "core playbook set" keys need an explicit ruling on whether they move too.

## Clarifications and Decisions

- `home_dir` stays top-level (it resolves the vault before any namespace matters); every other top-level key moves under `core`.
- Placement rule: a key one playbook owns goes to `core.{name}_playbook`; a key the core development loop or several playbooks share goes directly under `core`. `core` is the shipped playbook set and doubles as the worked example a user's own namespace copies.
- `git` is develop-only — `playbooks/_partials/_git_guide.j2` is imported by `develop/provision/base.md` alone, and `git.commit_message` is read by `develop/develop-loop/base.md` and `develop/wrap-up/base.md` — so it lands at `core.develop_playbook.git`.
- The `skills:` block is dropped entirely. `skills/chat/` and `skills/help/` are deleted outright — build artefacts, `src/files/` shells, `src/templates/skills/` bodies and `config_files.yaml` effort entries — along with whatever that orphans.
- `config.plan` is retired rather than relocated. Its transitions/superstates/hooks machinery has a single live caller: retro's `intake` step running `booping transition done {plan}` for skipped siblings; that move is ported onto `playbook-transition` / a `_scripts/` hook the way groom already does it. `_plan_transitions.j2` is already an orphan and `docs/plan_lifecycle_overview.md.j2` dies with `/chat`. Where the residual status vocabulary lives (the values `plan_status:` takes and the entry statuses retro / learn / code-review query on) is a draft-plan design call.
- Existing global- and project-tier config files are carried by a shipped vault migration under `migrations/`; the global tier is called out in the migration body as a manual step.
- No post-implementation prose reshape is expected — the work is mechanical plus report regeneration.
- Open risk carried into drafting: the sprint spans namespacing, a skills deletion, a lifecycle retirement and a migration, so it may pass the 35 SP split threshold. The natural seam is namespacing + migration first, lifecycle retirement second.
