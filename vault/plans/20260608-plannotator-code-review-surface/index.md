---
title: Plannotator-backed code-review surface (global, booping-decoupled)
type: feature
status: done
sp: 9
split_from: null
created: 2026-06-08 00:00
planned: 20260608 21:02
started: 20260608 21:26
completed: 2026-06-10 00:00
retro: retrospectives/20260610-plannotator-code-review-surface.md
goal: partial
commit: 4d075d4c05119552e925c1c632db1929d69f4fc4  # plugin HEAD at draft; informational only — this plan produces no plugin-repo diff
summary: "Plannotator browser diff-review surface for /code-review, wired outside the plugin repo via global agent + vault config"
---

# Plannotator-backed code-review surface (global, booping-decoupled)

# Plan Body

## Context

[Plannotator](https://github.com/backnotprop/plannotator) is a separate, already-installed
tool (`~/.local/bin/plannotator`, MIT/Apache-2.0): a browser-based diff-review surface backed
by a local HTTP server. This plan gives booping's `/code-review` an **optional** Plannotator
review surface:

- `/code-review` generates findings as it does today, then **pre-seeds** them into a running
  Plannotator review via the purpose-built `POST /api/external-annotations` endpoint.
- The human opens the browser review and sees **both the real code diff and the AI comments**
  inline, then annotates/confirms/dismisses.
- On submit, the human's feedback **round-trips back to the harness** (captured from the
  launcher's stdout), so the review loop closes.

**Hard separation (the whole point):** the booping plugin repo at
`/home/anton/Dev/@A/claude-booping` is **never touched** and never learns the word
"plannotator". Every deliverable lives in:

1. **Global `~/.claude/`** — a reusable transport script + a Claude Code agent that encapsulate
   all Plannotator transport and interaction.
2. **Per-project vault** (`~/Claude/{project}/`) — config + a `/code-review` extension that
   *attaches* the agent. This is the only wiring, and it lives outside the plugin repo.

This is an **independent alternative to the revdiff plan**
(`20260608-revdiff-interactive-code-review.md`, awaiting-plan-review) — same idea (seed findings
→ human reviews → feedback returns), different surface (browser HTTP vs terminal TUI). Per the
user's decision, **Plannotator ships first** and does **not** depend on revdiff's `review_surface`
mechanism. Where revdiff would have ridden a generic booping-core hook, this plan deliberately
avoids any booping-core change by using mechanisms booping **already exposes** (see Architecture).

This plan file lives in the vault only because the vault is the active project context; the vault
is a **separate git repo** from the booping plugin repo, so filing it here does not violate the
separation rule. No artifact below is committed to the plugin repo.

## Decisions

- **Zero booping-core change — ride existing extension points.** booping's `_available_agents.j2`
  already renders a project-config agent **with no `type`/`internal` flag** as
  `subagent_type="<id>"` — exactly the invocation form for a **global** `~/.claude/agents/<id>.md`
  agent (no `/compile`, no cli-wrapper). And `/code-review` already (a) renders
  `available_agents("code-review")` from `config.skills["code-review"].agents` (project-overridable
  via vault `config.yaml`) and (b) ends with the `_extra_instructions(skill_code-review)` hook fed
  from vault `_booping/skill_code-review.md`. So the agent is *registered* via vault config and
  *invoked* via a vault skill-extension — the plugin repo is untouched. Rejected: adding a generic
  review-surface/cli-delegation hook to booping core (unnecessary; the hooks already exist).
- **Agent background-launches; loop closes via launcher stdout.** A *manual* `plannotator review`
  sends the human's feedback to the human's own terminal, severing the harness loop (there is no
  persisted feedback file in the review path). So the transport **background-launches**
  `plannotator review`, owns the process, seeds it over HTTP while it serves, and captures the
  human's feedback from the backgrounded process's **stdout** on exit. "User opens the review
  themselves" = the human drives the in-browser annotation; the *process* is owned by the agent.
- **Seeding = `POST /api/external-annotations` (+ idempotent `DELETE`).** This endpoint is
  purpose-built for external/agent review; the `CodeAnnotation` type carries `source`, `severity`,
  and `reasoning` fields explicitly for external findings. The UI subscribes via SSE and replays a
  snapshot on connect, so there is **no timing race** — seeding before or after the browser loads
  both work. Each run does `DELETE /api/external-annotations?source=booping` before `POST` so
  re-runs don't duplicate. Rejected: `/api/draft` (loads once on mount, needs a user "restore?"
  click, mount-timing race — it's the human's autosave, not a seeding channel).
