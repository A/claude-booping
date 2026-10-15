---
type: adr
title: Specs are a core feature in three tiers
summary: Booping ships the specs format and its own specs; a global tier in the home dir and a project tier in the repo add their records, cross-tier refs go by namespace.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-15
status: accepted
values: [value/0003, value/0005, value/0011, value/0001]
rules: [booping:rule/0001]
---

## Context

The typed-records specs system (values, rules, ADRs, conflicts, stories, ideas,
references, runbooks) grew in one project and was copied into four: three game
projects and an assistant project. The copies drifted — none of the five shared
schemas match — and the cross-file checker exists in one copy only. Some decisions
belong to no single project: an engineering practice such as fakes and DI over mocks
applies to every project of one person. Booping already merges config, playbooks and
lessons across three tiers (core → global → project) and ships migrations with a
watermark in the project marker. The owner settled the shape in an alignment session
on 2026-10-14.

## Criteria

- One source for the format; projects stop drifting apart.
- A person's cross-project rules live once, not in each project.
- Everything stays reachable from the Obsidian vault.
- A rule from another tier resolves to the same record on every machine.

## Decision

The specs format is a core feature of booping, in three tiers:

- **core** — booping's repo: the format (README, schemas, later the checker and the
  setup and upgrade playbooks) and the shipped records in `specs/`, beside the core
  `playbooks/` — the rules whose `targets` steer core playbooks for every user.
  Booping's records about its own development — values, ADRs, stories, references,
  ideas, runbooks and the rules that concern only booping — are booping's project
  tier, `vault/specs/`, which is also the dogfood of the format.
- **global** — `<home_dir>/_specs/`, booping's existing global config level: one person's values and rules for every project.
- **project** — the project's vault itself: the type directories (`value/`, `rule/`,
  `adr/` …) sit at the vault root beside `plans/` and `retrospectives/`, with no `specs/`
  directory in between, so Obsidian shows them directly (owner, 2026-10-15). A project
  that wants specs to change in the same commit as its code points the tier at a
  directory in its repo instead, and the vault links to it.

A reference without a namespace points into its own tier. Another tier is named by a
namespace — `booping:` for core, the user's id for the global tier (default `$USER`,
confirmed at setup) — never by a path such as `~`, so the same reference names the
same person's record on every machine. An unresolved namespace (a collaborator, CI)
is a warning, not an error. A project that departs from a rule of a tier above
records it in its own ADR or conflict. Changes to the format reach projects as
booping migrations. Lessons become rules with `targets` and `brief`
([booping:rule/0001](../../../specs/rule/0001-lessons-are-rules.md)).

## Alternatives

| Option | Status | Complexity | Reversibility | Verdict |
|---|---|---|---|---|
| [Core feature of booping](#core-feature-of-booping) | accepted | medium | medium | Reuses booping's tiers, migrations and vault |
| [A separate specs repo](#a-separate-specs-repo) | rejected | medium | high | A second tier system next to booping's |
| [Copies per project](#copies-per-project) | rejected | low | high | What exists now; already drifted |

### Core feature of booping

Booping ships the format and merges the global and project tiers the way it merges
config and playbooks.

- **Pros:** booping's tier merge, migrations and vault already exist; lessons and
  rules join into one record; one place to look in Obsidian.
- **Cons:** booping grows; a project that wants specs needs booping.
- **Complexity:** medium — a checker, setup and upgrade playbooks, lesson injection
  from rules.
- **Reversibility:** medium — the records are plain files and outlive the tooling.

### A separate specs repo

A standalone repo with the guide, the schemas and the checker; projects vendor it
and are asked periodically to look at its updates.

- **Pros:** usable without booping.
- **Cons:** a second tier and update mechanism next to booping's; lessons stay a
  separate thing from rules.
- **Complexity:** medium.
- **Reversibility:** high.

### Copies per project

Each project keeps its own copy of the format and its own checker.

- **Pros:** no shared dependency.
- **Cons:** the copies drift — they already have; a person's cross-project rules
  repeat in every project or live outside specs.
- **Complexity:** low.
- **Reversibility:** high.

## Consequences

- `vault/_lessons/` was converted into rule records and removed by
  [migration 004](https://github.com/A/claude-booping/blob/master/migrations/004_lessons_to_rules/migration.md).
- The existing project copies migrate after the feature ships, each with a commit
  before the migration for rollback.
- [clarify] An exported global tier that a project imports, so a namespace resolves
  without the home dir, is out of scope for now.
- 2026-10-15: the core tier moved from `vault/specs/` to `specs/` at the repo root and
  holds only the shipped targeted rules; `vault/specs/` became booping's project tier.
  With both on one directory, a booping-only rule could not keep `targets` without
  reaching every user — rule/0013 and rule/0015 got their targets back as project rules.
- Confirmation: `just specs-check` validates both tiers; a project set up by the setup
  playbook resolves a `booping:` and a global reference.
- 2026-10-15: the project tier became the vault root itself — type directories beside
  `plans/`, no `specs/` in between; specs kept in a repo are the exception, linked
  into the vault. Specs that live in a notes repo do not change in the same commit as
  the code; open items and a specs sync catch the drift instead.
