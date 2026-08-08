---
title: Install stops seeding CLAUDE.md-duplicating extensions
type: refactoring
status: done
sp: 5
split_from: null
created: 2026-06-29 00:00
planned: 20260628 18:11
started: 20260628 18:23
completed: 2026-06-28 18:28
retro: retrospectives/20260722-seven-plan-retro.md
goal: success|partial|fail
summary: "/install seeds _booping extensions only for project-local signal CLAUDE.md
  lacks; no validation catalogue, no sizing stub"
commit: 04544de9a2f67efe8c87aad27b68636f65ce367d
---

# Install stops seeding CLAUDE.md-duplicating extensions

# Plan Body

## Context

`/install` Phase 4 **unconditionally** writes three `_booping/` extension files
(`agent_booping-developer.md`, `skill_groom.md`, `skill_develop.md`), with content
defined by the skeletons in `docs/install_extension_files.md`. Two defects:

1. **Duplicates CLAUDE.md.** `skill_groom.md` "Available validations" and
   `skill_develop.md` "Quality-check classification" / "Dev environment" re-list the
   project's commands (lint/typecheck/test/pre-commit) — which the repo `CLAUDE.md`
   already owns. The framework's own discovery order already puts repo `CLAUDE.md`
   first (`CLAUDE.md:114`), so the seeded copies are redundant and drift the moment
   `CLAUDE.md` changes. Confirmed live: `~/Claude/musictl/_booping/skill_groom.md`
   re-lists `just test` / `just lint` / `just typecheck` already documented in
   musictl's `CLAUDE.md`.
2. **Config-path stub.** When the user supplies no sizing override, the skeleton
   still seeds a `## Sizing calibration` section reading
   `(default — see src/config.yaml → sprint.default_threshold_sp)`. That value is
   already rendered into the groom skill body by the booping CLI
   (`_sprint_planning.j2` → "Split threshold: N SP"); extension bodies are injected
   **raw** (`_extra_instructions.j2` does `{{ _ei_body.strip() }}`), so the stub
   can neither render the value nor add signal. Pure noise re-read every groom.

After this change, `/install` seeds an extension file **only when it carries
project-local signal `CLAUDE.md` does not already own**, and skips it otherwise with
an explicit message. The command catalogue is never copied; the sizing stub is never
written.

## Decisions

- **Seed policy**: stop seeding command/validation catalogues entirely. For each
  candidate file, write only the blocks carrying project-local signal absent from the
  repo `CLAUDE.md`; otherwise skip the whole file — why: single-ownership; repo
  `CLAUDE.md` is already first in `/develop`'s discovery order, so a vault copy only
  adds drift.
- **`agent_booping-developer.md`**: keep seeding (stack + conventions) — it is the
  worker's project-local context and the agent briefing channel; not a command
  catalogue. No change to its seed condition.
- **`skill_groom.md`**: seed only when the user supplies a real groom override (e.g. a
  sprint cap value). No "Available validations" catalogue, no config-path
  `## Sizing calibration` placeholder — ever.
- **`skill_develop.md`**: seed only when there is dev signal `CLAUDE.md` lacks (e.g.
  required services / env setup not documented there). No command-list copy.
- **Skip-message content** (locked): when a file is not written, print exactly one
  line per skipped file:
  - `skipped skill_groom.md — no project-local groom override`
  - `skipped skill_develop.md — CLAUDE.md already documents the dev commands`
  Mirrors the existing `preserved existing: <path>` vocabulary. A written file prints
  `wrote <path>`.
- **Detection stays, output shrinks**: Phase 3 still detects stack (feeds the agent
  file) and reads repo `CLAUDE.md`; Phase 4 diffs detected commands against
  `CLAUDE.md` to decide the skip. The validations-catalogue / hook-vs-manual
  classification fields that fed the dropped blocks are removed from the Phase 3
  contract.

## Architecture

`/install` load-time inputs unchanged. The change is internal to Phases 3–4 prose and
the lazy-loaded skeleton doc:

- `src/templates/skills/install.md.j2` (runtime template — live, no rebuild) drives
  the detect → decide-seed flow.
- `docs/install_extension_files.md` (hand-authored lazy-load doc) carries the
  skeletons the skill loads "when ready to write".

No `src/config.yaml`, no Python, no partial API change. The `_extra_instructions.j2`
raw-injection path and the `/develop` discovery order (`CLAUDE.md:114`) are unchanged
— this plan only stops feeding them duplicate content.

## Milestones

### M1: Rewrite the install seed contract — 4 SP | done

**Goal**: `/install` seeds `_booping/skill_groom.md` / `skill_develop.md` only for
project-local signal absent from repo `CLAUDE.md`; the validations catalogue and the
config-path sizing stub are gone from both the skill and the skeleton doc.

**Verify**: `bin/booping render src/templates/skills/install.md.j2` renders cleanly;
read Phase 3–5 prose to confirm the conditional-seed flow + locked skip messages; read
`docs/install_extension_files.md` to confirm no catalogue / no sizing stub remain.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Rewrite Phase 4 (and trim Phase 3 contract): conditional per-file seed, CLAUDE.md-aware skip, locked skip/write messages, drop "write three extension files" framing | `src/templates/skills/install.md.j2` | 2 | done |
| 1.2 | Restructure skeletons: `skill_groom.md` → groom-override-only (no validations, no sizing stub); `skill_develop.md` → CLAUDE.md-absent dev signal only (no command list); `agent_booping-developer.md` unchanged | `docs/install_extension_files.md` | 2 | done |

