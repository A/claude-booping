---
title: "Autonomy modes — core.autonomy supervised | autonomous, gates honour it, migrate
  asks on a dirty branch"
type: "feature"
status: in-progress
sp: 18
related_to: null
created: 2026-10-15 16:09
planned: null
started: 2026-10-15 16:36
completed: null
code_reviews: []
sessions:
- f5f0d6c5-5081-40c4-813c-55027756aea0
- e272718e-474f-4519-bf25-2b31268b76b5
retro: null
summary: core.autonomy supervised|autonomous switches the driving protocol's 
  gates; defaults.md log; specs open items and migrate honour it
commit: c48e6178da1f237f8b8c9f649adcdc49fde8db2b
tracker_provider: null
tracker_request: null
tracker_issue: null
return_to: null
agents: '{"research-codebase": "a7a093416ced1ac16", "cross-review": "a6060b99f8c0c600d"}'
reviewed_at: 2026-10-15 16:27
---

# Autonomy modes — core.autonomy supervised | autonomous, gates honour it, migrate asks on a dirty branch

## Context

Every review gate stops for the user today, in every project ([adr/0015](../../specs/adr/0015-one-review-gate-per-run.md)). An unattended run exists only as hand-written prompt prose restated per invocation — "AUTONOMOUS RUN … auto-confirm gates … record every default in clarifications.md or develop-defaults.md". The specs playbook's open-items scenario ends at "next: `/playbook groom`", and migrate's question about uncommitted work "never blocks" while the auto-migrate notice tells the driver to run migrate "without asking the user". [adr/0027](../../specs/adr/0027-autonomy-modes.md) decides a project config key chooses the mode.

After this plan:

- `core.autonomy` — `supervised` (default) or `autonomous`; any other value stops every render in band; the project-context block shows the resolved mode.
- The `/playbook` driving protocol renders its gate and questions rules from the key: supervised is today's text byte for byte; autonomous presents each gate's receipt, auto-confirms it, settles step questions with the recommended option, and logs each through `booping defaults add`. A STOP notice and migrate's uncommitted-work question still stop.
- `booping defaults add` appends a `D{n}` entry to `defaults.md` beside the run artefact — the record of what the agent decided without review.
- The specs playbook renders the mode in its preamble; its open-items scenario takes items through groom and develop without stopping when autonomous, and hands off to groom (which stops at plan review) when supervised — adr/0027's confirmation line.
- migrate's survey names the branch with the uncommitted work and waits for the answer in either mode; the auto-migrate notice says so.

Goal (feature guidance): a project switches between a reviewed and an unattended way of working with one config key, and what an unattended run decided stays findable afterwards.

### Values in play

Per [booping:rule/0030](../../../specs/rule/0030-planning-shows-values-in-play.md):

- [value/0009](../../specs/value/0009-adjustable-control.md) adjustable control — the whole feature: the human picks how much freedom a project's runs get, takes it back by flipping one key, and every unreviewed decision lands in `defaults.md` (C4).
- [value/0015](../../specs/value/0015-deterministic-where-it-can-be.md) deterministic — the mode branch is picked by code at render (C3), the key is validated by code (C2), and the defaults sidecar's numbering, time and placement are CLI code (C4); the model only decides which option is the sensible default.
- [value/0003](../../specs/value/0003-single-source.md) single source — one conditional in the one driving partial instead of a branch per playbook's `review_gate` (C3); the per-invocation "AUTONOMOUS RUN" prose becomes config.
- [value/0007](../../specs/value/0007-plans-run-to-the-end.md) plans run to the end — autonomous groom settles its own questions so develop never waits.
- [value/0008](../../specs/value/0008-effective-human-review.md) effective human review — supervised projects keep every gate unchanged; the default is supervised.

### Departures

- **Autonomous groom settles questions with defaults** (departs from [booping:rule/0004](../../../specs/rule/0004-questions-settled-in-grooming.md), "settle every open question with the user"): sanctioned by adr/0027; the departure is visible, each default a `D{n}` entry the user can review before develop.
- **Autonomous runs auto-confirm their one gate** (departs from adr/0015): sanctioned by adr/0027, which amends it for autonomous projects; supervised is unchanged.
- **The specs scenario branches in prose on a rendered line, not in a Jinja conditional** (stretches [value/0002](../../specs/value/0002-minimal-effective-context.md) — the body carries both branches, two lines): the eval harness feeds `prompt.md` raw, so only a rendered value with prose branches lets a smoke case cover the autonomous arm (C5).
- **Snapshot reports are accepted inside the run** (departs from [rule/0013](../../specs/rule/0013-snapshot-baselines-accepted-by-user.md)): the owner's standing permission for this feature (2026-10-14) allows `just snapshots-accept` when every drifted hunk is one this plan describes (M04: specs, M05: migrate); develop lists each accepted report in its defaults record.