- **Deterministic port via `--port`.** The installed binary exposes a `--port <p>` flag (verified
  against `~/.local/bin/plannotator`; an older note claimed none existed — version drift). The
  script picks a free port and passes `--port`, so seeding/feedback target a known origin with no
  session-file discovery. `PLANNOTATOR_PORT` env is the equivalent fallback.
- **Two-layer transport: mechanical script + interaction agent.** A global shell script
  (`~/.claude/bin/booping-plannotator-review`) is the mechanical floor (port, launch, poll, seed,
  capture, exit codes). A global agent (`~/.claude/agents/plannotator-reviewer.md`) owns the
  *interaction*: map booping findings → the annotation contract, drive the script, return the
  human's feedback (+ a kept/dismissed/added delta). This mirrors booping's own
  wrapper-agent + `run-agent` split and keeps environment trivia out of the prompt (lesson 0004
  hierarchy).
- **Graceful degradation.** Plannotator binary absent OR server never comes up OR no findings →
  the agent reports degradation and `/code-review` falls back to today's exact chat-only output.
  Never hard-fail.
- **Annotation contract is fixed by Plannotator's `transformReviewInput`.** Required: `source`,
  `filePath`, `lineStart`, `lineEnd`, and at least one of `text`/`suggestedCode`. Optional: `side`
  (`old`/`new`, default `new`), `type` (`comment`/`suggestion`/`concern`), `scope` (`line`/`file`),
  `severity` (`important`/`nit`/`pre_existing`), `reasoning`, `author`, `suggestedCode`,
  `originalCode`. Batch shape `{ "annotations": [ … ] }` is atomic.

## Architecture

**Booping core: untouched.** No file under `/home/anton/Dev/@A/claude-booping` changes. The
integration attaches through two pre-existing booping extension points, both fed from the vault:

- `config.skills["code-review"].agents.<id>` (vault `config.yaml` deep-merge) → renders the agent
  into `/code-review`'s **Available Agents** table as `subagent_type="<id>"`.
- `_booping/skill_code-review.md` (vault) → injected at the end of the rendered `/code-review`
  body, adding the "seed-and-round-trip via the agent" route + chat-only fallback.

**Execution-model note (read before /develop):** every deliverable lives **outside** the booping
plugin repo (in `~/.claude/` and the vault). booping's `/develop` developer agents touch only the
attached repo, so they **cannot** build these artifacts. This plan is executed by **manual /
main-session authoring** guided by the milestones, plus **user-run live verification** (the
browser loop needs a real display + a human). Each milestone notes this. The plan's value is a
precise spec, not a `/develop`-automatable repo diff — there is no booping-repo diff to produce.

Runtime flow (interactive path):

```
/code-review phases (a)–(g)      # unchanged booping core: resolve diff target, generate findings
  └─ vault _booping/skill_code-review.md extension fires AFTER (g):
       if `plannotator-reviewer` is in the agent table AND user opted into the surface:
         brief the agent with: findings (file:line, severity, snippet, fix) + resolved diff ref
       else: today's chat-only output (g)

plannotator-reviewer agent (~/.claude/agents/plannotator-reviewer.md):
  map findings → annotation batch JSON (severity/type/side/anchor/text/suggestedCode/reasoning)
  write batch to a temp file (Write)
  run: ~/.claude/bin/booping-plannotator-review <ref> <batch.json>
  read script stdout = human feedback;  return feedback (+ delta) to /code-review
  binary absent / no server → report degradation → caller falls back to chat-only

~/.claude/bin/booping-plannotator-review <ref> <batch.json>:   # mechanical floor
  pick free port P
  background-launch: plannotator review <ref> --port P     # stdout → temp; server serves concurrently
  poll http://127.0.0.1:P/api/external-annotations until ready
  curl -X DELETE '…/api/external-annotations?source=booping'   # idempotent clear
  curl -X POST   '…/api/external-annotations' --data @<batch.json>
  print review URL on stderr            # human opens / drives the browser
  wait for the backgrounded process to exit (human submitted)
  cat its captured stdout → THIS script's stdout = the human's feedback
  exit-code contract (see I/O contract)
```

## Milestones

### M1: Global transport script — deterministic-port launch, seed, feedback capture — 3 SP | done

**Goal**: `~/.claude/bin/booping-plannotator-review <ref> <batch.json>` background-launches a
Plannotator review on a known port, seeds the findings batch, lets the human review, and emits the
human's feedback on stdout with a defined exit-code contract.

