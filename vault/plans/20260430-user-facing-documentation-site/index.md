---
title: User-facing documentation site
type: feature
status: done
sp: 25
split_from: null
created: 2026-04-30 00:00
planned: 20260430 15:37
started: 20260430 15:40
completed: null
retro: null
goal: null
summary: "New MkDocs documentation/ site published to gh-pages, README links out and /help lazy-loads per-skill pages"
---

# User-facing documentation site

## Context

booping currently ships end-user information across two surfaces: `README.md` (5-command quick start, features, statuses, extensibility) and `docs/` (lazy-loaded fragments owned by skills — `task_*.md`, `cross_validation.md`, `template_plan_frontmatter.md`, plan/review templates). There is no walkthrough-style documentation site, no per-skill reference, and no annotated tour of `src/config.yaml`. New users have to grep skill bodies to learn workflow nuance (e.g. milestone-grouping, the 35-SP soft cap, what `/code-review` does, what lives in `_booping/`).

This plan adds a separate `documentation/` source tree, builds it with MkDocs (readthedocs theme), and publishes to the `gh-pages` branch via GitHub Actions. README keeps its current quick-start + features overview and links out to the site for depth. `/help` switches to lazy-loading per-skill pages from `documentation/<name>.md` on the local checkout (filesystem path, same pattern as existing `docs/` lazy-loads).

`docs/` (plugin-internal lazy fragments) and `documentation/` (end-user site) are kept distinct; `CLAUDE.md` is updated to call out the distinction.

## Decisions

- **Site generator**: MkDocs with built-in `readthedocs` theme — no extra theme package, integrates with existing uv tooling, renders the same `.md` files that work on raw GitHub.
- **Source location**: `documentation/` at repo root, separate from `docs/` (which stays plugin-internal lazy-load fragments).
- **Publishing**: GitHub Actions workflow builds on push to `main` and deploys to the `gh-pages` branch (`peaceiris/actions-gh-pages`). Sources stay on `main`.
- **Published URL**: `https://A.github.io/claude-booping/` (derived from the `gh` remote `git@github.com:A/claude-booping.git`). Used in README link (Task 7.1) and `help.md` (Task 5.2).
- **README**: keeps current quick-start + features overview; adds a single link to the docs site. No deep content in README.
- **Page granularity**: per-skill page (one file per command) for future-proof updates — editing `/groom` docs touches one file, not a 2000-line page.
- **`/help` integration**: skill body lazy-loads from `documentation/<name>.md` via `${CLAUDE_PLUGIN_ROOT}/documentation/<name>.md`; same mechanism as existing `docs/` lazy-loads. Site is hosted purely for human reading.
- **Reshape milestone**: included — rendered multi-page output reliably exposes IA issues only post-build.

## Information architecture

```
documentation/
├── index.md            # Landing — intro paragraphs, loop diagram, why-booping goodies, ToC
├── quick_start.md      # End-to-end walkthrough: install → /chat orient → sprints.md → first /groom
├── install.md          # /install command + post-install setup
├── vault.md            # Vault file conventions: sprints.md, _booping/, lessons/, notes/, plans/, retrospectives/
├── groom.md            # /groom — what, command, best practices, story points, cross-validation, Config
├── develop.md          # /develop — what, command, best practices, milestone grouping, Config
├── code_review.md      # /code-review — why, command, best practices, stack detection, severity labels, Config
├── retro.md            # /retro — why, command, best practices (shit in/shit out), reviewing the retro file
├── learn.md            # /learn — why, command, best practices, what it writes (cross-link to vault.md)
├── chat.md             # /chat — orient command + escalation rule
├── help.md             # /help — lists commands, links to this site
├── project_config.md   # Tour of src/config.yaml + override mechanics + debug-context
└── cli.md              # CLI reference: render, render-sprints, build, debug-context, debug-template
```

`index.md` highlights:
- One-paragraph intro (mirrors README first paragraph).
- Loop diagram: `groom → develop → (code-review) → retro → learn`.
- "Why booping" goodies: artifacts as meta-source for documentation/research/historical traces; benchmarking surface (run same plan with different models, compare diffs); agile-iteration scaffolding made durable; story points as a personal estimation track record.
- ToC with one-line teaser per page.

