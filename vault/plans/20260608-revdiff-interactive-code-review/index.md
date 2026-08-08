---
title: revdiff-backed interactive /code-review
type: feature
status: cancelled
sp: 18
split_from: null
created: 2026-06-08 00:00
planned: 20260608 20:35
commit: 4d075d4c05119552e925c1c632db1929d69f4fc4
started: null
completed: null
retro: null
goal: null
summary: "revdiff terminal diff-review surface for /code-review, persisting review artifacts and feeding the delta into /learn"
---

# revdiff-backed interactive /code-review

# Plan Body

## Context

`/code-review` today is a **stateless side-skill**: it generates findings against a
resolved diff, prints them to chat grouped by severity, and writes nothing. Its skill body,
build-shell description, CLAUDE.md, README, and the docs site all assert "stateless / no
persistent report / chat-only".

This plan reverses that for a single, deliberate purpose: pre-seed the AI findings into an
external diff-review TUI ([`umputun/revdiff`](https://github.com/umputun/revdiff), MIT, v1.6.1,
already installed on this machine), let the human confirm/edit/dismiss/add annotations in the
terminal, capture their final set deterministically, persist it as a durable review artifact,
and feed the AI-vs-human **delta** into `/learn` so dismissed false-positives and recurring
human remarks become durable lessons. The next review run then enforces what was taught — the
self-learning loop is the point of the change.

The review **brain** (finding generation, ingestion, artifact, delta, lessons) stays in
booping. The review **surface** (revdiff launch, annotations file, capture) is an external
binary wired entirely through **project config + a vault launch script** — booping's committed
core never learns the word "revdiff". Swapping the project config later points the same brain at
a different surface (GitHub, Plannotator) without touching core.

What changes after: with a review surface configured and present, `/code-review` runs the
interactive loop and persists artifacts; with no surface configured, the binary missing, or no
compatible terminal, it degrades to today's exact chat-only behavior.

## Decisions

- **Transport = direct-bash-from-config, not the cli-agent/run-agent path** — The brief said
  "wire like the Gemini plan-validation". Research showed the Gemini wiring is a *standalone
  script invoked directly via Bash*, **not** the `run-agent`/native-wrapper cli-agent path.
  And the cli-agent path is a hard mismatch here: `run-agent` uses
  `subprocess.run(capture_output=True)` (no TTY) while revdiff is an **interactive TUI** needing
  a real terminal, and the native wrapper's validate-DoD/retry-once/report contract is
  meaningless for a human-in-loop launch. So the skill runs a config-provided launch command
  directly via Bash in the user's real terminal session.
- **Capture = launcher stdout (race-free), history dir as manual fallback** — The vault launch
  script runs revdiff with `--output <its-own-mktemp>` (revdiff does **not** auto-delete
  `--output`), reads that exact file on exit, and emits the captured set on **stdout**. The skill
  consumes launcher stdout — no "newest file" guess, no race, no `<repo-basename>` resolution in
  the skill. Exit code gates: `10` = captured, `0` = clean/none, else = real failure → degrade
  (`captured_exit_code` is a **config field**, not hardcoded). The persistent history file
  `~/.config/revdiff/history/<repo>/<timestamp>.md` (header `path`/`refs`/`commit` + `## Annotations`
  + `## Diff`) is documented only as a **manual-run fallback** in the recipe. Rejected: the
  shipped plugin hook (`ExitPlanMode`-specific); reading "newest history file" from the skill
  (race under concurrent sessions — see Risk register).
- **Overlay-host detection lives in the launch script, not the skill prompt** — The skill's
  preflight checks only that a surface is configured and `command -v <binary>` succeeds; the
  low-level overlay-host roster (tmux/zellij/kitty/wezterm/cmux/ghostty/iTerm2/emacs-vterm) is
  the launch script's concern. No compatible host → the script exits with a distinct code and the
  skill degrades to chat-only. Keeps the high-level orchestrator prompt free of environment
  trivia (lesson 0004 hierarchy).
- **Seeded review is ref-based; `--stdin` is out** — `--stdin` is mutually exclusive with
  `--annotations` (hard error), and we always pre-seed, so the seeded path never uses `--stdin`.
  A commit-range review is expressed as a single positional ref: `revdiff <plan.commit>..HEAD
  --annotations findings.md` (revdiff passes the `A..B` string verbatim to `git diff`). A
  **remote PR** isn't a local ref, so it must be materialized first — `gh pr checkout <n>` (or
  `git fetch origin pull/<n>/head:pr-<n>`) — then reviewed as `revdiff <base>..HEAD
  --annotations`. There is no seeded-PR-via-pipe path.