**Manual authoring** (lives in `~/.claude/`, outside any repo — not a `/develop` agent task).

**Verify**: with Plannotator installed, `echo '{"annotations":[]}' > /tmp/b.json &&
~/.claude/bin/booping-plannotator-review HEAD~1..HEAD /tmp/b.json` opens a review on the printed
port; submitting in the browser prints the feedback on stdout and exits `0`. With the binary
renamed away, the script exits `3` and prints a degradation message on stderr.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Script skeleton + lifecycle: parse `<ref>` + `<batch.json>` args; if `command -v plannotator` fails → stderr message + `exit 3`; pick a free TCP port with `P=$(python3 -c 'import socket; s=socket.socket(); s.bind(("",0)); print(s.getsockname()[1]); s.close()')`; background-launch `plannotator review "<ref>" --port "$P"` with its stdout/stderr redirected to a `mktemp` file, capturing its PID; install a `trap 'kill "$BG_PID" 2>/dev/null; rm -f "$TMP"' EXIT INT TERM` so an interrupt while waiting **kills the backgrounded server** (no orphaned process / leaked port) and removes temps; poll `GET http://127.0.0.1:$P/api/external-annotations` (curl, ~30×0.5s) until 200 or `exit 4`; print the review URL on stderr; `wait "$BG_PID"`; `cat` its captured stdout to **this script's stdout**; exit `0`. | `~/.claude/bin/booping-plannotator-review` | 2 | done |
| 1.2 | Seeding step (between readiness and `wait`): `curl -fsS -X DELETE "http://127.0.0.1:P/api/external-annotations?source=booping"` then `curl -fsS -X POST "http://127.0.0.1:P/api/external-annotations" -H 'content-type: application/json' --data @"<batch.json>"`; on POST failure → kill the bg server, stderr message, `exit 5`. Investigate whether a no-auto-open flag exists (`--browser none`?); if not, document that the browser auto-opens and the user just interacts with it. | `~/.claude/bin/booping-plannotator-review` | 1 | done |

#### Task 1.1 DoD

- [x] Script is executable (`chmod +x`) at `~/.claude/bin/booping-plannotator-review`.
- [x] `command -v plannotator` missing → stderr diagnostic + `exit 3` (caller degrades). **Verified live.**
- [x] Free port chosen via the specified `python3` socket one-liner (no `netstat` guess loop, no hardcoded range). **Deviation:** passed via `PLANNOTATOR_PORT` env, not the `--port` flag (the `review` flag is ignored — verified against the binary; env is honored).
- [x] Launches `plannotator review` in the background; server readiness is polled, not assumed; never blocks the seeding step. **Deviation:** readiness + actual origin come from `PLANNOTATOR_READY_FILE` (`{"url","port"}`), more reliable than a blind HTTP poll; `<ref>` is a PR URL or, for local review, ignored in favor of `$PWD`'s working tree (`review` takes no committed-range arg).
- [x] `trap … EXIT INT TERM` **kills the backgrounded server PID** and removes temps on every exit path — including a Ctrl-C while waiting for the human (no orphaned process, no leaked port). **Verified live** (server down after SIGTERM).
- [ ] On human submit, the backgrounded process's stdout (the feedback) is emitted on **this script's stdout**; `exit 0`. _(coded; live submit is M4 — needs a human.)_
- [x] Server-never-ready → `exit 4` with stderr diagnostic. _(coded; readiness path verified live, negative path not triggered.)_

#### Task 1.2 DoD

- [x] `DELETE ?source=booping` runs before `POST` (idempotent re-runs, no duplicate seeds). **Verified live** (re-run keeps count=1; `DELETE` → `{"ok":true,"removed":1}`).
- [x] Batch POSTed from the `<batch.json>` file with `content-type: application/json`; non-2xx → bg server killed, stderr diagnostic, `exit 5`. **Verified live** (POST → `{"ids":[…]}`).
- [x] Empty batch (`{"annotations":[]}`) is accepted end-to-end (no findings is a valid run).
- [x] Auto-open behavior documented in `--help` + recipe: browser auto-opens by default; `PLANNOTATOR_SKIP_BROWSER_OPEN=1` (exposed via `--no-open`) suppresses it.

---

### M2: Global interaction agent — findings→contract mapping + feedback round-trip — 3 SP | done

