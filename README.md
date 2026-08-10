# booping

A self-learning, project-scoped sprint workflow for Claude Code. booping turns a feature idea into a durable, on-disk loop — **groom → develop → retro → learn** — that uses sub-agents to avoid context rot, with an optional second-model cross-review of every plan. Every artifact (plans, retros, lessons, sprint snapshots) lives under `~/Claude/{project}/`, one folder per codebase.

![Vault open in Obsidian](docs/images/vault-in-obsidian.webp)

*Each project's vault is a plain Obsidian-friendly folder of markdown files.*

## What it's for

Take a feature at whatever maturity it arrives — a rough idea over an existing codebase, a half-formed brief, a detailed PRD — and drive it through one loop: groom it into a plan, develop it, review the diff, retro what shipped.

booping is **not** spec-driven development — it doesn't keep specs as a living mirror of the codebase. It's closer to scrum sprints: a plan is a sprint artifact, done and forgotten once it ships; what persists is the vault's history and the lessons the loop distils from it. Playbooks are plain markdown procedures — when the shipped loop doesn't fit, you write your own (see [Extensibility](#extensibility)).

## Obsidian-ready by design

The vault at `~/Claude/{project}/` is markdown-only with YAML frontmatter that Obsidian renders natively as Properties. One vault per project, side-by-side with whatever else you keep in `~/Claude/`. No lock-in — just files you can grep, version, and edit by hand.

This repo is developed with booping itself, and its vault is checked in at [`vault/`](vault/) — browse a [finished plan](vault/plans/202608081300_session-time-metrics/index.md), the [targeted lessons](vault/_lessons/) the loop has accumulated, or a [retrospective](vault/retrospectives/20260722-seven-plan-retro.md).

## Disclaimer

booping is aimed at **experienced developers and tech leads** — people comfortable making architectural calls, decomposing work, and telling a sharp plan from a vague one, a sound diff from a sloppy one.

It's built for **iterative, agile-style development**: maintenance, incremental features, or growing a project sprint by sprint. It is **not** a waterfall tool — don't hand it a whole-project spec and expect a finished product. One plan is one sprint; the loop compounds across many.

Drop a `config.yaml` into your vault and it overrides the defaults — sprint scale, task types, branch conventions and agent wiring are the natural targets. The `code-review` playbook (`/playbook code-review`) is a side-route for stack-aware review of a finished plan's diff, recorded as its own artifact under `codereviews/`.

**A note on maturity:** v1.0 works — the whole loop is dogfooded on this repo — but it's beta-grade. Expect rough edges (eval suites pending review, some skills-era legacy in the core). Installation trouble? Run `/playbook setup` and discuss the issue with it.

## Dependencies

Required: `uv` and `git`. Optional: a cross-review agent named in your config, for a second-model review of every drafted plan.

```bash
# macOS
brew install uv git

# Linux (Debian/Ubuntu)
sudo apt install -y git
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Installation

Inside Claude Code, register the marketplace once, then install the plugin:

```
/plugin marketplace add A/claude-booping
/plugin install booping@booping
```

Update later via `/plugin update booping` (or from the `/plugin` UI).

After installing, `cd` into the target repo and run `/playbook setup`. It settles the machine config, then scaffolds the vault (`plans/`, `retrospectives/`, `codereviews/`, `_lessons/`, `notes/`) and writes the `.booping` marker. Anything already in place is detected and skipped. The `booping` CLI logs its invocations to `.booping.log` at the vault root.

## Quick start

For a hand-holding walkthrough and per-command reference, see the [docs site](https://A.github.io/claude-booping/).

The full loop is five steps, each a **playbook** driven by `/playbook` — the plugin's one shipped skill and single entry point. Run them in order:

```bash
# Inside the target repo, once:
/playbook setup

# Spec a feature, bug, or refactor — free-text description.
# The more detailed your brief, the sharper the resulting plan:
/playbook groom — add per-tenant rate limiting to the public API

# Execute the plan (bare invocation resolves it from the vault queue):
/playbook develop
# …or name it:
/playbook develop — plans/202604260930_per-tenant-rate-limiting/index.md

# Retrospect on what shipped:
/playbook retro

# Fold the retro's findings into durable rules:
/playbook learn
```

Candidates are listed for you if you forget the exact path.

## Workflow

`groom` shapes the spec and waits for explicit user approval before handing off; `develop` claims the next ready plan and executes milestone by milestone; `retro` compares what shipped to the original spec; `learn` distils the retrospective into rules that bind the next sprint.

A plan is a directory, not a file: `plans/{slug}/index.md` carries the frontmatter, the approach and a generated `## Milestones` table, while each milestone is its own file under `milestones/` holding that milestone's tasks, definition of done and verification. That milestone file is what develop hands a coding agent as its contract, with `index.md` alongside as context.

There is no shared status table — **each playbook has its own status vocabulary** and advances its own run artifact through it. Groom and develop run on the plan, so its `status:` frontmatter is whatever those two last wrote, and the plan track ends when develop closes it — at `done`, or at `fail` or `cancelled`. Retro and learn are a **separate track** over a standalone retrospective under `retrospectives/`; code review is a third, over one file per run under `codereviews/`. The statuses those tracks write are their own artifact's, never the plan's.

```text
groom       framing → researching → drafting → cross-reviewing → presenting
            → awaiting-approval → ready-for-dev (terminal)
            (loopbacks: drafting → researching, awaiting-approval → drafting)
            (any non-terminal status → cancelled (terminal))

develop     awaiting-approval → ready-for-dev → in-progress
            → done (terminal) | fail (terminal)
            (any non-terminal status → cancelled (terminal))

retro       awaiting-retro → awaiting-learning (terminal)     [on retrospectives/{slug}.md]

learn       awaiting-learning → done (terminal)               [on retrospectives/{slug}.md]

code-review in-agent-review → human-review → done (terminal)  [on codereviews/{dir}/{ts}.md]
```

The tracks join the plan by frontmatter, not by status. A finished plan carries `retro: null` until a retrospective covers it, at which point retro stamps the retrospective's path there (or `skipped` when you skip it) — that null is the retro queue. Review joins by a **list**: `code_reviews:` starts empty and every closing review appends its path, so the key reads as history rather than a queue flag, and the review queue is every `done` plan, re-review included.

## Statuses

A plan's frontmatter status is written by groom or develop. Retro and learn write their own statuses onto the retrospective instead, and code review onto its own review file.

**groom**

- **`framing`** — clarifying the request and settling scope.
- **`researching`** — the blast-radius and web-research passes are running.
- **`drafting`** — design is being settled with you in conversation and written into `index.md` and one file per milestone.
- **`cross-reviewing`** — a second model is reviewing the draft (skipped when no reviewer is configured).
- **`presenting`** — the approval screen is on the table.
- **`awaiting-approval`** — waiting for your explicit approval or change request; groom's single review gate.
- **`ready-for-dev`** *(groom's terminal)* — approved, queued for develop to claim.

**develop**

- **`awaiting-approval`** — develop's entry status when a run starts on a plan still parked at groom's approval gate. Handing the plan to develop counts as the approval: it advances to `ready-for-dev` without asking.
- **`in-progress`** — develop has claimed the plan and is executing milestones.
- **`done`** *(develop's terminal)* — all milestones done and verification green. The end of the plan lifecycle; retro and code review pick the plan up from here through frontmatter, without moving it again.
- **`fail`** *(develop's terminal)* — an unrecoverable blocker after two documented fix attempts, with your approval to abort.

**groom / develop**

- **`cancelled`** *(terminal in both machines)* — you called the run off. Reachable from every non-terminal status of either machine. Groom snapshots the plan into the vault on the way out; develop stamps `completed:`.

**retro / learn** — on the retrospective at `retrospectives/{slug}.md`, not on a plan.

- **`awaiting-retro`** — retro's entry status, set when the run starts.
- **`awaiting-learning`** *(retro's terminal)* — the retrospective is written and signed off. Learn claims from here.
- **`done`** *(learn's terminal)* — every accepted lesson is written to its target.

Skipping a plan's retro writes no retrospective at all: the plan is stamped `retro: skipped`, taking it out of the queue while leaving its `status: done` alone.

**code-review** — on the review file at `codereviews/{dir}/{ts}.md`, one per run, not on a plan.

- **`in-agent-review`** — the review file is open on a confirmed scope and the review pass is producing findings.
- **`human-review`** — the findings are recorded and your verdict on them is pending.
- **`done`** *(code-review's terminal)* — every finding is applied, delegated or dropped, and the record is closed. Closing stamps `reviewed_at` and appends the review's path to the reviewed plan's `code_reviews:` list; an ad-hoc review (`plan: null`) links to nothing. The plan's own `status:` is never touched.

This README narrates the statuses — each playbook is the authority on its own transition rules and gates.

## Sprints & SPs

In booping, a **plan is a sprint** — the unit groom produces and develop executes end-to-end. Story Points (SP) measure the sprint's **complexity and review burden**, not effort or time. A 20-SP sprint might take a couple of hours on one project and a full day on another.

The 1–5 scale:

- **1 SP** — Simple text/config change, no risk.
- **2 SP** — Simple task, predictable, no risk.
- **3 SP** — Medium task, minor risks but predictable overall.
- **4 SP** — Complex task, medium risk, may need small research but clear enough.
- **5 SP** — Research task — developer needs to clarify and decompose further before proceeding.

Sprints over **35 SP** get hard to keep reviewable, so groom suggests a split into sibling sprints above that mark. It's a soft cap, **not a velocity** — booping has no fixed cadence and no per-week capacity. Tasks at 5 SP must be re-decomposed; develop bundles up to two consecutive milestones into a single agent briefing, so milestones are sized against that combined review burden.

## Extensibility

Playbooks stay wide-domain and stack-agnostic. Project-specific concerns live entirely in your vault:

- **`~/Claude/{project}/_lessons/`** — targeted rules from learn. Each carries a `targets:` list naming the playbooks, steps, agents and skills it reaches — that list is how a project teaches groom its conventions, develop its test runner, or a worker agent its house rules.
- **`~/Claude/{project}/plan_templates/*.md`** — project-local plan templates. Discovered alongside the core templates (`backend`, `frontend`, `claude-skill`, `cli`, `documentation`); can override a core one by sharing its `name`, or add new ones.
- **`~/Claude/{project}/review_templates/*.md`** — project-local code-review templates. Loaded by `code-review` alongside the core templates (`coding-architecture`, `python`, `security`); it picks the matching subset from the repo's manifests and each template's `description` frontmatter.
- **`~/Claude/{project}/_playbooks/`** — playbooks of your own, discovered by `/playbook` beside the shipped ones.

## Learning

`retro` reads the working set of finished plans, mines the session logs and git diff for what actually shipped, takes your raw feedback first, and writes one standalone `~/Claude/{project}/retrospectives/{slug}.md` — what worked, what didn't, divergences from spec, a goal verdict per plan. One retrospective can cover several plans; each gets its `retro:` stamped with the file's path.

`learn` then reviews the retrospective with you, picks the durable findings, and routes each to one of two destinations: a targeted lesson (`~/Claude/{project}/_lessons/{N}_{title}.md`, carrying a `targets:` list), or a one-line bullet in the attached repo's `CLAUDE.md`. Lessons are injected into the playbooks, steps, agents and skills they name. You confirm the whole review table before anything lands.

## What booping doesn't do

booping is a feedback loop, not an autopilot. Three things stay your job:

- **Plan review is still on you.** Groom produces a draft and waits at `awaiting-approval` for a reason — sharpen it, push back, ask for splits. As lessons accumulate, plans drift toward your style and constraints, but only if you fed the loop honest reviews. Shit in, shit out.
- **Code review is still on you.** Develop ships milestones; you own the quality bar. The `code-review` playbook is a helper that runs stack-aware passes over the diff and records its findings — but reading them, deciding what's off, and bringing them into retro so learn can turn them into rules is still your job.
- **Learning isn't automatic.** Retro and learn are scaffolding for a feedback loop, not a substitute for one. You still need to sit with the retrospective, confirm which findings are durable, and let learn write them down. Skip that step and the loop stalls.

Invest in the loop and it compounds. Treat it as a magic box and you'll get magic-box results.

## License

MIT — see [LICENSE](LICENSE).
