# /chat

The orient-and-working-mode command. Use it to land in a project, get your bearings, navigate the vault, and handle small ad-hoc tasks that do not warrant a plan file.

## Why

`/chat` is the entry point you reach for when you sit down at a project and want to know where things stand — what is in flight, what is parked, what just shipped — before deciding whether to run anything heavier. It is also the right tool for small one-off work: reading a plan, tweaking a frontmatter field, writing a quick note under `notes/`, answering a question about the codebase. Anything that does not produce a durable plan artefact lives here.

It is the only skill with an "orient" responsibility. The other skills assume you already know which plan you are working on; `/chat` is where that picture comes from.

## Command

```text
/chat
/chat we're continuing to wrap up the develop skill refactor — i'll give you ad-hoc tasks
/chat plans/20260423-refactor-develop-skill-to-groom-pattern.md address the issues from the previous implementation
```

Bare `/chat` orients against the current project. The free-text body is read verbatim — mention a plan path, a retro path, a question, or a small change request and the skill picks it up.

The free-text body is read verbatim. Anything you mention — a plan path, a retro path, a question about a lesson, a small change request — is picked up.

## What it is for

- **Orient.** Land in a project and see what is in flight, what is parked, and what is queued.
- **Navigate the vault.** Open plans, retros, lessons, and notes; cross-reference them; surface the relevant slice of `~/Claude/{project}/` for whatever you are about to do.
- **Light edits.** Frontmatter tweaks, manual status flips, small notes under `notes/`, single-line corrections to a plan that does not need re-grooming.
- **Ad-hoc small tasks.** Questions about the codebase, quick reads, one-off greps. The kind of work where opening a plan file would be heavier than the work itself.

See [Vault](vault.md) for the layout `/chat` navigates over.

## Escalation

`/chat` is bounded by what fits inside a single session without producing a durable artefact. When the conversation outgrows that boundary, escalate rather than stretch the skill:

- **Scope grows into real work** → `/groom <topic>`. Anything that needs research, milestones, story-point estimates, or a plan file belongs in `/groom`. The rule of thumb: if you would want a retro on it later, it is `/groom` material now.
- **A `ready-for-dev` plan is waiting** → `/develop <plan-path>`. `/chat` will route you there rather than trying to implement milestones inline.
- **A plan just finished** → `/retro <plan-path>` to capture findings; `/learn` afterwards.

The hand-off is explicit: `/chat` recommends the next command and stops, rather than reproducing another skill's workflow inline. See [/groom](groom.md), [/develop](develop.md), [/retro](retro.md), and [/learn](learn.md) for what each of those commands owns.