## Decisions

- **Scope**: part 4 only; `project-manager` (adr/0028) stays its own request — C1.
- **Key**: `core.autonomy: supervised | autonomous`, directly under `core`, default `supervised`; unknown value → in-band STOP — C2.
- **One switch**: the driving partial's gate and questions rules render per mode; no playbook's gate text changes — C3.
- **Defaults record**: `defaults.md` beside the run artefact, written only by `booping defaults add`; artefact-less runs list defaults in their final report — C4.
- **Specs scenario**: preamble renders the mode; two prose lines branch on it; autonomous chains groom → develop in one session — C5.
- **Migrate**: branch named, answer always awaited, decline proceeds; notice amended — C6.
- **Output text**: locked below — C7. **No split** (18 SP) — C8.

## Architecture

```
{vault}/config.yaml  core.autonomy ──merge──▶ config
        │
        ├─ render / render-playbook ── invalid value ──▶ STOP notice (in band)
        ├─ _project_context.j2 ──▶ "autonomy: {mode}" on every skill load
        ├─ _playbook_driving.j2 step 5 + questions ──▶ supervised: stop & wait
        │                                           └─ autonomous: present, auto-confirm,
        │                                              booping defaults add ──▶ {run dir}/defaults.md
        └─ specs playbook.md preamble "Autonomy: {mode}" ──▶ guide ## Open items
                                                             └─ autonomous: /playbook groom → /playbook develop
migrate survey ── uncommitted work + branch ──▶ always asked (neither key answers it)
```

## Output contract

### Project context

Line added after `git_commit:` in the initialized block:

```yaml
autonomy: {supervised|autonomous}
```

### Invalid value

```
**STOP — tell the user:** `core.autonomy` is `{value}`; it must be `supervised` or `autonomous`. Fix it in the config tier that sets it, then retry.
```

### Driving protocol, autonomous

Step 5:

> 5. After the batch completes, honor each member's `Review gate:` bullet in autonomous mode (`core.autonomy`): present that member's returned receipt labeled by step name alongside the gate text, auto-confirm the gate yourself — taking the step's proposal as given, including a gate whose wording asks through `AskUserQuestion` — log it with `booping defaults add --target {run artefact} --step {playbook}/{step} --asked "{the gate's question}" --default "{what you confirmed}" --why "{why}"`, and continue without waiting. That logged confirmation stands for the user's approval wherever a transition gate names one. `{run artefact}` is the artefact the render's `## State` section names, resolved against the run workdir — or the `--target` the run's transitions address when the machine declares no `artifact:`. Without a `## State` section there is no run artefact: do not call `booping defaults add`; list the default in the completion report instead. Two things still stop: a `**STOP — tell the user:**` notice, and a question a step marks as always asked.

Questions paragraph:

> A step return carrying questions for the user (a `## Questions:` block or equivalent), or a question the run would otherwise park → settle each yourself: the step's recommended option, else its first, else the most conservative answer the request supports; log each through `booping defaults add` as above, and continue. Never use `AskUserQuestion` for them, except a question the step marks as always asked.

### Migrate

Survey, replacing "It is not the review gate and it never blocks — a user who declines still proceeds.":

> It is not the review gate, and it is always asked: name the current branch with the uncommitted work, and wait for the answer whatever `core.auto_migrate` and `core.autonomy` say — neither answers it for the user. A user who declines still proceeds.

Auto-migrate notice:

```
**Auto-migrate:** this project is behind on booping migrations (recorded id {recorded}, latest shipped {latest}). Run `/playbook migrate` now — `core.auto_migrate` is on, so its approval is taken as given; its question about uncommitted work is still asked — then continue with the original request.
```

### Specs preamble and open-items scenario

Preamble line, after the tier list:

```
Autonomy: `{{ config.core.autonomy }}` (`core.autonomy`).
```

Scenario, replacing its `Next:` sentence:

> Supervised: next is `/playbook groom` naming the picked ids — groom links them to the plan and stops at its plan review.
> Autonomous: run `/playbook groom` naming the picked ids — none picked, every `open` item — then `/playbook develop` on the plan it readies, in this session, without stopping; a groom that splits develops the first plan and reports the parked stubs.

### booping defaults add

Run anywhere inside a booping project; paths vault-relative. Exit `0` success, `1` user error with one `error: …` line on stderr and nothing on stdout.

- `defaults add --target PATH --step TEXT --asked TEXT --default TEXT [--why TEXT]`
  - `--target` — vault-relative run artefact; must exist (`error: target not found: {path}`) and resolve inside the vault (`error: target outside the vault: {path}`).
  - `--asked`, `--default` — non-empty after normalisation (`error: --default must not be empty`).
  - `--asked`, `--default`, `--why` — whitespace-normalised to one line (`' '.join(s.split())`) before writing, so a multi-line value cannot open a heading or break the entry.
  - stdout: `{sidecar}#D{n}`, e.g. `plans/x/defaults.md#D1`.

