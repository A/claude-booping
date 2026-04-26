# booping

A project-scoped sprint workflow for Claude Code. booping turns a feature idea into a durable, on-disk loop — **groom → develop → retro → learn** — with mandatory sub-agent delegation so the orchestrator's context never drowns in implementation detail. Every artifact (plans, retros, lessons, sprint snapshots) lives under `~/Claude/{project}/`, one folder per codebase, so weeks-long programs stay legible long after the session ends.

![Vault open in Obsidian](docs/images/vault-in-obsidian.webp)

*Each project's vault is a plain Obsidian-friendly folder of markdown files.*

## Obsidian-ready by design

The vault at `~/Claude/{project}/` is markdown-only with YAML frontmatter that Obsidian renders natively as Properties. One vault per project, side-by-side with whatever else you keep in `~/Claude/`. No proprietary database, no lock-in — just files you can grep, version, and edit by hand. Open the folder in Obsidian for a graph view of plans, retros, and lessons; open it in your editor for everything else.

## Installation

### Development (fastest)

```bash
claude --plugin-dir /path/to/claude-booping/
```

Loads the plugin into the current session only.

### Via Claude Code marketplace (persistent)

```
/plugin marketplace add /path/to/claude-booping/
/plugin install booping@booping-local
```

The plugin ships with a `.claude-plugin/marketplace.json` so the second command works.

### Via git URL

```
/plugin marketplace add https://github.com/<you>/claude-booping
/plugin install booping@booping-local
```

After installing, `cd` into the target repo and run `/install`. That single step scaffolds `~/Claude/{project}/` (with `plans/`, `retrospectives/`, `lessons/`, `notes/`, `_booping/`), drops a `.booping` marker in the repo so future skills resolve the right vault, and seeds `CLAUDE.md` with a project-specific stub.

## Quick start

The full loop is five commands. Run them in order:

```bash
# Inside the target repo, once:
/install

# Spec a feature, bug, or refactor — free-text description:
/groom Add per-tenant rate limiting to the public API

# Execute the next ready plan (auto-claims from the queue):
/develop
# …or target a specific one:
/develop ~/Claude/{project}/plans/20260426-per-tenant-rate-limiting.md

# Retrospect on what shipped:
/retro ~/Claude/{project}/plans/20260426-per-tenant-rate-limiting.md

# Fold the retro's findings into durable rules:
/learn ~/Claude/{project}/retrospectives/20260426-per-tenant-rate-limiting.md
```

Plan paths are `~/Claude/{project}/plans/YYYYMMDD-{kebab-title}.md`. Retro paths are `~/Claude/{project}/retrospectives/YYYYMMDD-{kebab-title}.md`. The skills will list candidates if you forget the exact filename.

## Workflow

A plan moves through a small set of statuses owned by exactly one skill at a time. `/groom` shapes the spec and waits for explicit user approval before handing off; `/develop` claims the next ready plan and executes milestone by milestone; `/retro` compares what shipped to the original spec; `/learn` distils the retrospective into rules that bind the next sprint.

The status vocabulary below is the canonical set in `src/config.yaml` `plan.statuses`:

```text
/groom    backlog → in-spec → awaiting-plan-review → ready-for-dev
          (loopback: awaiting-plan-review → in-spec)
          (parking: in-spec → backlog)
          (cancellation: backlog/in-spec/awaiting-plan-review → cancelled)

/develop  ready-for-dev → in-progress → awaiting-retro
          (failure: in-progress → fail)

/retro    awaiting-retro → awaiting-learning
          (skip: awaiting-retro → done)

/learn    awaiting-learning → done

Terminal states: cancelled · done · fail
```

Status transitions are manual frontmatter edits applied by the owning skill when its trigger fires. After any transition, `bin/booping-plans --status <new-status>` confirms the queue.

## Use cases

Patterns observed across ~15 sprints on a real Django/DRF/Temporal backend.

**Multi-week feature programs.** A feature spans 40–60 SP across model changes, migrations, workflow rewrites, and frontend alignment. The original design stays visible in `plans/`, so a weekend away doesn't cost you the rationale.

**Tech-debt campaigns.** Service-layer extractions or LLM-client migrations touch dozens of files over multiple sprints. `lessons/` catches the meta-rules ("prefer protocol over base class", "don't mock the DB") so later sprints don't repeat earlier mistakes.

**Business-goal divergence.** A sprint finishes technically (`done`) but the business goal misses — the feature shipped, yet "the user-visible event system is slow". `/retro` records this with `goal: fail`; `/learn` turns the root cause into a rule that blocks the same pattern next time.

**Small unblocker sprints.** 7-SP spikes — a test helper, a migration dry-run, a preflight check. Grooming them is fast; skipping grooming turns them into 3-day rabbit holes.