**Goal**: `~/.claude/agents/plannotator-reviewer.md` is a Claude Code agent that takes a briefing
of booping findings + a diff ref, maps them to the Plannotator annotation contract, drives the M1
script, and returns the human's feedback (plus a kept/dismissed/added delta) to the caller.

**Manual authoring** (prompt artifact in `~/.claude/agents/` — not a `/develop` agent task).

**Verify**: invoke the agent (via the Agent tool, `subagent_type="plannotator-reviewer"`) with a
2–3 finding briefing on a small real diff; confirm annotations appear in the browser anchored to
the right lines/severity, and the agent returns the human's submitted feedback verbatim.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Agent frontmatter (`name: plannotator-reviewer`, `tools: Read, Write, Bash`, description) + body: define the **briefing contract** (findings as `file:lineStart[-lineEnd] · side · severity · snippet · proposed-fix · rationale`, plus the resolved diff `<ref>`); a **mapping table** booping→contract — `BLOCKER`→`severity: important`, `type: concern`; `SUGGESTION`→`type: suggestion`; `NIT`→`severity: nit`, `type: comment`; `text`=rationale/body, `suggestedCode`=fix, `originalCode`=offending snippet, `reasoning`=checklist/lesson cite, `author`/`source`=`booping`, anchor `filePath`+`lineStart`/`lineEnd`+`side` (`new` for `+`, `old` for `-`); write the `{"annotations":[…]}` batch via `Write` to a `mktemp`; run the M1 script. | `~/.claude/agents/plannotator-reviewer.md` | 2 | done |
| 2.2 | Report contract: the script's **stdout is the human's feedback as free text** (Plannotator emits `result.feedback`; an approval prints its approve-prompt; closing without feedback prints empty / a "closed without feedback" line — there is no per-annotation JSON in the review path). The agent's **final returned message = that feedback verbatim** (this *is* the Agent-tool result the `/code-review` orchestrator reads — no variable injection, no special format). Degradation: script `exit 3/4/5` → the agent's final message is an explicit "surface unavailable — fall back to chat-only" signal rather than an error. | `~/.claude/agents/plannotator-reviewer.md` | 1 | done |

#### Task 2.1 DoD

- [x] Agent is invokable as `subagent_type="plannotator-reviewer"` (global `~/.claude/agents/` registry; no `/compile`). Renders in `/code-review`'s Available Agents table — verified.
- [x] Briefing contract is explicit (what the caller must pass); mapping table covers all three booping severities → contract `type`/`severity`.
- [x] Anchors map `+`→`side: new`, `-`→`side: old`; whole-file remarks use `scope: file`.
- [x] Batch written via `Write` to a `mktemp` path (not the vault, not the repo); script invoked with `<ref> <batch.json>`.
- [x] No Plannotator transport trivia (port/poll/curl) in the agent prose — that is the script's job (lesson 0004 hierarchy).

#### Task 2.2 DoD

- [x] Plannotator's stdout shape is documented in the agent body: free-text feedback (`result.feedback`) / approve-prompt on approval / empty on close. No per-annotation JSON is assumed.
- [x] The agent's final returned message is the human feedback verbatim — consumed directly as the Agent-tool result by `/code-review` (no variable/format contract beyond the returned text).
- [x] Script exit `3`/`4`/`5` → agent's final message is an explicit degrade signal; never a hard error.
- [x] Source tag `booping` used consistently (set via `PLANNOTATOR_AGENT_SOURCE=booping`) so the M1 `DELETE ?source=booping` clears exactly this agent's seeds.

---

### M3: Per-project vault wiring + recipe — attach the surface, booping-repo-free — 2 SP | done

**Goal**: a project opts into the surface entirely from its vault: register the agent in
`config.yaml` and add the post-`(g)` delegation + fallback to `_booping/skill_code-review.md`.
Applied to `~/Claude/claude-booping/` as the first consumer. A global recipe documents the setup.

**Manual setup** (vault files + global doc — not a `/develop` agent task; the orchestrator edits
only `plans/`).