- **Canonical format = revdiff annotation markdown** — Header `## <file>[:<line>[:<endline>]]
  (<type>)`, `<type>` ∈ `+` / `-` / space / `file-level`; body is free markdown until the next
  `## `. revdiff has **no severity field**, so severity rides as a leading
  `[BLOCKER]`/`[SUGGESTION]`/`[NIT]` body tag (existing vocabulary). The same markdown is the AI
  seed, the on-disk artifact, and the captured human output — round-trippable, no JSON/HTTP.
- **Delta = anchor-keyed, skill-driven** — Kept/dismissed/added is computed by the key
  `file:line(:endline):type`, which is stable across body edits (no fragile text match) and no
  source marker needed. Computed by the model reading seed + output — **zero Python-core
  changes** (honors "skill logic in the template, not Python"). A `booping review-delta`
  subcommand is a possible follow-up if skill-driven diffing proves flaky.
- **code-review stays plan-lifecycle-stateless** — It gains persistence + a `/learn` feed but
  owns no status and transitions no plan. It keeps running ad-hoc on any target. Smallest
  lifecycle blast radius — `develop`/`retro` flow untouched, no `plan.statuses` change.
- **Learning loop closed, lean** — code-review writes a candidate-lessons block into the
  artifact; `/learn` is extended to accept a **review artifact as an alternate source** (like a
  retro), skipping its `awaiting-learning` plan-status gate for that path.
- **Anchor space = the resolved diff** — Findings are generated against `git diff <resolved
  target>` and the *same* target is handed to revdiff, so line/change-type anchors line up.
  Orphan records (any residual mismatch) are dropped by revdiff with a warning, never a crash.
- **Graceful degradation** — Surface unconfigured OR binary absent OR terminal incompatible OR
  exit code neither captured-nor-0 → fall back to chat-only. Never hard-fail.

## Architecture

Load-time inputs unchanged in shape: `_project_context`, `_available_agents("code-review")`,
`_review_template`, `_lessons`, `_extra_instructions(skill_code-review)`. New: the skill body
renders `config.skills["code-review"].review_surface` (nullable) and lazy-links
`docs/review_surface_setup.md`.

Runtime flow (interactive path):

```
preflight (skill): review_surface configured? AND command -v <binary> ?   any NO → chat-only
resolve target to a LOCAL REF (range / PR / plan / ask)
  - range/ref      → <ref> (e.g. <plan.commit>..HEAD, passed verbatim to git diff)
  - PR URL/number  → git fetch origin pull/<n>/head:refs/booping/pr-<n>  (NON-mutating; no checkout)
                     → <base>..refs/booping/pr-<n>
  - plan           → <plan.commit>..HEAD  (legacy plan w/o commit: → stop/ask)
  → git diff <ref>               # the anchor space
  → write findings.md via the Write tool at an mktemp path (revdiff markdown, [SEVERITY] tag)
  → bash <vault>/<review_surface.launch> <ref> <findings.md>
        # launch script owns ALL env trivia:
        #   - overlay-host detect (tmux/zellij/kitty/wezterm/cmux/ghostty/iTerm2/emacs-vterm);
        #     none present → distinct exit code → skill degrades to chat-only
        #   - overlay-launch revdiff <ref> --annotations findings.md --output <own-mktemp>
        #     --exit-code-on-annotations ; exit code via sentinel file
        #   - on exit: cat its --output file to STDOUT (race-free capture)
  → exit == captured_exit_code (10) → read launcher STDOUT (the final annotation set)
       exit == 0                    → no annotations (approved)
       else (incl. no-overlay code) → degrade to chat-only
  → write artifact  ~/Claude/{project}/reviews/<date>-<plan-or-range>.md  (kind: code-review + final set)
  → compute anchor-keyed delta → append candidate-lessons block to artifact
  → (later) /learn <artifact>  → dismissed→"don't flag", recurring→durable lessons
```

