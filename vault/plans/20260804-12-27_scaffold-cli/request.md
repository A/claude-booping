# Framing brief — Scaffold CLI

## Request

> i want to plan a `booping scaffold <template> <dest>` cli tool. It should take file/dir tree from config (core, global, project level, etc), and create the dir structure. Also i want to have a simple file content seeding, like file can have a string or multiline yaml string if it need to have some content (but i expect just couple of static lines). Before groom, show me 2-3 interface options, how it may look.

## Task type

`feature` — a new user-facing capability: a `scaffold` subcommand that does not exist today, plus a new `scaffold:` config surface for it.

- Not `bug`: nothing diverges from expected behaviour; there is no observed defect, no reproduction, no regression to guard.
- Not `refactoring`: the work adds a user-visible surface (a new CLI subcommand and a new config key) rather than changing internal structure behind unchanged behaviour — it fails the no-user-visible-change test.

## Problem

Today booping has one scaffolding path, `bin/booping-create-project`, which hardcodes the vault directory layout in a standalone uv script. Every other file/dir tree a user needs — a new playbook skeleton, a new step directory, a plan-template stub — is created by hand or by a skill writing files one at a time. There is no declarative way to say "this template means these directories and these seed files", and no way for a project or a machine-global config to define its own trees.

What must change: a `scaffold` subcommand on `bin/booping` that reads named templates from the existing three-tier config merge (core `src/config.yaml` → global `${XDG_CONFIG_HOME:-~/.config}/booping/config.yaml` → project `{vault}/config.yaml`) and materialises one of them into a destination directory — creating the directory structure, and seeding files whose content the template declares inline as a short string or a YAML block scalar.

## Clarifications and Decisions

- Config shape: **nested tree** (Option B) — `scaffold.{template}.tree` mirrors the real directory shape via YAML nesting; a mapping value is a directory, a string value is a file's content. Chosen over a flat path map (Option A) and an explicit entry list (Option C). Option C was ruled out because lists replace wholesale in the config merge, killing partial project override without new merge-by-path machinery.
- Content seeding is expected to stay small — "a couple of static lines" per file — not full document templates.
- Templates come from the existing config merge tiers, so a project can extend or override a core template.
- Tree encoding is **hybrid**: a string value is a file's content, a mapping value is a directory's children, and a mapping carrying the reserved key `type` is instead an explicit node descriptor (`type: file|dir` plus `content`, `mode`, and any future per-node keys). Shallow trees stay one line per level; the explicit form is available where a node needs more than content. `type` is a reserved filename inside a tree.
- Existing destination is an **error** — `booping scaffold` aborts with a non-zero exit unless `--force` is passed. Consequence accepted: seeding a step directory into an existing playbook goes through `--force` or through a nested destination path.
- Seeded content is **Jinja-rendered** through the same environment as `render` / `render-playbook`, with full project context available and `--set key=value` for per-run values.
- `bin/booping-create-project` is untouched. Scaffold is purely additive; the vault layout is not re-expressed as a scaffold template in this sprint.

- No `tree:` or `description:` wrapper. A template's value **is** its directory contents, so `scaffold.{name}` is uniformly a dir-children mapping under the same rule every nested level uses. Consequence accepted: a no-args listing can show only names and top-level entries, no subtitle.
- Addressing is by **dotted config path**, traversing the merged config anywhere: `booping scaffold playbook.scaffold ./playbooks/x`, `booping scaffold skills.install.project_scaffold ~/Claude/new`. Trees colocate with the config they serve. Consequences accepted: there is no registry, so no no-args listing; the config path is the user-facing name; and pointing at a key that is not tree-shaped is a runtime error the loader must report against the offending path.
- Tier extensibility comes from the existing `deep_merge`, not from addressing — a project adds or overrides leaves in any tier, and project always wins on collision. Core templates are deliberately not un-overridable.
- **Non-goal**: template updates. Unlike Copier's `copier update`, a scaffolded directory is a one-shot copy with no answers file and no later re-merge. Interactive prompting is likewise out of scope; `--set` is the non-interactive equivalent.
- Seed content renders through `rendering.build_source_env` with a plain `Environment`, no `SandboxedEnvironment` — config is the same trust level as every other booping template.

## Open

- **Goal** — the user-visible outcome after this ships is not yet stated. Must be settled before the plan can reach `ready-for-dev`.