Cross-link map (back-links into the new docs that must land in the same sprint):
- `README.md` — add single link to the docs site near the existing Quick start section.
- `src/templates/skills/help.md.j2` — switch to lazy-load from `documentation/<name>.md`.
- `CLAUDE.md` — Layout section gets a `documentation/` entry distinguishing it from `docs/`.

## Architecture

Build pipeline:
- `mkdocs.yml` at repo root (theme, nav, plugins, strict mode).
- `mkdocs` added to `booping-python/pyproject.toml` under a `docs` dependency group; `uv run --group docs mkdocs build` and `uv run --group docs mkdocs serve` are the entry points.
- `just docs` (build) and `just docs-serve` (live preview) Justfile targets wrap the uv calls.
- `.github/workflows/docs.yml` triggers on push to `main` (paths: `documentation/**`, `mkdocs.yml`, the workflow itself); installs uv, runs `mkdocs build --strict`, deploys `site/` to `gh-pages` via `peaceiris/actions-gh-pages@v4`.
- `.gitignore` ignores `site/` (mkdocs build output).

Lazy-load mechanism (existing pattern, no new code):
- Skills reference `${CLAUDE_PLUGIN_ROOT}/documentation/<name>.md` from their bodies; the plugin runtime resolves the path against the local checkout. The published `gh-pages` site does not affect skill behavior.

## Milestones

### M1: Scaffold MkDocs + GH Action — 3 SP | done

**Goal**: Empty `documentation/` skeleton builds locally and deploys to `gh-pages` on push to main.

**Verify**:
- `just docs` succeeds with `--strict` (no warnings).
- `just docs-serve` opens a local site at `http://127.0.0.1:8000` showing a placeholder index.
- Push branch to remote and confirm `docs.yml` workflow runs green; merge dry-run shows `gh-pages` would be updated.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Add mkdocs to booping-python `docs` dependency group; add `mkdocs.yml` (readthedocs theme, full nav matching IA above, `strict: true`); scaffold one-line placeholder file for **every** page in the IA sketch so `--strict` build does not fail on missing nav targets; `.gitignore` for `site/`. | `booping-python/pyproject.toml`, `mkdocs.yml`, `documentation/{index,quick_start,install,vault,groom,develop,code_review,retro,learn,chat,help,project_config,cli}.md`, `.gitignore` | 1 | done |
| 1.2 | Add `.github/workflows/docs.yml` — install uv, run `mkdocs build --strict`, write `.nojekyll` to `./site` so GitHub Pages does not run Jekyll over MkDocs output, deploy to `gh-pages` via `peaceiris/actions-gh-pages@v4`. Trigger on push to main with path filter on `documentation/**` and `mkdocs.yml`. Workflow has `permissions: contents: write` so the action can push to `gh-pages`. | `.github/workflows/docs.yml` | 1 | done |
| 1.3 | Add `just docs` and `just docs-serve` targets wrapping `uv run --group docs mkdocs ...`. | `justfile` | 1 | done |

#### Task 1.1 DoD

- [ ] `mkdocs.yml` exists at repo root with `theme: name: readthedocs`, `strict: true`, and full nav covering every page in the IA sketch.
- [ ] Every nav target has a corresponding one-line placeholder file under `documentation/` so `mkdocs build --strict` succeeds without warnings.
- [ ] `booping-python/pyproject.toml` has `[dependency-groups] docs = ["mkdocs"]`.
- [ ] `.gitignore` includes `site/`.

#### Task 1.2 DoD

