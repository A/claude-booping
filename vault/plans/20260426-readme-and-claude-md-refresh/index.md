---
title: README & CLAUDE.md Refresh
type: refactoring
status: done
sp: 7
split_from: null
created: 2026-04-26 00:00
planned: 20260426 13:31
started: 20260426 13:46
completed: 2026-04-26 18:48
retro: skipped
goal: skipped
summary: "Rewrite README value-first with an Obsidian vault screenshot and full doc sections; fix CLAUDE.md partials-count drift"
---

# README & CLAUDE.md Refresh

## Context

The plugin's template-pipeline migration is effectively complete (only `/chat` still hand-authored — pending). README.md and CLAUDE.md predate the pipeline and don't yet:

- Lead with a clear value proposition for first-time visitors.
- Show what artifacts look like (the Obsidian-ready vault is a real differentiator and currently invisible in docs).
- Document the lifecycle (statuses), sprint/SP concept, extensibility surfaces (`_booping/`, `plan_templates/`, `lessons/`), and the learning loop.
- Name dependencies (Claude Code host, `uv` for inline scripts, optional `GEMINI_API_KEY` for cross-validation).

CLAUDE.md additionally has drift: it claims four surviving `partial_*.md` files but `docs/` actually has six.

After this lands, README.md is the single entry point a first-time visitor or returning collaborator can read end-to-end, and CLAUDE.md accurately describes the current plugin shape.

## Decisions

