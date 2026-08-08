# Framing brief

## Request

> retro and code review are separate artefacts with separate state machines. I want them to be attached into different artifacts in the plan dir, and linked to the plans. So they work with own state machines, and plan is terminated when developed. Motivation: both aren't mandatory, but if they are skipped, plan left in non-terminal state

## Task type

`refactoring` — internal restructuring of the playbook run-state topology. No user-visible capability is added and none is removed; the same runs produce the same artefacts, only the machine each run attaches to changes.

- Not `feature`: retro and code review already exist and already produce their outputs. Nothing new becomes possible for the user; the test is "could the user do this before?" — yes.
- Not `bug`: today's behaviour matches its design. `retro` and `learn` were authored to advance the plan's own machine. The complaint is that the design is wrong, not that the implementation diverges from it.

## Problem

Today every post-groom playbook writes the **same** artifact, `plans/{slug}/index.md`, and advances the **same** run machine:

- `develop`: `awaiting-plan-review` → `ready-for-dev` → `in-progress` → `awaiting-retro` (terminal) | `fail`
- `retro`: `awaiting-retro` → `awaiting-learning` (terminal), writing `retro.md` as a side product linked via the plan's `retro:` key
- `learn`: `awaiting-learning` → `done` (terminal)
- `code-review`: no state at all — ephemeral, no workdir, no artefact

Consequence: the plan's terminal status is owned by `learn`, three playbooks downstream. Retro and learn are optional in practice, so a plan that ships and is never retro'd sits at `awaiting-retro` forever — indistinguishable in every listing from a plan whose retro is genuinely pending. Code review has no place in the model at all: it leaves no trace on the plan and its own progress (findings raised, verdict given, fixes applied) is not resumable.

What must change: `develop` becomes the plan's last word — the plan reaches a terminal status when the sprint closes. Retro and code review become **their own artefacts in the plan directory**, each with its own state machine and its own lifecycle, linked to the plan by frontmatter in both directions. Skipping either leaves the plan terminal and simply means the artefact does not exist.

## Clarifications and Decisions

_(to be filled from the answers below)_

## Open scope questions

1. **Plan's terminal status** — what does `develop` transition to when a sprint closes? `done`, keeping the current vocabulary but moving it three playbooks earlier, or a distinct name (`developed`, `shipped`) that leaves `done` free?
2. **`learn`'s attachment** — `learn` currently advances the plan (`awaiting-learning` → `done`). If the plan is already terminal, does `learn` attach to the **retro artefact's** machine (`retro.md`: `awaiting-learning` → `learned`), or stay on the plan with a separate second machine?
3. **Code-review artefact** — does `code-review` become stateful in this sprint (a `review.md` in the plan dir with `scoping`/`reviewing`/`awaiting-verdict`/`resolving`/`closed`), or is it out of scope, and this sprint only cuts retro loose?
4. **Multi-run artefacts** — a plan can be reviewed more than once (a second look after fixes is a new run today). One `review.md` overwritten per run, or numbered (`review-01.md`), or a `reviews/` subdirectory?
5. **Working set / multi-plan retro** — retro today covers a *working set* of sibling plans and closes them all through `script close-working-set`. If retro no longer touches plan status, what does that hook do — is the working-set concept retired, or does it survive as a `plans:` list on `retro.md` alone?
6. **Migration** — vaults hold plans currently parked at `awaiting-retro` / `awaiting-learning`. Ship a migration (`003_…`) that rewrites them to the new terminal vocabulary, or leave existing plans as historical residue?
7. **Post-implementation reshape** — this is prompt/manifest-shaped work whose rendered output often exposes information-architecture problems only after the render. Should the plan carry a final reshape milestone where the rendered playbooks come back for manual shaping?
