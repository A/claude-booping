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

`/learn` is the **only** authorised author for two surfaces inside the vault:

- **Global lessons** at `~/Claude/{project}/lessons/{N}_{title}.md` — durable rules every skill picks up via Preflight on every invocation. `N` is a monotonic counter so the directory stays ordered chronologically.
- **Per-skill and per-agent extension files** at `~/Claude/{project}/_booping/skill_<name>.md` and `~/Claude/{project}/_booping/agent_<full-agent-name>.md` (e.g. `agent_booping-developer.md`) — narrower rules that only reach the matching skill or worker agent, injected at load time. These are the right home for findings too specific to belong in global lessons (e.g. "when running `/develop` on this monorepo, prefer pnpm over npm").

See [Vault](vault.md#lessons) for the directory layout and how each file reaches the active context.

## Best practices

### Review every proposed update

`/learn` proposes — you commit. Read each proposed lesson and extension edit before approving. Three things to check:

- **Actionability.** A lesson should tell a future skill what to do, not just describe the past. "Be careful with migrations" is a description; "Run `manage.py migrate --plan` before applying any migration generated this session" is a rule.
- **Right home.** A rule that only matters for `/develop` belongs in `_booping/skill_develop.md`, not in global `lessons/` where every skill pays the context cost. Conversely, a cross-skill convention belongs in `lessons/`.
- **Direction.** A lesson should point forward. If the proposed update is really a complaint about the past plan, send it back — it is retro material, not lesson material.

### Shit in, shit out

`/learn` proposes updates from whatever the retro file says. Accepting proposals blindly produces conflicting and useless rules: redundant overlaps, contradictions with existing lessons, vague platitudes that fire on every plan and steer none. Review every proposal as if you were the one writing it — because once you approve, you are.

This is the second half of the same warning that applies to [/retro](retro.md#shit-in-shit-out): a sloppy retro produces sloppy lesson proposals, and a rubber-stamped `/learn` writes those sloppy proposals to disk where they will steer every future sprint.
