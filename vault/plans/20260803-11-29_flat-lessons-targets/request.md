# Framing brief

## Request

> now I want to plan next update: I want lessons to be a flat dir, and each lesson to have `targets` list in frontmatter. Also lessons in this dir should only be targeted against playbooks and agents, never against old skills.

Raised immediately after the `/learn` playbook port landed, with all five lifecycle playbooks (groom, develop, retro, learn, playbook-authoring) now in core. Today two parallel lesson systems exist: the vault's flat `lessons/` (id/title/retro frontmatter, injected wholesale and unscoped into legacy skills via `_lessons.j2`) and the playbook `_lessons/` dirs (per discovery root plus per playbook, `step:` frontmatter, scope encoded by directory location). Lessons 0004–0007 are currently duplicated across both systems.

## Task type

`feature` — a new routing capability for lessons: a `targets:` frontmatter list that does not exist today, a new discovery shape, and new injection semantics for agents.

- Not `bug`: nothing diverges from specified behaviour — both current lesson systems work as designed; the request is a capability neither has.
- Not `refactoring`: the change is user-visible by definition — lesson authors write a new frontmatter key, renders inject differently, and agents gain lesson injection they never had through this channel.

## Problem

Lesson scope is encoded by *location*, twice over. A skill lesson lives in the vault's `lessons/` and reaches every legacy skill unscoped through `_lessons.j2`. A playbook lesson lives in one of four `_lessons/` directories (root-level per discovery root, playbook-level per playbook dir, unioned across roots), reaches one playbook, and narrows to one step only via a `step:` frontmatter key. Routing a lesson means choosing the right directory, and the same rule wanted in two places means two files — which is exactly where the tree stands today, with 0004–0007 copied into `_playbooks/groom/_lessons/`.

The change: one flat lessons directory; each lesson carries a `targets:` list in frontmatter naming what it binds to; the legal target vocabulary is playbooks and agents only — legacy skills are not a target this directory can name.

## Clarifications and Decisions

- Two discovery roots for the new system, mirroring playbook discovery: global `{home_dir}/_lessons/` and project `{vault}/_lessons/`. Location encodes visibility (which projects see the lesson); `targets:` encodes routing. Same-filename shadowing project-over-global.
- New lessons live **only** in those two dirs — no per-playbook `_lessons/`, no playbook-root-level `_lessons/`, no core-root lessons dir.
- `targets:` vocabulary: playbook name (`groom`), playbook step (`groom/draft-plan`), agent (`agent:booping-developer`) — step granularity replaces today's `step:` key.
- Legal targets are playbooks and agents only; legacy skills are never a target the new dirs can name.
- Old vault `lessons/` stays legacy-only: keeps flowing to legacy skills via `_lessons.j2`, untouched by this plan.
- Parallel deprecation: every old mechanism (four playbook `_lessons/` scopes, `step:` key, `_lessons.j2` skill injection) keeps working this release; removal is a later plan.
- The harness emits a warning when legacy lessons exist (playbook `_lessons/` dirs with content), surfaced as a render-time `Note — tell the user:` notice.
- No manual prose-shape reshape expected after implementation.