- [ ] `.github/workflows/docs.yml` triggers on `push: branches: [main]` with path filter on `documentation/**`, `mkdocs.yml`, `.github/workflows/docs.yml`.
- [ ] Workflow has `permissions: contents: write` (workflow- or job-level).
- [ ] Workflow runs `uv sync --group docs` and `uv run --group docs mkdocs build --strict`.
- [ ] Workflow writes `.nojekyll` to the build output before deploy.
- [ ] Workflow deploys `./site` to `gh-pages` via `peaceiris/actions-gh-pages@v4` with `github_token: ${{ secrets.GITHUB_TOKEN }}`.
- [ ] Workflow is gated to `main` only — sprint-branch pushes are not expected to trigger it.

#### Task 1.3 DoD

- [ ] `just docs` runs `uv run --group docs --project booping-python mkdocs build --strict` (paths resolve correctly from repo root).
- [ ] `just docs-serve` runs the equivalent `mkdocs serve` and the local site loads.

---

### M2: Foundation pages — 4 SP | done

**Goal**: `index.md`, `quick_start.md`, `install.md`, `vault.md` are written and cross-link correctly.

**Verify**: `just docs-serve`; navigate from `index.md` to each foundation page and back; every cross-link resolves; the loop diagram renders.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Write `index.md` — intro paragraphs (mirror README opening), loop diagram, "why booping" goodies, ToC with one-line teaser per page. | `documentation/index.md` | 1 | done |
| 2.2 | Write `quick_start.md` — end-to-end walkthrough: install marketplace + plugin, run `/install`, run `/chat` to orient, read `sprints.md`, first `/groom`, first `/develop`, first `/retro`, first `/learn`. | `documentation/quick_start.md` | 1 | done |
| 2.3 | Write `install.md` — `/install` command, prerequisites (uv, git, optional `GEMINI_API_KEY`), what gets scaffolded, post-install verification. | `documentation/install.md` | 1 | done |
| 2.4 | Write `vault.md` — full vault layout reference: `plans/`, `retrospectives/`, `lessons/`, `notes/`, `_booping/skill_<name>.md`, `_booping/agent_<name>.md`, `plan_templates/`, `review_templates/`, `sprints.md` (auto-rendered, never hand-edit), `config.yaml` (project override). One section per file/dir with what it's for and who manages it. | `documentation/vault.md` | 1 | done |

#### Task 2.1 DoD

- [ ] Opening paragraph aligns with README's first paragraph (no contradiction).
- [ ] Loop diagram renders as a code block or simple ASCII; no broken image references.
- [ ] All four "why booping" goodies are present: artifacts-as-meta-source, benchmarking, agile-loop scaffolding, SP-as-track-record.
- [ ] ToC links resolve to every other page in the IA sketch.

#### Task 2.2 DoD

- [ ] Walkthrough is end-to-end: a new user can copy commands in order and reach `/learn` without external lookups.
- [ ] Includes the post-install orient flow: `/chat` to orient, then read `sprints.md`.
- [ ] No prose duplicating README's existing 5-command Quick start — link instead where appropriate.

#### Task 2.3 DoD

- [ ] Prerequisites enumerate uv + git as required and `GEMINI_API_KEY` as optional (note it enables `/groom` cross-validation).
- [ ] Documents what `/install` scaffolds (vault directories + `.booping` marker).
- [ ] Cross-link to `vault.md` for the directory tour rather than restating it.

#### Task 2.4 DoD

- [ ] Every directory and notable file in `~/Claude/{project}/` has a section.
- [ ] `sprints.md` section explicitly states it is CLI-regenerated and must not be hand-edited.
- [ ] `_booping/skill_<name>.md` and `_booping/agent_<name>.md` sections note they are `/learn`-managed (cross-link to `learn.md`).
- [ ] `plan_templates/` and `review_templates/` sections cross-link to `groom.md` and `code_review.md` respectively.

---

### M3: /groom + /develop pages — 4 SP | done

**Goal**: Two per-skill reference pages, each with What/Command/Best practices/Config sections.

