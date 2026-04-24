---
name: install
description: Scaffold a booping project under ~/Claude/{project}/ and attach it to the current repo. Use when onboarding a new repo or formalizing an existing one.
argument-hint: "[project-name]"
user-invocable: true
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Bash(ls ~/Claude/*)
  - Bash(ls ~/Claude)
  - Bash(ls -1 ~/Claude/*)
  - Bash(ls -1 ~/Claude)
  - Bash(ls -la ~/Claude/*)
  - Bash(ls -la ~/Claude)
  - Bash(booping-init:*)
  - AskUserQuestion
effort: high
---

# booping — /install

Bootstrap the current repo as a booping project. The skill performs the scaffolding — no script-running required from the user.

## Tool discipline

This skill does its detection with native tools, not shell pipes — no `grep`, no `cat`, no `|`. Specifically:

- Listing `~/Claude/`: use a plain `ls ~/Claude/` (no flags beyond `-1` / `-la`, no pipes). Filter out dotfiles in your own reasoning after reading the output.
- Reading JSON / markers: use the `Read` tool, not `cat`.
- Finding a `.booping-project` marker in CWD or ancestors: use `Glob` (e.g. `.booping-project`, `*/.booping-project`) or `Read` directly on the expected path. Don't shell out for this.

## Phase 1: Detect state

In parallel:

1. `ls ~/Claude/` — list existing booping projects. Ignore entries starting with `.` when summarizing.
2. Check for a `.booping-project` marker in CWD or ancestors — use `Read` on `<cwd>/.booping-project` (and one or two parent paths if relevant) or `Glob`. If `Read` returns "file does not exist", treat that as "no marker".

Summarize the detected state in one paragraph before asking anything. Example: "I see you already have projects `aurora-api`, `aurora-frontend`. CWD `/home/you/Dev/new-thing` has no marker."

## Phase 2: Decide mode

Use `AskUserQuestion` with three options:

- **new** — create a new project for this CWD
- **attach** — attach this CWD to an existing project (list them)
- **cancel** — do nothing

If `$ARGUMENTS` supplies a project name, default to `new` with that name (still confirm).

## Phase 3a: New project

1. Pick the project name. Default: basename of CWD, lowercased, kebab-cased. Confirm with the user.
2. Run `booping-init <name> <cwd>` — this creates `~/Claude/{name}/` with the standard layout and writes a `.booping-project` marker file in the CWD. (`booping-init` lives in the plugin's `bin/` and is auto-added to PATH when the plugin is enabled.)
3. Write a project `CLAUDE.md` tailored to the repo: one paragraph on what it is, attached repo path, the standard layout block, and the booping-commands block. Use [template-claude-md.md](template-claude-md.md) as a starting point.

## Phase 3b: Attach to existing

1. Pick the project name from the list.
2. Offer to write a `.booping-project` marker file in the CWD — confirm before writing.
3. Do not touch anything under `~/Claude/{name}/`.

## Phase 4: Verify

1. `ls ~/Claude/{name}/` — print the tree so the user can see what exists.
2. Confirm the `.booping-project` marker in the CWD (if one was written) by reading it.
3. Report what to do next: "Run `/chat` to start a discussion or `/groom <topic>` to spec a new piece of work."

## Phase 5: Populate developer-agent extension

After the scaffold lands, create `~/Claude/{project}/_booping/agent_booping-developer.md` with project-specific detail that the three developer tiers (junior/middle/senior) will all read at briefing time.

**Skip this phase entirely** if the user is attaching an existing project that already has this extension file — in that case, note "existing extension preserved at `~/Claude/{project}/_booping/agent_booping-developer.md`".

Ask the user four short questions via `AskUserQuestion`:

1. **Primary language(s)** — free text (e.g. "Python 3.12", "Rust 1.80", "TypeScript 5 + React 19").
2. **Test command** — free text (e.g. "just test", "pytest", "pnpm test").
3. **Lint/format command** — free text (e.g. "just lint", "ruff check + ruff format", "biome check").
4. **Dev environment notes** — free text, optional (e.g. "Docker Compose up + Redis required; migrations via `just migrate`").

Write the file with this shape (substitute the user's answers):

```markdown
# booping-developer (project extension)

Project-local rules and facts for all three developer-agent tiers (junior/middle/senior).

## Stack
{{answer 1}}

## Running tests
{{answer 2}}

## Lint / format
{{answer 3}}

## Dev environment
{{answer 4 if non-empty, else "(none)"}}

## Notes

- If a task touches areas outside the stack above, stop and escalate to the orchestrator before implementing.
- Always prefer the project's own commands over ad-hoc invocations. If the task specifies a Verify command, run that — don't substitute.
```

## Hard rules

- Never overwrite an existing `~/Claude/{name}/` directory without confirmation. If the target exists, default to attach-mode instead.
- Never write a `.booping-project` marker without asking.
- Never edit the repo's own `CLAUDE.md` (in the attached codebase) — this skill only writes under `~/Claude/{project}/`.
