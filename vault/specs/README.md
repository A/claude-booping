# specs/

Booping's own specs, written in the format booping will ship as a core feature: why
booping exists and what it is like (values), the constraints every decision obeys
(rules), the decisions with their rejected alternatives (ADRs), and the rest of what
the code cannot show. This set is also the dogfood of the format itself — the rules
on how records are written live here as records.

What lives where:

- **`vault/specs/`** — why and where the boundaries are: values, rules, decisions.
- **Vault artefacts** (`plans/`, `retrospectives/`, `codereviews/`, `notes/`) — work
  and its history; a decision made in a run goes up into an ADR here.
- **Code** (`booping-python/`, `booping-tracker/`, `playbooks/`, `src/`) — how things
  work. Anything recoverable from code, config or tests is documented only there.
- **`documentation/`** — the public docs site, for users; `docs/` — fragments the
  skills lazy-load at runtime.

`vault/docs/_specs/` (briefing, roles, features, targets, glossary, documented) is
deprecated: its content moves here; it stays until the `docs` playbook reads from
here. `vault/_lessons/` likewise stays until lesson injection reads rules
([rule/0001](rule/0001-lessons-are-rules.md)).

## Tiers

Specs come in three tiers ([adr/0001](adr/0001-specs-tiers.md)):

| Tier    | Where                                                    | Holds                                         |
|---------|----------------------------------------------------------|-----------------------------------------------|
| core    | this directory, shipped with booping                     | booping's values and rules, the format itself |
| global  | `<home_dir>/_specs/`                                     | one person's values and rules for every project |
| project | `specs/` in the project repo, or `<vault>/specs/` when the vault is in the repo | the project's own records |

A reference without a namespace points into its own tier: `rule/0003`. Another tier is
named by its namespace: `booping:rule/0003` for core, `<user>:rule/0003` for the global
tier (the id defaults to `$USER` and is confirmed at setup). A project that departs
from a rule of a tier above records it in its own ADR or conflict.

## Types

| Type       | Directory          | What for                                                          |
|------------|--------------------|-------------------------------------------------------------------|
| `values`   | `values/`          | Why it exists and what it is like; one file per area              |
| `rule`     | `rule/`            | A constraint every decision obeys, following from a value or a source |
| `adr`      | `adr/`             | One durable choice: context, options, decision, consequences      |
| `conflict` | `conflict/`        | Two or more values pulling apart, and how that is settled         |
| `story`    | `story/`           | Who wants what and why                                            |
| `idea`     | `idea/`            | A raw idea: the cheapest check that gives a verdict               |
| `reference`| `reference/`       | Facts the code does not show, one subject per file                |
| `runbook`  | `runbook/`         | An operator procedure the code does not show                      |

The shape of each type is `schemas/<type>.yaml`, a
[mdcheck](https://github.com/A/markdown-checker) rule file.

## Files

- One record — one markdown file with YAML frontmatter.
- Name — `<NNNN>-<slug>.md`: a four-digit number running within the type (the next
  one is the highest plus one) and a kebab-case latin slug.
- A reference to a record is `<type>/<NNNN>` (`adr/0001`); to one value, by anchor:
  `values/0001#adjustable-control`. In the body, references are ordinary relative
  markdown links.

## Frontmatter

Common to every type:

- `type` — the type, same as the directory;
- `title` — the title (`A ↔ B` for a conflict);
- `summary` — one line up to 200 characters: what is claimed, not what it is about;
- `created_by` — `owner` or `claude`;
- `created_at`, `updated_at` — `YYYY-MM-DD`;
- `reviewed` — optional, the date the owner read the record, as a `YYYY-MM-DD`
  string; only the owner sets it, never an agent. Empty — the owner has not read it
  yet, so what an agent did alone stays visible;
- `sources` — optional, the vault artefacts or files a record was distilled from
  (`[playbooks/groom/_specs/DECISIONS.md, retrospectives/…]`).

By type:

- `values` — no `status`.
- `rule` — `status`: `accepted` or `retired` (a retired rule stays so it is not
  reinvented). Optional `targets:` — where the rule is injected (`groom`,
  `develop/run`, `agent:<id>`, `skill:<name>`) — and `brief:`, the one or two lines
  injected there.
- `adr` — `status`: `proposed`, `accepted`, `superseded`, `rejected`; optional
  `values`, `rules`, `supersedes`.
- `conflict` — `status`: `open` or `resolved`; `values` — at least two value anchors.
- `story` — `status`: `done`, `planned`, `deferred`.
- `idea` — `status`: `open`, `validating`, `accepted` (went on: an ADR, a story, a
  plan), `rejected` (stays so it is not proposed again).
- `reference`, `runbook` — `status`: `live` or `retired`.

Reference fields are lists like `[values/0001#single-source, rule/0003]`. Back
references are not written.

## Body

- `values` — `## Values`, a `###` per value: a paragraph, then two items
  `**In practice:**` and `**Trade-off:**`; optional `## Not valued`.
- `rule` — `## Rule`, `## Follows from` (each item links a value, or the source a
  learnt rule came from: a retro, a review, an incident), optional `## Exceptions`.
- `adr` — `## Context`, optional `## Criteria`, `## Decision`, `## Alternatives`,
  `## Consequences`. Alternatives: a table `Option | Status | Complexity |
  Reversibility | Verdict` of 2-4 rows (the option links its own `###`), then a `###`
  per option: a paragraph, then `**Pros:**`, `**Cons:**`, `**Complexity:**`,
  `**Reversibility:**`. One record — one choice that is final, had a real
  alternative, and whose reason cannot be recovered from the code in minutes; the
  history of who decided when goes nowhere.
- `conflict` — `## Conflict`; `## Resolution` only when `resolved`.
- `story` — one sentence "As **who**, I want …, so that …" and `## Criteria`, one to
  five items.
- `idea` — `## Idea`, `## How to check` (the cheapest check that gives a verdict),
  `## Verdict` once checked: what came out, with a date, and where the idea went.
- `reference` — `## Facts` (one fact per item, with a date or version when it
  matters), optional `## How to check`.
- `runbook` — `## When`, optional `## Before you start`, `## Steps` (numbered),
  `## Check`, optional `## Rollback`.

A record states only what its source says
([rule/0002](rule/0002-unknown-is-marked.md)): what the source lacks is "not named in
the source", a reason that is only a preference is called the owner's preference.

## Marks

At the start of an item or sentence, then one sentence on what to settle:

- `[clarify]` — needs the owner's decision: a default the agent chose, an open
  detail of an accepted decision;
- `[unknown]` — the record disagrees with the code, and which is right is not
  confirmed.

List: `rg -n '\[(clarify|unknown)\]' vault/specs/`.

## Check

```
just specs-check
```

Checks every record against its type's schema (mdcheck). Shape of one file only:
unique numbers, link targets and anchors are not checked yet.