- **README structure** — value-first hook, then Obsidian screenshot, then progressively-disclosed reference docs in the order the user requested: Installation → Quick start → Workflow → Statuses → Sprints & SPs → Extensibility → Learning → Dependencies → License. Use cases section preserved (trimmed) after Workflow. Source: 2026 README best practices ([makeareadme.com](https://www.makeareadme.com/), [DEV: 2026 README guide](https://dev.to/iris1031/github-readme-template-the-complete-2026-guide-to-get-more-stars-3ck2)) — lead with the "why", keep copy-paste-ready commands, progressively disclose detail. Long is better than short for reference docs.
- **Obsidian-ready vault** — promoted to a named feature in README, illustrated by a screenshot of the vault opened in Obsidian. Frontmatter renders as Properties; all-markdown means graph view + backlinks work; one vault per project, no proprietary database. Also added as a one-liner in CLAUDE.md's "Project vault layout" section.
- **CLAUDE.md scope** — targeted refresh: replace dated "Status (April 2026)" header with stable "Status" + `Last updated:` line; fix the partials-list drift (state the actual six files); add an Obsidian-vault one-liner; add a one-line guardrail noting README's status overview is hand-maintained and must be revisited on config changes. Leave the "Migrating an old skill to template pipeline" playbook intact since `/chat` migration is still pending. We are explicitly **not** running a global four-check pass on the rest of CLAUDE.md — those sections were last touched as part of recent migration plans; if a hygiene gap surfaces during review, file it as a follow-up plan.
- **Image storage** — `docs/images/vault-in-obsidian.webp`, committed to the repo. README references it relatively. No CDN dependency.
- **Drift mitigation (status section duplication)** — README's Statuses section will be a **narrative summary**, not a high-fidelity transitions table: each status as a one-line bullet, terminal markers, and a one-line caption naming `src/config.yaml` `plan.statuses` as the canonical contract. This contains drift surface area while still giving first-time readers the gist. CLAUDE.md gets a one-line guardrail recording that this overview is hand-maintained.
- **Reshape pause as final milestone** — README is prose-heavy. M3 hands the rendered files back to the user before the plan transitions out, so any IA wrinkles get caught while the plan is still active rather than during retro.

## Architecture

Two artifacts, both at the repo root: `README.md`, `CLAUDE.md`. One supporting asset: `docs/images/vault-in-obsidian.webp`. No skill or config changes; no rendering pipeline involved (these are hand-authored docs that sit *outside* `src/templates/`).

The README references content that is itself rendered (e.g. it can quote `bin/booping-workflow` output once for illustration), but does not consume `src/config.yaml` directly — keeping it stable when config evolves.

## Milestones

### M1: README rewrite — 4 SP | done

**Goal**: README.md is restructured to value-first + Obsidian feature beat + the seven user-requested doc sections. Image asset committed.

**Verify**: open README.md in a markdown previewer; image renders; every section header in this milestone's plan exists; copy-paste the install commands and confirm they parse.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Convert and stage Obsidian screenshot at `docs/images/vault-in-obsidian.webp`. Source: `~/.claude/image-cache/8fbfcd3b-970a-4e13-b085-6fe5090b5ce2/2.png` (PNG, 2575×1492, ~1.18 MB). Target: WebP, max width 1600 px (height auto, preserve aspect), quality ~82, no metadata. If the source path no longer exists, halt and ask the user to re-share. | `docs/images/vault-in-obsidian.webp` | 1 | done |
| 1.2 | Rewrite README.md: value hook → screenshot → Obsidian-ready feature beat → Installation → Quick start → Workflow → Use cases (trimmed) → Statuses → Sprints & SPs → Extensibility → Learning → Dependencies → License | `README.md` | 3 | done |

#### Task 1.1 DoD

- [x] `mkdir -p docs/images` run; directory exists in the repo.
- [x] File present at `docs/images/vault-in-obsidian.webp` — WebP format, max width 1600 px, aspect ratio preserved, quality ~82, no embedded metadata. Recommended command: `magick ~/.claude/image-cache/8fbfcd3b-970a-4e13-b085-6fe5090b5ce2/2.png -resize '1600x>' -quality 82 -strip docs/images/vault-in-obsidian.webp` (any equivalent tool acceptable as long as the constraints hold).
- [x] Output file size is at least 50% smaller than the source PNG (target band: 150–400 KB; flag if outside). _Actual: ~73 KB (94% reduction). Below band — expected for flat-UI screenshots under WebP VP8; visual quality at q82 fine; accepted._
- [x] `file docs/images/vault-in-obsidian.webp` reports a valid RIFF/WebP image.
- [x] If source path is missing at execution time, the agent halts and surfaces the absence to the user — does not invent a placeholder, does not skip the embed.
- [x] File is staged in git (not just present on disk).

#### Task 1.2 DoD

- [x] **Value hook**: 1 short paragraph above the fold answers "what does booping do, why should I care", names the workflow loop (groom → develop → retro → learn), and names the artifact location (`~/Claude/{project}/`).
- [x] **Screenshot embed**: `![Vault open in Obsidian](docs/images/vault-in-obsidian.webp)` placed immediately after the value paragraph, before any docs sections, with a one-line caption explaining what the reader is seeing.
- [x] **Obsidian-ready feature beat**: section (or callout) explicitly stating the vault is markdown-only with YAML frontmatter that Obsidian renders as Properties; one vault per project under `~/Claude/{project}/`; works alongside the user's other notes; no proprietary database.
- [x] **Installation** section: dev mode (`claude --plugin-dir`), marketplace, git URL — copy-paste-ready blocks; `/install` post-install step explained.
- [x] **Quick start** section: minimal walkthrough showing **exactly these five commands** with the argument forms a user actually types: `/install` (no args, run inside the target repo); `/groom <free-text feature description>`; `/develop` (no args — auto-claims the next `ready-for-dev` plan; alternatively `/develop <plan-path>` to target a specific plan); `/retro <plan-path>`; `/learn <retro-path>`. Plan-path form: `~/Claude/{project}/plans/YYYYMMDD-{kebab-title}.md`. Retro-path form: `~/Claude/{project}/retrospectives/YYYYMMDD-{kebab-title}.md`.
- [x] **Workflow** section: short narrative + diagram of the loop (groom → develop → retro → learn) and which skill owns which arrows; reuses the same status vocabulary as `src/config.yaml` `plan.statuses`.
- [x] **Use cases** section: trimmed version of the current README's six patterns (multi-week feature programs, tech-debt campaigns, business-goal divergence, small unblocker sprints, cross-repo coordination, solo engineering with Claude Code). Keep the patterns; cut prose by ~30–50%.
- [x] **Statuses** section: **narrative summary** — bullet list, one line per status (`backlog`, `in-spec`, `awaiting-plan-review`, `ready-for-dev`, `in-progress`, `awaiting-retro`, `awaiting-learning`, `done`, `cancelled`, `fail`), terminal states marked. **Not** a full transitions/gates/on_exit table. Last sentence of the section names `src/config.yaml` `plan.statuses` as the canonical contract for transitions and gates, and points readers there for the full spec.
- [x] **Sprints & SPs** section: explains SP measures complexity + review burden (not effort/time), shows the 1–5 scale, names the 35-SP split threshold, explicitly says "not a velocity, no fixed cadence."
- [x] **Extensibility** section: per-project `_booping/skill_<name>.md` and `_booping/agent_<name>.md` overrides, project-local `plan_templates/*.md`, project-local `lessons/`, project's own `CLAUDE.md`. Names the future per-project `src/config.yaml` override path as planned.
- [x] **Learning** section: how `/retro` → `/learn` turns a sprint into rules that bind future grooming and execution. Names `lessons/{N}_{title}.md` shape.
- [x] **Dependencies** section: required = Claude Code host, `uv` (inline scripts auto-resolve their own deps — `jinja2`, `pyyaml`, `watchfiles`, `google-genai`), `git` (vault commits). Optional = `GEMINI_API_KEY` env var for `/groom` cross-validation via `bin/booping-external-llm-call`.
- [x] **License** line preserved. _Existing LICENSE (MIT) file present at repo root; added "MIT — see [LICENSE](LICENSE)" line — points at existing file rather than inventing._
- [x] No section restates a wholly synthetic future capability — only what's shipped or is explicitly listed in CLAUDE.md as planned.
- [x] All internal links resolve (`docs/images/vault-in-obsidian.webp`, any references to `~/Claude/{project}/` paths consistent with CLAUDE.md).

---

### M2: CLAUDE.md status & drift refresh — 2 SP | done

**Goal**: CLAUDE.md accurately describes the plugin's current shape (template pipeline live + `/chat` migration pending), fixes the partials-list count, and acknowledges the Obsidian-ready vault.

**Verify**: re-read CLAUDE.md top-to-bottom; status block reads stable rather than mid-migration; partial count matches `ls docs/partial_*.md | wc -l`; Obsidian one-liner present in vault layout section.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Replace dated "Status (April 2026)" header with stable "Status" + a `Last updated: 2026-04-26` line; reword bullets so they describe current state, not in-progress migration | `CLAUDE.md` | 1 | done |
| 2.2 | Fix partials-list drift (state the six actual files); add Obsidian-vault one-liner under "Project vault layout"; add a one-line guardrail noting README's status overview is hand-maintained and must be revisited on `src/config.yaml` `plan.statuses` changes | `CLAUDE.md` | 1 | done |

#### Task 2.1 DoD

- [x] Section header renamed from `## Status (April 2026)` to `## Status`.
- [x] Immediately under the new header, a single line: `_Last updated: 2026-04-26._` (italicized).
- [x] Existing bullets reworded to describe what *is* (e.g. "Template pipeline drives `/groom`, `/develop`, `/retro`, `/learn`"); do not reword the bullet about `/chat` — keep "Only `/chat` still authors its `SKILL.md` by hand" as factually accurate.
- [x] First-line framing of the section ("Migrating to a template-driven skill pipeline. State of play:") replaced with a current-state framing (e.g. "Template-driven skill pipeline is live. Current state:").
- [x] No factual changes to template pipeline or CLI inventory bullets.

#### Task 2.2 DoD

- [x] Layout section's `docs/partial_*.md` line is replaced with an enumeration of the six actual files: `partial_agents_researchers_delegator.md`, `partial_agents_researchers_strategy_senior_middle_junior.md`, `partial_cross_validation.md`, `partial_plan_statuses.md`, `partial_project_resolution.md`, `partial_read_lessons.md`. Note which are consumed by `/chat` vs. which are referenced from rendered skill transitions (`partial_cross_validation.md` is referenced from `groom` transitions).
- [x] One-line addition under "Project vault layout (`~/Claude/{project}/`)" naming the vault as Obsidian-ready (markdown + YAML frontmatter as Properties, no proprietary DB).
- [x] One-line guardrail added (anywhere sensible — recommended at the bottom of "Project vault layout" or "Editing conventions"): README.md's status overview is hand-maintained and must be revisited when `src/config.yaml` `plan.statuses` changes.
- [x] No other structural edits; "Migrating an old skill to template pipeline" playbook intact.

---

### M3: Reshape pause-for-review — 1 SP | done

**Goal**: Hand the rendered README.md and CLAUDE.md back to the user before the plan transitions out, so prose-shape / IA issues get caught while the plan is still active.

**Verify**: user has explicitly approved the rendered text. If they request changes, return to M1/M2 within this plan rather than deferring.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Pause: present rendered README.md + CLAUDE.md to the user; collect any reshape feedback; apply edits in-place; re-present until approved | `README.md`, `CLAUDE.md` | 1 | done |

#### Task 3.1 DoD

- [x] User has been shown the final rendered files (or pointed at them) and given a clear "any reshape needed?" prompt.
- [x] Any feedback applied as in-place edits to `README.md` / `CLAUDE.md` — no follow-up plan, no `awaiting-retro` carryover. _Two reshape passes applied during M3: (a) Information ownership + Information hierarchy in CLAUDE.md, value-hook tweak in README; (b) trim/restructure pass per user feedback — graph-view/`.booping`/CLAUDE.md-stub mentions removed, relative paths in Quick start, Use cases section deleted, Sprints & SPs reframed, Dependencies moved to top with macOS/Linux installs, Extensibility cleaned of vault-side CLAUDE.md and speculative config-override line, Learning expanded to mention `_booping/` extensions, value hook gained Gemini cross-validation phrase. CLAUDE.md gained a parallel correction: the project's CLAUDE.md is in the repo, not the vault._
- [x] User approval explicit ("looks good", "ship it", or equivalent). Silence does not count. _User: "looks good, commit and push" (2026-04-26 18:48)._

---

## Final Verification

- [x] `README.md` renders cleanly in a markdown viewer; image embeds; all sections from M1 DoD present. _Note: M3 reshape removed the Use cases section by user request and reordered Dependencies to the top — both are intentional supersedings of M1 DoD bullets, not regressions._
- [x] `CLAUDE.md` renders cleanly; partial count matches reality; status block reads stable.
- [x] `git status` shows only `README.md`, `CLAUDE.md`, `docs/images/vault-in-obsidian.webp` as changes (plus the plan file in the vault repo).
- [x] No skill, agent, config, or template files modified. _`just build` clean — no rendered output drift._
- [x] User has explicitly approved final text (M3).

## Risk register

- **Architectural blind spot — README ↔ config drift (advisory, accepted)**: Gemini cross-validation flagged that README's Statuses section will silently drift from `src/config.yaml` `plan.statuses` because no CI / render gate enforces parity. **Mitigation**: README's Statuses section is reduced to a narrative summary (one line per status) rather than a high-fidelity transitions table — drift surface area is small (status name + 1-line description). CLAUDE.md gains an explicit guardrail bullet pointing this out so future config changes prompt a README revisit. **Residual risk**: status names or descriptions can still drift between config edits and README revisits. Acceptable for now; if this becomes a real maintenance burden, the follow-up is to render the README's overview from config via `bin/booping-build` (out of scope here).

## Out of scope

- `/chat` migration (acknowledged pending; do not touch).
- Any skill, agent, or config edits.
- `docs/partial_*.md` cleanup (waits on `/chat` migration per existing CLAUDE.md plan).
- New plan templates or vault structure changes.
- A CONTRIBUTING.md, CODE_OF_CONDUCT.md, or changelog (not requested; would expand scope).
- Badges (status, CI, license) — not requested.

## CLAUDE.md impact

Owned by M2.

---

# Quality Checklist

## Frontmatter

- [x] Frontmatter matches the plan-frontmatter template.
- [x] `sp` (7) equals the sum of per-task SP across milestones (1+3+1+1+1 = 7).

## Content

- [x] Context names the user-visible behavior change (README is now value-first; CLAUDE.md is drift-free) — not "refactor docs internals."
- [x] DoD bullets are verifiable by reading the rendered output or running `ls` / `git status`.
- [x] Every task lists exact file paths.
- [x] Every task DoD uses checkboxes.
- [x] Every milestone has a Verify step.
- [x] Each milestone executable from a fresh session with only the plan as context.

## Skill-design hygiene

This plan does not modify skills, partials, or config — the skill-design hygiene checks (config vs prose, partials, lazy-loads) do not apply. The `claude-skill` template was used for shape only; no `src/templates/` or `src/config.yaml` files are touched.

## Four-check pass (information-architecture)

Per lesson [0004](../lessons/0004_information-architecture-pattern.md), every prompt-bearing artefact gets a four-check pass. README.md and CLAUDE.md are both prompt-bearing (CLAUDE.md is loaded into every session in this repo; README.md is occasionally loaded by Claude when answering project questions). The pass is **scoped to the blocks this plan touches**:

- **README.md (whole file)** — full pass on the rewritten body.
- **CLAUDE.md** — pass on the Status block, the partials-list line in Layout, and the new vault-layout / guardrail bullets only. Other CLAUDE.md sections are out of scope; if an unrelated hygiene gap surfaces during M3 review, file as a follow-up plan.
- [x] **Scoping**: every block in scope serves either README's first-time-reader role or CLAUDE.md's in-session-context role. No block is residue from a past correction.
- [x] **Duplication**: README's Statuses section is a *narrative* summary, not a duplicate of `src/config.yaml`'s transitions table. CLAUDE.md adds a guardrail line so future config changes prompt a README revisit.
- [x] **Configurability**: nothing in this plan adds a hardcoded value the user might want to tune.
- [x] **Hierarchy**: README sits at "what + why" level (first-time readers); CLAUDE.md sits at "how" level (Claude-in-session); neither carries the other's depth.

## Anti-patterns (must be absent)

- [x] No "TBD", "TODO", "implement later".
- [x] No task spanning unrelated concerns (each task is one file or one tightly-scoped section).
- [x] README's Statuses section is a narrative summary, not a high-fidelity duplicate of the config-driven transitions table.
- [x] No stale state names — uses the current `backlog → in-spec → ... → done` lifecycle.

## External references validated

- [x] Image source path (`~/.claude/image-cache/.../2.png`) confirmed present.
- [x] Output image path (`docs/images/vault-in-obsidian.webp`) is repo-relative.
- [x] All section names mirror current vocabulary in `src/config.yaml` (statuses, SP scale, skills).
- [x] Web research sources captured in Decisions.

## CLAUDE.md impact

- [x] CLAUDE.md changes are owned by M2; no schema or partial-API changes elsewhere that require a CLAUDE.md edit.
