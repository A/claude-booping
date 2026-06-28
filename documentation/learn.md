# /learn

Compress retro findings into durable, actionable rules: global lessons that every skill loads, plus per-skill and per-agent extension files that target a specific surface.

## Why

`/retro` records what happened on one plan. `/learn` is the step that turns those observations into rules booping will obey on every future plan. Without `/learn`, retros pile up unread and the same friction repeats sprint after sprint; with `/learn`, each sprint leaves the project a little better calibrated.

`/learn` reads the retro file from the plan currently in `awaiting-learning`, proposes a small set of updates (new lesson entries, edits to existing lessons, additions to the relevant `_booping/` extension files), and asks you to review each proposal before writing.

## Command

```text
/learn
/learn retrospectives/20260423-skill-refactors-chat-develop-retro.md
/learn ~/Claude/claude-booping/retrospectives/20260422-plans-as-data-refactor.md
```

Bare `/learn` picks the plan currently in `awaiting-learning`. Pass a retro file path to absorb lessons from a specific one.

`/learn` walks the plan from `awaiting-learning → done` once you have signed off on the proposed updates.

## What it writes

`/learn` routes every accepted finding to **exactly one** target. Three of the four targets live in the vault; the fourth is the attached repo's own `CLAUDE.md`:

- **Global lessons** at `~/Claude/{project}/lessons/{N}_{title}.md` — durable rules every skill picks up via Preflight on every invocation. `N` is a monotonic counter so the directory stays ordered chronologically.
- **Per-skill and per-agent extension files** at `~/Claude/{project}/_booping/skill_<name>.md` and `~/Claude/{project}/_booping/agent_<full-agent-name>.md` (e.g. `agent_booping-developer.md`) — narrower rules that only reach the matching skill or worker agent, injected at load time. These are the right home for findings too specific to belong in global lessons (e.g. "when running `/develop` on this monorepo, prefer pnpm over npm").
- **The repo's own `CLAUDE.md`** — when a finding is a project convention the model should follow regardless of booping (a coding standard, a structural rule), `/learn` adds it as a one-line bullet to the attached repo's `CLAUDE.md`. These edits are committed separately, in the repo working tree, not in the vault.

A finding never lands in two targets at once. When a candidate would otherwise span two, `/learn` decomposes it into one row per target before writing.

See [Vault](vault.md#lessons) for the vault directory layout and how each file reaches the active context.

### Update-vs-create sweep

Before drafting its proposals, `/learn` reads the existing lessons, extension files, and the repo `CLAUDE.md` to check whether each candidate is genuinely new. A candidate that duplicates or refines an existing rule becomes an **update** to that rule rather than a fresh, near-duplicate entry; a candidate that contradicts an existing rule is flagged as a **conflict** for you to resolve in the review table. This keeps the lesson set from accumulating redundant or self-contradicting rules over many sprints.

### The review table

Every candidate is presented in a single review table before anything is written — one row per landing site, with columns `#`, `Target`, `Type`, `Rule`, and `Example`. You accept all, or reject individual rows by number (e.g. `2 5`), or append your own row in the same shape. Nothing is written until you respond; table acceptance is the consent for the whole write pass — there are no per-row prompts. (The exact column shape and accept/reject syntax live in the plugin-internal `docs/learn_review_table.md` that the skill loads at runtime.)

## Best practices

### Review every proposed update

`/learn` proposes — you commit. Read each proposed lesson and extension edit before approving. Three things to check:

- **Actionability.** A lesson should tell a future skill what to do, not just describe the past. "Be careful with migrations" is a description; "Run `manage.py migrate --plan` before applying any migration generated this session" is a rule.
- **Right home.** A rule that only matters for `/develop` belongs in `_booping/skill_develop.md`, not in global `lessons/` where every skill pays the context cost. Conversely, a cross-skill convention belongs in `lessons/`.
- **Direction.** A lesson should point forward. If the proposed update is really a complaint about the past plan, send it back — it is retro material, not lesson material.

### Shit in, shit out

`/learn` proposes updates from whatever the retro file says. Accepting proposals blindly produces conflicting and useless rules: redundant overlaps, contradictions with existing lessons, vague platitudes that fire on every plan and steer none. Review every proposal as if you were the one writing it — because once you approve, you are.

This is the second half of the same warning that applies to [/retro](retro.md#shit-in-shit-out): a sloppy retro produces sloppy lesson proposals, and a rubber-stamped `/learn` writes those sloppy proposals to disk where they will steer every future sprint.
