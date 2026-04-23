This partial activates plugin-edit mode for `/learn` when a debug flag is present alongside the calling SKILL.md.

## Guard

Run the mechanical check before doing anything else:

```bash
test -f <skill-dir>/.debug_enabled
```

- Exit code **1** (file absent): do nothing further. The activation block below is dead context for this run.
- Exit code **0** (file present): record `debug_active=true` and continue into the activation block.

## Activation block

`debug_active=true` extends the learning-target matrix defined in `docs/partial_learn_targets.md` with three additional types. Do not redefine the matrix header — add rows only:

| Type | Holds | Picked when |
|------|-------|-------------|
| `plugin-skill` | A skill file inside the plugin repo (`skills/<name>/SKILL.md` or a partial it owns) | The accepted learning changes methodology for a skill in the plugin itself, not in a specific user project |
| `plugin-agent` | An agent definition inside the plugin repo (`agents/<name>.md`) | The accepted learning changes how an agent is defined or prompted across all projects |
| `plugin-partial` | A shared partial or template inside the plugin repo (`docs/partial_*.md`, `docs/template_*.md`) | The accepted learning changes a reusable fragment that multiple skills reference |

**Commit boundary.** After writing all plugin-* targets in a single run, commit them together:

```bash
cd <plugin-repo-root> && git add <changed files> && git commit -m "<conventional commit message>"
```

Derive `<plugin-repo-root>` from `<skill-dir>`: a skill lives at `skills/<name>/`, so the repo root is two levels up (`dirname` of `dirname` of `<skill-dir>`). Do not hardcode any path.

Plugin-* rows follow the same decomposition rule as base types: if one accepted learning would span two plugin targets, split it into two rows.
