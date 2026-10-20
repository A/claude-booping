# groom playbook

Spec a sprint: take a rough request and produce a reviewable plan under `~/Claude/{project}/plans/{slug}/` — an `index.md` plus one directory per milestone under `milestones/`, each holding that milestone's tasks, story points, and definition of done.

Grooming is a **playbook**, not a skill — it is driven by [`/playbook`](playbook.md):

```text
/playbook groom
```

## What it does

Run states: `framing` → `researching` → `drafting` → `cross-reviewing` → `presenting` → `awaiting-approval` → `ready-for-dev`. Two loopbacks: `drafting → researching` when the design needs code the research stage missed, and `awaiting-approval → drafting` when your change request touches the plan itself.

Almost every step runs in your session — inline, or assisted (heavy reads go to the research agent, which returns a bounded summary). `researching` and `drafting` are both stages of the one `draft-plan` step. The exception is `cross-review`, which hands the drafted plan to a second-model reviewer and does nothing unless you name one. `present` is the run's single approval gate.

The output is a plan directory `~/Claude/{project}/plans/{slug}/`. Its `index.md` carries the approach, the scope and the YAML frontmatter the rest of the loop (`develop`, `retro`, `learn`) reads; each milestone gets a directory of its own under `milestones/`, holding a milestone file that repeats the directory's name, and that file — not a section of the index — is what develop hands a coding agent as its contract, with room beside it for what the sprint later writes about that milestone. Groom creates the directory with one `booping create` call from a config-declared tree, so the fresh `index.md` arrives complete — including a real `commit:` stamped with repo HEAD at creation. The plan itself is drafted as one file, `draft.md`, beside `index.md`; `booping plan split` cuts it into `index.md`'s body and the milestone files, and generates `index.md`'s `## Milestones` and `## Groups` tables and the plan's total story points — never hand-kept. `draft.md` stays as the drafting source: a fix or a change request edits it and splits again. The intake briefing lands beside it. The directory doubles as the run workdir, so a groom run is **resumable**: its run state lives in the same `index.md`.

A plan is always a directory: `core.plans.glob` resolves `plans/*/index.md` and nothing else, and `core.plans.milestones.glob` resolves the milestone file inside each milestone directory. A vault still holding flat `plans/{slug}.md` files converts them with `/playbook migrate`.

Four steps, in dependency order:

| Step | What it does |
|------|--------------|
| `intake` | Clarify the request, settle scope, create the plan directory — briefing, identity frontmatter, `commit:` at repo HEAD — with one `booping create` call |
| `draft-plan` | Research the code the request touches, draft the whole plan into `draft.md` against a plan template, split it into milestone files and check them |
| `cross-review` | Hand the drafted plan to a second-model reviewer for severity findings — skipped unless `core.groom_playbook.cross_review_agent` names one (unset by default) |
| `present` | Present approach, milestones, SP totals and the milestone-contract check; the run's single approval gate |

### draft-plan

`draft-plan` works in four stages, all in your session:

1. **Research** — reads the code the request touches and what it depends on (bulk reads go to the research agent) and posts the facts, with file paths, in chat. This is the `researching` status.
2. **Draft** — picks the plan template matching the dominant surface and writes the whole plan to `draft.md`: every template section, and one `### M{nn} — {title}` block per milestone, opened by `sp:` and `depends_on:` lines and holding the four sub-headings named in `core.groom_playbook.split.sections`. What the code and the request settle, it decides and records as an assumption; a call only you can make is asked in chat, or — in an autonomous run — written to the plan's `clarifications.md` while the run parks.
3. **Split** — runs `booping plan split draft.md --replace`. A draft it cannot cut (exit 3 or 4) goes to `core.groom_playbook.split_fallback_agent`, which rewrites it into the format outside the vault; the run copies the result over `draft.md` and splits again.
4. **Check** — runs [mdcheck](install.md#prerequisites) over the milestone files against the groom milestone schema ([below](#the-milestone-check)) and fixes the milestones it flags in `draft.md`, then splits again — at most three rounds. Findings left after that are shown at `present`.

The one-pass draft and the split are backed by booping's own groom and split benchmarks ([adr/0030](https://github.com/A/claude-booping/blob/master/vault/adr/0030-groom-drafts-the-whole-plan-in-one-pass.md), [adr/0031](https://github.com/A/claude-booping/blob/master/vault/adr/0031-a-script-cuts-the-plan-into-milestone-files.md)).

When you correct the run — reject a proposal, rewrite what it wrote, answer a gate differently than it suggested — it logs your words verbatim, with the session id and a link to the plan, as one file under the vault's `corrections/`. [Retro](retro.md) starts from those entries.

## Starting a run

```text
/playbook groom
```

Bare invocation picks up whatever you have been discussing in the current session. Name a parked plan or an existing draft to keep iterating on it:

```text
/playbook groom — continue plans/202604301120_documentation-site/index.md, here's feedback to address
```

Everything you say in the invocation reaches `intake` verbatim.

## Best practices

### More detail in the prompt = sharper plan

The playbook works from your request, the codebase, and the accumulated rules. The request is the only knob fully under your control — the more concrete it is, the less the run has to guess.

Brief request — lots of room for misalignment:

```text
/playbook groom — add rate limiting
```

Detailed request — sharply scoped, fewer rounds of revision:

```text
/playbook groom — add per-IP rate limiting to the /api/* routes in apps/api/.
Use Redis (already a dep). 100 req/min default; configurable via env.
Return 429 with Retry-After. No new middleware framework — extend the
existing one in apps/api/middleware/.
```

### Free-text extras

Useful things to mention up front:

- **Reference a template** — "use the bug-investigation template" selects a specific plan template.

Branch selection is **not** groom's job — the [develop playbook](develop.md)'s `provision` step picks and confirms it.

### Define your own plan templates

Drop `*.md` files into `~/Claude/{project}/plan_templates/` to extend or override the templates that ship with the plugin. Each template needs frontmatter (`name`, `description`) and two top-level sections (`# Plan Body`, `# Quality Checklist`). A project-local template with the same `name` as a core template overrides it.

See [Vault](vault.md) for the directory layout.

## booping plan split

Runs on its own as well as inside `draft-plan`, on a hand-written draft.

### `booping plan split DRAFT [--out DIR] [--replace]`

Cuts a one-file plan into `index.md` and one milestone file per `### M{nn} — {title}` block.

- **`DRAFT`** — the one-file plan.
- **`--out DIR`** — the plan directory to write; defaults to `DRAFT`'s directory.
- **`--replace`** — remove existing milestone directories under `DIR` (those matching `core.plans.milestones.glob`) before writing.

It writes `DIR/milestones/M{nn}-{kebab}/M{nn}-{kebab}.md` per milestone, each rendered from `core.groom_playbook.milestone_template` with the block's sections under its headings, and `DIR/index.md`: the existing frontmatter kept (else the draft's own, else none), `sp:` restamped with the milestones' sum when the key exists, and the body the draft's plan sections in order, with the generated `## Milestones` table and a `## Groups` table where the draft's milestones stood. Groups pack contiguous milestones, in `id` order, while their summed SP stays at or under `core.sprint.max_sp`; a lone milestone is always a group.

stdin is not read. stdout prints one line per milestone — `M{nn}-{kebab} sp={n|null} sections=tasks:{lines},dod:{lines},references:{lines},verify:{lines}` — then one `group G{k}: M{nn}, … ({sum} SP)` line per group, then `demoted: {n}` when top-level headings inside a milestone were demoted. stderr carries one `flag: {text}` line per flag (a missing `sp`, a `depends_on` naming a later milestone, …) and `error: {message}` on failure.

| Exit | Meaning |
|------|---------|
| `0` | written, no flags |
| `1` | usage or config error |
| `2` | refused — milestone files exist and `--replace` was not given — or a write failed |
| `3` | no milestone heading found; nothing written |
| `4` | written, with flags |

## The milestone check

`playbooks/groom/_schemas/milestone.yaml` is an mdcheck rule file; run it on its own to re-check a plan after editing its milestone files:

