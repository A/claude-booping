## What storypoints measure

Storypoints estimate the **total complexity and risk** of getting a task to a merged, accepted state. AI does the implementation cheaply; the real cost lives elsewhere:

- **Inherent complexity / risk** of the work — design judgment required, blast radius, ambiguity, integration surface.
- **Burden of human code review** — how much careful reading the diff demands before the user can trust it.
- **Re-work cycles** — addressing review feedback, design tweaks, additional tests after the first pass lands.

Estimate against complexity + review burden, not lines of code or agent runtime.

## Scale (1–5)

Use this scale verbatim:

| SP | Meaning |
|----|---------|
| 1  | Simple text/config change, no risk |
| 2  | Simple task, predictable, no risk |
| 3  | Medium task, minor risks but predictable overall |
| 4  | Complex task, medium risk, may need small research but clear enough |
| 5  | Research task — developer needs to clarify and decompose further before proceeding |

A task estimated **5 SP must be re-decomposed** before `status: ready-for-dev`. Do not hand a 5-SP task to `/develop`.

For the SP→agent mapping used by /develop, see [agent delegator](partial_agent_delegator.md).

## Estimation flow

1. Estimate per task using the 1–5 scale.
2. Sum per milestone; present per-milestone totals alongside per-task estimates.
3. Sum per sprint; present total before promoting to `ready-for-dev`.
4. Ask the user for adjustment before finalizing.

## Sprint sizing

After estimates are in:

- **Threshold**: if total SP > ~30–35, flag it: *"This sprint is N SP — consider splitting."*
- **Defensive buffer for high-uncertainty work** (frontend migrations, LLM/ML pipelines, search relevance, data quality, anything where correctness is statistical or emergent): treat the nominal SP as 1.3–1.5× higher and flag accordingly. Even a nominal 25 SP sprint may effectively be 35–40.

## Project-specific calibration

Sprint cap, buffer factor, and any project-specific sizing rules live in `~/Claude/{project_name}/_booping/skill_groom.md`. They override the defaults above.