**Verify**: `just docs-serve`; render both pages; check Config sections list real keys from `src/config.yaml` (no invented knobs).

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Write `groom.md` — What it does; command form; best practices (more detail = sharper plan with brief vs. detailed example, free-text extras like branch name / stop-after-milestone / search web, define your own plan templates with link to `~/Claude/{project}/plan_templates/`); review-the-plan checklist; story points (1–5 scale, 35-SP soft cap, 5-SP re-decompose gate); cross-validation (set `GEMINI_API_KEY` to enable, runs once per plan); confirm step. Config section: `sprint.default_threshold_sp`, `sprint.redecompose_threshold`, `tasks`, `plan.statuses`. | `documentation/groom.md` | 2 | done |
| 3.2 | Write `develop.md` — What it does; command form (auto-claim vs. specific path); best practices (ask `/develop` to stop after each milestone and start a fresh session, do code review in a fresh session to avoid context growth, try other models like GLM for implementation and use opus for `/code-review`); review-code feedback list workflow. Config section: `sprint.max_milestones_per_agent` (groups consecutive milestones into one agent briefing), `git.branches` (branch prefix conventions), `skills.develop.agents`. | `documentation/develop.md` | 2 | done |

#### Task 3.1 DoD

- [ ] "Best practices" lists at least: more-detail-is-better (with concrete example), free-text prompt extras, project-local plan templates.
- [ ] Story points section restates the 1–5 scale and the 35-SP soft cap; does not invent thresholds.
- [ ] Cross-validation section: documents `GEMINI_API_KEY` as opt-in, "once per plan", and that it skips silently without the key. No hard call-cap claim.
- [ ] Config section lists exactly the keys `/groom` consumes; cross-link to `project_config.md` for override mechanics.

#### Task 3.2 DoD

- [ ] States explicitly that `/develop` runs all milestone groups in one session by default; "stop after each milestone" is a user-prompt-level instruction, not default behavior.
- [ ] Documents milestone grouping: up to `max_milestones_per_agent` consecutive milestones per agent briefing.
- [ ] Best-practices section covers fresh-session code review, alternative-model implementation pattern.
- [ ] No 5-SP refusal claim (that gate lives in `/groom`, not `/develop`).
- [ ] Config section enumerates `sprint.max_milestones_per_agent`, `git.branches`, `skills.develop.agents`.

---

### M4: /code-review + /retro + /learn pages — 4 SP | done

**Goal**: Three per-skill reference pages.

**Verify**: `just docs-serve`; navigate the three pages; cross-links to `vault.md` from `learn.md` resolve.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Write `code_review.md` — Why (quality gate; useful when implementation ran on a non-opus model); command form; best practices (define your own review templates, link to `~/Claude/{project}/review_templates/`); behavior notes (stateless side-skill — no plan-lifecycle status, no persistent report; auto stack-detect from manifest files; severity labels BLOCKER/SUGGESTION/NIT; trivial fixes inline, non-trivial → `booping-developer`). Config section: `code_review.stack_markers`. | `documentation/code_review.md` | 2 | done |
| 4.2 | Write `retro.md` — Why (asks user about tensions/change requests during develop, scans session logs and git diff, captures detailed project- and task-specific feedback); command form; best practices ("shit in, shit out" — command helps with questions but the user is responsible for thinking what should change); reviewing the retro file. | `documentation/retro.md` | 1 | done |
| 4.3 | Write `learn.md` — Why (compresses retros into durable rules + extension files); command form; best practices (review each proposed update for actionability and direction; "shit in, shit out" — accept blindly = conflicting/useless rules); what it writes (cross-link to `vault.md` for `lessons/`, `_booping/skill_<name>.md`, `_booping/agent_<name>.md` — note these are `/learn`-managed). | `documentation/learn.md` | 1 | done |

#### Task 4.1 DoD

- [ ] States `/code-review` is stateless (no plan status, no persistent report).
- [ ] Documents severity labels: BLOCKER / SUGGESTION / NIT.
- [ ] Documents stack auto-detect from manifest files (`pyproject.toml`, `package.json`, etc.).
- [ ] Distinguishes inline trivial fixes from `booping-developer` escalation for non-trivial fixes.
- [ ] Config section names `code_review.stack_markers` and shows one example mapping.

#### Task 4.2 DoD

