---
reviewed_at: 2026-08-08 18:24
---

# claude-booping — Documentation surfaces

Markdown surfaces only, one row per destination file or per documented directory; anything
that is rendered, executed, or seeded elsewhere is out of the set.

| Surface | Format & conventions | Audience | Depth |
| --- | --- | --- | --- |
| `README.md` | Hand-authored, ~180 lines. Opens with a one-paragraph pitch and an Obsidian vault screenshot, then Disclaimer, Dependencies (per-OS install blocks), Installation (in-app `/plugin` commands), workflow narrative, and a hand-maintained Statuses section restating the per-playbook `states:` blocks. Fenced shell/command examples; links out to the MkDocs site for depth. | An engineer evaluating the plugin from the GitHub page: what it is, whether it fits their workflow, how to install, what the loop looks like. | What-and-why plus first install only. Command references, config keys, and playbook mechanics are out of place — they belong on the site. |
| `documentation/` | MkDocs site source (`docs_dir: documentation`, readthedocs theme, `strict: true`), published to gh-pages on push to `master` via `just docs`. Nav is declared in `mkdocs.yml`: Home, Quick start, Install, Vault, Playbooks, Project config, external agents, then one page per workflow playbook. Pages run 30–480 lines, bare relative `.md` links, sparing `!!!` admonitions, H2-sectioned reference prose with fenced config/command examples. | Users following quick start, per-playbook commands, and status vocabularies; advanced users after the three-tier config merge, templates, lessons, playbook authoring, and external-agent wiring. | The deep public reference — exhaustive on behavior and configuration. Plugin internals (build pipeline, snapshots, evals) stay out; those are contributor territory. |
| `docs/` (top-level `*.md` fragments) | Hand-authored plugin-internal fragments, no build step, lazy-loaded at run time via `${CLAUDE_PLUGIN_ROOT}/docs/<name>.md` links from skills, playbook steps, and config. Short (10–65 lines), imperative, one route-specific concern per file (e.g. `how_to_initialize_project.md`, `retro_summary_format.md`). | Agents mid-run following a lazy-linked route; contributors deciding where route-specific detail belongs instead of inlining it. | Exactly what the linking step needs and nothing more — minimum useful context. Anything a human reader would browse belongs on the site instead. |
| `CLAUDE.md` | Session-loaded project guide, checked into the repo root. Dense H2 sections (Commands, Layout, Rendering pipelines, Config, Playbooks, Lifecycle, Principles, Editing conventions); one-line-per-item bullets, backticked paths and commands, links into `documentation/` for full references. Schema-over-prose: it points at `src/config.yaml` and `states:` blocks rather than restating them. | Agents (and contributors) opening a session on this repo: where things live, which command gates a change, which files are build artifacts versus live edits. | The map, not the data — orientation and invariants only. Restated config values, status lists, or long procedure prose are drift and out of place. |
| `CHANGELOG.md` | Repo-root, Keep a Changelog shape since 2026-08-09: a standing `## Unreleased` section above dated releases (first entry v1.0.0), past-tense user-voiced bullets grouped Added / Changed / Removed. Entries in the public voice of the release notes (`.claude/skills/release`), user-visible changes only, conventional-commit history as raw material, not content. | Users and advanced users deciding whether to upgrade and what a release changes for their vaults and config. | One entry per release, a few lines each: behavior changes, new config keys, migrations to run. Internal refactors and CI churn stay out. |

## Not surfaces

- `playbooks/**` (manifests, step `prompt.md`, `_partials/`, `_specs/`, `_fixtures/`, `_lib/`, `_scripts/`) — playbook source: prose that is executed as instructions, not read as documentation; owned by the playbook editing loop.
- `playbooks/*/_reports/*.md` — generated render snapshots, written only by `just snapshots-accept`.
- `skills/**/SKILL.md`, `agents/*.md` — build artifacts of `just build`; the source lives in `src/files/` and `src/templates/`.
- `src/files/**`, `src/templates/**` — Jinja sources of rendered surfaces, not destinations.
- `migrations/*/migration.md` — executable vault-migration procedures driven by the `migrate` playbook; frontmatter `id` is machinery, not prose for readers.
- `docs/plan_templates/`, `docs/review_templates/` — vault seed templates copied into user projects, not read in place.
- `docs/images/` — non-markdown assets.
- `.claude/skills/release/SKILL.md` — repo-local maintainer procedure, executed not browsed.
- `booping-python/tests/**` fixture markdown — test data.
- `site/` — MkDocs build output.
- Source files, module headers, and inline comments — owned by `develop`.
