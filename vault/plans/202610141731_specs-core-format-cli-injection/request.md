# Request

## Request

> groom AUTONOMOUS RUN. The owner is not available during this run: do not ask questions and do not wait at review gates — auto-confirm every gate yourself, settle unclear points with a sensible default marked [clarify] in the plan, and at the end write every open question and every default you chose to `clarifications.md` beside the plan's index.md (the groom sidecar). End at `ready-for-dev`.
>
> You run in the worktree /home/anton/Dev/@A/claude-booping-specs on branch `feat/specs` (do not switch branches, never push). The running booping plugin is the master checkout; this worktree is where the feature is built.
>
> ## Request: specs as a core feature of booping — first plan
>
> Read first: `vault/specs/README.md` (the format), `vault/specs/adr/0001-specs-tiers.md` (the decision: three tiers core → global → project, namespaces, lessons become rules), `vault/specs/rule/0001-lessons-are-rules.md`, the values in `vault/specs/value/`, and the rules in `vault/specs/rule/` — every plan choice must obey them. The specs are the source of truth for why; the plan is how.
>
> Goal of the whole feature: booping ships the typed-records specs format (value, rule, adr, conflict, story, idea, reference, runbook) and tooling for it; a global tier at `<home_dir>/_specs/` and a project tier (`specs/` in the repo, or `<vault>/specs/` when the vault is in the repo; configurable) add records; cross-tier refs go by namespace (`booping:rule/0003`, `<user>:rule/0001` with the user id from config, default `$USER`); a rule with `targets:` + `brief:` is injected into the targeted playbook step/agent/skill like a lesson is today.
>
> Scope of THIS plan (groom it; if it exceeds the split threshold, recommend the split and groom the first part only):
> 1. The shipped format moves out of the vault: schemas and the format guide live where booping ships them (e.g. `src/specs/`), and `vault/specs/` keeps only booping's own records and uses the shipped schemas.
> 2. A `booping specs` CLI in `booping-python` (Python, following the repo's CLI conventions, covered by the txtar contract corpus per adr/0020): `check` (each record against its type schema via mdcheck, plus cross-file checks: unique numbers per type, file name pattern, relative link targets exist, reference fields — `values`, `rules`, `supersedes`, `sources` — resolve, namespaced refs resolve across tiers with an unresolved namespace being a warning not an error), `next <type>`, `ls [--type]` (ref, status, summary). Port the logic, not the code, from `/home/anton/Dev/@A/shatterlings/crates/specs/src/` (Rust: check.rs, doc.rs, lib.rs, main.rs, review.rs, tags.rs); site.rs and hook.rs are out of scope here. `just specs-check` calls it; it stays in `just ci`.
> 3. Tier resolution in config: the specs path per tier and the user namespace id, following the existing core → global → project config merge (adr/0004); no new tier mechanism.
> 4. Rule injection: `booping render-playbook` (and agent/skill bodies, where lessons are injected today) also inject every accepted rule from all three tiers whose `targets:` match, as its `brief` plus a link to the record. Lessons keep working unchanged in parallel until a later migration.
>
> Out of scope (list them in the plan as follow-ups, do not groom): the specs site (aggregating several roots for notes pages), `specs-setup` / `specs-upgrade` playbooks and the vault migration that moves lessons into rules, `learn` writing rules instead of lessons, adapting the vault `docs` playbook to the new records, moving the hermes-pet and shatterlings copies onto the shipped format.

## Task type

`feature` — booping gains user-facing capabilities it lacks today: a shipped specs format, a `booping specs` CLI, specs tier config and targeted-rule injection. Not `bug`: nothing observed diverges from expected behaviour; the specs format has no shipped implementation to be wrong. Not `refactoring`: the change is user-visible (new CLI verbs, new config keys, new injected `## Rules` content in rendered bodies), so a no-behaviour-change DoD cannot hold.

## Problem

Today the typed-records format (README + mdcheck schemas) lives only inside booping's own vault at `vault/specs/`, checked by a `just specs-check` recipe that runs mdcheck per file and nothing cross-file; other projects carry drifted copies with a Rust checker in one of them. Booping knows nothing about specs: no tier paths in config, no namespace id, no CLI, and the targeted knowledge a run receives comes only from `_lessons/` files. After this plan, booping ships the format at a plugin location, `booping specs check|next|ls` validates and lists a tier's records with cross-file and cross-tier checks, config names each tier's specs root and the user's namespace, and every accepted rule with matching `targets:` from the core, global and project tiers reaches the targeted playbook step, agent or skill body as its `brief` plus a link — alongside lessons, which keep working.

## Clarifications and Decisions

- Autonomous run: no owner present; every gate auto-confirmed, every default marked `[clarify]` in the plan and listed in `clarifications.md`.
- Scope is items 1–4 of the request; the listed out-of-scope items become follow-ups in the plan.
- Split threshold 35 SP: if the four items exceed it, the plan recommends the split and grooms the first slice only.