Transport ownership: committed core ships the **mechanism** (the config key + the
detection/launch/capture/ingest phases) and a documented **recipe**
(`docs/review_surface_setup.md`). Activation is a one-time **user/vault step**: the project
`config.yaml` override sets `review_surface`, and `_booping/revdiff-launch.sh` holds the
tmux-popup + revdiff specifics. Develop agents touch only repo code and the orchestrator only
edits `plans/`, so the vault wiring is applied by the user (M7), guided by the recipe.

`/learn` interaction: a second valid intake source (review artifact) alongside the retro path;
the retro path and its `awaiting-learning` gate are unchanged.

## Milestones

### M1: Findings serialized in revdiff-anchored markdown — 3 SP | pending

**Goal**: `/code-review` generates findings against the resolved diff and writes a
revdiff-format `findings.md` (anchored `## file:line(:end) (type)`, body opening with a
`[SEVERITY]` tag), reusing the existing checklist/lesson/DoD/intent machinery.

**Verify**: `bin/booping render src/templates/skills/code-review.md.j2` — inspect the new
serialization phase; confirm no `{{ }}` leaks.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Add a findings-serialization phase after (f): instruct the model to create a temp dir (`mktemp -d` via Bash) and write `findings.md` there **via the `Write` tool** in revdiff markdown — header grammar `## <file>[:<line>[:<endline>]] (<type>)`, `<type>` ∈ `+`/`-`/space/`file-level`, body free markdown opening with `[BLOCKER]`/`[SUGGESTION]`/`[NIT]`. Anchor to the exact post-image (`+`) / pre-image (`-`) line from `git diff <resolved target>`; whole-file remarks use `file-level`. State that the same `<target>` is later handed to the surface so anchors align. | `src/templates/skills/code-review.md.j2` | 3 | pending |

#### Task 1.1 DoD

- [ ] Rendered skill resolves a diff via `git diff <target>` and generates findings against it, with the same `<target>` reused for the surface launch.
- [ ] revdiff header grammar documented exactly; `<type>` set is `+`/`-`/space/`file-level`; body is free markdown until the next `## `.
- [ ] Severity carried as a leading `[BLOCKER]`/`[SUGGESTION]`/`[NIT]` body tag (revdiff has no severity field).
- [ ] Reuses the existing (e) checklists + (f) lesson/DoD/intent checks — no parallel finding machinery introduced.
- [ ] `findings.md` is written via the `Write` tool to an `mktemp -d` path, not to the vault; `Write` + `Bash(mktemp *)` are in allowed-tools.
- [ ] Renders clean; no `{{ }}` leaks; no stale state names.

---

### M2: Target→local-ref resolution, overlay preflight, launch + degradation, config schema — 4 SP | pending

**Goal**: the skill resolves any target to a **local git ref** revdiff can seed, and enters the
interactive surface only when `review_surface` is configured AND its binary is present AND an
overlay-host terminal is present; otherwise it falls back to today's chat-only path. Capture is
gated by the configured exit code.

