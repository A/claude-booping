---
id: "04"
title: "Document rule injection"
sp: 3
status: pending
plan: "vault/plans/202610141732_specs-rule-injection/index.md"
---

# M04: Document rule injection

The public docs, the project guide and the specs format guide say where an accepted targeted rule is injected, what the injected line looks like, and how lessons sit beside it.

**Scope**: docs only, no code. Files: `documentation/playbook.md`, `documentation/specs.md`, `CLAUDE.md`, `src/specs/README.md`. Audience of `documentation/` and `src/specs/README.md`: booping users who author rules — they see targets, brief, the rendered section, the link forms, the tier order, `--no-rules`; loader internals (module names, realpath, model fields) stay out ([rule/0008](../../../../specs/rule/0008-audience-scoped-content.md)).

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | `## Rules` section in the playbook reference beside `## Lessons`: which rules inject (accepted, targets + brief, three tiers, global dropped in pinned renders), target forms (link to the lessons target table, not a copy), the section shape, the ref and link forms, one rule per file when two tiers share a directory, rules before lessons, the notes, `--no-rules`; `--no-rules` added where `--no-lessons` is documented; an injection paragraph in the specs page linking to it | `documentation/playbook.md`, `documentation/specs.md` | 2 | pending |
| 4.2 | `CLAUDE.md` Playbooks section: a **Rules** bullet beside **Lessons**; Agent wiring bullet says "a targeted lesson or rule". `src/specs/README.md`: the rule `targets:` line links to the injection docs | `CLAUDE.md`, `src/specs/README.md` | 1 | pending |

## Definition of Done

### Task 4.1

- [ ] `documentation/playbook.md` has a `## Rules` section covering every point in the task row, with the section shape shown as a fenced example matching M02's locked text.
- [ ] No loader internals in either page; the target-form table exists once (lessons section) and is linked, not copied.
- [ ] `documentation/specs.md` links `playbook.md#rules`; `just docs` exits 0.

### Task 4.2

- [ ] `CLAUDE.md` names rule injection beside lessons in one bullet, with no restated config literal.
- [ ] `src/specs/README.md` rule bullet links the injection docs; `just specs-check` stays clean.

## References

- `documentation/playbook.md` `## Lessons` section — shape and depth to match.
- `vault/docs/_specs/targets.md` — depth ceilings per documentation surface.

## Verify

`just docs` — exits 0 (the build is `--strict`, so any new warning fails it).

Return: only the list of changed files, then the last line of the Verify output.
