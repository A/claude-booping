---
title: Actualize documentation site and README against v0.1.5
type: feature
status: done
sp: 17
split_from: null
created: 2026-06-14 00:00
planned: 20260614 13:25
commit: 59e6ead5216859226b38667467acb3cc7f2b292b
started: 20260614 13:40
completed: 2026-06-14 14:05
retro: retrospectives/20260722-seven-plan-retro.md
goal: success|partial|fail
summary: "Correct documentation site + README drift against v0.1.5: /develop selection, code-review homepage IA, stale claims"
---

# Actualize documentation site and README against v0.1.5

# Plan Body

## Context

**Audience**: end users of the booping plugin (people running `/groom`, `/develop`, etc.) plus contributors reading the README to understand the framework. The published MkDocs site (`documentation/`, deployed to gh-pages from `master` on push) and the repo `README.md` are the two surfaces this plan touches.

**Gap**: the `documentation/` pages are mostly frozen at their Apr 30 authoring date; the plugin has since advanced to v0.1.5. The drift falls in three buckets:

- **Correctness** — flat-wrong claims: `/develop` described as auto-claiming the oldest `ready-for-dev` plan (it actually presents an `AskUserQuestion` candidate list drawn from `ready-for-dev` **and** `awaiting-plan-review`); `booping-researcher`'s role in `/develop` overstated; `/retro` git-diff described as a primary discrete input; README:3 overstating Gemini cross-validation as unconditional ("before development begins") when it is optional (only when `GEMINI_API_KEY` is set).
- **IA** — the homepage loop diagram surfaces `/code-review` only as a parenthetical side-route appended to the develop node, even though it is a first-class stateless skill with its own nav page. This is the specific gap the user noticed ("no codereview on the homepage").
- **Discoverability** — many pages omit real, shipped features: multi-plan `/retro`, the skip-retro path, `/install`-seeded `_booping/` extension files, the `.booping` marker, `sprints.md` drift caveat, `disable_internal_agents` / `internal` config keys, `sprint.scale` config key, `/chat` plan-lifecycle-overview rendering, researcher delegation, and the `documentation` plan template (missing from both README and the docs).

**Confirmed clean** (no work needed): the 0.1.5 cli-agent / `/compile` / native-wrapper retirement already reached the docs tree — a grep for `compile`, `cli-agent`, `native wrapper`, `type: cli`, `render-cli-agent` returns zero stale hits across `documentation/`. This plan does **not** re-audit that retirement.

**Relationship to existing content**: this is an in-place correction + expansion of existing pages and the README. No new pages, no new commands, no site-generator/theme changes.

## Decisions

- **Site generator / theme / hosting**: unchanged — MkDocs (`readthedocs` theme), `docs_dir: documentation`, `strict: true`, deployed to gh-pages from `master` via `.github/workflows/docs.yml` on push touching `documentation/**` or `mkdocs.yml`. No config/theme/CI work in scope.
- **README in scope**: yes. README.md is GitHub-rendered (not part of the MkDocs build), so README edits do not trigger the docs CI — but they are part of "actualize everything" and are grouped with the homepage-IA milestone.
- **No reshape milestone**: user explicitly declined a post-build reshape pause. Pages are corrected and shipped directly; the per-milestone `mkdocs build --strict` (`just docs`) green check is the rendered-output gate.
- **Source of truth for every fact**: the developer agent must verify each claim against current source before writing — `src/templates/skills/*.md.j2` for command behavior, `agents/*.md` for the agent roster, `src/config.yaml` for statuses/transitions/sprint/agents/keys, `CLAUDE.md` for architecture, `.claude-plugin/plugin.json` for version. Prose must render the source, never restate a guessed value.

## Information architecture

No page tree change — every page already exists. Per-page purpose unchanged; the work is content accuracy + completeness within each.

```
documentation/
├── index.md          # homepage — loop diagram (elevate /code-review to first-class)
├── quick_start.md     # researcher-role fix, /code-review step, sprints.md caveat
├── install.md         # seeded _booping/ extension files
├── vault.md           # .booping marker, seeded extension files, sprints.md drift caveat
├── project_config.md  # config snapshot internal:true, disable_internal_agents/internal keys
├── integrating-external-agents.md  # cross-link to project_config key tour
├── groom.md           # sprint.scale config key
├── develop.md         # bare-invocation behavior (3 spots)
├── code_review.md     # researcher delegation, skills.code-review.status config
├── retro.md           # git-diff input fix, multi-plan runs, skip-retro path
├── learn.md           # update-vs-create sweep, CLAUDE.md write target, review-table link
├── chat.md            # plan-lifecycle-overview render, researcher delegation
└── help.md            # pointer to integrating-external-agents.md
README.md              # :3 cross-validation overstatement, :19 beta/now-live language, :135 documentation template
```