**Verify**: `bin/booping render src/templates/skills/code-review.md.j2`; then `just build` and
`git diff -- skills/code-review/SKILL.md` (only frontmatter/allowed-tools + body render line
should change).

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Add nullable `skills.code-review.review_surface` to committed `src/config.yaml` with an inline schema comment (`name`, `launch` [vault-relative script], `captured_exit_code`, `binary`); default `null`. Render its presence in the skill body (render nothing when null). | `src/config.yaml`, `src/templates/skills/code-review.md.j2` | 1 | pending |
| 2.2 | Make the seeded path resolve every target to a **local ref** (`--stdin` ⊥ `--annotations`, so no piping): range/ref → verbatim `A..B`; plan → `<plan.commit>..HEAD` (legacy no-`commit:` → stop/ask); PR URL/number → **non-mutating** `git fetch origin pull/<n>/head:refs/booping/pr-<n>` (creates a ref **without** switching branches — no `gh pr checkout`, no working-tree mutation) then `<base>..refs/booping/pr-<n>`. Generate findings against `git diff <ref>` and pass the same `<ref>` to the surface. | `src/templates/skills/code-review.md.j2` | 1 | pending |
| 2.3 | Preflight + launch + degradation. Skill preflight is high-level only: `review_surface` set AND `command -v <binary>` — fail either → chat-only (existing (g)), never hard-fail. On pass run `bash <vault>/<launch> <ref> <findings.md>`; the launch script owns overlay-host detection and returns a distinct exit code when no host is present. Interpret exit vs `captured_exit_code` (`10` captured → read launcher stdout / `0` none / else incl. no-overlay → degrade). Add launch/detection Bash perms to the build shell. | `src/templates/skills/code-review.md.j2`, `src/files/skills/code-review/SKILL.md.j2` | 2 | pending |

#### Task 2.1 DoD

- [ ] `review_surface` present in `src/config.yaml`, default `null`, with an inline comment naming the four fields.
- [ ] Skill body reads `config.skills["code-review"].review_surface` and renders nothing extra when null.
- [ ] No revdiff-specific string in committed `src/config.yaml` (mechanism only; recipe lives in docs/vault).

#### Task 2.2 DoD

- [ ] Seeded path never uses `--stdin`; every target resolves to a local ref revdiff accepts (`A..B` verbatim).
- [ ] PR targets are materialized via **non-mutating** `git fetch …:refs/booping/pr-<n>` (no branch switch, no `gh pr checkout`); working tree is untouched.
- [ ] Plan target → `<plan.commit>..HEAD`; legacy plan without `commit:` halts and asks.
- [ ] Findings are generated against `git diff <ref>` with the same `<ref>` handed to the surface (anchors align).

#### Task 2.3 DoD

- [ ] Skill preflight is high-level (configured + `command -v`); overlay-host detection is delegated to the launch script (no terminal roster in the skill body — lesson 0004 hierarchy).
- [ ] Degradation: binary absent OR launch script signals no-overlay OR exit ∉ {10, 0} → chat-only without hard-fail.
- [ ] `captured_exit_code` comes from config, not hardcoded; `10` = captured (read launcher stdout), `0` = none/approved.
- [ ] Build-shell `allowed-tools` gains the needed perms (`Bash(command -v *)`, `Bash(bash *)`, `Bash(git fetch *)`, `Bash(mktemp *)`); `Write` retained.
- [ ] `just build` materializes `skills/code-review/SKILL.md`; diff shows only intended frontmatter changes.

---

### M3: Capture (history dir) → durable vault artifact — 2 SP | pending

**Goal**: on a captured exit, read the human's final annotation set from the **canonical history
dir** and write a persistent review artifact under `~/Claude/{project}/reviews/`.

**Verify**: `bin/booping render src/templates/skills/code-review.md.j2`; confirm the artifact
phase names the history-read, the path, and the frontmatter shape.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Add a capture+artifact phase: take the human's final annotation set from **launcher stdout** (the launch script reads its own `--output` file → race-free). Write `~/Claude/{project}/reviews/<YYYYMMDD>-<plan-slug-or-range>.md` with YAML frontmatter (`kind: code-review`, `target`, `base_commit`, `plan` [or null], `timestamp`) + the final annotation set verbatim. Create `reviews/` when missing. (Manual-run history-dir fallback is documented in the M6.2 recipe, not implemented in the skill.) | `src/templates/skills/code-review.md.j2` | 2 | pending |

#### Task 3.1 DoD