**Cross-repo coordination.** One feature spanning two repos (e.g. `aurora-api` + `aurora-frontend`). One sprint row per project; retros cross-reference each other.

**Solo engineering with Claude Code.** Sub-agent delegation is the lever: the orchestrator stays under control because workers handle the actual edits, and the human reviews diffs without wading through chain-of-thought.

booping is not useful for one-shot scripts or throwaway prototypes. It earns its weight when you're on a codebase long enough to care about what shipped last month.

## Statuses

A plan carries one of the following statuses in its frontmatter. Terminal states are marked.

- **`backlog`** — Parked plan. Split-sibling stubs and user-filed ideas not yet in grooming.
- **`in-spec`** — `/groom` is actively researching, designing, and drafting.
- **`awaiting-plan-review`** — Draft complete; `/groom` is presenting and awaiting explicit user approval, change request, or cancellation.
- **`ready-for-dev`** — Approved. Queued for `/develop` to claim.
- **`in-progress`** — `/develop` has claimed the plan and is executing milestones.
- **`awaiting-retro`** — All milestones done; waiting for `/retro` to write the retrospective.
- **`awaiting-learning`** — Retro written; waiting for `/learn` to absorb lessons.
- **`done`** *(terminal)* — `/learn` has absorbed all lessons.
- **`cancelled`** *(terminal)* — User shelved the plan.
- **`fail`** *(terminal)* — `/develop` hit an unrecoverable blocker.

`src/config.yaml` `plan.statuses` is the canonical contract for the full transition table — including triggers (`when`), gates, artifacts, and `on_exit` mutations. Read it there if you need the exact rules; this README only narrates them.

## Sprints & SPs

Story Points (SP) measure **complexity and review burden**, not effort or time. A 3-SP task may take an hour or a day; what matters is how much judgement and how many trade-offs are in flight.

The 1–5 scale (`src/config.yaml` `sprint.scale`):

- **1 SP** — Simple text/config change, no risk.
- **2 SP** — Simple task, predictable, no risk.
- **3 SP** — Medium task, minor risks but predictable overall.
- **4 SP** — Complex task, medium risk, may need small research but clear enough.
- **5 SP** — Research task — developer needs to clarify and decompose further before proceeding.

A plan whose total exceeds **35 SP** (the `sprint.default_threshold_sp`) should be split into sibling sprints during grooming. This is a heuristic ceiling on review burden, **not a velocity** — booping has no fixed cadence and no per-week capacity. Tasks at 5 SP must be re-decomposed; tasks at 1 SP should be grouped into a single agent briefing.

## Extensibility

Wide-domain skills stay stack-agnostic. Project-specific concerns live entirely in your vault:

- **`~/Claude/{project}/_booping/skill_<name>.md`** — per-skill extension. Loaded automatically into the skill's context at invocation. Use it to teach `/groom` your codebase's conventions or `/develop` your test runner.
- **`~/Claude/{project}/_booping/agent_<name>.md`** — per-agent extension. Injected into the matching agent's body at load time so worker agents inherit project rules without separate reads.
- **`~/Claude/{project}/plan_templates/*.md`** — project-local plan templates. Discovered alongside the core templates; can override a core one by sharing its `name` or add entirely new ones.
- **`~/Claude/{project}/lessons/`** — accumulated rules from `/learn`. Read by skills' Preflight on every invocation.
- **`~/Claude/{project}/CLAUDE.md`** — project conventions. Loaded by skills.

A per-project override of `src/config.yaml` (so you can tune the plan lifecycle, sprint scale, task types, and agent wiring without forking the plugin) is the planned next step on the customisation surface.

## Learning

`/retro` and `/learn` are the loop that makes booping worth more than the sum of its sprints.

`/retro` reads the plan, scans the session logs and git diff for what actually shipped, and writes a retrospective at `~/Claude/{project}/retrospectives/YYYYMMDD-{kebab-title}.md` — what worked, what didn't, divergences from spec, the business goal outcome.

`/learn` then reviews the retrospective with the user, picks the durable findings, and writes them as `~/Claude/{project}/lessons/{N}_{title}.md`. Lessons are loaded automatically by future `/groom` and `/develop` invocations, so the next sprint inherits the rules of every earlier one. The user confirms each lesson before it lands.

## Dependencies

**Required:**

- **Claude Code** — the host. booping is a plugin; it doesn't run standalone.
- **`uv`** — every CLI in `bin/` is an inline-script (PEP 723) that auto-resolves its own deps (`jinja2`, `pyyaml`, `watchfiles`, `google-genai`). No `pip install`, no virtualenv to manage.
- **`git`** — vault commits and (in `/develop`) sprint branches.

**Optional:**

- **`GEMINI_API_KEY`** environment variable — enables `/groom`'s cross-validation pass via `bin/booping-external-llm-call`. Without it, the cross-validation gate is skipped.

## License

MIT — see [LICENSE](LICENSE).