#### Task 1.1 DoD

- [ ] Phase 4 no longer says "write **three** extension files"; it states the
      per-file seed-or-skip rule keyed on "is this already in repo `CLAUDE.md`?".
- [ ] Phase 3 field list drops the validations-catalogue / hook-vs-manual /
      configured-manual fields that only fed the removed blocks; stack + env signal
      for the kept files retained.
- [ ] Skip path prints exactly the locked lines:
      `skipped skill_groom.md — no project-local groom override` and
      `skipped skill_develop.md — CLAUDE.md already documents the dev commands`;
      written files print `wrote <path>`.
- [ ] `skill_groom.md` is seeded only on a real user-supplied groom override; never a
      config-path sizing stub.
- [ ] Rendered skill body reviewed — no `{{placeholder}}` leak, no stale "three files"
      reference, attach-mode skip-if-exists / stack-mismatch guards still intact.

#### Task 1.2 DoD

- [ ] `## Available validations` block removed from the `skill_groom.md` skeleton.
- [ ] `## Sizing calibration` config-path placeholder removed; skeleton notes it is
      written only when a real override exists.
- [ ] `skill_develop.md` skeleton no longer copies a command list; it carries only
      dev signal `CLAUDE.md` lacks (e.g. required services), or instructs to skip.
- [ ] `agent_booping-developer.md` skeleton unchanged.
- [ ] Doc intro reflects "seed only project-local signal CLAUDE.md lacks", not
      "skeletons populated by Phase 4" for all three.

---

### M2: Sync user-facing docs — 1 SP | done

**Goal**: the public docs no longer describe `/install` as seeding three catalogue
files.

**Verify**: re-read the two pages; confirm no "validation catalogue + sizing
calibration" / "seeds three" wording remains and the new seed policy is stated.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Update install + vault docs to the conditional-seed policy | `documentation/install.md`, `documentation/vault.md` | 1 | done |

#### Task 2.1 DoD

- [ ] `documentation/install.md:50-53` no longer says "/install seeds three from the
      stack it detects"; describes seed-only-project-local-signal + skip behavior.
- [ ] `documentation/vault.md:38-39` no longer describes `skill_groom.md` as
      "validation catalogue + sizing calibration" or `skill_develop.md` as
      "quality-check classification + env notes"; reflects the project-local-override
      role.
- [ ] No other `documentation/` page still claims install seeds command catalogues.

---

## Final Verification

- [ ] `bin/booping render src/templates/skills/install.md.j2` produces clean output
      (no rebuild needed — runtime template).
- [ ] Rendered install skill reviewed: no stale "three files", no `{{placeholder}}`
      leak, locked skip/write messages present, attach-mode guards intact.
- [ ] `docs/install_extension_files.md` carries no validations catalogue and no
      config-path sizing stub; `agent_booping-developer.md` skeleton unchanged.
- [ ] `documentation/install.md` + `documentation/vault.md` match the new policy.
- [ ] `_booping/skill_groom.md` / `skill_develop.md` still inline correctly via
      `_extra_instructions.j2` when a project *does* author them (raw-injection path
      unchanged).

## Out of scope

- No `src/config.yaml`, Python, or partial-API changes.
- No change to `/develop`'s discovery order or `/groom`'s override-reading behavior —
  both already handle absent extension files.
- No change to `agent_booping-developer.md`'s seed condition (still seeded).
- Cleanup of already-seeded project vaults (e.g. `~/Claude/musictl/_booping/`) — the
  user handles those directly.
- `bin/booping-create-project` — already seeds an empty `_booping/`; no change.

## CLAUDE.md impact

No CLAUDE.md changes required — the discovery order line (`CLAUDE.md:114`) stays valid
(repo `CLAUDE.md` → `_booping/skill_develop.md` → stack inspection); this plan only
stops `/install` from writing a duplicate second copy, which the order already
tolerates as optional.

---

# Quality Checklist

## Frontmatter

- [x] Frontmatter matches plan frontmatter shape.
- [x] `sp` (5) equals sum of per-task SP (2 + 2 + 1).

## Content

- [x] Context names the behavior change visible in rendered output, not "refactor internals".
- [x] DoD bullets verifiable by reading rendered output or a diff.
- [x] Every task lists exact template / doc paths.
- [x] Every task DoD uses checkboxes.
- [x] Every milestone has a `Verify` step.
- [x] Each milestone executable from a fresh session with only the plan as context.

## Skill-design hygiene

- [x] No structured facts moved into prose (none changed; config untouched).
- [x] Single-consumer content stays in skill body / skeleton doc.
- [x] Skeletons remain a lazy-load doc under `docs/`.
- [x] `!`commands`` / raw-injection paths unchanged.
- [x] No restated flow / state descriptions.
- [x] No stack-specific details added to the skill body.

## Anti-patterns (must be absent)

- [x] No "TBD" / "TODO" / "implement later".
- [x] No task spanning unrelated concerns.
- [x] No prose duplicating a rendered table/partial.
- [x] No stale state names.

## External references validated

- [x] All referenced paths exist (`install.md.j2`, `install_extension_files.md`, `documentation/install.md`, `documentation/vault.md`).
- [x] Lazy-load doc link (`docs/install_extension_files.md`) resolves from the skill.

## CLAUDE.md impact

- [x] No config-schema / partial-API / artifact-path change → no CLAUDE.md edit owed.
