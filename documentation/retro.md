# retro playbook

Capture a project- and plan-specific retrospective for a shipped plan: what diverged, what felt off during development, what the diff and session log reveal — saved next to the plan and ready for the [learn playbook](learn.md) to compress.

Retro is a **playbook**, not a skill — it is driven by [`/playbook`](playbook.md):

```text
/playbook retro
```

## Why

Retro is the moment booping turns lived experience into a written record. Without it, every irritation that surfaced during development evaporates the moment the session closes; with it, those irritations become the input to a durable rule.

The run draws from **two inputs**:

- **User-asked questions.** `gather-feedback` takes your raw open-ended take first — four questions asked one at a time, before any mined finding is mentioned — then walks the mined items with you for accept / dismiss / your own wording. These are the high-signal sources because you noticed the friction in the moment.
- **Session-log mining and a plan-stage lesson check.** `prepare` delegates both in parallel, mining the development session transcript for tensions you did not flag explicitly — repeated retries, abandoned approaches, places where the agent did something the plan did not specify — and checking the planning stage against the active lesson set. The code diff is grounding context for these reads, not a separate scan phase. The mined list is **withheld** until your raw take is on record.

The two inputs are stitched into one `retro.md` written into the primary plan's own directory.

## What it does

Six steps, in dependency order:

| Step | What it does |
|------|--------------|
| `intake` | Settle the working set — validate the plan sits at retro's entry status, offer the others as include / postpone / skip-and-mark-done, then read each adopted plan for context |
| `prepare` | Mine the session logs and run the plan-stage lesson check in parallel; build the issue list without showing it |
| `gather-feedback` | Your raw take first, then the mined items batch by batch; close with a per-plan goal verdict |
| `research-issues` | Root-cause each accepted issue and design concrete prevention moves |
| `synthesize` | Draft against the retrospective template, run its self-review checklist, show you a chat summary while holding the draft unwritten |
| `save` | Write `retro.md`, fire the exit transition, stamp the retro reference and goal verdict on every plan in the working set |

The run walks the plan from `awaiting-retro → awaiting-learning` once the retro is written and you have signed off. Its state lives in the plan's `index.md`, so a stopped run is resumable.

### Multiple plans in one run

A retro can cover more than one plan. `intake` offers every other plan at the entry status as **include**, **postpone** (leave it queued), or **skip retro and mark it done**.

The written retro carries `plans:` as a YAML list (even for a single plan) and a `goal_verdicts:` mapping with your per-plan verdict, so a multi-plan retro records each plan's outcome separately.

### Skipping the retro

Some plans are not worth a retrospective — a stale split stub, a trivial change you already understand. Pick **skip retro and mark it done** in the per-plan prompt: that plan walks straight from `awaiting-retro → done` (bypassing `awaiting-learning`), stamped `goal: skipped`, with no retro file and no learn step. Use it deliberately — a skipped plan contributes nothing to the lesson loop.

## Best practices

### Shit in, shit out

The retro is only as honest as your answers. The run asks targeted questions and gives you a structure to fill, but it cannot invent insight you did not surface. If you breeze through with "fine, fine, ship it", the retro records nothing useful and [learn](learn.md) has nothing to compress into a lesson.

You are responsible for thinking about what should change. The playbook helps you write it down.

In practice:

- Take the interview seriously even when the plan went well — the durable lessons often come from successful sprints, not just painful ones.
- If a friction point is hard to name, describe the symptom rather than skip the question. Learn can work from "the agent kept re-reading the same three files before each milestone" — it cannot work from "context was annoying".
- Distinguish "this plan was unusual" from "this is how I want booping to behave from now on". Only the second category is worth a lesson.

## Reviewing the retro file

Read `retro.md` before letting [learn](learn.md) act on it. The goal is to separate **durable findings** from **one-off complaints**.

What to keep:

- **Durable findings** — patterns that will recur across sprints. "The agent picks the wrong test runner when both pytest and unittest are present" is a project rule worth lifting into a targeted lesson.
- **Process gaps** — places where the lifecycle itself failed you. "I wanted to stop after milestone 2 but did not realise I had to say so up front" is feedback for the prompt habits you bring to groom and develop runs.

What to mark as one-off:

- **Plan-specific complaints** — issues caused by this particular plan being under-specified. Fix the plan or your next prompt; do not codify a rule.
- **Mood and momentum notes** — useful context for you, but not lesson material.

A clear note in the retro (a short tag, a separate section, or an inline annotation) tells learn which findings to compress into rules and which to leave behind. Without that triage you are asking learn to invent the distinction itself, and that is exactly where "shit in, shit out" bites hardest.
