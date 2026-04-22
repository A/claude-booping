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
3. Read `~/Claude/.booping/projects.json` if present via the `Read` tool. If it doesn't exist, treat as empty.

Summarize the detected state in one paragraph before asking anything. Example: "I see you already have projects `aurora-api`, `aurora-frontend`. CWD `/home/you/Dev/new-thing` has no marker."

## Phase 2: Decide mode

Use `AskUserQuestion` with three options:

- **new** — create a new project for this CWD
- **attach** — attach this CWD to an existing project (list them)
- **cancel** — do nothing

If `$ARGUMENTS` supplies a project name, default to `new` with that name (still confirm).

## Phase 3a: New project

1. Pick the project name. Default: basename of CWD, lowercased, kebab-cased. Confirm with the user.
2. Run `booping-init <name> <cwd>` — this creates `~/Claude/{name}/` with the standard layout, registers the path in `projects.json`, and writes a `.booping-project` marker file in the CWD. (`booping-init` lives in the plugin's `bin/` and is auto-added to PATH when the plugin is enabled.)
3. Write a project `CLAUDE.md` tailored to the repo: one paragraph on what it is, attached repo path, the standard layout block, and the booping-commands block. Use [template-claude-md.md](template-claude-md.md) as a starting point.

## Phase 3b: Attach to existing

1. Pick the project name from the list.
2. Append `{cwd: <CWD>, project: <name>}` to `projects.json` `paths`.
3. Offer to write a `.booping-project` marker file in the CWD — confirm before writing.
4. Do not touch anything under `~/Claude/{name}/`.

## Phase 4: Verify

1. `ls ~/Claude/{name}/` — print the tree so the user can see what exists.
2. Show the registered mapping by reading `~/Claude/.booping/projects.json` via the `Read` tool.
3. Report what to do next: "Run `/chat` to start a discussion or `/groom <topic>` to spec a new piece of work."

## Hard rules

- Never overwrite an existing `~/Claude/{name}/` directory without confirmation. If the target exists, default to attach-mode instead.
- Never write a `.booping-project` marker without asking.
- Never edit the repo's own `CLAUDE.md` (in the attached codebase) — this skill only writes under `~/Claude/{project}/`.
