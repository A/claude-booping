# learn playbook

Compress retro findings into durable, actionable rules: rule records in the project's [specs](specs.md) tier that reach the playbooks, steps, agents and skills they target, plus one-line project facts in the repo's own `CLAUDE.md`.

Learning is a **playbook**, not a skill — it is driven by [`/playbook`](playbook.md):

```text
/playbook learn
```

## Why

The [retro playbook](retro.md) records what happened on a set of shipped plans. Learn turns those observations into rules booping obeys on every future plan; without it, retros pile up unread and the same friction repeats sprint after sprint.

The unit of work is a standalone retrospective — `retrospectives/{slug}.md` at `awaiting-learning`, never a plan directory. It reads that file and each plan in its `plans:` list, proposes a small set of updates, and writes nothing until you confirm the whole set. The **retrospective** then walks `awaiting-learning → done`; the plans it covers are `done` before the run starts and stay `done` throughout.

## What it does

Six steps, in dependency order:

| Step | What it does |
|------|--------------|
| `intake` | Resolve the retrospective and its working set; validate the entry status |
| `extract-candidates` | Decompose the retro into atomic rules, each routed to a single destination |
| `dedup-sweep` | Filtered read of the rules of all three specs tiers and the repo `CLAUDE.md` — update vs create vs covered vs conflict |
| `review-table` | Present the unified review table; you accept, reject rows, or add your own |
| `write` | Write the accepted items, one pass per target type |
| `transition` | Close the retrospective at `done` and commit |

The run workdir is the **vault root** and every `booping playbook-state` / `booping playbook-transition` call passes `--target retrospectives/{slug}.md`, so a stopped run is resumable.

## What it writes

Two destinations, and every accepted finding lands in **exactly one** of them. A candidate that would span both is decomposed into one row per destination before writing.

- **A rule record in the project specs tier** at `rule/{NNNN}-{slug}.md` under the tier root — each carrying a `targets:` list naming the playbooks, playbook steps, agents and skills the rule applies to, and a `brief:` of one or two lines that is what those targets receive. A rule that should only reach one worker agent or one skill is a rule targeting it, not a separate file. When the project has no specs tier yet, the run creates it first with [`booping specs init --tier project`](specs.md#booping-specs-init); `{NNNN}` is the next free number from `booping specs next rule`. After writing, `booping specs check --tier project` must report no error on the new records.
- **The repo's own `CLAUDE.md`** — a finding that is a project fact aiding fresh-agent project understanding (a layout path, a CLI command, a code-side convention) becomes a one-line bullet there. Those edits stay in the repo working tree for you to commit, and never touch the global `~/.claude/CLAUDE.md`.

Learn writes only the project tier. A finding the shipped (`core`) or your `global` tier already covers is shown as `covered` and not written; a finding that departs from one of their rules is written as a project rule that opens with a `[clarify]` sentence naming the departed rule, so you can record the departure in an ADR. See [Specs → Tiers](specs.md#tiers) for where each tier lives.

### What a learnt rule looks like

```markdown
---
type: rule
title: "Name every artifact path absolutely"
summary: "Briefings and reports name vault and repo files by absolute path, never relative to a guessed cwd."
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: accepted
targets:
  - groom/draft-plan
  - agent:booping-developer
brief: "Name every artifact by absolute path; a relative path breaks once the worker's cwd differs."
sources: [vault/retrospectives/202610031129_flat-paths.md]
---

## Rule

Name every vault and repo file by its absolute path in briefings and reports.

**Example**: A briefing that said `plans/x/index.md` sent the worker to read a file under the repo, not the vault.

## Follows from

- [Retro: 202610031129_flat-paths](../../retrospectives/202610031129_flat-paths.md)
```

Every target named in `targets:` receives the `brief:` together with a link to the record, in a `## Rules` section of its rendered body — see [Playbooks → Rules](playbook.md#rules). `created_by: claude` marks the record as learnt; `reviewed` is never written by learn, only by you. `sources:` is present only when the vault lives inside the repo; `## Follows from` links the value the rule follows from when one fits, else the retrospective.

### Targets are fetched, never guessed

A rule with no valid `targets:` reaches nothing, so routing has to be exact. Before proposing, the run reads the **target space**: a table of contents of every discovered playbook, then a targets fetch for only the playbooks a candidate touches, listing their step names and addressable agents. Entries come from that fetch, and the exact `targets:` list each rule carries is assigned in the review table before the record is written.

Target forms are `{playbook}`, `{playbook}/{step}`, `agent:{id}` and `skill:{name}` — exact names only, no globs.

### Update-vs-create sweep

Before drafting proposals, `dedup-sweep` reads the rules of the three specs tiers and the repo `CLAUDE.md` to check whether each candidate is genuinely new. A candidate that duplicates or refines a project rule becomes an **update** to that record, edited in place, rather than a near-duplicate. A candidate a `core` or `global` rule already holds is **covered**; one that contradicts a rule is flagged a **conflict** for you to resolve in the review table. That is what keeps the rule set from accumulating redundant or self-contradicting rules over many sprints.

### The review table

Every candidate appears in a single review table before anything is written — one row per landing site, with columns `#`, `Target`, `Type`, `Targets`, `Brief`, `Rule` and `Example`:

| Column | Holds |
|--------|-------|
| `#` | A stable row number, used to reject rows. |
| `Target` | Where the row lands: `rule/{NNNN}-{slug}.md` for a new rule (the number is provisional until write), the existing `rule/NNNN` for an update, `CLAUDE.md`, or the covering rule's ref. |
| `Type` | `rule`, `claude-md` or `covered` — a `covered` row is shown, never written. |
| `Targets` | The exact `targets:` entries the rule is written with, drawn from the fetched target space; `—` for `claude-md` and `covered`. |
| `Brief` | The one or two lines injected into each target; `—` for `claude-md` and `covered`. |
| `Rule` | One imperative sentence, one concern. |
| `Example` | One concrete sentence — what went wrong or right. |

You accept all, reject rows by number (e.g. `2 5`), or append your own row in the same shape; a row of yours carrying two rules is split into two before writing. Nothing is written until you respond; table acceptance is the consent for the whole write pass — there are no per-row prompts.

## Best practices

### Review every proposed update

The run proposes — you commit. Read each proposed rule — its brief above all, since that is what the targets receive — and each `CLAUDE.md` bullet before approving. Three things to check:

- **Actionability.** A rule should tell a future run what to do, not just describe the past. "Be careful with migrations" is a description; "Run `manage.py migrate --plan` before applying any migration generated this session" is a rule.
- **Right home.** A rule that only matters for one step targets that step, not one targeting the whole playbook where every run pays the context cost.
- **Direction.** A rule should point forward. If the proposed update is really a complaint about the past plan, send it back — it is retro material, not rule material.

### Shit in, shit out

Proposals come from whatever the retro says. Accepting them blindly produces conflicting and useless rules: redundant overlaps, contradictions with existing rules, vague platitudes that fire on every plan and steer none. Review every proposal as if you were writing it — because once you approve, you are.

The second half of the same warning as [retro](retro.md#shit-in-shit-out): a sloppy retro produces sloppy rule proposals, and a rubber-stamped write pass puts those proposals on disk where they steer every future sprint.