**Verify**: `bin/booping render src/templates/skills/code-review.md.j2` (run from the plugin repo,
reading the vault override) shows `plannotator-reviewer` in the Available Agents table as
`subagent_type="plannotator-reviewer"` and the extension text appended at the end — with **no diff
to any tracked file in the plugin repo**.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Add to vault `config.yaml`: `skills.code-review.agents.plannotator-reviewer` (plain native — no `type`/`internal`) with `good_for` ("interactive browser review of a diff with AI findings pre-seeded; human confirms/dismisses; feedback returns") / `bad_for` ("headless/CI; no display; quick chat-only review"). Confirm it renders as `subagent_type="plannotator-reviewer"`. | `~/Claude/claude-booping/config.yaml` | 1 | done |
| 3.2 | Add `_booping/skill_code-review.md` extension: after phase (g), when the user opts into the Plannotator surface AND `plannotator-reviewer` is in the agent table, brief that agent with the findings + resolved diff ref instead of chat-only; the agent's **returned message (the human feedback) is the Agent-tool result** — phase (h) proceeds from that text directly; on the agent's degrade signal or no opt-in, use today's chat-only (g). Put the human-facing recipe (install, two-file vault wiring, degradation) in the script's `--help` + a standalone `~/.claude/booping-plannotator-review.recipe.md` — **not** in the agent prompt (the agent body carries only what it needs to run; lesson 0004 scoping). | `~/Claude/claude-booping/_booping/skill_code-review.md`, `~/.claude/bin/booping-plannotator-review`, `~/.claude/booping-plannotator-review.recipe.md` | 1 | done |

#### Task 3.1 DoD

- [x] Vault `config.yaml` registers `plannotator-reviewer` under `skills.code-review.agents` with `good_for`/`bad_for`; no `type`/`internal` keys.
- [x] Rendered `/code-review` Available Agents table shows it as `subagent_type="plannotator-reviewer"`. **Verified.**
- [x] `git -C /home/anton/Dev/@A/claude-booping status` shows **no** changes (plugin repo untouched). **Verified** (only pre-existing untracked `.gitattributes`).

#### Task 3.2 DoD

- [x] `_booping/skill_code-review.md` adds the post-(g) seed-and-round-trip route + explicit chat-only fallback; lives only in the vault.
- [x] The extension consumes the agent's returned text directly as the Agent-tool result (no invented variable/format); phase (h) proceeds from it.
- [x] Human-facing recipe lives in `--help` + a standalone recipe file (`~/.claude/booping-plannotator-review.recipe.md`) — **not** in the agent prompt (scoping); the agent body carries only its run instructions.
- [x] Rendered `/code-review` body includes the extension text at the end (via the existing `_extra_instructions` hook); plugin repo still shows no diff. **Verified.**

---

### M4: Reshape pause + live end-to-end verification — 1 SP | pending

**Goal**: run the full seed → human-review → feedback loop on a real repo, then reshape the agent
body + vault extension prose for IA before the plan transitions out.

**Manual** (needs a display + a human; the only place the loop is real).

**Verify**: one live `/code-review` run on a small diff in this repo seeds annotations into the
browser, the human annotates and submits, and the feedback returns to the harness; user signs off
on the reshaped agent + extension prose.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Pause-for-review: run `/code-review` on a small range in `~/Dev/@A/claude-booping` with the surface opted in; exercise seed → review → submit → feedback; reshape `~/.claude/agents/plannotator-reviewer.md` and `~/Claude/claude-booping/_booping/skill_code-review.md` for clarity/IA based on what the live render exposes. | `~/.claude/agents/plannotator-reviewer.md`, `~/Claude/claude-booping/_booping/skill_code-review.md` | 1 | pending |

#### Task 4.1 DoD

- [ ] One live interactive review confirmed: findings seeded + anchored correctly, human feedback returned to the harness.
- [ ] Idempotent re-run verified (re-seeding does not duplicate — `DELETE ?source=booping` works).
- [ ] Degradation verified: with the surface not opted in (or binary absent), `/code-review` is behaviorally identical to today's chat-only flow.
- [ ] Agent + extension prose reshaped per user IA feedback.

---

## I/O contract

`~/.claude/bin/booping-plannotator-review` — the mechanical floor.

- **Arguments**: `booping-plannotator-review <ref> <batch.json>` — `<ref>` a git ref/range passed
  verbatim to `plannotator review`; `<batch.json>` a file holding `{"annotations":[…]}`.
- **stdin**: none.
- **stdout**: the human's submitted feedback, verbatim (empty if approved/closed without feedback).
- **stderr**: diagnostics only — review URL, seed status, warnings, degradation messages.
- **Exit codes**: `0` = ran and captured (feedback on stdout, possibly empty); `3` = Plannotator
  binary absent (caller degrades to chat-only); `4` = server never became ready; `5` = seed POST
  failed.

## Final Verification

- [ ] `git -C /home/anton/Dev/@A/claude-booping status --porcelain` is **empty** — the plugin repo
  was never modified (the core separation invariant).
