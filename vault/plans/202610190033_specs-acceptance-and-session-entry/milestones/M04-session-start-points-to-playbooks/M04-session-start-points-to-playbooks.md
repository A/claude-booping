---
id: "04"
title: "Session start points to playbooks"
sp: 8
status: done
plan: "plans/202610190033_specs-acceptance-and-session-entry/index.md"
---

# M04: Session start points to playbooks

## Tasks

**Goal:** a Claude Code session started anywhere inside a booping project gets the locked session-start block; elsewhere it gets nothing.
**Scope:** `.claude-plugin/plugin.json`, a new `hooks/` directory, a new template, e2e cases, docs, CLAUDE.md layout.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | `hooks/session-start.sh`: walk up from the cwd for `.booping`; none → exit 0 silent; found → `"$CLAUDE_PLUGIN_ROOT/bin/booping" render src/templates/hooks/session_start.md.j2`; any failure → exit 0, no output. `plugin.json` gains `hooks.SessionStart` with a 10 s timeout (shape: the caveman plugin's) | `hooks/session-start.sh`, `.claude-plugin/plugin.json` | 2 | done |
| 4.2 | Template: the locked session-start block over `context.playbooks`, two columns | `src/templates/hooks/session_start.md.j2` | 2 | done |
| 4.3 | e2e: the template renders the block with project and global playbooks inside a project; the script prints nothing outside a project and nothing on a failing render | `booping-python/e2e/cases/render/session-start-*.txtar` | 2 | done |
| 4.4 | Docs: a "Session start" section in `documentation/playbook.md` (what it injects, how a project starts as the manager via its CLAUDE.md); README mention; CLAUDE.md Layout gains `hooks/` | `documentation/playbook.md`, `README.md`, `CLAUDE.md` | 2 | done |

Test surface: the template render and the hook script, integration tier through e2e txtar — inside a project, outside, failing render.

## Definition of Done

Task 4.1
- [x] `cd /tmp && CLAUDE_PLUGIN_ROOT=$PWD/… hooks/session-start.sh` prints nothing and exits 0; inside this repo it prints the block.

Task 4.2
- [x] The rendered block matches the locked output; no column beyond Playbook and Trigger.

Task 4.3
- [x] `just e2e -k session-start` passes.

Task 4.4
- [x] The docs say how a project opts into the manager at start; CLAUDE.md Layout lists `hooks/`.

Return: the files changed and the Verify verdict, nothing else.

## References

- `src/templates/skills/playbook.md.j2` — the playbook loop to mirror.
- `~/.claude/plugins/marketplaces/caveman/.claude-plugin/plugin.json` — hook declaration shape.

## Verify

`just e2e -k session-start && bin/booping render src/templates/hooks/session_start.md.j2 | head -5`
