How a booping skill picks worker agents and groups tasks into briefings.

Each briefing includes a `Contract:` block — the concatenation of `partial_agents_developer_rules.md`, `partial_agents_developer_workflow.md`, and `partial_extra_instructions.md` — prepended by the skill at runtime. Agents receive the full operating contract in the briefing and do not scan the plugin tree.

## Strategies

- [mid/senior](partial_agents_strategy_mid_senior.md) — two active tiers: `booping-developer-middle` (Sonnet) for 1–2 SP batched tasks and `booping-developer-senior` (Opus, reasoning high) for 3–4 SP design-judgment tasks. Default for most sprints.