```text
mdcheck ${CLAUDE_PLUGIN_ROOT}/playbooks/groom/_schemas/milestone.yaml {plan-dir}/milestones/*/M*.md
```

- **SP** — each task's SP cell in the `## Tasks` table is 1–4, below `core.sprint.redecompose_threshold`, and the milestone's frontmatter `sp` is at most `core.sprint.max_sp` (15); the schema restates both as static patterns, so a changed value needs the schema changed too.
- **Verify** — the first paragraph of `## Verify` is one inline code span: the milestone's single command.
- **Tasks** — `## Tasks` names at least one file path, a backticked token holding `/` or a `.ext`.
- **Definition of Done** — `## Definition of Done` has at least one checkbox item.

mdcheck exits `0` when clean, `1` with findings, one line per finding naming the file, the line and the failed rule.

## Reviewing the plan

What to check before approving at `present`, the run's **only** review gate:

- **Goal is sharp.** The `summary` in frontmatter matches the request, with no scope creep.
- **Milestones cover the goal end-to-end.** No silent gaps, no "and then ..." vagueness in the last milestone.
- **Tasks are sized honestly.** No 5-SP tasks except deliberate research spikes (see Story points).
- **Definitions of done are verifiable.** Each DoD checkbox is mechanically confirmable — not "code looks good".

Approve explicitly ("looks good", "ship it") to move the plan to `ready-for-dev`, groom's terminal status and the queue the [develop playbook](develop.md) claims from. A change request touching architecture, scope, milestones, tasks or estimates sends the run back to `drafting`.

## Story points

booping uses a 1–5 scale for per-task estimates, set in `src/config.yaml`:

- **1** — Simple text/config change, no risk.
- **2** — Simple task, predictable, no risk.
- **3** — Medium task, minor risks but predictable overall.
- **4** — Complex task, medium risk, may need small research but clear enough.
- **5** — Research task — the developer needs to clarify and decompose further before proceeding.

Two thresholds drive the playbook's behaviour, both configurable:

- **`core.sprint.default_threshold_sp` (default `35`)** — soft cap on plan size. Above this, `present` proposes splitting the plan into sibling stubs rather than shipping one mega-sprint.
- **`core.sprint.redecompose_threshold` (default `5`)** — a task estimated at ≥ this value is research and must be split before the run can leave `drafting`; a hard gate on the `drafting → cross-reviewing` edge, checked by [the milestone check](#the-milestone-check). A milestone is the sum of its tasks, capped by `core.sprint.max_sp`.

Both thresholds are ceilings, not velocity targets. A 12-SP plan is fine; a 38-SP plan is the trigger to consider a split.

## Config

The playbook reads these keys from `src/config.yaml`. See [Project config](project_config.md) for the deep-merge override mechanics; per-project tweaks live in `~/Claude/{project}/config.yaml`.

- **`core.sprint.default_threshold_sp`** — soft cap on total SP per plan; above this the run proposes a split.
- **`core.sprint.redecompose_threshold`** — per-task SP value at or above which the task must be split.
- **`core.sprint.scale`** — the 1–5 SP definitions (each a `{sp, meaning}` entry).
- **`core.task_types`** — list of `{type, description, doc_uri}` entries (`feature`, `bug`, `refactoring`). The request is classified against this list; the matching `doc_uri` lazy-loads detailed guidance for that task type.
- **`core.groom_playbook.cross_review_agent`** — the agent that cross-reviews the drafted plan. `null` by default, which skips the `cross-reviewing` step entirely.
- **`core.groom_playbook.split.sections`** — the four milestone sub-headings, in order (tasks, definition of done, references, verify): the draft's `####` headings and the milestone file's `##` headings.
- **`core.groom_playbook.split_fallback_agent`** — the `model:effort` of the agent that rewrites a draft `booping plan split` cannot cut (default `opus:medium`); `null` makes the run rewrite it itself.
- **`core.research_agent`** — the agent assisted steps hand their bulk reads to (default `booping:booping-researcher`). Shared across playbooks, so it sits directly under `core`.