- [ ] Final set taken from launcher stdout (race-free); no "newest history file" guess in the skill.
- [ ] Artifact written to `~/Claude/{project}/reviews/<date>-<plan-or-range>.md`; `reviews/` created if absent.
- [ ] Frontmatter carries `kind: code-review`, `target`, `base_commit`, `plan` (or null), ISO `timestamp`.
- [ ] Body is the final annotation set verbatim (valid round-trip revdiff markdown).
- [ ] Vault write done by the orchestrator (skill owns vault I/O), consistent with hard rules.

---

### M4: Anchor-keyed delta + candidate-lessons block — 2 SP | pending

**Goal**: the skill computes the AI-vs-human delta (anchor key `file:line(:end):type`) and
appends a candidate-lessons block to the artifact.

**Verify**: `bin/booping render src/templates/skills/code-review.md.j2`; confirm the delta phase
specifies the anchor key and the three buckets.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Add a delta phase: instruct the model to first enumerate **both** anchor-key sets explicitly (one `file:line(:end):type` key per finding, sorted) from `findings.md` (seed) and the captured set, then classify each key — in seed not output = **dismissed** (false positive); in output not seed = **human-added**; in both = **kept** (flag when body text edited). Append `## Review delta` + a candidate-lessons section to the artifact. Skill-driven (read both via Read; no Python core change). | `src/templates/skills/code-review.md.j2` | 2 | pending |

#### Task 4.1 DoD

- [ ] Both anchor-key sets are enumerated explicitly (sorted) before diffing — forces deterministic comparison, mitigates LLM set-diff drift.
- [ ] Delta keyed on `file:line(:end):type`, not body-text match.
- [ ] Three buckets surfaced: kept, dismissed (false-positive), human-added.
- [ ] Candidate-lessons block appended to the artifact for `/learn` to consume.
- [ ] No Python-core change (delta computed in-skill).

---

### M5: /learn accepts a review artifact as a source — 3 SP | pending

**Goal**: `/learn` recognizes a review-artifact argument as an alternate intake (no
`awaiting-learning` plan required) and extracts candidates from its delta / candidate-lessons
block. The retro intake is unchanged.

**Verify**: `bin/booping render src/templates/skills/learn.md.j2`; confirm the Phase 0 branch
and that the retro path still validates `awaiting-learning`.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | Extend `/learn` Phase 0 with an explicit branch: if `$ARGUMENTS` is a path under `reviews/` **and** its YAML frontmatter has `kind: code-review` → skip the retro/plan-status path and source candidates from its `## Review delta` block. Phase 1: dismissed → "stop flagging X" candidates; recurring human-added → durable-rule candidates. Leave the retro path and its `awaiting-learning` gate intact. | `src/templates/skills/learn.md.j2` | 3 | pending |

#### Task 5.1 DoD

- [ ] `/learn` branch is explicit: arg under `reviews/` with `kind: code-review` frontmatter → review path (skips the `awaiting-learning` plan-status gate); otherwise retro path.
- [ ] Dismissed (false-positive) remarks → "don't flag" candidates; recurring human-added remarks → durable lesson candidates, routed through the existing target matrix.
- [ ] Retro intake unchanged (regression: retro path still resolves a plan and validates status).
- [ ] Renders clean; no stale state names; no `{{ }}` leaks.

---

### M6: Reverse the stateless contract + config/docs/CLAUDE/build + reference cleanup — 3 SP | pending

**Goal**: every now-false "stateless / no-persistent-report / chat-only" claim is removed or
corrected; the new config key, `reviews/` vault dir, and setup recipe are documented; artifacts
rebuilt. (Stale-reference cleanup is in-sprint per lesson 0005.)