Cross-links to keep resolving: every internal link the build's `strict: true` validates; README's link to plan-templates list.

## Milestones

Ordered so each milestone produces an independently reviewable, build-green slice. No milestone exceeds 4 SP; none requires re-decomposition. Each milestone's `Verify` runs `just docs` (`mkdocs build --strict`) and loads the affected pages.

### M1: Correctness fixes — flat-wrong claims — 5 SP | done

**Goal**: every factually-incorrect statement across the docs + README:3 is corrected to match current skill/agent behavior.

**Verify**: `just docs` builds green with `--strict`; re-read each edited claim against its source-of-truth file and confirm it now matches; load `develop.md`, `quick_start.md`, `retro.md` rendered pages and confirm corrected text.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Fix `/develop` bare-invocation description: it does NOT auto-claim the oldest `ready-for-dev` plan — it presents an `AskUserQuestion` single-select candidate list drawn from `ready-for-dev` AND `awaiting-plan-review` (per `src/templates/skills/develop.md.j2` "Plan selection"). Correct all three spots. | `documentation/develop.md` (:3, :7, :23) | 2 | done |
| 1.2 | Fix `booping-researcher`'s role in `/develop`: scoped to the Phase 0 drift spot-check (given many plan-named files, confirm file shape matches plan assumptions) per `skills.develop.agents.booping-researcher.good_for`, not general code-reading during milestone execution. | `documentation/quick_start.md` (:72) | 1 | done |
| 1.3 | Fix `/retro` inputs: git diff is not a separate discrete scan phase — `/retro` mines the `/develop` session transcript (via `booping-researcher`) and runs a plan-stage lesson check; the code diff is grounding context, not a primary input phase. Match `src/templates/skills/retro.md.j2`. | `documentation/retro.md` (:12) | 1 | done |
| 1.4 | Fix README:3 Gemini overstatement: cross-validation is **optional**, only when `GEMINI_API_KEY` is set (cf. index.md:3 "with optional Gemini cross-validation"); current README text "cross-validates each plan against Gemini before development begins" reads as unconditional. | `README.md` (:3) | 1 | done |

#### Task 1.1 DoD

- [ ] All three develop.md spots describe the `AskUserQuestion` candidate-list behavior over `ready-for-dev` + `awaiting-plan-review`; no "auto-claims the oldest" wording remains.
- [ ] "What it does" line (:3) no longer says "Claim a `ready-for-dev` plan" as if singular/automatic; reflects interactive selection.
- [ ] Verified against `src/templates/skills/develop.md.j2` Plan selection block (the `selectattr('status','in',['ready-for-dev','awaiting-plan-review'])` filter).

#### Task 1.2 DoD

- [ ] quick_start.md describes researcher use in `/develop` as the narrow Phase 0 drift check, not general milestone-time code reads.
- [ ] Verified against `skills.develop.agents.booping-researcher.good_for` in `src/config.yaml`.

#### Task 1.3 DoD

- [ ] retro.md no longer lists "the produced diff" as a primary discrete input alongside session logs; describes session-log mining (via researcher) + plan-stage lesson check.
- [ ] Verified against `src/templates/skills/retro.md.j2` phase structure.

#### Task 1.4 DoD

- [ ] README:3 states cross-validation is optional and conditional on `GEMINI_API_KEY`; wording consistent with index.md:3.
- [ ] No broken links introduced; `just docs` not required for README (GitHub-rendered) but no MkDocs link references README content.

---

### M2: Homepage IA + README freshness — 4 SP | done

**Goal**: `/code-review` is a first-class, labeled element of the homepage loop diagram; README launch-note language and plan-template list are current.

**Verify**: `just docs` builds green with `--strict`; load rendered `index.md` and confirm `/code-review` reads as a first-class step (labeled node/branch), not a buried parenthetical; visually confirm the ASCII diagram still renders correctly in the `readthedocs` theme; render README in a GitHub markdown previewer and confirm the disclaimer + plan-template list read as current.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Redraw the homepage loop diagram so `/code-review` appears as a first-class labeled element (its own box/branch off `develop`, clearly named), not a parenthetical comment. Keep it accurate: stateless side-route on the in-progress diff, not a lifecycle status. Update the surrounding prose if needed for consistency. | `documentation/index.md` (:9–29, :47 already lists it in Read-next) | 2 | done |
| 2.2 | Rewrite README:19 disclaimer paragraph: drop "in beta / now live / now available" launch-note framing; describe per-project config and `/code-review` as established v0.1.5 features matter-of-factly. | `README.md` (:19) | 1 | done |
| 2.3 | Add `documentation` to the core plan-templates list in README:135 (currently `backend`, `frontend`, `claude-skill`, `cli`). Verify the full current core set against `docs/plan_templates/*.md`. | `README.md` (:135) | 1 | done |