- [ ] Live loop works end-to-end on a real diff: seed → browser review → submit → feedback returned.
- [ ] Idempotent re-runs do not duplicate seeded annotations.
- [ ] Surface-off / binary-absent path is behaviorally identical to today's chat-only `/code-review`.
- [ ] Script `--help` + agent header document install, vault wiring, and exit-code contract.

## Out of scope

- In-UI "Ask AI" / Plannotator custom-agents (`/api/ai/*`, `agents/*.yaml`) — explicitly dropped;
  Plannotator is a dumb review surface here, findings come from booping's `/code-review`.
- Any booping plugin-repo change (skill bodies, `src/`, config, docs) — the integration is
  global + vault only, by construction.
- A persistent vault review artifact / `/learn` feed — the agent returns feedback to the live
  `/code-review` run; durable-artifact + learning loop is a possible follow-up (and is where the
  revdiff plan goes further).
- **Per-annotation kept/dismissed/added delta** — dropped from v1: the review path emits only the
  human's free-text feedback on stdout, with no reliable post-submit snapshot of the final
  annotation set (the server shuts down on `waitForDecision`). Computing a delta would need a
  race-prone `GET /api/external-annotations` poll. Deferred with the durable-artifact follow-up.
- Plan-review-via-Plannotator (markdown/annotate modes) — this is code review only.
- PR-URL review materialization — v1 targets local git refs/ranges (Plannotator accepts a PR URL
  positional, but loop-closure + anchoring for remote PRs is deferred).
- Multi-user / shared review sessions.

## CLAUDE.md impact

- **Plugin repo `CLAUDE.md`**: **no change** — and that is the point. Nothing Plannotator-related
  enters the plugin repo, so its `CLAUDE.md`, README, config, and docs stay untouched.
- No stale references created: all artifacts are new and global/vault-local; nothing existing is
  renamed or deleted (lesson 0005 — no follow-up sweep needed).

## Risk register

Mechanism validated against the installed binary `~/.local/bin/plannotator` (tokens
`external-annotations`, `PLANNOTATOR_PORT`, `--port`, `waitForDecision`, `transformReviewInput`,
`suggestedCode`, `pre_existing` all present) plus the prior-session findings doc.

Gemini cross-validation (2026-06-08) — all critical risks addressed in-plan:

- **Plannotator stdout schema (resolved).** Review path emits only the human's free-text feedback
  (`result.feedback`), no per-annotation JSON. v1 returns that verbatim; the per-annotation delta is
  moved to Out of scope (would need a race-prone snapshot poll).
- **Free-port selection (resolved).** M1.1 specifies the exact `python3` socket one-liner — no
  brittle `netstat`/hardcoded-range guessing.
- **Hook integration (resolved).** The agent's returned message *is* the Agent-tool result the
  `/code-review` orchestrator reads; phase (h) proceeds from that text. No invented variable/format.
- **Agent-prompt scoping (resolved).** Human-facing install/wiring docs live in `--help` + a
  standalone recipe file, not in the agent prompt (lesson 0004).
- **Orphaned bg server on interrupt (resolved).** M1.1 `trap … EXIT INT TERM` kills the
  backgrounded Plannotator PID, so a Ctrl-C while waiting for the human leaks no process/port.

# Quality Checklist

(Verification rubric for this plan — checked before leaving `in-spec`; not part of the executable body.)

- [ ] Frontmatter matches the plan frontmatter template; `sp` (9) = sum of task SP (2 + 1 + 2 + 1 + 1 + 1 + 1).
- [ ] Context names the observable behavior change (optional Plannotator surface for `/code-review`) and the hard separation invariant.
- [ ] Every task lists exact file paths (all under `~/.claude/` or the vault — none under the plugin repo).
- [ ] Every milestone has a `Verify` step; every DoD uses checkboxes.
- [ ] Mechanism facts (annotation contract, endpoints, exit codes) validated against the installed binary, not assumed.
- [ ] No plugin-repo file appears in any task `Files` column (separation invariant is structural, not just stated).
- [ ] Degradation path defined for every failure mode (binary absent, server down, seed failure, no opt-in).
- [ ] Reshape pause is the final milestone (M4), not deferred to the awaiting-retro window.
- [ ] Execution-model reality (manual / global authoring, not `/develop` repo agents) stated explicitly.
- [ ] No "TBD/TODO"; no task spanning unrelated concerns; no silent failure path.