### defaults.md

Plain markdown, no frontmatter, seeded with `# Defaults` on the first `add`. One H2 per entry, in the order logged:

```markdown
# Defaults

## D1 — develop/provision — 2026-10-15 16:40

**Asked:** Confirm the branch name `feat/autonomy-modes`?

**Default:** `feat/autonomy-modes`, the proposed name

**Why:** core.autonomy is autonomous; the proposal follows the branch conventions

**Artifact:** [index.md](index.md)
```

- `D{n}` numbered from `D1` across the file, next = highest + 1, never reused.
- Heading: id, `--step` verbatim, local date and time (`core.macros.date`, `+%Y-%m-%d %H:%M`).
- `**Why:**` — `--why`, or `not stated` without it.
- `**Artifact:**` — a link to `--target`, relative to the sidecar.

## Milestones

| id | title | sp | status |
| --- | --- | --- | --- |
| 01 | [core.autonomy key, invalid-value STOP, project-context line](milestones/M01-the-autonomy-key/M01-the-autonomy-key.md) | 3 | done |
| 02 | [booping defaults add writes the defaults sidecar](milestones/M02-defaults-add-writes-the-sidecar/M02-defaults-add-writes-the-sidecar.md) | 4 | done |
| 03 | [The driving protocol renders gates and questions per mode](milestones/M03-driving-protocol-honours-the-mode/M03-driving-protocol-honours-the-mode.md) | 3 | done |
| 04 | [The specs open-items scenario honours the mode](milestones/M04-specs-open-items-honour-the-mode/M04-specs-open-items-honour-the-mode.md) | 3 | done |
| 05 | [Migrate always asks about uncommitted work on the branch](milestones/M05-migrate-always-asks-on-a-dirty-branch/M05-migrate-always-asks-on-a-dirty-branch.md) | 3 | pending |
| 06 | [Docs and CLAUDE.md name the mode](milestones/M06-docs-and-claude-md/M06-docs-and-claude-md.md) | 2 | pending |

## Final Verification

- [ ] `bin/booping render src/templates/skills/playbook.md.j2` shows `autonomy: supervised` and the unchanged supervised step 5; with `--set core.autonomy=autonomous` the autonomous step 5 and questions paragraph of `## Output contract`.
- [ ] Rendered skill body reviewed: no `{{placeholder}}` leaks, no stale "never blocks" wording in migrate.
- [ ] Targeted rules still inline into `bin/booping render-playbook groom`'s `## Rules`.
- [ ] `just snapshots` drifts only in `playbooks/specs/_reports/output.md` (M04) and `playbooks/migrate/_reports/output.md` (M05); each accepted per the run's snapshot policy.
- [ ] `just smoke specs/guide` passes all four cases.
- [ ] `just ci` is green.

## Out of scope

- The core `project-manager` playbook (adr/0028) — its own request; it will read `core.autonomy` when groomed. Its budget and window gates, run registry and computed status go with it.
- Retro reading `defaults.md` as a feed — the sidecar is findable now; wiring it into `prepare` is a follow-up.
- Per-playbook or per-run overrides of the mode — `--set core.autonomy=…` on a render already gives one run its own mode.
- Changing any playbook's `review_gate` text, `playbook.yaml` transition gates or groom's `awaiting-clarification` state — the driving protocol covers them (C3).
- A story record for the surface (the `docs` playbook owns stories).

## CLAUDE.md impact

Owned by M06: `## Commands` CLI list gains `defaults` (`add`); `## Config` gains a `core.autonomy` bullet; `## Lifecycle` gains a **Defaults** bullet beside **Corrections**.

## Risk register

- Snapshot drift in the specs and migrate reports (M04, M05) must be accepted before `just ci` can pass — cross-review flagged this against rule/0013. Disposition: the owner's standing permission for this feature (2026-10-14) covers it; the develop runner, never a worker, runs `just snapshots-accept` only when every drifted hunk is one M04 or M05 describes, and logs each accepted report as a default.

- An autonomous run waits forever on migrate's uncommitted-work question when nobody is there — accepted: adr/0027 calls that state one that should not exist and wants it asked in either mode.
- The driver may still reach for `AskUserQuestion` from a gate's own wording (develop's provision) — mitigated: the autonomous step 5 names that case explicitly.
- A value typo silently meaning supervised — removed by the STOP (C2).
- `booping defaults add` duplicates the correction writer's seeding and numbering — accepted for now; extracting a shared sidecar writer is a refactor the worker may do in M02 only if it keeps both corpora green.
