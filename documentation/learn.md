# learn playbook

Compress retro findings into durable, actionable rules: targeted lessons that reach the playbooks, steps, agents and skills they name, plus one-line project facts in the repo's own `CLAUDE.md`.

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
| `dedup-sweep` | Filtered read of existing lessons and the repo `CLAUDE.md` — update vs create vs conflict |
| `review-table` | Present the unified review table; you accept, reject rows, or add your own |
| `write` | Write the accepted items, one pass per target type |
| `transition` | Close the retrospective at `done` and commit |

The run workdir is the **vault root** and every `booping playbook-state` / `booping playbook-transition` call passes `--target retrospectives/{slug}.md`, so a stopped run is resumable.

## What it writes

Two destinations, and every accepted finding lands in **exactly one** of them. A candidate that would span both is decomposed into one row per destination before writing.

- **Targeted lessons** at `{vault}/_lessons/{N}_{title}.md` — each carrying a `targets:` frontmatter list naming the playbooks, playbook steps, agents and skills the rule applies to. A rule that should only reach one worker agent or one skill is a lesson targeting it, not a separate file. `N` is a monotonic counter, keeping the directory chronological.
- **The repo's own `CLAUDE.md`** — a finding that is a project fact aiding fresh-agent project understanding (a layout path, a CLI command, a code-side convention) becomes a one-line bullet there. Those edits are committed in the repo working tree, not the vault, and never touch the global `~/.claude/CLAUDE.md`.

See [Vault](vault.md#_lessons) for the directory layout and how each file reaches the active context.

### Targets are fetched, never guessed

A `_lessons/` file with no valid `targets:` reaches nothing, so routing has to be exact. Before proposing, the run reads the **target space**: a table of contents of every discovered playbook, then a targets fetch for only the playbooks a candidate touches, listing their step names and addressable agents. Entries come from that fetch, and the exact `targets:` entry each lesson carries is assigned in the review table before the lesson is written into the vault's `_lessons/`.

```markdown
---
id: 7
title: Name every artifact path absolutely
targets:
  - groom/draft-plan
  - agent:booping-developer
retro: retrospectives/202608031129_flat-lessons.md
created: 2026-08-03
---
```

Target forms are `{playbook}`, `{playbook}/{step}`, `agent:{id}` and `skill:{name}` — exact names only, no globs. See [Playbooks → Lessons](playbook.md#lessons) for where each one surfaces.

!!! note "Legacy `lessons/`"
    `{vault}/lessons/` is read by nothing and written by nothing — only a `_lessons/` file with a valid `targets:` list reaches a run. Nothing moves between the two on its own; while the legacy directory still holds files, a render of any playbook emits a non-blocking note asking you to migrate them.

### Update-vs-create sweep

Before drafting proposals, `dedup-sweep` reads the existing lessons and the repo `CLAUDE.md` to check whether each candidate is genuinely new. A candidate that duplicates or refines an existing rule becomes an **update** to that rule rather than a near-duplicate; one that contradicts a rule is flagged a **conflict** for you to resolve in the review table — that is what keeps the lesson set from accumulating redundant or self-contradicting rules over many sprints.

### The review table

Every candidate appears in a single review table before anything is written — one row per landing site, with columns `#`, `Target`, `Type`, `Rule`, `Example` and `Targets`. `Target` is the exact destination path — a `_lessons/` file, or the repo's `CLAUDE.md`. The `Targets` column carries the exact `targets:` entries the lesson will be written with — a playbook, a `{playbook}/{step}`, an `agent:{id}` or a `skill:{name}`, drawn from the fetched target space and copied verbatim into the file's `targets:` list — so the routing is assigned here, before anything lands in `_lessons/`; a `CLAUDE.md` row carries `—`, since its path is its routing. You accept all, reject rows by number (e.g. `2 5`), or append your own row in the same shape. Nothing is written until you respond; table acceptance is the consent for the whole write pass — there are no per-row prompts.

## Best practices

### Review every proposed update

The run proposes — you commit. Read each proposed lesson and `CLAUDE.md` bullet before approving. Three things to check:

- **Actionability.** A lesson should tell a future run what to do, not just describe the past. "Be careful with migrations" is a description; "Run `manage.py migrate --plan` before applying any migration generated this session" is a rule.
- **Right home.** A rule that only matters for one step belongs in a lesson targeting that step, not one targeting the whole playbook where every run pays the context cost.
- **Direction.** A lesson should point forward. If the proposed update is really a complaint about the past plan, send it back — it is retro material, not lesson material.

### Shit in, shit out

Proposals come from whatever the retro says. Accepting them blindly produces conflicting and useless rules: redundant overlaps, contradictions with existing lessons, vague platitudes that fire on every plan and steer none. Review every proposal as if you were writing it — because once you approve, you are.

The second half of the same warning as [retro](retro.md#shit-in-shit-out): a sloppy retro produces sloppy lesson proposals, and a rubber-stamped write pass puts those proposals on disk where they steer every future sprint.
