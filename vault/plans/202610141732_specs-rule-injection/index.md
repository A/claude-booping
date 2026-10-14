---
title: "Specs rule injection — targeted rules from three tiers into playbook, agent
  and skill bodies"
type: "feature"
status: in-progress
sp: 23
related_to: plans/202610141731_specs-core-format-cli-injection/index.md
created: 2026-10-14 17:42
planned: null
started: 2026-10-14 19:10
completed: null
code_reviews: []
sessions:
- 49e4cb90-6c29-4738-81f1-88d4adc4b259
- 6b70255a-7607-4a86-8613-75a66a61dcfc
retro: null
summary: Inject accepted targeted rules from core, global and project specs 
  tiers as brief plus link beside lessons
commit: 4964ceb611e30b662a4f88cf77569c315a5e087d
tracker_provider: null
tracker_request: null
tracker_issue: null
return_to: null
agents:
  research-codebase: a698a450f756f2eff
  cross-review: a93bb738fbcd23a8a
  intake: ac6da67f7546f6634
  develop-loop/M01-targeted-rule-loader: ada3895535401bc57
  develop-loop/M02-rules-on-render-playbook-surfaces: a435d26f994e4ef88
  develop-loop/M03-rules-in-agent-and-skill-bodies: a0cf51434bae97dbf
  develop-loop/M04-rule-injection-docs: a37bffa08489583c7
  verify: a08b9b2abce2c9e90
reviewed_at: 2026-10-14 19:07
---

# Specs rule injection — targeted rules from three tiers into playbook, agent and skill bodies

## Context

`booping render-playbook` (composed, `--step`, inline-step surfaces) and the internal agent and skill bodies inject targeted **lessons** today, from `<home_dir>/_lessons/` and `{vault}/_lessons/`. The parent plan ([specs core format, CLI](../202610141731_specs-core-format-cli-injection/index.md), done) shipped the specs format with three tiers (`core.specs.tiers`) and rules carrying `targets:` + `brief:`, but no render surface reads them: a targeted rule is documentation only. After this plan, every surface that injects lessons also prints a `## Rules` section listing each `status: accepted` rule from the core, global and project tiers whose `targets:` match — its brief plus a link to the record ([rule/0001](../../specs/rule/0001-lessons-are-rules.md)) — and lessons keep working unchanged beside it. Request and framing: [request.md](request.md); every default this autonomous run took: [clarifications.md](clarifications.md).

## Decisions

- **One loader, two consumers**: `booping.specs.rules.load_targeted_rules(tiers)` fills `Context.targeted_rules` / `Context.rule_skips`; render-playbook and the agent/skill partials only select and render — the lessons split between loader and surface, mirrored ([value/0003](../../specs/value/0003-single-source.md)).
- **Which rules**: `status: accepted` with both `targets` and `brief`; retired and untargeted rules never inject (parent C11 relies on this to keep rule/0013 and rule/0015 booping-only).
- **Brief plus link, one line per rule**: locked content in clarifications C1 — a step gets the brief and reads the body on demand ([value/0002](../../specs/value/0002-minimal-effective-context.md)).
- **Ref and link per tier** (C2): ref namespaced as specs refs are; core link `${CLAUDE_PLUGIN_ROOT}/…`, project link repo-relative, global absolute — the two forms that reach hermetic renders are machine-independent ([rule/0027](../../specs/rule/0027-renders-reproducible.md)).
- **Tier coincidence** (C3): dedupe by realpath, first tier in core → global → project order wins — booping's own repo has core and project on `vault/specs/`.
- **Placement** (C4): `## Rules` directly before `## Lessons`.
- **Opt-out** (C5): separate `--no-rules`; `--no-lessons` unchanged.
- **Problems in band** (C6): skipped targeted rules and unknown-step targets are non-blocking notes on render-playbook surfaces ([rule/0029](../../specs/rule/0029-failures-reported-in-band.md)); `booping specs check` stays the validator.
- **Pinned renders**: the global tier is dropped under `--project` as `resolve_tiers` already does; core and project stay, so core rules show in the committed reports (parent C13).
- **Lessons untouched**: no lesson file, loader or surface changes; lesson/rule duplicates in booping's own runs are accepted (parent C12); `learn` keeps writing lessons (C8).

## Architecture

```
Context.assemble()
  ├─ Lesson.load_targeted(...)            → targeted_lessons           (unchanged)
  └─ resolve_tiers(cfg, …, vault_override) → [core, global?, project?]
       └─ load_targeted_rules(tiers)       → targeted_rules, rule_skips (M01)

render-playbook  ── playbook/step matching (shared with lessons) ── _rules.j2 ── ## Rules  (M02)
                 └─ rule_skips + unknown-step targets ── **Note — tell the user:**       (M02)
agent/skill body ── _targeted_rules.j2 (agent:{id} | skill:{name}) ── _rules.j2         (M03)
```

