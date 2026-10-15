---
id: "01"
title: "core.autonomy key, invalid-value STOP, project-context line"
sp: 3
status: pending
plan: "plans/202610151609_autonomy-modes/index.md"
---

# M01: core.autonomy key, invalid-value STOP, project-context line

`core.autonomy` exists with default `supervised`, an unknown value stops every render surface with an in-band STOP, and the project-context block shows the resolved mode.

**Scope**: `src/config.yaml` gains `core.autonomy: supervised` directly under `core`, beside `auto_migrate`, with a comment in that block's style naming both values and its readers (the driving protocol, specs, migrate). A new check in `booping-python/src/booping/autonomy.py`, shaped like `migrations.render_gate` — called by `booping-python/src/booping/commands/render.py` and `commands/render_playbook.py` at the same point — returns the STOP notice of `index.md` `## Output contract` when the final value — every tier merged and every `--set` override applied, so it runs after both render commands apply `--set` —  is anything but `supervised` or `autonomous`; the notice replaces the render, exit 0, the way the behind-vault notice does. Config that cannot be read is left to the existing migration check. `src/templates/_partials/_project_context.j2` gains the `autonomy:` line of the contract after `git_commit:` in the initialized branch only.

Tests: integration tier, txtar cases — `config-get core.autonomy` prints `supervised` with no tier setting it; a project-tier `autonomous` wins; `render-playbook` of a fixture playbook with `core.autonomy: autonomus` in the project tier prints the STOP notice alone; the same through `render`; `render-playbook --set core.autonomy=autonomus` with no tier setting it prints the same notice. Expected output hand-written.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Config key with comment; the invalid-value check wired into both render commands; the project-context line. | `src/config.yaml`, new `booping-python/src/booping/autonomy.py`, `booping-python/src/booping/commands/render.py`, `booping-python/src/booping/commands/render_playbook.py`, `src/templates/_partials/_project_context.j2` | 2 | pending |
| 1.2 | The txtar cases named in Tests. | `booping-python/e2e/cases/config-get/autonomy-*.txtar`, `booping-python/e2e/cases/render-playbook/autonomy-*.txtar`, `booping-python/e2e/cases/render/autonomy-*.txtar` | 1 | pending |

## Definition of Done

### Task 1.1

- [ ] `bin/booping config-get core.autonomy` prints `supervised` in this repo.
- [ ] The STOP notice matches `index.md` `## Output contract` character for character, with the offending value in it.
- [ ] `bin/booping render src/templates/skills/playbook.md.j2` shows `autonomy: supervised` in its project-context block.
- [ ] No other render output changes.

### Task 1.2

- [ ] One case per behaviour named in Tests; each STOP case asserts exit 0, the notice alone on stdout, and that the fixture preamble is absent.

Return: the list of changed files, nothing else.

## References

- `booping-python/src/booping/migrations.py` — `render_gate` and `auto_migrate`: tier resolution and notice shape to copy.
- `booping-python/e2e/cases/render-playbook/auto-migrate-off-in-the-project-tier-stops-the-playbook-render.txtar` — project-tier config fixture for a render-stopping notice.
- `booping-python/e2e/cases/config-get/project-tier-overrides-the-global-tier.txtar` — config-get tier fixture.

## Verify

`just e2e -k autonomy`
