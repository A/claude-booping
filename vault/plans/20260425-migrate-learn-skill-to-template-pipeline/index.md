---
title: Migrate /learn skill to template pipeline
type: refactoring
status: done
sp: 6
split_from: null
created: 2026-04-25 00:00
planned: 20260426 00:35
started: 20260426 00:41
completed: 2026-04-26 00:56
retro: skipped
goal: skipped
summary: "Migrate /learn to template pipeline: reshaped routing matrix, prose-read lessons (not eager), new debug-mode CLI"
---

# Migrate /learn skill to template pipeline

## Context

`/groom`, `/develop`, and `/retro` are now generated from `src/templates/skills/*.md.j2` against `src/config.yaml`. Their bodies use `{% include "_partials/_project_context.j2" %}`, `{{ plan_transitions.render(<skill>) }}`, `{{ available_agents.render(<skill>) }}`, and inline `!`bin/booping-lessons`` / `!`bin/booping-extra-instructions skill_<name>.md`` so lessons and project overrides arrive at load time without preflight reads.

`/learn` is still hand-authored at `skills/learn/SKILL.md`. Its Preflight loads nine items via markdown links to seven `docs/partial_*.md` / `docs/template_*.md` files. Six of those seven files are exclusive to `/learn` (consumers: itself + each other) and are deletable once the rendered SKILL stops referencing them. The seventh — `partial_read_lessons.md` — has a second consumer (`/chat`, also unmigrated) so it stays.

The `awaiting-learning → done` transition is already in `src/config.yaml` under `plan.statuses.awaiting-learning`, owned by `learn` — the data side of the contract is intact; only the skill body needs to be regenerated against it.

After this plan, `skills/learn/SKILL.md` is a generated artifact rendered from `src/templates/skills/learn.md.j2`. Its Preflight section disappears entirely, replaced by:

- `{% include "_partials/_project_context.j2" %}` for project context.
- `{{ plan_transitions.render("learn") }}` for the single owned transition.
- `{{ available_agents.render("learn") }}` — invoked for shape consistency with sibling skills, but renders empty (no agents in `config.skills.learn`); the `_available_agents.j2` macro is updated to short-circuit when the agents map is missing or empty.
- `{% include "_partials/_learn_targets.j2" %}` for the routing matrix — reshaped around four named targets with validated example filenames the skill can use to infer exact write paths.
- `!`bin/booping-debug-mode learn`` — a new bin command that prints the debug-mode message (with the absolute plugin path filled in) when `<plugin>/skills/learn/.debug_enabled` exists, and prints nothing otherwise. No lazy-load file; no `test -f` guard in body; no matrix-extension types.
- Lazy `[review table format](../../docs/learn_review_table.md)` link inside Phase 2 where it is consumed. The doc is generated from `src/templates/docs/learn_review_table.md.j2` (so `src/` holds only templates; `docs/` holds rendered output).
- Eager `{% include "_partials/_lesson_template.j2" %}` inside Phase 3 — the lesson body shape must be in context at write time, so it is hard-wired via partial rather than lazy-linked.

Lessons (`~/Claude/{project}/lessons/*.md`), project-local extra instructions (`~/Claude/{project}/_booping/skill_learn.md`), and the repo `CLAUDE.md` are **read by prose instruction inside Phase 1.5** (the update-vs-create sweep), not pre-loaded at skill-load time via `!`commands``. Two reasons: (1) /learn is the skill that *produces* lessons — eagerly loading them at the top of body would put them in context **before** Phase 1's candidate extraction, biasing extraction toward existing rules; (2) extra instructions for /learn naturally apply during the same sweep, so reading them at the same time keeps the targets co-located in the prose. The skill body instructs the orchestrator to read these files when the sweep begins; no `!`bin/booping-lessons`` line, no `!`bin/booping-extra-instructions skill_learn.md`` line. This is a deliberate exception to the load-time pattern used by `/groom`, `/develop`, `/retro` — those skills *consume* lessons; `/learn` *writes* them.

## Decisions

- **Routing matrix reshape**: drop the legacy `Type | Holds | Picked when` matrix in favor of `Target | When to use | Lands at | Examples`. Four base targets:
  - **Lesson** (`lessons/{N}_<kebab>.md`) — cross-framework principle reaching every skill (e.g. "Challenge code design by SOLID principles", "Use AAA in test cases", "Design skill template partials by information hierarchy").
  - **Skill extra instructions** (`_booping/skill_<skill>.md`) — tweak/extend a single skill's method (e.g. `skill_groom.md`: "plan CLAUDE.md changes ahead within plan scope"). Skill-name examples: `skill_groom.md`, `skill_develop.md`, `skill_retro.md`, `skill_learn.md`, `skill_chat.md`, `skill_install.md`, `skill_help.md`.
  - **Agent extra instructions** (`_booping/agent_<full-agent-name>.md`) — hook a single agent's behavior (e.g. `agent_booping-developer-middle.md`: "always run tests before reporting done"; `agent_booping-researcher.md`: "search only on reddit"). Agent-name examples: `agent_booping-researcher.md`, `agent_booping-developer-middle.md`, `agent_booping-developer-senior.md`. **Note**: agent extension filenames carry the full agent name including the `booping-` prefix — this is what `bin/booping-extra-instructions` reads from each agent's body. A shorter naming convention is out of scope for this migration.
  - **Repository CLAUDE.md** (`<repo>/CLAUDE.md`) — project-fact aiding fresh-agent project understanding (layout, command, convention).
  Decomposition rule preserved (one rule = one target). The matrix names categories with examples; the skill infers the exact filename per candidate.

- **Routing matrix lives in `_partials/_learn_targets.j2` (Jinja include), not in `src/config.yaml`**: the matrix is consulted on every successful `/learn` run, so it must be present in the body without forcing a tool call. Putting it in config would force structured data into the schema for a single consumer with prose-y `When to use` / `Lands at` / `Examples` cells. Static partial is the cleanest fit and matches CLAUDE.md's "Hard-wire with j2 partials: use `{% include %}` for content that *must* be present every invocation" rule. **Skill/agent example lists are hand-authored** in the partial; updating the partial when a new skill/agent is added is a one-line edit. (Generating these dynamically from config is plausible but speculative — defer until a second skill needs the same enumeration.)

- **Review-table format lazy-loads from Phase 2 via a generated doc**: the column shape, accept-all syntax, and split-rule are reference material the model needs only when rendering the review table once per run. Move the body of `docs/template_learn_review_table.md` to a new template `src/templates/docs/learn_review_table.md.j2` (rendered to `docs/learn_review_table.md` by `bin/booping-build`); link from Phase 2 as `[review table format](../../docs/learn_review_table.md)`. **`src/` holds only templates** — generated reference docs land in `docs/`; the previous draft's `src/docs/learn_review_table.md` would have put hand-authored content under `src/`, breaking that boundary.

