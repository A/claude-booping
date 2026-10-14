# Clarifications

Autonomous groom run on 2026-10-14: the owner was unavailable, so every question below was settled by the run with the default marked "default applied". Each stays reviewable and amendable before develop starts ([value/0009](../../specs/value/0009-adjustable-control.md), [rule/0002](../../specs/rule/0002-unknown-is-marked.md)).

## C1 — split of the request — answered

**Asked:** 2026-10-14 — intake

**Question:** The five items together run past the 35 SP split threshold. Where is the dependency seam?

**Options:**

- This plan: `learn` writes rules, a `booping specs init` mechanic, `setup` provisions both tiers, rule/0001 regains its targets, and the docs of those; parked: the lessons migration, rule-only injection and booping's own vault migration (default applied)
- This plan: migration + rule-only injection; parked: learn and setup

**Answer:** First option — default applied. This plan ships on its own: existing lessons keep injecting while every new learning lands as a rule, so no state between the plans is broken. The second order is not shippable alone: removing lesson injection while `learn` still writes lessons makes every new lesson inject nowhere. The parked plan is useless without this one, which is the seam the groom's split rule asks for. Parked stub: see `index.md` `## Parked siblings`.

## C2 — fate of `--no-lessons` — answered

**Asked:** 2026-10-14 — intake

**Question:** When lesson injection goes (parked plan), is `--no-lessons` kept as an alias of `--no-rules` or removed?

**Options:**

- Removed (default applied)
- Alias of `--no-rules`

**Answer:** Removed — default applied, recorded here for the parked plan. [value/0003](../../specs/value/0003-single-source.md): an alias is two names for one switch and keeps a dead concept in `--help` and the docs. Nothing outside the e2e corpus and `documentation/playbook.md` passes it (grep, 2026-10-14), so no caller breaks.

## C3 — tier creation is a CLI verb — answered

**Asked:** 2026-10-14 — draft-plan

**Question:** Three surfaces need to create a specs tier — `learn` (first rule in a project without a tier), `setup`, and the parked migration. Prose in each, or one mechanic?

**Options:**

- New verb `booping specs init --tier {global|project}` (default applied)
- Each playbook step creates the directories itself

**Answer:** New verb — default applied. [rule/0025](../../specs/rule/0025-mechanics-run-as-code.md) (deterministic mechanics run as code) and [value/0003](../../specs/value/0003-single-source.md). Behaviour:

- `--tier project` (default): resolves the root as `booping specs` does. Vault inside the repo → creates `{vault}/specs/`. Vault outside the repo → creates `{repo}/specs/` and the symlink `{vault}/specs → {repo}/specs` ([adr/0001](../../specs/adr/0001-specs-tiers.md)).
- `--tier global`: creates `{home_dir}/_specs/`.
- `--tier core`: rejected (the plugin ships it).
- Writes the tier README only when absent; never overwrites an existing file; a second run changes nothing.
- An existing `{vault}/specs` that is not a symlink to `{repo}/specs` when the vault is outside the repo → exit 1, nothing written.

## C4 — `specs init` output and README content — answered

**Asked:** 2026-10-14 — draft-plan

**Question:** [rule/0010](../../specs/rule/0010-output-content-locked-in-grooming.md) wants the exact content locked. Stdout and tier README?

**Answer:** Default applied. Stdout, one line per action in the order taken, then the tier root:

```
created dir {path}
created file {path}
linked {link} -> {target}
{absolute tier root}
```

Nothing to do → only the last line. Errors go to stderr as `specs init: {message}`, exit 1. Paths in action lines are absolute.

Project tier `README.md`:

```
# specs/

This project's specs tier: values, rules, ADRs and the other typed records, in booping's specs format — the guide is `src/specs/README.md` in the booping plugin. Check with `booping specs check --tier project`.
```

Global tier `README.md` (`{namespace}` = the resolved global namespace):

```
# _specs/ — global tier (namespace `{namespace}`)

One person's values and rules for every project, in booping's specs format — the guide is `src/specs/README.md` in the booping plugin. Referenced from a project as `{namespace}:rule/NNNN`. Check with `booping specs check --tier global`.
```

## C5 — the rule record learn writes — answered

**Asked:** 2026-10-14 — draft-plan

**Question:** Shape of a learnt rule?

**Answer:** Default applied, per `src/specs/README.md`:

- Path `{project tier root}/rule/{NNNN}-{slug}.md`; the root is the last stdout line of `booping specs init --tier project` (run first, it creates the tier when absent), `{NNNN}` from `booping specs next rule --tier project`.
- Frontmatter: `type: rule`, `title`, `summary`, `created_by: claude`, `created_at`/`updated_at` = run date, `status: accepted`, `targets:` = the row's Targets cell, `brief:` = the row's Brief cell (quoted), `sources:` = the retro path relative to the repo root when the vault is inside the repo, omitted otherwise (a `sources` entry must resolve against the repo root). `reviewed` is never written — only the owner sets it ([value/0009](../../specs/value/0009-adjustable-control.md)).
- Body: `## Rule` — a compact paragraph plus one example line; `## Follows from` — a link to the value it follows from when one of the project's or booping's values names it, else the retrospective (a relative link when the vault is inside the repo, else the plain text `retrospectives/{slug}.md` in the project vault, since a record behind the symlink cannot link into the vault).
- After writing: `booping specs check --tier project` must report no error on the new files.

## C6 — learn's reach across tiers — answered

**Asked:** 2026-10-14 — draft-plan

**Question:** `learn` writes only the project tier. What happens to a candidate already covered by a core or global rule, or by a lesson?

**Answer:** Default applied:

- Covered by a core or global rule, or a global lesson → sweep verdict `covered by {ref}`; the row is shown with Type `covered` and never written.
- Conflicting with a core or global rule → verdict `conflict with {ref}`; if accepted, written as a project rule whose body carries a `[clarify]` mark naming the departed rule — `src/specs/README.md` wants a departure recorded in an ADR, which is the owner's call, not learn's.
- Duplicate of a project rule → `update existing at rule/NNNN`, edited in place (`updated_at` bumped).
- Duplicate of a lesson in `{vault}/_lessons/` → `update existing at _lessons/{file}`, written as a new project rule carrying the merged content, and the lesson file deleted in the same run — learn never writes or edits a lesson again ([rule/0001](../../specs/rule/0001-lessons-are-rules.md)).

## C7 — learn commit — answered

**Asked:** 2026-10-14 — draft-plan

**Question:** The closing hook stages `_lessons` today. What does it stage now?

**Answer:** `close-working-set --stage _lessons specs` — default applied. `_lessons` stays for a lesson deleted by a C6 conversion; `specs` stages the project tier when it is inside the vault. When the vault is outside the repo, `{vault}/specs` is a symlink and the records live in the repo, uncommitted for the user, exactly as learn's `CLAUDE.md` bullets are today ([rule/0019](../../specs/rule/0019-driver-owns-vault-workers-own-code.md)).

## C8 — setup and the global namespace — answered

**Asked:** 2026-10-14 — draft-plan

**Question:** Where does setup store the global namespace, and when does it ask?

**Answer:** Default applied. `setup-booping` asks once, default `$USER`, and writes `core.specs.tiers.global.namespace: {id}` into the global config (`${XDG_CONFIG_HOME:-~/.config}/booping/config.yaml`) beside `home_dir`, keeping every other key; a config already carrying the key is not asked again. It then runs `booping specs init --tier global`. `setup-project` runs `booping specs init --tier project` once the vault and marker exist. The vault scaffold's `_lessons:` entry stays until the parked plan removes lessons.

## C9 — rule/0001 restored — answered

**Asked:** 2026-10-14 — draft-plan

**Question:** rule/0001's targets and brief?

**Answer:** Default applied: `targets: [learn]`, `brief: "Write every accepted learning as a rule record in the project specs tier (targets, a self-sufficient one-or-two-line brief, Rule and Follows from) or as a repo CLAUDE.md bullet; never as a lesson file."` `## Exceptions` removed, `updated_at: 2026-10-14`.

## C10 — learn evals — answered

**Asked:** 2026-10-14 — draft-plan

**Question:** The `extract-candidates` and `write` suites assert lesson output. Update and run?

**Answer:** Default applied: fixtures and asserts move to rules; the milestone runs the deterministic `smoke` tier only, with `EVAL_PR=0` (no PR comment); `regress` (llm-rubric) is left to the owner. Evals never gate CI.

## C11 — docs scope of this plan — answered

**Asked:** 2026-10-14 — draft-plan

**Question:** Which docs move in this plan?

**Answer:** Default applied: only what this plan changes — learn's destinations and review table, `specs init`, setup's tier and namespace, rule/0001. Lesson injection docs (`documentation/playbook.md` `#lessons`, `--no-lessons`) stay true until the parked plan and move with it ([rule/0007](../../specs/rule/0007-stale-references-cleaned-in-sprint.md) binds per sprint, and nothing this plan does stales them).
