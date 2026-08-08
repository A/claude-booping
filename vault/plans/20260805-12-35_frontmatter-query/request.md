# Framing brief

## Request

> groom this into a plan

The request closes a design conversation held immediately before it. The substance settled there: a generic frontmatter query surface (CLI + Jinja) addressed by dotted config path, replacing `context.plans`, `render-sprints`, and the three hand-rolled snapshot renderers in the playbook hook scripts; plus a `macro()` form for config-declared commands callable from Jinja.

## Task type

`feature` — the work adds user-facing capability that does not exist today: a new `booping query` subcommand, a new Jinja query surface available to every playbook and skill body, and new config schema (query specs addressed by dotted path, `plans.glob`). Playbook authors gain something they cannot express now.

- Not `bug`: nothing diverges from documented behaviour. `context.plans`, `render-sprints` and the script renderers all work as specified; the complaint is duplication and eager loading, not defect.
- Not `refactoring`: the type requires no user-visible behaviour change, and this run adds a command, a config schema and a template API. The internal cleanups it also carries (dropping `context.plans`, collapsing three renderers) are consequences of the new surface, not the deliverable.

## Problem

**Today.** Frontmatter listing is implemented four times over. `Context.assemble()` loads and parses every plan in the vault on every skill and playbook render, whether or not the body mentions plans (`booping-python/src/booping/context/plan.py:48`), exposing typed `Plan` objects that five template sites filter with `selectattr` (`src/templates/skills/code-review.md.j2:21`, `playbooks/code-review/scope/opus-5.md:9`, `playbooks/retro/playbook.md:26`, `playbooks/learn/playbook.md:31`, `playbooks/groom/intake/fable-5.md:9`). The `render-sprints` command renders one fixed shape from the same data. The three playbook hook scripts (`playbooks/groom/_scripts/_plan_status.py:71`, `playbooks/retro/_scripts/close-working-set:102`, `playbooks/learn/_scripts/close-working-set:103`) each re-implement frontmatter parsing and markdown-table emission in standalone Python, because they are deliberately booping-free. The snapshot's header string is duplicated across all four and is already stale.

A playbook author who wants a list the core did not anticipate has no surface at all: `context.plans` is fixed in shape and scope, and nothing exposes any other markdown directory.

**What must change.** One loader, three faces: a `booping query` subcommand for scripts and debugging, a Jinja filter for bodies, and config-declared query specs addressed by dotted path (`booping query --config develop.developable_plans`) so a query lives beside its consumer and rides the core to global to project merge like every other config value. The query returns rows, not rendered markdown, so callers filter and sort in-template and render at the end. With it in place `context.plans` leaves the context, `render-sprints` loses its last caller, the three script renderers collapse to one call, and `sprints.md` is seeded by `vault.scaffold` and thereafter rewritten by the hooks.

## Clarifications and Decisions

- Queries are addressed by **dotted config path**, matching the convention `booping config-get {dotted.key}` and `booping scaffold {dotted.config.path} {dest}` already use. No `queries:` registry namespace; a query lives under whatever key its consumer owns.
- The query returns **rows (list of mappings), not markdown**. Table rendering is a separate output mode / filter, so a caller can narrow a preset before rendering.
- Outputs: `table` (markdown), `json`, `yaml`, `paths`.
- Both a config-addressed form and an ad-hoc glob form exist; the CLI is a thin wrapper over the shared loader, kept for debugging (`--output json` isolates data bugs from template bugs).
- `glob` is optional on a query spec, defaulting to a well-known `plans.glob` list, so a vault with legacy flat plans overrides one key rather than every query.
- Macros are **argv lists, not shell strings**, invoked as `macro()` from Jinja. In scope for this sprint, alongside the query surface.
- **This plan supersedes `plans/20260804-18-27_booperiser-cli`.** Booperiser is not built: booping is simplified in place instead. Any decision of that plan reused here is re-decided on its own merits, not inherited.
- **`booping` hosts the query surface** — no second CLI.
- **Core sheds its typed model.** Dropping `context.plans` also retires the `Plan` dataclass and `Plan.load_all`; plans leave the core context entirely. This is one step of a larger direction: core becomes a glue layer that lets users write their own playbooks and serves the core playbooks through the same surface, owning no domain-specific logic of its own.
- **`render-sprints` is deleted**, not kept as a repair tool.
- The plan lifecycle state machine removal, and dropping the `chat` and `help` skills, are a **separate sprint** — this one neither depends on nor blocks it.
- Already done in the working tree, not part of this plan: the `groom`, `develop`, `install`, `retro` and `learn` skills are retired in favour of their playbooks.
