# /retro

Capture a project- and task-specific retrospective for a shipped plan: what diverged, what felt off during `/develop`, what the diff and session log reveal, in a single retro file ready for [/learn](learn.md) to compress.

## Why

`/retro` is the moment booping turns lived experience into a written record. Without it, every irritation that surfaced during `/develop` evaporates the moment the session closes; with it, those irritations become the input to a durable rule.

The skill draws from **two inputs**:

- **User-asked questions.** `/retro` interviews you — what felt smooth, what felt forced, where you had to push back on the agent, where the plan was wrong. These are the high-signal sources because you noticed the friction in the moment.
- **Session-log mining and plan-stage lesson check.** `/retro` delegates to `booping-researcher` to mine the `/develop` session transcript for tensions you did not flag explicitly — repeated retries, abandoned approaches, places where the agent did something the plan did not specify — and to check the planning stage against the active lessons. The code diff is grounding context for these reads, not a separate scan phase. These are the issues you might not have logged but that the artifacts remember.

The two inputs are stitched into one retro file under `~/Claude/{project}/retrospectives/`, named to match the plan it covers.

## Command

```text
/retro
/retro plans/20260422-plans-as-data-refactor.md
/retro ~/Claude/claude-booping/plans/20260425-migrate-retro-skill-to-template-pipeline.md
```

Bare `/retro` picks the plan currently in `awaiting-retro`. Pass a plan path to retro a specific one — absolute, `~/Claude/...`, or vault-relative all work.

`/retro` walks the plan from `awaiting-retro → awaiting-learning` once the retro file is written and you have signed off.

### Multiple plans in one run

A retro can cover more than one plan. Pass several plan paths to retro them together, or run bare and pick from the `awaiting-retro` list — the picker is multi-select, so you can fold several finished plans into one retrospective. When you name some plans on the command line and others are also sitting in `awaiting-retro`, `/retro` asks you per remaining plan whether to **include** it in this run, **postpone** it (leave it queued), or **skip retro and mark it done**.

The written retro file always carries `plans:` as a YAML list (even for a single plan) and a `goal_verdicts:` mapping with your per-plan verdict, so a multi-plan retro records each plan's outcome separately.

### Skipping the retro

Some plans are not worth a retrospective — a stale split stub, a trivial change you already understand. For those, pick **skip retro and mark it done** in the per-plan prompt. `/retro` then walks that plan straight from `awaiting-retro → done` (bypassing `awaiting-learning`), stamping `goal: skipped` in its frontmatter, with no retrospective file and no `/learn` step. Use it deliberately — a skipped plan contributes nothing to the lesson loop.

## Best practices

### Shit in, shit out

The retro is only as honest as your answers. `/retro` will ask you targeted questions and give you a structure to fill, but it cannot invent insight you did not surface. If you breeze through the questions with "fine, fine, ship it", the retro records nothing useful and [/learn](learn.md) has nothing to compress into a lesson.

You are responsible for thinking about what should change. The skill helps you write it down.

In practice:

- Take the `/retro` interview seriously even when the plan went well — the durable lessons often come from successful sprints, not just painful ones.
- If a friction point is hard to name, describe the symptom rather than skip the question. `/learn` can work from "the agent kept re-reading the same three files before each milestone" — it cannot work from "context was annoying".
- Distinguish "this plan was unusual" from "this is how I want booping to behave from now on". Only the second category is worth a lesson.

## Reviewing the retro file

After `/retro` writes the file, read it before letting [/learn](learn.md) act on it. The goal is to separate **durable findings** from **one-off complaints**.

What to keep:

- **Durable findings** — patterns that will recur across sprints. "The agent picks the wrong test runner when both pytest and unittest are present" is a project rule worth lifting into `_booping/skill_develop.md` or `lessons/`.
- **Process gaps** — places where the lifecycle itself failed you. "I wanted to stop after milestone 2 but did not realise I had to say so up front" is feedback for the prompt habits you bring to `/groom` and `/develop`.

What to mark as one-off:

- **Plan-specific complaints** — issues caused by this particular plan being under-specified. Fix the plan or your next prompt; do not codify a rule.
- **Mood and momentum notes** — useful context for you, but not lesson material.

A clear note in the retro file (a short tag, a separate section, or just an inline annotation) tells `/learn` which findings to compress into rules and which to leave behind. Without this triage you are asking `/learn` to invent the distinction itself, and that is exactly the place "shit in, shit out" bites hardest.
