# retro playbook

Capture a project- and plan-specific retrospective for a shipped plan: what diverged, what felt off during development, what the diff and session log reveal — saved as a standalone file under `retrospectives/` and ready for the [learn playbook](learn.md) to compress.

Retro is a **playbook**, not a skill — it is driven by [`/playbook`](playbook.md):

```text
/playbook retro
```

## Why

Retro turns lived experience into a written record: friction that would otherwise evaporate when the session closes becomes the input to a durable rule.

The run draws from **two inputs**:

- **User-asked questions.** `gather-feedback` takes your raw open-ended take first — four questions asked one at a time, before any mined finding is mentioned — then walks the mined items with you for accept / dismiss / your own wording.
- **Session-log mining and a plan-stage lesson check.** `prepare` delegates both in parallel, mining the development session transcript for what you said at the time but never filed — pushback at the agent's choices, mid-sprint change requests, comments you made on the code itself, and places the session shows a loaded lesson ignored — and checking the plan as written against the active lesson set. The code diff is grounding context for these reads, not a separate scan phase. The mined list is **withheld** until your raw take is on record.

The two inputs are stitched into one `retrospectives/{YYYYMMDDHHMM}_{kebab-title}.md`, a standalone file in the vault — one per run, whatever the size of the working set.

## What it does

Six steps, in dependency order:

| Step | What it does |
|------|--------------|
| `intake` | Settle the working set — validate the plan is in the retro queue (`status: done`, `retro: null`), offer the others as include / postpone / skip, then read each adopted plan for context |
| `prepare` | Mine the session logs and run the plan-stage lesson check in parallel; build the issue list without showing it |
| `gather-feedback` | Your raw take first, then the mined items batch by batch; close with a per-plan goal verdict |
| `research-issues` | Root-cause each accepted issue and design concrete prevention moves |
| `synthesize` | Draft against the retrospective template, run its self-review checklist, show you a chat summary while holding the draft unwritten |
| `save` | Write `retrospectives/{slug}.md`, fire the exit transition, stamp the `retro:` back-link and goal verdict on every plan in the working set |

Retro runs as its **own track** over that standalone `retrospectives/{slug}.md` artifact — never another move on the plan. The file is created at `awaiting-retro`, advances to `awaiting-learning` once it is written and you have signed off, and [learn](learn.md) later closes it at `done`. The covered plans stay at `done` throughout; the only mark retro leaves on a plan is the `retro:` back-link in its frontmatter, and the retro queue is exactly the plans still missing that link — every `status: done` plan with `retro: null`. The workdir is the vault root; every `booping playbook-state` / `booping playbook-transition` call passes `--target retrospectives/{slug}.md`, so state lives in that file and a stopped run is resumable.

### Multiple plans in one run

A retro can cover more than one plan. `intake` offers every other queued plan — `status: done` with `retro: null` — as **include**, **postpone** (leave it queued), or **skip**.

The written retrospective carries `plan:` (the primary), `plans:` as a YAML list (even for a single plan) and a `goal_verdicts:` mapping with your per-plan verdict. Every covered plan points back through its own `retro:` key.

### Skipping the retro

Some plans are not worth a retrospective — a stale split stub, a trivial change you already understand. Pick **skip** in the per-plan prompt: the `drop-plan` script stamps `retro: skipped` on that plan, taking it out of the queue for good; its `status:` stays `done`. Use it deliberately — a skipped plan contributes nothing to the lesson loop.

## Best practices

### Shit in, shit out

The retro is only as honest as your answers — the run gives you targeted questions and a structure to fill, but it cannot invent insight you did not surface. Breeze through with "fine, fine, ship it" and the retro records nothing useful, leaving [learn](learn.md) nothing to compress into a lesson.

In practice:

- Take the interview seriously even when the plan went well — the durable lessons often come from successful sprints, not just painful ones.
- If a friction point is hard to name, describe the symptom rather than skip the question. Learn can work from "the agent kept re-reading the same three files before each milestone" — it cannot work from "context was annoying".
- Distinguish "this plan was unusual" from "this is how I want booping to behave from now on". Only the second is worth a lesson.

## Reviewing the retro file

Read the written retrospective before letting [learn](learn.md) act on it, separating **durable findings** from **one-off complaints**.

What to keep:

- **Durable findings** — patterns that will recur across sprints. "The agent picks the wrong test runner when both pytest and unittest are present" is a project rule worth lifting into a targeted lesson.
- **Process gaps** — places where the lifecycle itself failed you. "I wanted to stop after milestone 2 but did not realise I had to say so up front" is feedback for the prompt habits you bring to groom and develop runs.

What to mark as one-off:

- **Plan-specific complaints** — issues caused by this particular plan being under-specified. Fix the plan or your next prompt; do not codify a rule.
- **Mood and momentum notes** — useful context for you, but not lesson material.

A clear note in the retro (a short tag, a separate section, or an inline annotation) tells learn which findings to compress into rules and which to leave behind. Without that triage you are asking learn to invent the distinction itself, and that is exactly where "shit in, shit out" bites hardest.