#### Task 2.1 DoD

- [ ] The loop diagram names `/code-review` as a distinct labeled element, not only inside a `(optional side-route: …)` parenthetical.
- [ ] Diagram remains factually correct: `/code-review` is stateless (no plan status), operates on the in-progress diff, optional.
- [ ] ASCII art renders cleanly in the built site (load the page; no broken alignment in the `readthedocs` theme).
- [ ] Read-next list (:47) still resolves to `code_review.md`.

#### Task 2.2 DoD

- [ ] No "in beta", "now live", or "now available" launch-announcement phrasing remains in README:19.
- [ ] Per-project config and `/code-review` described as current capabilities.

#### Task 2.3 DoD

- [ ] README plan-templates list includes `documentation` and matches the actual files under `docs/plan_templates/`.
- [ ] No other stale template name in the list (cross-check `backend`, `frontend`, `claude-skill`, `cli`, `documentation`).

---

### M3: Config-docs coverage — 4 SP | done

**Goal**: `project_config.md` (and the two pages that lean on it) accurately reflect the current `src/config.yaml` schema, including the internal-agent keys and `sprint.scale`.

**Verify**: `just docs` builds green with `--strict`; diff the documented config snapshot against the live `src/config.yaml` and confirm shape parity for the agent blocks; load `project_config.md`, `groom.md`, `integrating-external-agents.md` and confirm cross-links resolve.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Update the embedded config snapshot to include `internal: true` on every built-in agent entry (matches live `src/config.yaml`); add `skills.<name>.disable_internal_agents` and `skills.<name>.agents.<id>.internal` to the "Top-level keys" section with one-line descriptions. | `documentation/project_config.md` | 2 | done |
| 3.2 | Add `sprint.scale` (the 1–5 SP definitions) to the groom.md Config section as the configurable key driving the rendered scale prose. | `documentation/groom.md` (:117–118) | 1 | done |
| 3.3 | Add a cross-link from `integrating-external-agents.md` (its `disable_internal_agents` mention) to the project_config.md key tour where the flag is now formally documented. | `documentation/integrating-external-agents.md` | 1 | done |

#### Task 3.1 DoD

- [ ] Config snapshot shows `internal: true` on built-in agent blocks, matching `src/config.yaml`.
- [ ] "Top-level keys" section documents `disable_internal_agents` and per-agent `internal`.
- [ ] Verified against current `src/config.yaml` and the schema description in `CLAUDE.md`.

#### Task 3.2 DoD

- [ ] groom.md Config section names `sprint.scale` alongside the existing `sprint.*` keys.
- [ ] Verified against `src/config.yaml` `sprint.scale`.

#### Task 3.3 DoD

- [ ] integrating-external-agents.md links `disable_internal_agents` to the project_config.md key tour; link resolves under `--strict`.

---

### M4: Missing-feature discoverability sweep — 4 SP | done

**Goal**: every documented page surfaces the real, shipped features a user would expect from it. Additive coverage only — no contradiction of M1 corrections.

**Verify**: `just docs` builds green with `--strict`; load each edited page and confirm the added feature note is accurate against its source-of-truth template; confirm all new internal cross-links resolve.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | vault.md: add the `.booping` marker file to the vault tour; note the three `_booping/` extension files seeded by `/install` (`agent_booping-developer.md`, `skill_groom.md`, `skill_develop.md`); add the `sprints.md` drift caveat (can be stale between `/chat` refreshes; no auto-refresh hook yet). | `documentation/vault.md` | 1 | done |
| 4.2 | install.md: list the three seeded `_booping/` extension files alongside the directory scaffold (per `src/templates/skills/install.md.j2` Phase 4). quick_start.md: add the `sprints.md` drift caveat and surface `/code-review` as the optional step between `/develop` and `/retro`. | `documentation/install.md`, `documentation/quick_start.md` | 1 | done |
| 4.3 | retro.md: document multi-plan retro runs and the skip-retro path (`awaiting-retro → done`, `goal: skipped`). learn.md: document the update-vs-create sweep (Phase 1.5), repo `CLAUDE.md` as a write target (Phase 3), and link/describe the review-table interaction (`docs/learn_review_table.md`). | `documentation/retro.md`, `documentation/learn.md` | 1 | done |
| 4.4 | code_review.md: note `booping-researcher` for blast-radius reads on diffs ≥5 files, and that `skills.code-review.status` controls the argument-free plan picker. chat.md: note plan-lifecycle-overview rendering (`bin/booping render src/templates/docs/plan_lifecycle_overview.md.j2`) and researcher delegation for vault-wide reads. help.md: add a pointer to integrating-external-agents.md. | `documentation/code_review.md`, `documentation/chat.md`, `documentation/help.md` | 1 | done |

