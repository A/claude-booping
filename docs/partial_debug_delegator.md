Cheap gate for plugin-edit behaviour in `/learn`. Carries no activation content — only the mechanical check and the conditional-load instruction, so non-debug runs never pull the activation body into context.

## Guard

Run the mechanical check before doing anything else:

```bash
test -f <skill-dir>/.debug_enabled
```

- Exit code **1** (file absent): do nothing further. Do not load `docs/partial_debug_learn.md`; its content is dead context for this run.
- Exit code **0** (file present): record `debug_active=true` and load `docs/partial_debug_learn.md` for the activation block.

`<skill-dir>` is the directory of the SKILL.md that loaded this partial (the orchestrator resolves it from its own context). Never hardcode a path.