**Verify**: `just build`; `git diff -- skills/`; `grep -rn "stateless\|no persistent report\|chat-only" src/ skills/ docs/ documentation/ CLAUDE.md README.md`.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 6.1 | Rewrite the skill body's top-line description, **Hard rules**, and **What /code-review does NOT do**: drop the no-persistent-report / "stateless side-skill" / chat-only lines; state the persistence + `/learn`-feed reality; keep "no commits/push" and "owns/transitions no plan status" (still true). Update the build-shell `description`. | `src/templates/skills/code-review.md.j2`, `src/files/skills/code-review/SKILL.md.j2` | 1 | pending |
| 6.2 | New `docs/review_surface_setup.md`: the revdiff recipe — the project `config.yaml` `review_surface` block + a complete `_booping/revdiff-launch.sh` (overlay launch via tmux `display-popup -E` running `revdiff <ref> --annotations <seed> --exit-code-on-annotations`, with exit-code propagated through a sentinel file; emit the captured set on stdout by reading the newest history file). Document: ref-based seeding only (`--stdin` ⊥ `--annotations`), PR materialization (`gh pr checkout` / `git fetch pull/<n>/head`), the overlay-host requirement, history-dir capture (`~/.config/revdiff/history/<repo>/*.md`), install lines (`brew install umputun/apps/revdiff`, `paru -S revdiff`), and the graceful-degradation note. Lazy-link it from the skill body. | `docs/review_surface_setup.md`, `src/templates/skills/code-review.md.j2` | 1 | pending |
| 6.3 | Reference cleanup + docs: fix every stale "stateless/chat-only/no-persistent" claim in `CLAUDE.md`, `README.md`, and the `documentation/` code-review page; add CLAUDE.md entries for the `review_surface` config key, the `reviews/` vault dir, and `docs/review_surface_setup.md`. `just build`. | `CLAUDE.md`, `README.md`, `documentation/*` (code-review page) | 1 | pending |

#### Task 6.1 DoD

- [ ] No surviving "stateless side-skill" / "no persistent report" / "chat-only" claim in the skill body or build-shell description.
- [ ] Hard rules + NOT-do reflect persistence + `/learn` feed; still assert no commits/push and no owned/transitioned status.

#### Task 6.2 DoD

- [ ] `docs/review_surface_setup.md` carries a working config block + a complete launch script (no TBD): overlay launch, ref-based `revdiff <ref> --annotations <seed>`, sentinel exit-code propagation, history-dir capture.
- [ ] Doc states the hard constraints: `--stdin` ⊥ `--annotations` (seeded path is ref-only), PR-to-local-ref materialization, overlay-host requirement.
- [ ] Install (`brew`/`paru`) + graceful-degradation notes present.
- [ ] Skill body lazy-links the doc via `[label](${CLAUDE_PLUGIN_ROOT}/docs/review_surface_setup.md)`.

#### Task 6.3 DoD

- [ ] CLAUDE.md documents the `review_surface` config key, the `reviews/` vault dir, and the setup doc.
- [ ] `README.md` + `documentation/` code-review page no longer claim statelessness/no-persistence where false.
- [ ] `grep -rn "stateless\|no persistent report\|chat-only"` over the repo returns only intentional/historical hits.
- [ ] `just build` clean; `git diff -- skills/` shows only intended changes.

---

### M7: Reshape pause + live interactive verification — 1 SP | pending

**Goal**: `/develop` hands the rendered `code-review` skill body + a real review artifact back to
the user for prose-shape shaping, and the user verifies the full interactive loop on a real
terminal (the only place with a TTY) before the plan leaves `in-progress`.

**Verify**: a live revdiff session on this repo produces a `reviews/` artifact; user signs off on
the reshaped skill body.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 7.1 | Pause-for-review: user applies the vault recipe (project `config.yaml` `review_surface` + `_booping/revdiff-launch.sh`) to `~/Claude/claude-booping/` (manual setup — not an agent task), runs `/code-review` on a small range, exercises the seed → refine → capture → artifact loop, and reshapes the rendered skill body for IA. Apply shaping edits to the skill template. | `src/templates/skills/code-review.md.j2` | 1 | pending |

#### Task 7.1 DoD

- [ ] One live interactive review run on this repo (revdiff popup, seed → refine → capture → artifact) confirmed working.
- [ ] Vault recipe applied to `~/Claude/claude-booping/` and confirmed (manual setup step).
- [ ] Rendered skill body reshaped per user IA feedback; no `{{ }}` leaks, no duplicated tables.