- **Lesson body shape includes eagerly inside Phase 3 via a partial**: `docs/template_lesson.md`'s frontmatter + Rule/Example shape is consumed every time Phase 3 writes a lesson, and is small. The body must be in context at the moment of writing — a lazy link risks the model writing without re-fetching. Move the body to `src/templates/_partials/_lesson_template.j2` and `{% include %}` it inside Phase 3. No corresponding rendered `docs/` file: the partial is hard-wired into the skill body, so there is no separate-file consumer that needs a stable URL. Hard rules (c) and (h) (which currently link to `template_lesson.md`) reword to "see the lesson body shape included in Phase 3 above" — no link.

- **Debug mode is a single inline `!`command``** — drop the matrix-extension approach entirely (no `plugin-skill` / `plugin-agent` / `plugin-partial` types, no `learn_debug_extras.md` lazy-load, no `## Debug guard` prose section, no `test -f` guard inlined into body). Replace with a new CLI `bin/booping-debug-mode <skill>` that resolves the plugin root from its own location and prints either the message with the absolute template path filled in, or nothing. Inlined into body via `!`bin/booping-debug-mode learn``.

  Output when enabled (single paragraph, exact wording):

  > Debug mode enabled. You can update this skill at `<absolute-plugin-root>/src/templates/skills/learn.md.j2`. If the issue is generic enough to fix on the framework level, review the skill code and suggest changes to the user.

  Empty output when disabled. Toggle file stays at `<plugin>/skills/learn/.debug_enabled`, gitignored. The bin command (not the skill body) is the single source of truth for debug behavior.

- **`_available_agents.j2` macro handles empty/missing agents**: update the macro to short-circuit and render nothing when `config.skills[skill].agents` is missing or empty. Keep `{{ available_agents.render("learn") }}` invoked in the learn template for shape consistency with sibling skills. `config.skills.learn` carries no `agents` map; the rendered body has no "Available Agents" section. Other generated skills are unaffected (their agents maps are non-empty).

- **Lessons + extra instructions read by prose instruction inside Phase 1.5, not via `!`commands`` at skill load**: `/learn` is the skill that *produces* lessons. Eagerly loading the existing set via `!`bin/booping-lessons`` at top-of-body would put existing rules in context **before** Phase 1's candidate extraction, biasing extraction toward what already exists. Project-local extra instructions (`_booping/skill_learn.md`) follow the same logic — they tune /learn's method, so they only need to be in context once the orchestrator is doing the sweep. Replace both eager `!`commands`` with prose instruction inside Phase 1.5: at the start of the sweep, the orchestrator reads `~/Claude/{project}/lessons/*.md`, `~/Claude/{project}/_booping/skill_learn.md` (if present), and the repo `CLAUDE.md`. This is a deliberate exception to the load-time pattern used by sibling skills — `/groom`, `/develop`, `/retro` *consume* lessons (eager load is correct); `/learn` *writes* them (prose-driven read is correct). The behavior of the empty-vault / missing-file cases stays the same: prose instructs the orchestrator to skip silently when a target is empty or absent.

- **Drop the explicit "Read attached repo's `CLAUDE.md`" Preflight bullet**: neither `/groom`, `/develop`, nor `/retro` carries it. Phase 1.5 prose explicitly names the repo `CLAUDE.md` as one of the sweep targets — that consumer is preserved; the duplicative Preflight pre-load is dropped.

- **Drop the duplicative `partial_plan_statuses.md` Preflight bullet**: the rendered transitions table from `plan_transitions.render("learn")` carries the single owned status (`awaiting-learning`). A separate plan-statuses preload was redundant when /retro migrated and is redundant here.

- **Keep all phase content verbatim except the surgical swaps named in M2's task DoD**: Phases 0–5, "Single-location rule", and "What learn does NOT do" stay byte-identical post-migration. Reason: this is a shape migration, not a behavior change; minimizing prose drift makes the regenerated diff readable.

- **Drop Hard rules (e) and (f)**: rules (e) ("matrix lives in `partial_learn_targets`, do not inline") and (f) ("review-table column docs live in `template_learn_review_table`, do not inline") are template-edit-time invariants, not runtime guidance for the /learn agent. With the template pipeline, the SKILL.md is generated; structural enforcement of "no parallel matrix in body prose" comes from the Jinja partial / lazy-load layer, not from runtime prose rules. Remaining hard rules (a)–(d), (g), (h) describe runtime behavior the agent must honor and stay verbatim. Lesson 0004 four-check pass on the carried-over hard rules confirms (e)/(f) fail the **scoping** check.

- **Drop the "Does not delegate candidate classification to role agents — those agents have been deleted" bullet from "What learn does NOT do"**: this bullet is residue from the previous /learn refactor (it referenced the now-deleted booping-techlead/PM/QA agents). Its intent — "orchestrator owns extraction" — is positively expressed in Hard rule (a), so the negative is duplicative. Lesson 0004 four-check pass: fails **scoping** (residue from past correction) and **duplication** (covered by hard rule (a)). The remaining three bullets in "What learn does NOT do" pair negatives with positive direction and stay verbatim. **The plan pre-decides this drop here so M2 transcription is purely mechanical**; the executing agent does not run a 4-check pass dynamically.

- **Phase 1.5 sweep prose updated to consolidate the read targets**: the existing Phase 1.5 prose says `ls ~/Claude/{project_name}/lessons/` followed by per-candidate filtered reads of `_booping/` and the repo `CLAUDE.md`. Replace step 1 with prose: at the start of Phase 1.5, read every file under `~/Claude/{project_name}/lessons/` (skip silently if the directory is empty), `~/Claude/{project_name}/_booping/skill_learn.md` (skip silently if absent), and the attached repo's `CLAUDE.md` (skip silently if absent). These are the lookup set for the dup-check sweep. The remaining Phase 1.5 prose (per-candidate filtering, sweep verdict) stays verbatim. This is the only Phase-content edit beyond the lazy-link / eager-include swaps.

## Architecture

Load-time inputs for the rendered `skills/learn/SKILL.md`:

```
/learn invocation
  ↓ {% include "_partials/_project_context.j2" %}      → !`bin/booping-project-name`
  ↓ {{ plan_transitions.render("learn") }}             → awaiting-learning row from config.plan.statuses
  ↓ {{ available_agents.render("learn") }}             → empty (macro short-circuits on missing agents map)
  ↓ {% include "_partials/_learn_targets.j2" %}        → 4-target routing matrix (target / when / lands at / examples)
  ↓ !`bin/booping-debug-mode learn`                    → debug message with absolute template path, or empty
  ↓ Phase 0..5 (verbatim from current SKILL body, with the swaps named below)
  ↓   Phase 1.5 first action: prose-driven reads of   → lessons/, _booping/skill_learn.md, repo CLAUDE.md
  ↓                            the lookup set
  ↓   Phase 2 lazy-loads [review table format](../../docs/learn_review_table.md)
  ↓   Phase 3 eager-includes {% include "_partials/_lesson_template.j2" %}
  ↓ ## Single-location rule, ## Hard rules, ## What learn does NOT do (verbatim with documented drops)
```