- [ ] Why-section names both inputs: user-asked questions AND session-log/git-diff scan.
- [ ] "Shit in, shit out" framing is explicit and explains user responsibility.
- [ ] Reviewing-the-retro section names what to look for (durable findings vs. one-off complaints).

#### Task 4.3 DoD

- [ ] States `/learn` writes both global lessons (`lessons/{N}_{title}.md`) and per-skill / per-agent extension files (`_booping/skill_<name>.md`, `_booping/agent_<name>.md`).
- [ ] Cross-links to `vault.md` for the file-layout details rather than duplicating.
- [ ] Best-practices section covers reviewing proposed updates AND "shit in, shit out" — both warnings are present.

---

### M5: /chat + /help pages — 2 SP | done

**Goal**: Two final per-skill pages.

**Verify**: `just docs-serve`; both pages render and cross-link.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | Write `chat.md` — frame as the orient/working-mode command (vault navigation, light edits, ad-hoc small tasks); escalation rule (when scope grows, escalates to `/groom`). | `documentation/chat.md` | 1 | done |
| 5.2 | Write `help.md` — lists every booping command with a one-line summary and a link to its dedicated page; points to the docs site URL. | `documentation/help.md` | 1 | done |

#### Task 5.1 DoD

- [ ] Frames `/chat` as orient/working-mode, not just a chat interface.
- [ ] Documents the escalation rule (chat → groom when scope grows).
- [ ] Does not document internal rendering details (status tables auto-rendered on orient is internal).

#### Task 5.2 DoD

- [ ] Lists every booping command (groom, develop, code-review, retro, learn, chat, help, install) with one-line summary.
- [ ] Each command links to its dedicated documentation page.
- [ ] Top of page links to the published docs site.

---

### M6: project_config + cli pages — 2 SP | done

**Goal**: Reference pages for config and CLI.

**Verify**: `just docs-serve`; every config key documented exists in `src/config.yaml`; every CLI command runs as documented.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 6.1 | Write `project_config.md` — tour of `src/config.yaml`: every top-level key (`sprint`, `git`, `tasks`, `plan.statuses`, `skills.<name>.agents`, `code_review.stack_markers`) with what it controls. Override mechanics: `~/Claude/{project}/config.yaml` deep-merges over `src/config.yaml` at render time (no rebuild); dict keys merge, list keys replace wholesale. Cross-link to `cli.md` for `booping debug-context` to verify merged values. | `documentation/project_config.md` | 1 | done |
| 6.2 | Write `cli.md` — short reference for every `bin/booping` subcommand: `render`, `render-sprints`, `build`, `debug-context`, `debug-template`. Synopsis, args, when to use. | `documentation/cli.md` | 1 | done |

#### Task 6.1 DoD

- [ ] Every documented top-level key exists in `src/config.yaml`.
- [ ] Override mechanics state explicitly: deep-merge, dict merges, lists replace wholesale, takes effect at next skill load.
- [ ] At least one realistic override example (e.g. tweaking `sprint.default_threshold_sp` or adding a `git.branches` row).
- [ ] Cross-links to `cli.md` for `booping debug-context`.

#### Task 6.2 DoD

- [ ] Every subcommand listed exists in `booping-python/src/booping/commands/`.
- [ ] Each entry has synopsis + when-to-use.
- [ ] No invented flags.

---

### M7: Reference cleanup — 3 SP | done

**Goal**: Every existing surface that should link to or away from the new docs is updated. No deferred sweep.

**Verify**: README link resolves to docs site; `/help` skill renders with new lazy-load links; `CLAUDE.md` Layout section mentions `documentation/`.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 7.1 | Update `README.md` — add a single link to the documentation site near the existing Quick start section ("For a hand-holding walkthrough and per-command reference, see the docs site"). Keep all existing README content. | `README.md` | 1 | done |
| 7.2 | Update `/help` skill body to lazy-load from `documentation/<name>.md`. Edit the runtime template at `src/templates/skills/help.md.j2`; rebuild via `just build`. Each command in `/help`'s list links to `${CLAUDE_PLUGIN_ROOT}/documentation/<name>.md` for the lazy-load and to the published docs URL for human reference. | `src/templates/skills/help.md.j2`, `skills/help/SKILL.md` (build artefact) | 1 | done |
| 7.3 | Update `CLAUDE.md` Layout section to add a `documentation/` entry distinguishing it from `docs/` ("end-user docs site source; built and deployed to `gh-pages` by `.github/workflows/docs.yml`"). Update Editing conventions section if needed. | `CLAUDE.md` | 1 | done |