Callers of the output: the `/playbook` skill reads render-playbook stdout; agent and skill thin shells render their bodies at load via `booping render`; `scripts/snapshots.py` renders every core playbook with `--project playbooks/_fixtures/vault` into the committed `_reports/output.md`. Today's targeted core rules (0001 → learn, 0004 → groom, develop, 0006 → groom, 0007–0010 → groom/draft-plan) move the groom, develop and learn reports.

## Milestones

| id | title | sp | status |
| --- | --- | --- | --- |
| 01 | [Targeted rule loader across the three tiers](milestones/M01-targeted-rule-loader/M01-targeted-rule-loader.md) | 7 | done |
| 02 | [Rules section on the render-playbook surfaces](milestones/M02-rules-on-render-playbook-surfaces/M02-rules-on-render-playbook-surfaces.md) | 9 | done |
| 03 | [Rules section in agent and skill bodies](milestones/M03-rules-in-agent-and-skill-bodies/M03-rules-in-agent-and-skill-bodies.md) | 4 | done |
| 04 | [Document rule injection](milestones/M04-rule-injection-docs/M04-rule-injection-docs.md) | 3 | done |

## I/O contract

- **Arguments / flags**: `booping render-playbook {name} [--step {step}] [--project {vault}] [--no-lessons] [--no-rules]` — `--no-rules` is new and drops every rules section and rule notice. `booping render {template}` takes no new flag.
- **stdin**: none.
- **stdout**: markdown. New section, byte for byte (C1):

  ```
  ## Rules

  The following {n} rule(s) apply to this {playbook|step|agent|skill}. Never silently violate one{; conflict → stop and flag}. Read a rule's record when its brief is not enough.

  - {brief} [{ref}]({link})
  ```

  `; conflict → stop and flag` on the composed playbook surface only. New notices among the existing ones: `**Note — tell the user:** rule {link} is not injected — {reason}. Run \`booping specs check\` on its tier.` and `**Note — tell the user:** rule {link} targets step \`{step}\` of playbook \`{name}\`, which has no such step.`
- **stderr**: unchanged.
- **Exit codes**: unchanged — `0` on every render including one carrying rule notices; existing usage errors keep theirs.

## Final Verification

- [ ] Help text lists `--no-rules`.
- [ ] Happy path: `bin/booping render-playbook groom` from this repo shows `## Rules` with rule/0004 and rule/0006 once each, `booping:` refs, `${CLAUDE_PLUGIN_ROOT}/vault/specs/rule/…` links; `--step draft-plan` shows 0007–0010.
- [ ] Failure path: a targeted rule with a bad target yields its note at exit 0 (pinned by an M02 e2e case).
- [ ] The rendered `/playbook` skill body and both internal agent bodies render cleanly (`bin/booping render src/templates/skills/playbook.md.j2`, `…/agents/booping-researcher.md.j2`).
- [ ] `just lint typecheck pytest e2e mdcheck specs-check docs` green.
- [ ] `just snapshots` shows drift only in `playbooks/{groom,develop,learn}/_reports/output.md`, only `## Rules` sections; the runner shows it to the owner, who accepts it — no run writes `_reports/` ([rule/0013](../../specs/rule/0013-snapshot-baselines-accepted-by-user.md)). `just ci` is green after the owner accepts.

## Out of scope

- Migrating `_lessons/` to rules, retiring lessons, changing `learn` to write rules (C8).
- Rule injection anywhere lessons are not injected today; the orphaned `src/templates/_partials/_lessons.j2`.
- Eval suites or fixtures re-tuned for the new section (evals run on demand, never in CI).
- Retargeting or editing any `vault/specs/` rule (parent C11 already settled the core set).

## CLAUDE.md impact

Playbooks section gains a **Rules** bullet beside **Lessons**; Principles → Agent wiring says "a targeted lesson or rule" (M04 task 4.2). The Commands section's `bin/booping` line needs no change — no new subcommand.

## Risk register

- **mdcheck over the new reports**: the `## Rules` section may trip a structural rule of `just mdcheck` once the reports are accepted — runner checks it before asking the owner to accept; a failing rule is fixed in `_rules.j2`, not in the mdcheck config.
- **Dev checkout ≠ plugin root**: with an installed plugin next to a worktree, core and project rules are different files and both inject (C3) — booping-dev only, accepted.
- **rule/0001 vs learn's body** (C8): the injected brief contradicts learn's current lesson-writing steps until the lessons migration; the playbook surface's "conflict → stop and flag" surfaces it.