Skill/agent boundary unchanged: orchestrator owns all reads/writes; no agent delegation from `/learn`. Vault commits stay scoped via `cd ~/Claude/{project}` per Phase 5. Debug-mode behavior simplifies to "if the bin command emits the message, the user is editing the framework — surface it; else proceed normally." No `!`bin/booping-lessons`` or `!`bin/booping-extra-instructions skill_learn.md`` line in the body — those reads are prose-driven inside Phase 1.5 (see Decisions).

Six `docs/` files lose their last consumer once M2 rebuilds and are pruned in M3:

| File | Replacement | Sole consumer? |
|------|-------------|----------------|
| `docs/partial_plan_transitions_learn.md` | `plan_transitions.render("learn")` macro | yes |
| `docs/partial_learn_targets.md` | `_partials/_learn_targets.j2` partial (reshaped) | consumers: /learn + partial_debug_learn (also pruned) |
| `docs/partial_debug_delegator.md` | replaced by `bin/booping-debug-mode` | yes |
| `docs/partial_debug_learn.md` | replaced by `bin/booping-debug-mode` (no separate file) | consumers: /learn + partial_debug_delegator (also pruned) |
| `docs/template_learn_review_table.md` | `docs/learn_review_table.md` (rendered from `src/templates/docs/learn_review_table.md.j2`) — lazy-loaded from Phase 2 | consumers: /learn + partial_learn_targets (also pruned) |
| `docs/template_lesson.md` | `src/templates/_partials/_lesson_template.j2` (eager `{% include %}` in Phase 3) | yes |

`docs/partial_read_lessons.md` is **not** pruned — `skills/chat/SKILL.md` is still hand-authored and references it.

## Milestones

### M1: Stage source files + bin command + macro tweak — 2 SP | done

**Goal**: New `src/` files exist for M2 to reference; the new `docs/learn_review_table.md` is generated by `bin/booping-build`; new `bin/booping-debug-mode` script is in place and executable; `_available_agents.j2` handles empty agents; `src/config.yaml` carries `skills.learn.effort`. Rendered skills (other than the new generated doc) are unchanged after this milestone (no template authored yet); the build runs cleanly.

**Verify**:

```bash
test -f /home/anton/Dev/@A/claude-booping/src/templates/_partials/_learn_targets.j2 \
  && test -f /home/anton/Dev/@A/claude-booping/src/templates/docs/learn_review_table.md.j2 \
  && test -f /home/anton/Dev/@A/claude-booping/src/templates/_partials/_lesson_template.j2 \
  && test -x /home/anton/Dev/@A/claude-booping/bin/booping-debug-mode \
  && echo OK source files
grep -E '^  learn:$' /home/anton/Dev/@A/claude-booping/src/config.yaml
/home/anton/Dev/@A/claude-booping/bin/booping-build && echo OK build
test -f /home/anton/Dev/@A/claude-booping/docs/learn_review_table.md \
  && echo OK generated review-table doc

# No regression on previously-rendered skills
git -C /home/anton/Dev/@A/claude-booping diff --quiet skills/groom/SKILL.md skills/develop/SKILL.md skills/retro/SKILL.md skills/learn/SKILL.md \
  && echo "OK no rendered-skill regression"

# Smoke-test the new bin command
( cd /home/anton/Dev/@A/claude-booping && rm -f skills/learn/.debug_enabled && OUT=$(./bin/booping-debug-mode learn) && [ -z "$OUT" ] && echo "OK debug off prints nothing" )
( cd /home/anton/Dev/@A/claude-booping && touch skills/learn/.debug_enabled && OUT=$(./bin/booping-debug-mode learn) && echo "$OUT" | grep -q "Debug mode enabled" && echo "$OUT" | grep -q "src/templates/skills/learn.md.j2" && rm skills/learn/.debug_enabled && echo "OK debug on prints message with absolute template path" )
```

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Add `skills.learn.effort: high` to the `skills:` map in `src/config.yaml` (alongside `develop`, `groom`, `retro`). No `agents:` map — /learn does not delegate. | `src/config.yaml` | 0 | done |
| 1.2 | Update `src/templates/_partials/_available_agents.j2` macro to short-circuit when `config.skills[skill].agents` is missing or empty (render nothing). Existing skills (`groom`, `develop`, `retro`) all carry non-empty agents maps, so their rendered output is unchanged. | `src/templates/_partials/_available_agents.j2` | 1 | done |
| 1.3 | Author `src/templates/_partials/_learn_targets.j2` — the reshaped routing matrix with four named targets, validated example filenames, decomposition rule. Static markdown; no Jinja control flow. | `src/templates/_partials/_learn_targets.j2` (new) | 0 | done |
| 1.4 | Author `src/templates/docs/learn_review_table.md.j2` — review-table column shape, user interaction conventions, split rule. Renders to `docs/learn_review_table.md` via `bin/booping-build`. Body transcribed from `docs/template_learn_review_table.md`. | `src/templates/docs/learn_review_table.md.j2` (new), `docs/learn_review_table.md` (generated) | 0 | done |
| 1.5 | Author `src/templates/_partials/_lesson_template.j2` — lesson frontmatter + Rule/Example body shape. Body transcribed from `docs/template_lesson.md`. Pure markdown (no Jinja control flow); will be `{% include %}`d by Phase 3 in the rendered learn skill. | `src/templates/_partials/_lesson_template.j2` (new) | 0 | done |
| 1.6 | Author `bin/booping-debug-mode` (`uv` inline script, executable). Resolves plugin root from `Path(__file__).resolve().parent.parent`. Prints the debug-mode message (with absolute template path filled in) when `<plugin-root>/skills/<skill>/.debug_enabled` exists; prints nothing otherwise. Sole CLI argument: the skill name. | `bin/booping-debug-mode` (new) | 1 | done |

