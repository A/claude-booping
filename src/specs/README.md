# Specs format

The format of a specs tier: why a project exists and what it is like (values), the
constraints every decision obeys (rules), the decisions with their rejected
alternatives (ADRs), and the rest of what the code cannot show. Every tier follows
this guide; the tier root is the directory holding a tier's type directories.

## Tiers

Specs come in three tiers:

| Tier    | Where                                                    | Holds                                         |
|---------|----------------------------------------------------------|-----------------------------------------------|
| core    | shipped with booping, at `specs/` in the plugin          | booping's rules for every project             |
| global  | `<home_dir>/_specs/`                                     | one person's values and rules for every project |
| project | the vault root — type directories beside `plans/`; or a repo directory set by `core.specs.tiers.project.path`, linked into the vault as `<vault>/specs` by `booping specs init` | the project's own records |

A reference without a namespace points into its own tier: `rule/0003`. Another tier is
named by its namespace: `booping:rule/0003` for core, `<user>:rule/0003` for the global
tier (the id defaults to `$USER` and is confirmed at setup). A project that departs
from a rule of a tier above records it in its own ADR or conflict. A tier is created with
`booping specs init --tier global|project`.

## Types

| Type       | Directory          | What for                                                          |
|------------|--------------------|-------------------------------------------------------------------|
| `value`    | `value/`           | One value: why it exists and what it is like, or a non-value      |
| `rule`     | `rule/`            | A constraint every decision obeys, following from a value or a source |
| `adr`      | `adr/`             | One durable choice: context, options, decision, consequences      |
| `conflict` | `conflict/`        | Two or more values pulling apart, and how that is settled         |
| `story`    | `story/`           | Who wants what and why                                            |
| `idea`     | `idea/`            | A raw idea: the cheapest check that gives a verdict               |
| `reference`| `reference/`       | Facts the code does not show, one subject per file                |
| `runbook`  | `runbook/`         | An operator procedure the code does not show                      |

These are the shipped types. The shape of each is [`schemas/<type>.yaml`](schemas/), a
[mdcheck](https://github.com/A/markdown-checker) rule file; a tier's types are the
stems of its effective schema set (below).

## Tier schemas

A tier root may hold its own files beside the type directories:

- `_schemas/<type>.yaml` — a mdcheck rule file. A stem the shipped set has overrides
  that type's shape for this tier; a new stem adds a type, with its own `<type>/`
  directory. The overlay is per tier: a tier's schemas never reach another tier. The
  leading underscore keeps it apart from the types — a type is a kebab-case latin
  stem, and a `_`-prefixed directory is never read as records.
- `tags.yaml` — the tags dictionary, a mapping `tag: one-line description`. When it
  exists, every record's optional `tags:` list is checked against it: each tag is
  `area[:sub]` kebab-case, is a key of the dictionary, and an `area:sub` tag needs
  `area` there too.

A tier schema may never rename what booping reads: the frontmatter keys `type`,
`status`, `kind`, `targets`, `brief`, `values`, `rules`, `supersedes`, `sources`,
`reviewed`, `created_by`, their values, and the status cell of an ADR's alternatives.

## Files

- One record — one markdown file with YAML frontmatter, at `<type>/` under the tier
  root.
- Name — `<NNNN>-<slug>.md`: a four-digit number running within the type (the next
  one is the highest plus one) and a kebab-case latin slug.
- A reference to a record is `<type>/<NNNN>` (`adr/0001`, `value/0009`). In the body,
  references are ordinary relative markdown links. The site renders a type's records
  together, so splitting a set into records costs no readability.

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

- `value` — no `status`; `kind`: `value` or `non-value` (what we deliberately do
  not optimise for).
- `rule` — `status`: `accepted` or `retired` (a retired rule stays so it is not
  reinvented). Optional `targets:` — where the rule is injected (`groom`,
  `develop/run`, `agent:<id>`, `skill:<name>`) — and `brief:`, the one or two lines
  injected there — enough on their own for most of the work, without restating what
  the agent checks or knows anyway ([how rules are injected](https://A.github.io/claude-booping/playbook/#rules)).
- `adr` — `status`: `proposed`, `accepted`, `superseded`, `rejected`; optional
  `values` (value refs), `rules`, `supersedes`.
- `conflict` — `status`: `open` or `resolved`; `values` — at least two value refs.
- `story` — `status`: `done`, `planned`, `deferred`.
- `idea` — `status`: `open`, `validating`, `accepted` (went on: an ADR, a story, a
  plan), `rejected` (stays so it is not proposed again).
- `reference`, `runbook` — `status`: `live` or `retired`.

Reference fields are lists like `[value/0003, rule/0003]`. Back
references are not written.

## Body

- `value` — a paragraph stating the value, `## In practice`, then `## Trade-off`
  (absent for a non-value).
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

A record's content may be in any language; its structural headings, bold labels, table
columns and frontmatter keys stay the English ones above, so one schema set serves every
tier. A tier's own schemas add types and fields — they are not for translation.

A record states only what its source says (`booping:rule/0002`): what the source
lacks is "not named in the source", a reason that is only a preference is called the
owner's preference.

## Marks

At the start of an item or sentence, then one sentence on what to settle:

- `[clarify]` — needs the owner's decision: a default the agent chose, an open
  detail of an accepted decision;
- `[unknown]` — the record disagrees with the code, and which is right is not
  confirmed.

List: `rg -n '\[(clarify|unknown)\]' <tier root>`.

## Check

```
booping specs check --tier core|global|project
```

Checks one tier (default `project`). Errors:

- `schema` — each record against its type's schema in the tier's effective set
  (mdcheck); a tier schema mdcheck cannot load is one finding on that file;
- `layout` — every record sits in a type directory; a tier rooted at the vault reads only
  type directories and ignores the rest of the vault;
- `filename` — the name is `<NNNN>-<slug>.md`;
- `id` — numbers are unique within a type;
- `frontmatter` — the frontmatter parses and its `type:` matches the directory;
- `targets` — a rule's `targets:` and `brief:` come together, and every target parses
  as a target;
- `link` — every relative link target exists;
- `ref` — `values` point at values, `rules` at rules, `supersedes` at ADRs;
- `sources` — every `sources` path exists, resolved against the tier's anchor (core —
  the plugin root, global — `<home_dir>`, project — the repo root); an entry
  containing `://` is skipped;
- `tags` — every record's `tags:` against the tier's `tags.yaml`, and the dictionary's
  own shape; no `tags.yaml`, no check;
- `alternatives` — an ADR's alternatives table and its `###` options match one to one,
  under the section and column names the ADR schema declares; an `accepted` or
  `superseded` ADR has exactly one option accepted, any other at most one.

Warning:

- `namespace` — a cross-tier reference whose namespace names no configured tier, or
  whose tier directory does not exist on this machine.
