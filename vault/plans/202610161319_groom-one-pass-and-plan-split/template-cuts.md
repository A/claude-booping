# Template cuts

Lines removed from the five core plan templates (M07). Rule ids are the ablation's 16 "cut" rules (adr/0030); "code" means `booping plan split` / `booping plan check` / draft-plan's format now owns the item; "7.1" means the milestone-files merge.

## backend.md

| Rule / reason | Removed |
|---|---|
| ctx_current_state | Context bullet "**Current state** — what exists today, what's missing or broken." ("Cover three beats" → "two beats") |
| decisions_justified | "One bullet per decision: **topic**, the decision, and a one-sentence justification." and "- **{Topic}**: {decision} — {why}" |
| research_facts | not present in this template (now draft-plan's research stage) |
| arch_concrete_refs | "Integration points. Reference concrete files and functions." |
| arch_diagram | "One diagram when the flow is non-trivial." |
| ms_index_table | Milestones "Generated table — one row per milestone file, projected with `core.plans.milestones.table_columns` by `booping query`. Derived output: no hand-written rows, no milestone bodies in this file." |
| sp_per_milestone | not present in this template (draft-plan's format block) |
| no_two_ways | checklist "No milestone's Scope or Tasks offers two ways to do the same thing" |
| no_tbd | anti-patterns "No "TBD", "TODO", "implement later", "details to follow"." |
| no_similar_to | anti-patterns "No "Similar to Task N" without specifying what's similar." |
| no_either_or | anti-patterns "No "either X or Y" unresolved — pick one, justify in Decisions." |
| no_vague_tasks | anti-patterns "No "handle edge cases", "add error handling", "clean up" as standalone tasks." |
| req_coverage | checklist "Every requirement in the user's request maps to at least one task, or is explicitly deferred in Out of scope with justification." |
| ext_verified | whole "## External references validated" block (registry versions, third-party API endpoints, verification note) |
| names_consistent | whole "## Consistency" block (names, file paths, data structures) |
| persistence_rollback | Backend-specific "New data persistence (migration, schema change, new index) is called out explicitly and paired with a rollback note." |
| anti-pattern block | "No task spanning unrelated concerns"; "No milestone that requires reading more than its own file and `index.md` to execute" |
| code | "`sp` equals the sum of the milestone files' `sp`."; "Every milestone is a file in `milestones/`…"; "`index.md`'s milestone table has one row per milestone file…"; "Every milestone file's `## Verify` is … scoped…"; "Every task lists exact file paths…"; Scope clause ", so it executes without reading another milestone" |
| 7.1 | "## Milestone files" seeding paragraph (`booping scaffold core.groom_playbook.milestone_scaffold`); Verify's whole-repo-gates sentence (stated once in draft-plan) |
| checklist no longer walked (C10) | intro "Verify before leaving `in-spec`. Every item must be satisfiable by reading the plan directory alone."; subsection "Out of scope + coverage" renamed "Out of scope" |

## claude_skill.md

| Rule / reason | Removed |
|---|---|
| ctx_current_state | "Current behavior," from Context |
| decisions_justified | "- **{Topic}**: {decision} — {why}" |
| research_facts | not present in this template |
| arch_concrete_refs | not present in this template |
| arch_diagram | "Diagram the skill's load-time inputs (…) if non-trivial." — the load-time inputs list kept in the Architecture sentence |
| ms_index_table | Milestones "Generated table — …" line |
| sp_per_milestone | not present in this template |
| no_two_ways | checklist "No milestone's Scope or Tasks offers two ways to do the same thing" |
| no_tbd | anti-patterns "No "TBD", "TODO", "implement later", "details to follow"." |
| no_similar_to | not present in this template |
| no_either_or | not present in this template |
| no_vague_tasks | not present in this template |
| req_coverage | not present in this template |
| ext_verified | whole "## External references validated" block ("Template paths reference files that exist", "Lazy-load doc links resolve from the rendered skill's location") |
| names_consistent | not present in this template |
| persistence_rollback | not present in this template |
| anti-pattern block | "No task spanning unrelated concerns (config schema + renderer + multiple skills in one row)"; "No prose section that duplicates a rendered table or partial"; "No "Phase 1..N" numbered workflow…"; "No stale state names" |
| code | `sp` sum; every milestone a file; index table; "Every milestone file's `## Verify` includes a rebuild and stays scoped…"; "Every task lists exact template / partial / config paths"; "Each milestone file executable from a fresh session…" |
| 7.1 | "## Milestone files" seeding paragraph; Verify's whole-repo-gates sentence |

## cli.md

| Rule / reason | Removed |
|---|---|
| ctx_current_state | "Current behavior," from Context |
| decisions_justified | "- **{Topic}**: {decision} — {why}" |
| research_facts | not present in this template |
| arch_concrete_refs | not present in this template |
| arch_diagram | not present in this template |
| ms_index_table | Milestones "Generated table — …" line |
| sp_per_milestone | not present in this template |
| no_two_ways | checklist "No milestone's Scope or Tasks offers two ways to do the same thing" |
| no_tbd | anti-patterns "No "TBD", "TODO", "implement later", "handle error cases later"." |
| no_similar_to | not present in this template |
| no_either_or | not present in this template |
| no_vague_tasks | not present in this template |
| req_coverage | not present in this template |
| ext_verified | whole "## External references validated" block ("Dependency versions … confirmed against current registry", "Any OS command the CLI shells out to is verified to exist…") |
| names_consistent | not present in this template |
| persistence_rollback | not present in this template |
| anti-pattern block | "No task spanning unrelated concerns"; "No "add a command for X" without specifying argument shape + output"; "No silent failures…"; "No CLI that prints to stdout and stderr the same content" |
| code | `sp` sum; every milestone a file; index table; "Every milestone file's `## Verify` is an invocation scoped…"; "Every task lists exact files"; "Each milestone file executable from a fresh session…" |
| 7.1 | "## Milestone files" seeding paragraph; Verify's "Scoped to this milestone — whole-repo gates…" sentence |

## documentation.md

| Rule / reason | Removed |
|---|---|
| ctx_current_state | not present in this template |
| decisions_justified | "- **{Topic}**: {decision} — {why}" |
| research_facts | not present in this template |
| arch_concrete_refs | not present in this template |
| arch_diagram | not present in this template |
| ms_index_table | "The table below is generated — one row per milestone file, … no milestone bodies in this file." |
| sp_per_milestone | not present in this template |
| no_two_ways | checklist "No milestone's Scope or Tasks offers two ways to do the same thing" |
| no_tbd | anti-patterns "No "TBD", "TODO", "details to follow" in pages that ship." |
| no_similar_to | not present in this template |
| no_either_or | not present in this template |
| no_vague_tasks | not present in this template |
| req_coverage | not present in this template |
| ext_verified | whole "## External references validated" block ("Every package version, theme name, … checked against current upstream docs", "All cross-links resolve from the rendered site") |
| names_consistent | not present in this template |
| persistence_rollback | not present in this template |
| anti-pattern block | "No mixed audiences in one page"; "No giant single-page dump…"; "No content that restates the schema/code source of truth…" |
| code | `sp` sum; every milestone a file; index table; "Every milestone file's `## Verify` includes a build or local-serve check… no whole-repo gate"; "Every task lists exact file paths"; "Each milestone file executable from a fresh session…" |
| 7.1 | "## Milestone files" seeding paragraph; Verify's whole-repo-gates sentence, reduced to "The strict full-site build and the CI workflow run belong in Final Verification." |

## frontend.md

| Rule / reason | Removed |
|---|---|
| ctx_current_state | "Current UI state," from Context |
| decisions_justified | "- **{Topic}**: {decision} — {why}" |
| research_facts | not present in this template |
| arch_concrete_refs | "Reference concrete files." |
| arch_diagram | not present in this template |
| ms_index_table | Milestones "Generated table — …" line |
| sp_per_milestone | not present in this template |
| no_two_ways | checklist "No milestone's Scope or Tasks offers two ways to do the same thing" |
| no_tbd | anti-patterns "No "TBD", "TODO", "implement later", "styling TBD", "handle states later"." |
| no_similar_to | not present in this template |
| no_either_or | not present in this template |
| no_vague_tasks | not present in this template |
| req_coverage | not present in this template |
| ext_verified | whole "## External references validated" block ("Package / library versions confirmed against registry", "API endpoints the UI consumes are verified to exist…") |
| names_consistent | not present in this template |
| persistence_rollback | not present in this template |
| anti-pattern block | "No task spanning unrelated concerns"; "No task that adds a component without also specifying its props, states, and where it mounts"; "No "match the design" without linking the source of truth" |
| code | `sp` sum; every milestone a file; index table; "Every milestone file's `## Verify` is scoped…"; "Every task lists exact files"; "Each milestone file executable from a fresh session…" |
| 7.1 | "## Milestone files" seeding paragraph; Verify's whole-repo-gates sentence |