---

## Final Verification

- [ ] `just build` renders cleanly; `bin/booping render src/templates/skills/code-review.md.j2` and `bin/booping render src/templates/skills/learn.md.j2` produce clean output (no `{{ }}` leaks, no stale state names).
- [ ] `just lint`, `just typecheck`, `just test` pass (no Python-core change expected, but the suite must stay green).
- [ ] Degradation verified by inspection: with `review_surface` null, the rendered skill is behaviorally identical to today's chat-only flow.
- [ ] Project-local extension points (`_booping/skill_code-review.md`, `_booping/skill_learn.md`) still inline correctly.
- [ ] `grep -rn "stateless\|no persistent report\|chat-only"` over the repo returns only intentional/historical hits.

## Out of scope

- In-UI "ask-AI" / discussion comments (revdiff stays "dumb"; manual).
- GitHub / Plannotator transports (deferred alternate surfaces — same brain, different config).
- Plan-review-via-revdiff (future unification; v1 is code review only).
- Multi-user review.
- A new owned plan-lifecycle status for `code-review` (stays status-less).
- Any Python-core change — no `run-agent` touch, no new subcommand; the delta is skill-driven (a `booping review-delta` helper is a possible follow-up only).

## Risk register

From Gemini cross-validation (2026-06-08):

- **History-read race (resolved for the orchestrated path).** Reading the "newest" history file is
  unsafe under concurrent/manual revdiff sessions. **Resolved**: the orchestrated path captures via
  **launcher stdout**, which reads the launcher's own `--output` temp — race-free. The history dir
  is documented only as a manual-run fallback (M6.2). Residual risk applies solely to that manual
  fallback and is **accepted**.
- **PR working-tree mutation (resolved).** `gh pr checkout` switches branches with no teardown.
  **Resolved**: PR targets are materialized with non-mutating `git fetch …:refs/booping/pr-<n>`
  (creates a ref, no checkout). Working tree is never switched (M2.2).
- **LLM set-diff determinism (mitigated, residual accepted).** Skill-driven anchor-key diffing could
  drop/hallucinate keys. **Mitigated**: M4.1 forces explicit sorted enumeration of both key sets
  before classifying; finding counts are small (tens, not thousands). Residual risk **accepted** for
  v1; a `booping review-delta` subcommand is the escalation path if it proves flaky.

## CLAUDE.md impact

M6 owns these edits:
- **Config schema** section: add `skills.code-review.review_surface` (nullable; `name`, `launch`, `captured_exit_code`, `binary`).
- **Project vault layout** section: add `reviews/<date>-<plan-or-range>.md` (durable review artifacts).
- **Skill/CLI description** for `code-review`: it is now persistent (writes artifacts, feeds `/learn`); still owns no plan status.
- **Docs list**: add `docs/review_surface_setup.md`.
- **README** Statuses section: no change (no `plan.statuses` change), but the code-review narrative is corrected.

# Quality Checklist

(Verification rubric for this plan — checked before leaving `in-spec`; not part of the executable body.)

- [ ] Frontmatter matches the plan frontmatter template; `sp` (18) = sum of task SP (3 + 4 + 2 + 2 + 3 + 3 + 1).
- [ ] Context names the rendered-behavior change, not "refactor internals".
- [ ] Every task lists exact template/partial/config paths; every DoD uses checkboxes.
- [ ] Every milestone has a `Verify` step that includes a render/rebuild.
- [ ] Structured facts (the `review_surface` schema) go in `src/config.yaml`, not prose.
- [ ] No stack-specific details in the skill body (revdiff specifics live in docs/vault).
- [ ] No "TBD/TODO"; no task spanning unrelated concerns; no prose duplicating a rendered table.
- [ ] Lazy-load doc link (`docs/review_surface_setup.md`) resolves from the rendered skill.
- [ ] Reference cleanup is in-sprint (M6.3), not a follow-up sweep (lesson 0005).
- [ ] Reshape pause is the final milestone (M7), not left to the awaiting-retro window.
</content>
</invoke>
