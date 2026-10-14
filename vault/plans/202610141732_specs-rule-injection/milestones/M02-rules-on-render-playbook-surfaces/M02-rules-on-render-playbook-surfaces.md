---
id: "02"
title: "Rules section on the render-playbook surfaces"
sp: 9
status: done
plan: "vault/plans/202610141732_specs-rule-injection/index.md"
---

# M02: Rules section on the render-playbook surfaces

`booping render-playbook` prints a `## Rules` section before `## Lessons` on the composed, `--step` and inline-step surfaces for every targeted rule matching the playbook or step, raises non-blocking notes for rules it cannot take, and accepts `--no-rules`.

**Scope**: `booping render-playbook {name} [--step {step}] [--no-rules]`. Files: `booping-python/src/booping/commands/render_playbook.py`, new partial `src/templates/_partials/_rules.j2`, new e2e cases under `booping-python/e2e/cases/render-playbook/`. Consumes `Context.targeted_rules` / `Context.rule_skips` from M01. Callers: the `/playbook` skill reads this stdout; the committed `playbooks/*/_reports/output.md` are renders of it (their drift is the owner's to accept — never run `just snapshots-accept`, never write `_reports/`).

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | `_rules.j2` partial (args `rules`, `surface`) and matching: generalize `playbook_lessons` / `step_lessons` to any item with `parsed_targets` and use them for rules; render `## Rules` directly before the lessons section on the composed surface, the `--step` surface and inline-step sections | `src/templates/_partials/_rules.j2`, `booping-python/src/booping/commands/render_playbook.py` | 3 | done |
| 2.2 | `--no-rules` flag: strips every rules section and every rule notice; `--no-lessons` unchanged | `booping-python/src/booping/commands/render_playbook.py` | 1 | done |
| 2.3 | Rule notices: one `**Note — tell the user:**` per `RuleSkip` and per rule step target naming a step this playbook lacks | `booping-python/src/booping/commands/render_playbook.py` | 2 | done |
| 2.4 | e2e cases pinning the section, the notices and the flag; rebaseline the `--help` case | `booping-python/e2e/cases/render-playbook/*.txtar` | 3 | done |

Section content (locked, [clarifications.md](../../clarifications.md) C1), byte for byte:

```
## Rules

The following {n} rule(s) apply to this {playbook|step}. Never silently violate one{; conflict → stop and flag}. Read a rule's record when its brief is not enough.

- **{title}** — {brief} [{ref}]({link})
```

`; conflict → stop and flag` on the playbook surface only, as the lessons section does. One bullet per rule, M01's order. Title and brief inserted as variables, never Jinja-rendered. No rules → no section and no blank lines left behind.

Notice texts (C6):

- skip: `**Note — tell the user:** rule {path} is not injected — {reason}. Run \`booping specs check\` on its tier.`
- unknown step: `**Note — tell the user:** rule {path} targets step \`{step}\` of playbook \`{name}\`, which has no such step.`

`{path}` is the rule's `link` value. Skip notices print on every `render-playbook` surface that prints notices today; unknown-step notices only when rendering the targeted playbook.

## Definition of Done

### Task 2.1

- [x] A playbook-targeted rule renders in the composed output's `## Rules` section, before `## Lessons` when both exist, at the lessons position when only rules exist.
- [x] A `{playbook}/{step}`-targeted rule renders on that step's `--step` output and its inline-step section, never on the composed playbook section.
- [x] One partial serves both surfaces; the matching helpers are shared by lessons and rules (no second copy of the target-matching logic).

### Task 2.2

- [x] `--no-rules` removes every rules section and rule notice; lessons unaffected.
- [x] `render-playbook --help` lists `--no-rules`.

### Task 2.3

- [x] Both notice texts print exactly as above; exit code stays 0.
- [x] An untargeted or retired rule raises nothing.

### Task 2.4

- [x] New cases, tier fixtures built in the case: core tier via an xdg config setting `core.specs.tiers.core.path: ~/core-specs` (`~` is the case's home) and `namespace: fx`; global tier under `home/Claude/_specs/` with an explicit `core.specs.tiers.global.namespace`; project tier under the case's repo.
- [x] Cases cover: section shape with one rule per tier in core/global/project order with each ref and link form; step-targeted rule on `--step` and on an inlined step only; rules before lessons; retired and untargeted rules render nowhere; core and project on one directory renders each rule once; both notices; `--no-rules`; a `--project` pinned render drops the global rule.
- [x] `help-lists-every-flag-including-no-lessons.txtar` rebaselined with `--txtar-update` and nothing else in it changed; any other case that moves is listed in the return.

## References

- `booping-python/e2e/cases/render-playbook/the-lessons-section-is-a-count-sentence-then-one-heading-per-lesson.txtar`, `step-lessons-are-appended-to-an-inlined-step-section.txtar`, `a-lesson-targeting-an-unknown-step-is-a-non-blocking-note.txtar` — case shapes to copy.
- `src/templates/_partials/_playbook_lessons.j2` — partial shape; `booping-python/e2e/README.md` — case-format notes.

## Verify

`just e2e -k render-playbook` — all pass.

Return: only the list of changed files and the list of rebaselined e2e cases, then the last line of the Verify output.