#### Task 7.1 DoD

- [ ] README has exactly one new link to the docs site (no duplicates).
- [ ] Existing README content is unchanged (no inadvertent edits to Quick start, statuses, sprints, etc.).
- [ ] Link target resolves once `gh-pages` deploys.

#### Task 7.2 DoD

- [ ] `src/templates/skills/help.md.j2` lazy-loads from `${CLAUDE_PLUGIN_ROOT}/documentation/<name>.md` for every booping command.
- [ ] Four-check IA pass run on the modified `help.md.j2` (Scoping, Duplication, Configurability, Hierarchy — see lesson 0004); each check confirmed in the commit message or plan notes.
- [ ] `just build` runs cleanly; `skills/help/SKILL.md` is regenerated.
- [ ] `bin/booping render src/templates/skills/help.md.j2` produces output containing valid `documentation/` paths.

#### Task 7.3 DoD

- [ ] `CLAUDE.md` Layout section names `documentation/` and explains how it differs from `docs/`.
- [ ] Editing conventions section addresses `documentation/*.md` (hand-authored, no build step touches the source — only mkdocs publishes).

---

### M8: Reshape — 3 SP | pending

**Goal**: User reads the rendered site end-to-end and files prose/structure feedback; feedback is applied before the plan transitions out of `in-progress`.

**Verify**: User reviews `gh-pages` deploy (or local `just docs-serve`); files feedback as a list; every item is either applied or explicitly deferred with rationale.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 8.1 | Pause for user review. Hand the rendered site URL (or local-serve URL) back to the user. Collect feedback as a numbered list. | (no file changes) | 1 | pending |
| 8.2 | Apply feedback list. Each item is either resolved with a code/doc change or explicitly deferred with a one-line rationale appended to the plan. | `documentation/**/*.md` (and any cross-referenced surfaces) | 2 | pending |

#### Task 8.1 DoD

- [ ] User has reviewed every page on the published or locally-served site.
- [ ] Feedback list is captured in the plan (or in a notes file referenced from the plan).

#### Task 8.2 DoD

- [ ] Every feedback item is addressed: applied or explicitly deferred.
- [ ] No deferred item silently dropped.
- [ ] `just docs` still runs strict-clean after changes.

---

## Final Verification

- [ ] `just docs` succeeds with `--strict` (no warnings).
- [ ] `just docs-serve` opens locally and every page renders without broken cross-links.
- [ ] On `main`, the GH Action runs green and `gh-pages` is updated; published site loads with full nav.
- [ ] README link resolves to the published site.
- [ ] `/help` skill renders cleanly (`bin/booping render src/templates/skills/help.md.j2`); lazy-load links point at real `documentation/` files.
- [ ] `CLAUDE.md` Layout section includes `documentation/` and distinguishes it from `docs/`.
- [ ] Project quality gates pass: `just lint`, `just typecheck`, `just test`.
- [ ] Reshape feedback list fully addressed.

## Out of scope

- No translation / multi-language support.
- No search-index tuning beyond the readthedocs theme defaults.
- No new commands documented (only existing booping commands).
- No skill-body rewrites beyond `/help` (which is required to wire the lazy-load).
- No changes to `docs/` (plugin-internal lazy-load fragments stay where they are).
- No removal of existing README sections (only addition of one link).

## CLAUDE.md impact

- Layout section: add `documentation/` entry; distinguish from `docs/`.
- Editing conventions: add a line that `documentation/*.md` is hand-authored and only `mkdocs build` touches it; the build is GH Action-driven, not local-build-on-commit.

Owned by Task 7.3.