(Tasks 1.1/1.3/1.4/1.5 are 0 SP each — mechanical config / partial / template authoring. Bundled into Task 1.2's briefing in practice but listed separately for DoD precision. Task 1.2 carries the macro change; Task 1.6 carries the new CLI script.)

#### Task 1.1 DoD

- [x] `skills.learn.effort: high` exists under `skills:` in `src/config.yaml`.
- [x] No `skills.learn.agents:` map (/learn has no delegations).
- [x] No other `skills.<name>` blocks edited.

#### Task 1.2 DoD

- [x] `src/templates/_partials/_available_agents.j2` macro short-circuits and renders empty when `config.skills[skill].get("agents", {})` is falsy.
- [x] When the agents map is non-empty, the macro renders the same output as before (the `## Available Agents` heading + per-agent blocks).
- [x] `bin/booping-build` exits 0; `git diff skills/groom/SKILL.md skills/develop/SKILL.md skills/retro/SKILL.md` is empty (no regression for skills with non-empty agents).
- [x] A dry-run with a stub config containing `skills.learn = {effort: high}` (no `agents` key) confirms `available_agents.render("learn")` returns empty without raising `StrictUndefined`.

#### Task 1.3 DoD

- [x] `src/templates/_partials/_learn_targets.j2` exists.
- [x] Opens with one short intro paragraph stating the matrix is the routing contract for /learn candidates and that every accepted learning lands in exactly one target.
- [x] Contains a four-row markdown table with columns `Target | When to use | Lands at | Examples`. Rows:
  - **Lesson** | "Cross-framework principle reaching every skill — design heuristic, test discipline, IA rule. Concrete, short, with one example." | `lessons/{N}_<kebab>.md` | "Challenge code design by SOLID principles", "Use AAA in test cases", "Design skill template partials by information hierarchy"
  - **Skill extra instructions** | "Tweak or extend a single skill's method (groom / develop / retro / learn / chat / install / help)." | `_booping/skill_<skill>.md` | `skill_groom.md`, `skill_develop.md`, `skill_retro.md`, `skill_learn.md`, `skill_chat.md`, `skill_install.md`, `skill_help.md`
  - **Agent extra instructions** | "Hook a single agent's behavior. Compact list." | `_booping/agent_<full-agent-name>.md` | `agent_booping-researcher.md`, `agent_booping-developer-middle.md`, `agent_booping-developer-senior.md`
  - **Repository CLAUDE.md** | "Project-fact aiding fresh-agent project understanding — layout path, CLI command, code-side convention. One-bullet additions; no paragraph rewrites." | `<repo>/CLAUDE.md` | (no example filenames — single canonical target)
- [x] Below the table: a short Decomposition rule paragraph ("If a candidate would otherwise span two targets, decompose into two distinct rows; never duplicate the same rule across targets.").
- [x] Below that: a short note that the skill **infers** the exact filename per candidate; the example lists are validation aids, not full enumerations.
- [x] Agent-extension example filenames carry the **full agent name** including the `booping-` prefix (e.g. `agent_booping-developer-middle.md`, NOT `agent_developer_middle.md`) — matches the path `bin/booping-extra-instructions` reads from each agent template.
- [x] No Jinja control flow ({% if %}, {% for %}, etc.) — pure markdown.
- [x] `bin/booping-build` parses the file (no `TemplateSyntaxError`).
- [x] Body ≤ ~50 lines.

#### Task 1.4 DoD

- [x] `src/templates/docs/learn_review_table.md.j2` exists.
- [x] Body covers: column shape (`# | Target | Type | Brief description`), per-column guidance, user interaction (`Accept all, or enter row numbers to reject (e.g. 2 5):`), accept-all default, user-added-row convention, multi-target split rule.
- [x] Content transcribed from `docs/template_learn_review_table.md` (the body content is unchanged; only the source location moves into the template tree).
- [x] No Jinja control flow ({% if %}, {% for %}, {{ var }}) — pure markdown wrapped in a `.j2` extension so `bin/booping-build` picks it up under `src/templates/docs/`. Placeholder-looking tokens (e.g. `{{One-sentence rule}}`) inside the body must be escaped (`{% raw %} ... {% endraw %}`) so the build doesn't try to render them.
- [x] After `bin/booping-build`, `docs/learn_review_table.md` exists and matches the template body byte-for-byte modulo `{% raw %}` unwrapping.

#### Task 1.5 DoD

- [x] `src/templates/_partials/_lesson_template.j2` exists.
- [x] Frontmatter block (id / title / retro / created) and body block (`**Rule**:` / `**Example**:`) transcribed verbatim from `docs/template_lesson.md`.
- [x] Placeholder syntax (`{{N}}`, `{{One-sentence rule...}}`, etc.) preserved verbatim — these are rendered by the orchestrator at lesson-write time, not by Jinja. Wrap the entire body in `{% raw %} ... {% endraw %}` so `bin/booping-build` does not attempt to render the placeholders.
- [x] No corresponding `docs/lesson_template.md` rendered file — this partial is `{% include %}`d directly into Phase 3 of the learn skill (eager hard-wire), not lazy-linked from a doc.

#### Task 1.6 DoD

- [x] `bin/booping-debug-mode` exists, is executable (`chmod +x`), and runs as a `uv` inline script (matches the shape of sibling `bin/` scripts).
- [x] Single CLI argument: skill name (e.g. `learn`). Resolves the plugin root from the script's own location (`Path(__file__).resolve().parent.parent`); never reads cwd, never accepts a path argument.
- [x] When `<plugin-root>/skills/<skill>/.debug_enabled` exists, prints exactly:

  ```
  Debug mode enabled. You can update this skill at <ABSOLUTE-PLUGIN-ROOT>/src/templates/skills/<skill>.md.j2. If the issue is generic enough to fix on the framework level, review the skill code and suggest changes to the user.
  ```

  with `<ABSOLUTE-PLUGIN-ROOT>` substituted to the resolved plugin root (no placeholder, no `~`). Trailing newline OK.
- [x] When the toggle file does not exist, prints nothing (empty stdout, exit 0).
- [x] When the skill name is unknown (no matching `skills/<skill>/` directory), prints nothing and exits 0 (silent no-op — the bin command's job is to surface debug state, not to validate skill existence).
- [x] Smoke-tested: with `.debug_enabled` absent → empty output; with `.debug_enabled` present → message includes `src/templates/skills/learn.md.j2` and the absolute plugin root (verified via `grep` against the plugin root path).

---

### M2: Render learn.md.j2 — 3 SP | done

**Goal**: `skills/learn/SKILL.md` becomes a generated artifact rendered from `src/templates/skills/learn.md.j2`. Preflight section gone; project context, transitions, agents-empty, matrix, and debug-mode CLI inline via the standard partials/CLI commands. Lessons + extra instructions + repo CLAUDE.md are read by prose instruction inside Phase 1.5 (no `!`bin/booping-lessons``, no `!`bin/booping-extra-instructions`` lines anywhere in the body). Phase 2 lazy-links the rendered review-table doc; Phase 3 eager-includes the lesson-template partial. Phases 0–5, "Single-location rule", "What learn does NOT do", and "Hard rules" preserved verbatim except for the documented drops and link/include swaps.

**Verify**:

```bash
/home/anton/Dev/@A/claude-booping/bin/booping-build && echo OK build
test -f /home/anton/Dev/@A/claude-booping/src/templates/skills/learn.md.j2 \
  && test -f /home/anton/Dev/@A/claude-booping/skills/learn/SKILL.md \
  && echo OK files

# Preflight section gone
grep -E '^## Preflight' /home/anton/Dev/@A/claude-booping/skills/learn/SKILL.md \
  && { echo "FAIL: Preflight section still present"; exit 1; } \
  || echo "OK no Preflight section"

# Standard pipeline blocks present
grep -qE '^## Project Context' /home/anton/Dev/@A/claude-booping/skills/learn/SKILL.md && echo OK project-context
grep -qE '^## Plan Transitions' /home/anton/Dev/@A/claude-booping/skills/learn/SKILL.md && echo OK transitions
grep -qE '^### `awaiting-learning`' /home/anton/Dev/@A/claude-booping/skills/learn/SKILL.md && echo OK status

# Available Agents heading is ABSENT (empty agents map → macro short-circuits)
grep -qE '^## Available Agents' /home/anton/Dev/@A/claude-booping/skills/learn/SKILL.md \
  && { echo "FAIL: Available Agents heading should be absent for /learn"; exit 1; } \
  || echo "OK Available Agents block empty"

# Matrix rendered with new column shape
grep -qE '\| Target \| When to use \| Lands at \| Examples \|' /home/anton/Dev/@A/claude-booping/skills/learn/SKILL.md && echo OK matrix-rendered

# Phase content preserved
for phase in 'Phase 0' 'Phase 1 ' 'Phase 1.5' 'Phase 2' 'Phase 3' 'Phase 4' 'Phase 5'; do
  grep -qE "^## $phase" /home/anton/Dev/@A/claude-booping/skills/learn/SKILL.md \
    && echo "OK $phase" \
    || { echo "FAIL: $phase missing"; exit 1; }
done

# Phase 2 lazy-link points at the GENERATED docs/ file, NOT src/docs/
grep -qE '\(\.\./\.\./docs/learn_review_table\.md\)' /home/anton/Dev/@A/claude-booping/skills/learn/SKILL.md && echo OK review-table-link
grep -qE 'src/docs/learn_review_table' /home/anton/Dev/@A/claude-booping/skills/learn/SKILL.md \
  && { echo "FAIL: review-table link still points at src/docs/"; exit 1; } \
  || echo "OK no src/docs/ ref for review-table"

# Phase 3 must contain the lesson-template body INLINE (eager include), not a lazy link
grep -qE 'src/docs/lesson_template|docs/lesson_template' /home/anton/Dev/@A/claude-booping/skills/learn/SKILL.md \
  && { echo "FAIL: lesson_template referenced as a doc — should be eager include"; exit 1; } \
  || echo "OK no lesson_template doc link"
# Markers from the included partial body must be present
grep -qE '\*\*Rule\*\*:' /home/anton/Dev/@A/claude-booping/skills/learn/SKILL.md && echo OK lesson-shape-included
grep -qE '\*\*Example\*\*:' /home/anton/Dev/@A/claude-booping/skills/learn/SKILL.md && echo OK lesson-example-included

# Debug mode is the inline CLI, not a lazy-load
grep -qE '^!`bin/booping-debug-mode learn`$' /home/anton/Dev/@A/claude-booping/skills/learn/SKILL.md && echo OK debug-mode-cli
grep -nE '^## Debug guard' /home/anton/Dev/@A/claude-booping/skills/learn/SKILL.md \
  && { echo "FAIL: ## Debug guard section should not exist"; exit 1; } \
  || echo "OK no Debug guard section"
grep -nE 'src/docs/learn_debug_extras.md|test -f.*\.debug_enabled' /home/anton/Dev/@A/claude-booping/skills/learn/SKILL.md \
  && { echo "FAIL: legacy debug guard tokens in body"; exit 1; } \
  || echo "OK no legacy debug guard tokens"

# Stale partial/template references gone
grep -nE 'partial_(plan_transitions_learn|learn_targets|debug_delegator|debug_learn|read_lessons|project_resolution|plan_statuses)|template_(learn_review_table|lesson)' \
  /home/anton/Dev/@A/claude-booping/skills/learn/SKILL.md \
  && { echo "FAIL: legacy partial/template ref in rendered skill"; exit 1; } \
  || echo "OK no legacy partial refs"

# `!`bin/booping-lessons`` MUST NOT appear anywhere in the rendered body — Phase 1.5 reads via prose
grep -nE '!`bin/booping-lessons`' /home/anton/Dev/@A/claude-booping/skills/learn/SKILL.md \
  && { echo "FAIL: !`bin/booping-lessons` should not appear in /learn body — reads are prose-driven in Phase 1.5"; exit 1; } \
  || echo "OK no !bin/booping-lessons line"

# `!`bin/booping-extra-instructions skill_learn.md`` MUST NOT appear — read in Phase 1.5 prose
grep -nE '!`bin/booping-extra-instructions' /home/anton/Dev/@A/claude-booping/skills/learn/SKILL.md \
  && { echo "FAIL: !`bin/booping-extra-instructions` should not appear in /learn body — read in Phase 1.5 prose"; exit 1; } \
  || echo "OK no !bin/booping-extra-instructions line"

# Phase 1.5 prose must explicitly name the three sweep targets
PHASE15_BODY=$(awk '/^## Phase 1\.5/,/^## Phase 2/' /home/anton/Dev/@A/claude-booping/skills/learn/SKILL.md)
echo "$PHASE15_BODY" | grep -q 'lessons/' && echo OK phase15-mentions-lessons
echo "$PHASE15_BODY" | grep -q '_booping/skill_learn' && echo OK phase15-mentions-extra-instructions
echo "$PHASE15_BODY" | grep -qE 'CLAUDE\.md' && echo OK phase15-mentions-repo-claudemd

# No placeholder leaks
grep -nE '\{\{|\{%' /home/anton/Dev/@A/claude-booping/skills/learn/SKILL.md \
  && { echo "FAIL: Jinja placeholder leak"; exit 1; } \
  || echo "OK no placeholder leak"

# Other generated skills unchanged
git -C /home/anton/Dev/@A/claude-booping diff --quiet skills/groom/SKILL.md skills/develop/SKILL.md skills/retro/SKILL.md \
  && echo "OK other rendered skills unchanged"
```

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Author `src/templates/skills/learn.md.j2` — frontmatter (templated `effort`), imports, partials/macros, debug-mode CLI line, Phase 0–5 + Single-location rule + Hard rules + NOT-do block transcribed from existing skill body with documented drops, lazy review-table link in Phase 2 (pointing at `../../docs/learn_review_table.md`), eager `{% include "_partials/_lesson_template.j2" %}` in Phase 3, Phase 1.5 first step replaced with prose instruction to read `lessons/`, `_booping/skill_learn.md`, and the repo `CLAUDE.md`. **No `!`bin/booping-lessons`` line, no `!`bin/booping-extra-instructions`` line anywhere in the body.** Run `bin/booping-build`; commit the rendered `skills/learn/SKILL.md` alongside the template. | `src/templates/skills/learn.md.j2` (new), `skills/learn/SKILL.md` (regenerated) | 3 | done |

#### Task 2.1 DoD

**Sequence (order matters — running `bin/booping-build` overwrites `skills/learn/SKILL.md`)**:

1. Read `skills/learn/SKILL.md` first and transcribe its `allowed-tools` list verbatim into the new template's frontmatter. Do this **before** any build command runs. The list includes the constrained Bash entries (`ls *`, `test *`, `git add *`, `git commit *`, `grep *`) and `Read`, `Write`, `Edit`, `Glob`, `Grep`, `AskUserQuestion`. Add `Bash(bin/booping-debug-mode:*)` and `Bash(bin/booping-project-name:*)` to allow the inline commands actually invoked from the body. **Do not add** `Bash(bin/booping-lessons:*)` or `Bash(bin/booping-extra-instructions:*)` — those CLIs are not invoked from /learn's body (Phase 1.5 reads the underlying files via prose instruction, using the existing `Read` and `ls *` permissions).
2. Transcribe Phase 0 through Phase 5 and the "Single-location rule" paragraph **verbatim** (no rewording, no sentence drops). For "What learn does NOT do", carry over the first three bullets verbatim and **drop the fourth bullet** (`Does not delegate candidate classification to role agents — those agents have been deleted`) entirely — pre-decided in Decisions; not a runtime 4-check pass. For "Hard rules", carry over rules (a), (b), (c), (d), (g), (h) verbatim and **drop rules (e) and (f)** entirely — pre-decided in Decisions; not a runtime 4-check pass. The only inline edits permitted inside the verbatim sections:
   - Phase 1.5 first step: replace ``1. `ls ~/Claude/{project_name}/lessons/` — enumerate existing lessons.`` with this paragraph (verbatim):

     > Read every lesson under `~/Claude/{project_name}/lessons/` (skip silently if the directory is empty), `~/Claude/{project_name}/_booping/skill_learn.md` (skip silently if absent), and the attached repo's `CLAUDE.md` (skip silently if absent). Together these are the lookup set for the dup-check sweep. Do not invoke `bin/booping-lessons` or `bin/booping-extra-instructions` here — read the files directly so the eager-load bias is avoided.

     Phase 1.5 step 2 ("enumerate `_booping/`") and step 3 ("read repo `CLAUDE.md`") **collapse into the new step 1** above; remove the standalone numbering for those two steps. The remaining steps (per-candidate filtering, sweep verdict) stay verbatim, renumbered.
   - Phase 2 first paragraph: replace `[template_learn_review_table](../../docs/template_learn_review_table.md)` reference with `[review table format](../../docs/learn_review_table.md)` — note the path points at the **rendered** doc under `docs/`, not `src/docs/`.
   - Phase 3 bullet listing path templates: replace `[template_lesson.md](../../docs/template_lesson.md)` with the literal Jinja line `{% include "_partials/_lesson_template.j2" %}` placed **inline at the point where the body shape is needed** (eager include, not a link). The surrounding sentence reframes from "follow the template at …" to "follow the lesson body shape inlined below:" so the next block is the included partial.
   - Hard rule (c) and (h): drop the `template_lesson.md` link entirely; reword the sentence to reference "the lesson body shape included in Phase 3 above" instead of a linked file.
   - Phase 5 first paragraph: replace `[partial_plan_transitions_learn](../../docs/partial_plan_transitions_learn.md)` with the in-body reference "the transitions table above".
   - Single-location rule paragraph: drop the trailing reference to `[partial_learn_targets](../../docs/partial_learn_targets.md)` ("The `Type` vocabulary and routing tests live in [partial_learn_targets]; do not restate the matrix here.") and replace with "The four targets, when-to-use tests, and example filenames live in the matrix rendered above; do not restate it elsewhere in this body."
3. For inline CLI command syntax (`bin/booping-debug-mode learn`, `bin/booping-project-name` via the project-context include), copy the exact form from `src/templates/skills/retro.md.j2`. Do not retype the inline-command markup from prose description; copy the bytes directly. Literal form, for unambiguous reference (on its own line in the body):

   ```
   !`bin/booping-debug-mode learn`
   ```

4. Run `bin/booping-build` once after the template is complete.

**Structural DoD**:

- [x] Frontmatter: `name: learn`, `description` carried over verbatim, `argument-hint: [retrospective file path]`, `user-invocable: true`, `effort: {{ config.skills.learn.effort }}`, `allowed-tools` list transcribed verbatim from the pre-build `skills/learn/SKILL.md` plus `Bash(bin/booping-debug-mode:*)` and `Bash(bin/booping-project-name:*)`. The list does **not** include `Bash(bin/booping-lessons:*)` or `Bash(bin/booping-extra-instructions:*)`.
- [x] Body opens with `# booping — /learn` heading and the existing two-paragraph opening ("Turn retrospective findings..." + "This skill is **wide-domain**..." sentence) carried over verbatim.
- [x] `{% include "_partials/_project_context.j2" %}` placed immediately after the opening paragraphs.
- [x] `{{ plan_transitions.render("learn") }}` placed after the project-context include.
- [x] `{{ available_agents.render("learn") }}` placed after the transitions table — renders empty (no `## Available Agents` heading in the rendered body).
- [x] `{% include "_partials/_learn_targets.j2" %}` placed after the agents-empty render — replaces the `partial_learn_targets.md` Preflight bullet.
- [x] `!`bin/booping-debug-mode learn`` placed on its own line after the matrix include — replaces the legacy two-file debug delegator/activation split. **No `## Debug guard` section**, **no `test -f` line in body**, **no `[debug extras]` lazy-load link**.
- [x] Old `## Preflight` section deleted in its entirety.
- [x] The legacy "Read attached repo's `CLAUDE.md`" Preflight bullet is gone. Phase 1.5 prose names it explicitly as one of the sweep targets.
- [x] The legacy "Read from `~/Claude/{project}/_booping/skill_learn.md`" Preflight bullet is gone. Phase 1.5 prose names it explicitly as one of the sweep targets. **No `!`bin/booping-extra-instructions skill_learn.md`` line anywhere in the body.**
- [x] The legacy top-of-body lessons load is gone. **No `!`bin/booping-lessons`` line anywhere in the body** — Phase 1.5 prose instructs the orchestrator to read the `lessons/` directory directly. Verify with `grep -nE '!`bin/booping-(lessons|extra-instructions)`' skills/learn/SKILL.md` returns zero matches.
- [x] `## High-level workflow` section: 6 numbered bullets carried over verbatim.
- [x] `## Single-location rule` paragraph carried over verbatim, with the link to `partial_learn_targets.md` replaced by the in-body reference described in step 2.
- [x] Phase 0 through Phase 5 carried over verbatim except for the link swaps, the eager-include swap, and the Phase 1.5 first-step swap named in step 2 of the sequence above. Every other sentence — including Phase 0's verbatim STOP error message, the renumbered Phase 1.5 per-candidate filtering / sweep verdict steps, Phase 5's vault-commit `cd ~/Claude/{project_name} && git ...` block — is unchanged.
- [x] Phase 3 contains the lesson body shape inline — `**Rule**:` and `**Example**:` markers appear in the rendered body (proves the partial was included). The rendered body contains **no** link to `docs/lesson_template.md` or `src/docs/lesson_template.md`.
- [x] Phase 2 link target: `[review table format](../../docs/learn_review_table.md)` — points at the rendered `docs/` file, not `src/docs/`. The rendered body contains **no** `src/docs/` reference at all.
- [x] `## What learn does NOT do` section: carries over the first three bullets verbatim; drops the fourth bullet per Decisions.
- [x] Hard rules section: rules (a), (b), (c), (d), (g), (h) preserved verbatim from the existing skill body. Rule (c) and (h) reworded to drop the `template_lesson.md` link and reference "the lesson body shape included in Phase 3 above" instead. Rules (e) and (f) **dropped** per Decisions.
- [x] `rg 'partial_(plan_transitions_learn|learn_targets|debug_delegator|debug_learn|read_lessons|project_resolution|plan_statuses)|template_(learn_review_table|lesson)' skills/learn/SKILL.md` returns zero matches.
- [x] `rg '\{\{|\{%' skills/learn/SKILL.md` returns zero matches (no Jinja placeholder leaks).
- [x] Rendered `skills/learn/SKILL.md` checked in alongside the template.

---

### M3: Prune orphaned files + CLAUDE.md — 1 SP | done

**Goal**: Six legacy `docs/` files unique to `/learn` deleted. CLAUDE.md "Status" block updated to reflect that `/learn` is now template-driven.

**Verify**:

```bash
# All six target files gone
for f in partial_plan_transitions_learn partial_learn_targets partial_debug_delegator partial_debug_learn template_learn_review_table template_lesson; do
  test -f /home/anton/Dev/@A/claude-booping/docs/$f.md \
    && { echo "FAIL: $f.md still exists"; exit 1; } \
    || echo "OK $f.md gone"
done

# No leftover references in plugin source (post-deletion)
rg -l 'partial_plan_transitions_learn|partial_learn_targets|partial_debug_delegator|partial_debug_learn|template_learn_review_table|template_lesson' \
  /home/anton/Dev/@A/claude-booping/skills /home/anton/Dev/@A/claude-booping/src \
  /home/anton/Dev/@A/claude-booping/agents /home/anton/Dev/@A/claude-booping/bin \
  /home/anton/Dev/@A/claude-booping/docs \
  && { echo "FAIL: legacy ref remains"; exit 1; } \
  || echo "OK no legacy refs"

# CLAUDE.md status flipped
grep -E 'template-driven' /home/anton/Dev/@A/claude-booping/CLAUDE.md | head -3

# partial_read_lessons NOT deleted (chat still uses it)
test -f /home/anton/Dev/@A/claude-booping/docs/partial_read_lessons.md \
  && echo "OK partial_read_lessons preserved" \
  || { echo "FAIL: partial_read_lessons deleted prematurely"; exit 1; }

# Build still clean
/home/anton/Dev/@A/claude-booping/bin/booping-build && echo OK build
```

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | `git rm` the six target files; verify post-deletion that no other plugin file references them; update CLAUDE.md "Status (April 2026)" block to move `/learn` from hand-authored holdouts to template-driven list. | `docs/partial_plan_transitions_learn.md`, `docs/partial_learn_targets.md`, `docs/partial_debug_delegator.md`, `docs/partial_debug_learn.md`, `docs/template_learn_review_table.md`, `docs/template_lesson.md`, `CLAUDE.md` | 1 | done |

#### Task 3.1 DoD

**Sequence (grep order matters — delete first, then verify on the post-deletion tree, so no false positives from cross-references between the six files-being-deleted)**:

1. `git rm` all six target files in a single command.
2. Run the leftover-reference grep across the post-deletion tree.
3. Edit `CLAUDE.md` Status block.
4. Run `bin/booping-build`; confirm `git diff skills/learn/SKILL.md` is empty (no rendered-skill change from M3).

**Checks**:

- [x] Six target files removed: `git ls-files docs/partial_plan_transitions_learn.md docs/partial_learn_targets.md docs/partial_debug_delegator.md docs/partial_debug_learn.md docs/template_learn_review_table.md docs/template_lesson.md` returns empty.
- [x] After deletion, `rg -l 'partial_plan_transitions_learn|partial_learn_targets|partial_debug_delegator|partial_debug_learn|template_learn_review_table|template_lesson' skills/ src/ agents/ bin/ docs/` returns zero paths. Worker pastes the verbatim command and stdout in the Done report (Lesson 0002).
- [x] CLAUDE.md "Status (April 2026)" block: bullet listing template-driven skills now reads ``**`/groom`, `/develop`, `/retro`, and `/learn`** are fully template-driven`` (or equivalent); the hand-authored holdouts bullet drops `learn` and reads ``**Other skills** (`chat`, `install`, `help`)``.
- [x] No other `docs/partial_*.md` or `docs/template_*.md` files deleted by this task — `partial_read_lessons.md`, `partial_project_resolution.md`, `partial_plan_statuses.md`, `partial_cross_validation.md`, etc. all still have readers in unmigrated skills.
- [x] `bin/booping-build` exits 0.
- [x] `git diff skills/learn/SKILL.md` is empty after the build.

---

## Final Verification

- [x] `bin/booping-build` regenerates `skills/groom/SKILL.md`, `skills/develop/SKILL.md`, `skills/retro/SKILL.md`, and `skills/learn/SKILL.md` cleanly.
- [x] `rg -l 'partial_plan_transitions_learn|partial_learn_targets|partial_debug_delegator|partial_debug_learn|template_learn_review_table|template_lesson' skills/ src/ agents/ bin/ docs/` returns zero matches.
- [x] Rendered `skills/learn/SKILL.md` satisfies the claude-skill Quality Checklist — no stale state names, no `{{placeholder}}` leaks, every lazy link resolves, `Hard rules` and `What learn does NOT do` carried over verbatim except for the explicit drops + lazy-link swaps in M2's task DoD.
- [x] Side-by-side spot-check of pre/post-migration `skills/learn/SKILL.md` confirms phase content is byte-identical except for the documented swaps.
- [x] CLAUDE.md "Status (April 2026)" lists `/learn` among the template-driven skills.
- [x] Six `docs/` files pruned; no other `docs/partial_*.md` / `docs/template_*.md` deleted.
- [x] `bin/booping-debug-mode` smoke-test passes both states (toggle absent → empty; toggle present → message with absolute template path).
- [x] `_available_agents.j2` macro renders nothing for /learn and unchanged output for groom/develop/retro.
- [x] `booping-plans --status ready-for-dev` reports this plan after /groom's promotion; `booping-plans --status in-progress` reports it after /develop claims.

## Out of scope

- `/chat`, `/install`, `/help` migrations — those skills stay hand-authored until their own plans (`/install`+`/help` migration is already `ready-for-dev`).
- Any redesign of `/learn` behavior beyond the documented drops (Hard rules e/f, "Does not delegate candidate classification" bullet) and lazy-link swaps.
- Renaming the agent-extension filename convention (dropping the `booping-` prefix). The current `agent_booping-<name>.md` shape is what `bin/booping-extra-instructions` and every agent template's `!`...`` line already reference; renaming it is a multi-file change orthogonal to this migration.
- Generating skill/agent example lists in `_learn_targets.j2` dynamically from config. Hand-authored is sufficient until a second skill needs the same enumeration.
- Moving the routing matrix into `src/config.yaml` as structured data. Single-consumer prose-y data; partial is the right home.
- Building a CLI/UI for toggling debug mode. The mechanism is `touch <plugin>/skills/learn/.debug_enabled` / `rm` — no skill needed.
- Changes to `src/config.yaml`'s `plan.statuses.awaiting-learning` block — already correct.
- Touching `agents/booping-researcher.md` or `agents/booping-developer-*.md` — `/learn` does no agent delegation.
- Deleting any `docs/partial_*.md` other than the six listed.
- Migrating existing `src/docs/*.md` files (`task_feature.md`, `task_bug.md`, `task_refactoring.md`, `how_to_initialize_project.md`) into the `src/templates/docs/` → `docs/` pipeline. Today these are hand-authored under `src/docs/` and lazy-linked by `/groom` and `/install`. The "src/ holds only templates" boundary applies to them too, but their migration is a separate plan; this plan establishes the precedent (new doc lazy-loads land under `docs/` via `src/templates/docs/`) without retroactively touching the existing four.

## Risk register

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Phase content diverges silently during transcription (a sentence dropped, a verbatim error message reworded) | medium | Task 2.1 sequence step 1 reads pre-build SKILL.md before any build runs. Step 2 enumerates the exact swaps allowed; everything else is verbatim. M2 Verify includes a side-by-side review against the pre-migration body in Final Verification. |
| `_partials/_learn_targets.j2` accidentally adds Jinja control flow and breaks the build | low | Task 1.3 DoD pins "no Jinja control flow"; M1 Verify runs `bin/booping-build`. |
| `_available_agents.j2` macro tweak regresses groom/develop/retro rendering | low | Task 1.2 DoD requires `git diff` on those three rendered skills returns empty after the build. |
| `bin/booping-debug-mode` outputs an absolute path that varies per developer machine | accepted | The bin command resolves the plugin root from `Path(__file__).resolve().parent.parent` — so output is per-checkout. That is the intent: the path tells the user *where their checkout's template lives*, not a portable string. The output is consumed at runtime, not committed. |
| Six-file pruning takes a stale grep — a leftover reference survives in a less-obvious file | medium | Task 3.1 DoD requires the grep output pasted in the Done report (Lesson 0002), not just a prose claim. Final Verification re-runs the grep across the whole plugin tree. |
| `partial_read_lessons.md` accidentally deleted (it has a second consumer in `/chat`) | low | Task 3.1 DoD explicitly excludes it; M3 Verify positively asserts it still exists. |
| Lazy-load link path resolution wrong from `skills/learn/SKILL.md` | low | Phase 2 link points at `../../docs/learn_review_table.md` (rendered, not `src/docs/`); skill lives at `skills/learn/SKILL.md`, so `../../docs/` resolves to `<plugin-root>/docs/`. M2 Verify includes the path checks. |
| Lessons or extra instructions accidentally re-eagerly-loaded via `!`bin/booping-lessons`` or `!`bin/booping-extra-instructions skill_learn.md`` (e.g. by copy-paste from `retro.md.j2`), biasing Phase 1 extraction | medium | M2 Verify positively asserts both `grep -nE '!`bin/booping-lessons`'` and `grep -nE '!`bin/booping-extra-instructions`'` against the rendered body return zero matches. Failure stops the milestone. Decision text and structural DoD both call this out. |
| Phase 1.5 prose-driven reads accidentally drop one of the three sweep targets (lessons/, _booping/skill_learn.md, repo CLAUDE.md) | medium | M2 Verify extracts the Phase 1.5 body block and positively asserts each target name is present. M2 task DoD specifies the exact wording of the replacement paragraph for verbatim transcription. |
| Lesson template eager include silently fails (Jinja can't find `_partials/_lesson_template.j2`, or the placeholders inside aren't `{% raw %}`-wrapped and crash the build) | medium | Task 1.5 DoD requires the body wrapped in `{% raw %} ... {% endraw %}`. M1 Verify runs `bin/booping-build` after the partial is in place but before the learn skill template references it; M2 Verify asserts `**Rule**:` / `**Example**:` markers appear in the rendered learn SKILL.md (proves the include resolved). |
| Routing-matrix examples include incorrect agent filenames (e.g. `agent_developer_middle.md` instead of `agent_booping-developer-middle.md`) | medium | Task 1.3 DoD pins the exact filenames including the `booping-` prefix and asserts agent-extension examples carry the full agent name. M2 doesn't touch the matrix; it's purely M1 / M3-bound. |
| `bin/booping-debug-mode` invoked without the `Bash(bin/booping-debug-mode:*)` permission and Claude Code blocks the `!`...`` invocation | medium | Task 2.1 step 1 explicitly adds `Bash(bin/booping-debug-mode:*)` and `Bash(bin/booping-project-name:*)` to the `allowed-tools` list (the only two `!`bin/...`` invocations in the rendered body). M2 Verify confirms the entries exist in the rendered frontmatter. |

## Applies lessons

- `lessons/0004_information-architecture-pattern.md` — applies to every artefact this plan ships (`learn.md.j2`, `_learn_targets.j2`, the new `src/templates/docs/learn_review_table.md.j2` doc template, the new `_partials/_lesson_template.j2` eager-include partial, the new `bin/booping-debug-mode` script, the `_available_agents.j2` tweak, the deleted-file pruning, the CLAUDE.md edit). Each must pass the four-check pass: scoping, duplication, configurability, hierarchy. Specifically: M2's rendered SKILL must not re-author the matrix in body prose (scoping/duplication); the inline `!`bin/booping-debug-mode learn`` line must not duplicate the message text in body prose (duplication); the matrix examples must sit at the right level of detail — categories named at body level, exact write paths inferred at runtime (hierarchy); the routing-matrix targets must each have a clear positive trigger ("when to use") rather than only a negative ("not a lesson because...") (scoping); and the choice of *eager* (lesson body shape, hard-wired in Phase 3) vs *lazy* (review-table format, linked from Phase 2) vs *prose-driven* (lessons / extra instructions / repo CLAUDE.md, read inside Phase 1.5) loading must match each artefact's actual usage pattern (scoping + hierarchy) — load-time bias is itself an IA failure mode for the skill that produces lessons.

## CLAUDE.md impact

Update plugin `CLAUDE.md` "Status (April 2026)" block: move `/learn` from the hand-authored holdouts list to the template-driven list. Resulting state:

- Template-driven: `/groom`, `/develop`, `/retro`, `/learn`.
- Hand-authored holdouts: `chat`, `install`, `help`.

(If the `/install`+`/help` migration plan lands first, the holdouts shrink further and the wording adjusts accordingly. The plan's M3 task pins the exact substitution — drop `learn` from the holdouts list.)

The vault `~/Claude/claude-booping/CLAUDE.md` is not touched — the migration is wide-domain shape work; project-local extensions live in `_booping/skill_learn.md` (which this plan does not edit).
