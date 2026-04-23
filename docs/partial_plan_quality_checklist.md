# Plan quality checklist

Run after writing the plan file. Every item must be satisfiable by reading the file alone.

## Frontmatter

- [ ] Frontmatter matches [template_plan_frontmatter.md](template_plan_frontmatter.md) — every required field present and shaped correctly.
- [ ] `sp` equals the sum of per-task SP across milestones.
- [ ] `business_goal` is set (non-empty) for `feature` and `refactoring` plans.

## Content

- [ ] Context explains the "why now", not just the "what"
- [ ] For features and refactorings: business goal is phrased as the user/internal-visible outcome, not engineering output
- [ ] Definition of Done bullets are testable (verifiable by running a command or reading an output)
- [ ] Decisions table lists real alternatives — no empty "Alternative considered" rows
- [ ] Lessons applied section lists lesson file paths, not paraphrased rules
- [ ] Every milestone has a `Verify` command
- [ ] Every task has exact file paths, not "related files" or "somewhere in X"
- [ ] Every task DoD has checkboxes, never prose paragraphs

## Anti-patterns (must be absent)

- [ ] No "TBD", "TODO", "implement later", "details to follow"
- [ ] No "Similar to Task N" without specifying what's similar
- [ ] No "handle edge cases", "add error handling", "clean up" as standalone tasks
- [ ] No "either X or Y" unresolved — pick one, justify in Decisions
- [ ] No task spanning multiple concerns (model + API + frontend in one row)
- [ ] No milestone that requires reading more than the plan file to execute

## External references validated

- [ ] Docker image tags verified against Docker Hub / official source
- [ ] Package versions confirmed against PyPI / npm / crates.io
- [ ] Third-party API endpoints and flags validated against current docs
- [ ] No assumed package / image / API without a verification note

## Out of scope

- [ ] Out-of-scope section present and lists at least one excluded concern (prevents "anything goes" interpretation)

## Spec-to-task coverage

- [ ] Every requirement from the user's request maps to at least one task
- [ ] No requirement is partially covered — each is fully addressed, or explicitly deferred with justification in Out of scope

## Consistency

- [ ] Function/class names used in one task match their definition in another
- [ ] File paths are consistent across all tasks
- [ ] Data structures (schemas, models) match between producer and consumer tasks

## CLAUDE.md impact

- [ ] Section present and concrete — either names the specific project CLAUDE.md sections/bullets to update (with an owning task) or explicitly states "No CLAUDE.md changes required" with a one-line justification
- [ ] If the sprint introduces a registry/builder/harness, changes a public data shape, or relocates a "how to add X" procedure, there is a concrete task to update CLAUDE.md in the same sprint — not deferred to retro

## Project-local extensions

- [ ] If `~/Claude/{project}/_booping/skill_groom.md` exists, its checklist items were applied on top of this one