#### Task 4.1 DoD

- [ ] vault.md describes `.booping`, the seeded extension files, and the `sprints.md` drift caveat; each verified against `install.md`/`CLAUDE.md`/`src/templates/skills/install.md.j2`.
- [ ] No contradiction with the M1 sprints.md / researcher wording.

#### Task 4.2 DoD

- [ ] install.md lists the three seeded extension files; verified against `src/templates/skills/install.md.j2` Phase 4.
- [ ] quick_start.md carries the sprints.md drift caveat and an optional `/code-review` step between `/develop` and `/retro`.

#### Task 4.3 DoD

- [ ] retro.md documents multi-plan runs and the skip-retro (`goal: skipped`) path; verified against `src/templates/skills/retro.md.j2`.
- [ ] learn.md documents the update-vs-create sweep, `CLAUDE.md` as a write target, and the review-table format; verified against `src/templates/skills/learn.md.j2` and `docs/learn_review_table.md`.

#### Task 4.4 DoD

- [ ] code_review.md mentions researcher (≥5-file diffs) and the `skills.code-review.status` knob; verified against `src/templates/skills/code-review.md.j2` and `src/config.yaml`.
- [ ] chat.md mentions lifecycle-overview rendering and researcher delegation; verified against `src/templates/skills/chat.md.j2`.
- [ ] help.md points to integrating-external-agents.md; link resolves under `--strict`.

---

## Final Verification

- [ ] `just docs` (`mkdocs build --strict`) succeeds with zero warnings.
- [ ] Every internal cross-link resolves in the built site (guaranteed by `--strict`, but spot-load index/develop/retro/project_config to confirm).
- [ ] Every corrected claim re-verified against its source-of-truth file (no fact written from memory).
- [ ] README renders cleanly in a GitHub markdown previewer; plan-template list and disclaimer current.
- [ ] grep `documentation/` and `README.md` once more for `compile`, `cli-agent`, `native wrapper`, `type: cli` → still zero (no regression reintroducing retired concepts).

## Out of scope

- No new documentation pages and no new commands documented.
- No skill-body, agent-body, partial, or `src/config.yaml` edits — docs/README only (the docs must match the code, not the reverse).
- No MkDocs config, theme, or CI-workflow changes.
- No reshape / post-build IA-review milestone (user declined).
- No re-audit of the cli-agent / `/compile` retirement — already confirmed clean in the docs tree.
- No translation, no image/screenshot changes.

## CLAUDE.md impact

No `CLAUDE.md` changes required — this plan changes documentation content only; it does not alter the `documentation/` layout, build pipeline, CI, or any top-level structure already described in `CLAUDE.md`.

---

# Quality Checklist

## Frontmatter

- [x] Frontmatter matches the plan-frontmatter shape.
- [x] `sp` (17) equals the sum of per-task SP across milestones: M1 (2+1+1+1=5) + M2 (2+1+1=4) + M3 (2+1+1=4) + M4 (1+1+1+1=4) = 17.

## Content

- [x] Context names the audience (end users + contributors) and the gap (Apr-30 freeze vs v0.1.5).
- [x] IA sketch present; every page carries a one-line purpose.
- [x] Each page is a milestone task or grouped with siblings under one milestone — no orphan pages.
- [x] DoD bullets verifiable by loading the rendered page or running `just docs`.
- [x] Every task lists exact file paths.
- [x] Every milestone has a `Verify` step including a `just docs` build check.
- [x] Each milestone executable from a fresh session with only the plan as context.

## Documentation hygiene

- [x] No prose duplicated across pages — shared facts (sprints.md caveat) link to a single description rather than restating.
- [x] Code blocks tagged with correct language; commands runnable as written.
- [x] No "coming soon" placeholders.

## Cross-references

- [x] Surfaces that should link to corrected content are updated in the same sprint (README plan-template list, integrating-external-agents → project_config cross-link).
- [x] No surface is invalidated/removed by this work (no deletions).
- [x] `CLAUDE.md` impact assessed → none required.

## Anti-patterns (must be absent)

- [x] No "TBD"/"TODO" in shipped pages.
- [x] No mixed audiences interleaved in one page.
- [x] No single-page dump / wrong split — page tree unchanged.
- [x] No prose restating the schema where a link/render would do — config facts cite `src/config.yaml`.

## External references validated

- [x] Plugin version (0.1.5), CLI subcommands, agent roster, config keys, plan-template names all cross-checked against source during grooming; developer re-verifies each at write time per task DoDs.
- [x] All cross-links must resolve from the rendered site (`--strict` enforces).
