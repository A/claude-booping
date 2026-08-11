---
name: cli
description: CLI tool work — argument parsing, subcommands, I/O, error handling, exit codes. Standalone scripts or larger CLI suites.
---

# Plan Body

## Context

What CLI (or subcommand) this plan affects. Current behavior, gap, change after.

## Decisions

- **{Topic}**: {decision} — {why}

Typical topics: argument shape, subcommand layout, I/O format (JSON vs text), exit-code contract, config-file vs flags, dependency footprint.

## Architecture

How the CLI fits the surrounding toolchain. Input sources, output sinks, side effects. If invoked by other tools or skills (e.g. inlined via `!`command``), name the callers and their expected output shape.

## Milestones

Generated table — one row per milestone file, projected with `core.plans.milestones.table_columns` by `booping query`. Derived output: no hand-written rows, no milestone bodies in this file.

## Milestone files

One file per milestone directory under the plan directory's `milestones/`, named after that directory and seeded by `booping scaffold core.groom_playbook.milestone_scaffold` — the seed owns the file's frontmatter keys and its required headings. Write the body into that skeleton:

- **Goal** — one sentence directly under the H1: the observable change in CLI behavior.
- **Scope** — the subcommands and flags in play, the files this milestone touches, and any caller (skill, script) whose expected output shape it affects.
- `## Tasks` — one row per task:

  | Task | Description | Files | SP | Status |
  |------|-------------|-------|----|--------|
  | 1.1 | ... | `bin/mytool`, `tests/fixtures/*.txt` | 2 | pending |

- `## Definition of Done` — one `### Task {n}.{m}` block per task, checkbox bullets only: happy-path invocation produces the expected output, `--help` reflects the new surface, exit code matches the contract (0 on success, ≠0 on defined failure modes).
- `## Verify` — exact invocation + expected output (e.g. `./bin/mytool --flag arg 2>&1 | diff - tests/fixtures/expected.txt`). Scoped to this milestone — whole-repo gates (full test suite, repo-wide lint/typecheck, an aggregate `ci` target) run once in `index.md`'s Final Verification, never per milestone.

## I/O contract

Document the CLI's input/output surface explicitly.

- **Arguments / flags**: `tool [--flag VALUE] <positional>` — what each controls.
- **stdin**: what's read (format, when optional).
- **stdout**: format + shape (plain text? JSON? markdown for skill inlining?).
- **stderr**: diagnostics, warnings, errors.
- **Exit codes**: `0 = success`, `1 = user error`, `2 = internal error`, etc.

## Final Verification

- [ ] Help text updated and accurate.
- [ ] Happy-path + at least one failure-path invocation verified.
- [ ] Exit codes match the documented contract.
- [ ] If inlined via `!`command``: the consumer skill renders cleanly.

## Out of scope

Explicit exclusions — e.g. "no new config-file format", "sync-only; async variant later".

## CLAUDE.md impact

Name sections to update (new CLI in the `CLI` section, new inlining point in a skill), or state "No CLAUDE.md changes required — {justification}".

---

# Quality Checklist

## Frontmatter

- [ ] `title` matches the plan's H1 and `type` is the task type chosen at intake.
- [ ] `sp` equals the sum of the milestone files' `sp`.

## Content

- [ ] Context names the user-visible CLI behavior change.
- [ ] DoD bullets are verifiable by invocation + output diff.
- [ ] Every task lists exact files.
- [ ] Every task DoD uses checkboxes, not prose.
- [ ] Every milestone is a file in `milestones/` carrying its own goal, tasks, DoD and Verify — no milestone body in `index.md`.
- [ ] `index.md`'s milestone table has one row per milestone file and matches their frontmatter.
- [ ] Every milestone file's `## Verify` is an invocation scoped to what that milestone changed — no whole-repo gate (full suite, repo-wide lint/typecheck, aggregate `ci` target); those belong to `index.md`'s Final Verification.
- [ ] Each milestone file executable from a fresh session with only it and `index.md` as context.

## I/O contract

- [ ] Argument / flag shape is enumerated, not "add some flags".
- [ ] Output format for stdout is specified (plain / JSON / markdown).
- [ ] Exit codes are defined for every failure mode the CLI distinguishes.

## Anti-patterns (must be absent)

- [ ] No "TBD", "TODO", "implement later", "handle error cases later".
- [ ] No task spanning unrelated concerns (parser + subcommand + I/O format in one row).
- [ ] No "add a command for X" without specifying argument shape + output.
- [ ] No silent failures — every error path has an exit code and stderr message.
- [ ] No CLI that prints to stdout and stderr the same content (makes piping ambiguous).

## External references validated

- [ ] Dependency versions (PyPI, cargo, npm) confirmed against current registry.
- [ ] Any OS command the CLI shells out to is verified to exist on supported platforms.

## CLAUDE.md impact

- [ ] `## CLI` section (or equivalent) updated with the new tool / subcommand, or explicitly states "No CLAUDE.md changes required".
