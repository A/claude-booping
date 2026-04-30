# /retro

Capture a project- and task-specific retrospective for a shipped plan: what diverged, what felt off during `/develop`, what the diff and session log reveal, in a single retro file ready for [/learn](learn.md) to compress.

## Why

`/retro` is the moment booping turns lived experience into a written record. Without it, every irritation that surfaced during `/develop` evaporates the moment the session closes; with it, those irritations become the input to a durable rule.

The skill draws from **two inputs**:

- **User-asked questions.** `/retro` interviews you — what felt smooth, what felt forced, where you had to push back on the agent, where the plan was wrong. These are the high-signal sources because you noticed the friction in the moment.
- **Session-log and git-diff scan.** `/retro` reads the `/develop` session transcript and the produced diff to surface tensions you did not flag explicitly — repeated retries, abandoned approaches, churn between commits, places where the agent did something the plan did not specify. These are the issues you might not have logged but that the artifacts remember.

The two inputs are stitched into one retro file under `~/Claude/{project}/retrospectives/`, named to match the plan it covers.

## Command

```text
/retro                                  # retro the plan currently in awaiting-retro
/retro plans/YYYYMMDD-{kebab-title}.md  # retro a specific plan
```

`/retro` walks the plan from `awaiting-retro → awaiting-learning` once the retro file is written and you have signed off.

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
