---
status: done
reviewed_at: 20260731 19:14
fixtures_reviewed_at: 20260731 19:27
suite_reviewed_at: 20260731 19:47
---

# research-codebase

[← index](../../index.md)

## Contract

- **Needs** —
  - the confirmed framing — the restated problem and the task type
  - the scope boundaries the user confirmed
  - the repository's code and the conventions it follows
- **Value** — the blast radius in the attached repo: what the work moves, what it must imitate,
  and which conventions bind it — so `design` argues from the actual code instead of
  assumptions. The step runs as its own sub-agent, so the heavy reads happen here and only the
  map reaches the driver; it does not delegate further to `booping-researcher`.
- **Output files** —
  - `[CREATED] _runs/groom/{slug}/research-codebase.md`:
    - touched surfaces — files, modules, integrations and external surfaces the work moves,
      each with why it moves and how risky the move is
    - prior art — the closest existing implementations the work should follow, by path
    - conventions in play — the repo rules that bind this work (project guide, build
      artefacts, ownership boundaries), each stated as a constraint on the design
    - unknowns for design — what the codebase could not settle, phrased as the call `design`
      has to make
    - a greenfield surface is reported as such ("no prior art in the repo"), never omitted —
      the step has no skip note
    - no frontmatter: the map carries no gate, so nothing stamps it
- **Harness return** — `## Changed:` list; `## Notes:` — the blast-radius headline (how many
  files across how many modules, the riskiest surface) and each unknown left for `design`.
- **Review gate** —
  - none — the map is not shown for approval on its own; it reaches the user folded into
    `design.md` and is reviewed at the design gate

## Example artifact

`_runs/groom/20260731-14-05_sprints-report-script/research-codebase.md`:

```markdown
# Blast radius — sprints report as a playbook script

## Touched surfaces

| Surface | Where | Why it moves | Risk |
| --- | --- | --- | --- |
| `render-sprints` hook | `booping-python/src/booping/hooks.py` | retired once playbooks own the render | medium — every `transition` edge fires it today |
| sprints template | `src/templates/sprints.md.j2` | moves under the playbook's `_scripts/` | low |
| post-hook list | `src/config.yaml` (`plan.hooks.post`) | drops `render-sprints` | medium — existing vaults pin it |

## Prior art

- `_scripts/` hooks already run with `BOOPING_WORKDIR` / `BOOPING_ARTIFACT` in the env — the
  working precedent for a playbook-local side effect.
- `bin/booping-create-project` is the reference shape for a standalone uv inline script.

## Conventions in play

- `skills/` and `agents/` are build artefacts — edit `src/files/**.j2`, then `just build`.
- Structured data lives in `src/config.yaml`; a skill body never restates it as prose.

## Unknowns for design

- Whether a script deriving the vault from `BOOPING_WORKDIR` holds for a repo-local vault.
```

## Return Format

```markdown
## Changed:
- [CREATED] _runs/groom/20260731-14-05_sprints-report-script/research-codebase.md

## Notes:
- blast radius: 7 files across 3 modules, 1 external surface (the `booping` CLI)
- for design: vault resolution from `BOOPING_WORKDIR` on a repo-local vault
```
