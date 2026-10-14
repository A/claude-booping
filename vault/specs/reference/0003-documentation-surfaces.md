---
type: reference
title: Documentation surfaces
summary: Booping's markdown documentation surfaces, each with its audience and the depth ceiling past which content belongs elsewhere; executed or generated markdown is not a surface.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-15
status: live
sources: [https://github.com/A/claude-booping/blob/c7e43b43dfe5fc1c0fafe253dd148d7e62ea231e/vault/docs/_specs/targets.md]
---

## Facts

- `README.md` — for an engineer evaluating the plugin from the GitHub page: what it is,
  whether it fits, how to install, what the loop looks like. Ceiling: what-and-why plus
  first install; command references, config keys and playbook mechanics belong on the
  site. Its Statuses section is hand-maintained over the per-playbook `states:` blocks.
- `documentation/` (the MkDocs site) — for users (quick start, per-playbook commands,
  status vocabularies) and advanced users (config merge, templates, rules, playbook
  authoring, external agents). The deep public reference, exhaustive on behaviour and
  configuration; plugin internals (build pipeline, snapshots, evals) stay out.
- `documentation/recipes/` — for advanced users and contributors: one blogpost-like,
  end-to-end guide per non-trivial setup, in the user's own voice, linked from the
  README. Content is dictated by the user, never derived from delivered work; a
  documentation sweep may review a recipe for staleness but never generates or extends
  one, and a missing recipe is never a documentation gap. Reference pages stay the
  authority on behaviour.
- `docs/` (top-level fragments) — for agents mid-run following a lazy link, and
  contributors deciding where route-specific detail belongs. Ceiling: exactly what the
  linking step needs; anything a human would browse belongs on the site.
- `CLAUDE.md` — for agents and contributors opening a session on the repo: where things
  live, which command gates a change, which files are build artefacts. Ceiling: the map,
  not the data; restated config values, status lists or long procedures are drift.
- `CHANGELOG.md` — for users and advanced users deciding whether to upgrade. Keep a
  Changelog shape, one entry per release in the public voice of the release notes:
  behaviour changes, new config keys, migrations to run; internal refactors and CI
  churn stay out.
- The product-vision spec set — for Claude itself, read before writing any other
  surface so a change lands in the right place; a stale set mis-aims every surface
  downstream. Ceiling: the project's model of itself (vision, roles, features,
  surfaces); never how-to prose, run history or implementation detail. The surface is
  the project specs tier records the `docs` playbook reads: the value records,
  reference/0001–0003 and the story records.
- Not surfaces: playbook source (`playbooks/**` manifests, step prompts, partials,
  fixtures, scripts), the generated `playbooks/*/_reports/*.md` snapshots, the
  `skills/` and `agents/` thin shells, `src/templates/**`, `migrations/*/migration.md`,
  the seeded `docs/plan_templates/` and `docs/review_templates/`, `docs/images/`,
  `.claude/skills/release/SKILL.md`, test fixture markdown, the `site/` build output,
  and source comments — they are executed, generated or seeded, not read as
  documentation.
