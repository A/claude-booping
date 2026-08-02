---
status: done
reviewed_at: 20260731 19:14
fixtures_reviewed_at: 20260731 19:27
suite_reviewed_at: 20260731 19:47
---

# research-codebase

[← index](../../index.md)

## Contract

- **Delegation** — assisted: the runner renders and owns the step and decides what is mapped;
  the heavy reads are delegated to the researcher agent config names, which returns the
  compressed map; the runner posts it in chat.
- **Needs** —
  - the confirmed framing brief — the restated problem, the task type and the settled
    decisions
  - the repository's code and the conventions it follows
- **Value** — the blast radius in the attached repo: what the work moves, what it must imitate,
  and which conventions bind it — so `draft-plan` argues from the actual code instead of
  assumptions. The heavy reads happen in the researcher agent; only the map reaches the runner's
  context. A specific fact the repo cannot settle (an installed tool's flag, a pinned version's
  behaviour) may be checked against local ground truth first — `tool --help`, lockfiles — and
  the web only for the one fact, through the same agent; surveying external practice stays
  `research-web`'s job.
- **Output files** —
  - none — the map is posted in chat, not written to the plan directory:
    - touched surfaces — files, modules, integrations and external surfaces the work moves,
      each with why it moves and how risky the move is
    - prior art — the closest existing implementations the work should follow, by path
    - conventions in play — the repo rules that bind this work (project guide, build
      artefacts, ownership boundaries), each stated as a constraint on the design
    - unknowns for the design — what the codebase could not settle, phrased as the call
      `draft-plan` has to make; open external questions land here too, for `research-web`
      to take up
    - a greenfield surface is reported as such ("no prior art in the repo"), never omitted —
      the step has no skip note
- **Step report** — the map itself, closed by `## Notes:` — the blast-radius headline (how
  many files across how many modules, the riskiest surface) and each unknown left for the
  design conversation in `draft-plan`.
- **Review gate** —
  - none — the map is not shown for approval on its own; it reaches the user folded into the
    design conversation in `draft-plan`

## Example findings

Posted in chat, the `## Blast radius` map:

```markdown
## Blast radius

### Touched surfaces

| Surface | Where | Why it moves | Risk |
| --- | --- | --- | --- |
| `render-sprints` hook | `booping-python/src/booping/hooks.py` | retired once playbooks own the render | medium — every `transition` edge fires it today |
| sprints template | `src/templates/sprints.md.j2` | moves under the playbook's `_scripts/` | low |
| post-hook list | `src/config.yaml` (`plan.hooks.post`) | drops `render-sprints` | medium — existing vaults pin it |

### Prior art

- `_scripts/` hooks already run with `BOOPING_WORKDIR` / `BOOPING_ARTIFACT` in the env — the
  working precedent for a playbook-local side effect.
- `bin/booping-create-project` is the reference shape for a standalone uv inline script.

### Conventions in play

- `skills/` and `agents/` are build artefacts — edit `src/files/**.j2`, then `just build`.
- Structured data lives in `src/config.yaml`; a skill body never restates it as prose.

### Unknowns for design

- Whether a script deriving the vault from `BOOPING_WORKDIR` holds for a repo-local vault.
```

## Return Format

```markdown
## Notes:
- blast radius: 7 files across 3 modules, 1 external surface (the `booping` CLI)
- for design: vault resolution from `BOOPING_WORKDIR` on a repo-local vault
```
