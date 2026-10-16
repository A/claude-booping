---
name: cli
description: CLI tool work — argument parsing, subcommands, I/O, error handling, exit codes. Standalone scripts or larger CLI suites.
---

# Plan Body

## Context

What CLI (or subcommand) this plan affects. Gap, change after.

## Decisions

Typical topics: argument shape, subcommand layout, I/O format (JSON vs text), exit-code contract, config-file vs flags, dependency footprint.

## Architecture

How the CLI fits the surrounding toolchain. Input sources, output sinks, side effects. If invoked by other tools or skills (e.g. inlined via `!`command``), name the callers and their expected output shape.

## Milestones

One `### M{nn} — {title}` block per milestone, in the format draft-plan states. Its content:

- **Tasks** — opens with a **Goal** line (one sentence: the observable change in CLI behavior) and a **Scope** line (the subcommands and flags in play, the files this milestone touches, and any caller — skill, script — whose expected output shape it affects), then one row per task:

  | Task | Description | Files | SP | Status |
  |------|-------------|-------|----|--------|
  | 1.1 | ... | `bin/mytool`, `tests/fixtures/*.txt` | 2 | pending |

- **Definition of Done** — one `Task {n}.{m}` block per task, checkbox bullets only: happy-path invocation produces the expected output, `--help` reflects the new surface, exit code matches the contract (0 on success, ≠0 on defined failure modes).
- **References** — where such files exist, 1–3 existing commands, fixtures or corpus cases whose shape this milestone copies, by path, plus the path of any format spec it must not go looking for.
- **Verify** — exact invocation + expected output (e.g. `./bin/mytool --flag arg 2>&1 | diff - tests/fixtures/expected.txt`).

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

## Content

- [ ] Context names the user-visible CLI behavior change.
- [ ] DoD bullets are verifiable by invocation + output diff.
- [ ] Every task DoD uses checkboxes, not prose.
- [ ] Every milestone's References names 1–3 existing files to copy the shape of where such files exist, or states that none applies.
- [ ] No milestone asks for a deliverable in the worker's report — each is named as a path plus "Create" or "Append to", relative to the repo root or the plan directory.

## I/O contract

- [ ] Argument / flag shape is enumerated, not "add some flags".
- [ ] Output format for stdout is specified (plain / JSON / markdown).
- [ ] Exit codes are defined for every failure mode the CLI distinguishes.

## CLAUDE.md impact

- [ ] `## CLI` section (or equivalent) updated with the new tool / subcommand, or explicitly states "No CLAUDE.md changes required".
