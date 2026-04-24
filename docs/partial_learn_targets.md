Every accepted learning lands in exactly one target. Select the type whose `Picked when` test the candidate satisfies first; if none fit cleanly, decompose (see below).

| Type | Holds | Picked when |
|------|-------|-------------|
| `lesson` | A cross-cutting principle that constrains future planning or implementation (`~/Claude/<project>/lessons/<N>_<kebab>.md`) | The rule generalizes beyond a single skill or agent — it states a principle that multiple skills or agents would consult. |
| `skill-ext` | A methodology change for one named skill in this project (`_booping/skill_<name>.md`) | The rule changes per-skill behaviour that only applies inside this project; the skill name is determinable from the candidate text |
| `agent-ext` | An extra instruction for one named agent in this project (`_booping/agent_<name>.md`) | The rule changes how a specific agent does its work; the agent name is determinable from the candidate text |
| `repo-claude-md` | A project-fact for the attached repo (`<repo>/CLAUDE.md`) | The rule describes a layout path, CLI command, or code-side convention that a fresh agent reading the repo must know to work safely |

## Examples

**Example routing**: feedback like "branch-naming convention should include a sprint-code prefix for this project" routes to `skill-ext` with the file `_booping/skill_develop.md` — the convention is develop-specific and project-local, not a general principle.

## Decomposition rule

If a candidate would otherwise span two targets, decompose it into two distinct rows in the review table — one row per target. Never write the same rule to two targets.

## Extending the matrix

Other partials (such as `docs/partial_debug_learn.md`) may activate additional types at runtime by appending rows to this matrix. Base types defined here are never redefined by those partials.
