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

### M1: {Milestone name} — {SP} SP | pending

**Goal**: one sentence — the observable change in CLI behavior.

**Verify**: exact invocation + expected output (e.g. `./bin/mytool --flag arg 2>&1 | diff - tests/fixtures/expected.txt`).

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | ... | `bin/mytool`, `tests/fixtures/*.txt` | 2 | pending |

#### Task 1.1 DoD

- [ ] Happy-path invocation produces expected output.
- [ ] `--help` reflects the new surface.
- [ ] Exit code matches the contract (0 on success, ≠0 on defined failure modes).

---

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

- [ ] Frontmatter matches [plan frontmatter](../../docs/template_plan_frontmatter.md).
- [ ] `sp` equals the sum of per-task SP across milestones.

## Content

- [ ] Context names the user-visible CLI behavior change.
- [ ] DoD bullets are verifiable by invocation + output diff.
- [ ] Every task lists exact files.
- [ ] Every task DoD uses checkboxes, not prose.
- [ ] Every milestone has a `Verify` invocation.
- [ ] Each milestone executable from a fresh session with only the plan as context.

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
