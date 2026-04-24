# How to initialize a booping project

When a skill is invoked but no `.booping` file exists in the current working directory, you must onboard the user before continuing with their original request.

## Steps

1. **Propose a project name.**
   - Default to the kebab-cased directory basename (e.g. `claude-booping` for `~/Dev/@A/claude-booping`).
   - If the basename is generic (`app`, `backend`, `repo`, `src`), combine with the parent: `{parent}-{basename}`.
2. **Confirm with the user** — accept their alternative if they offer one.
3. **Ask about `.gitignore`** — should `.booping` be gitignored? Usually yes for personal or multi-dev repos where each contributor picks their own project name.
4. **Write `.booping`** in the repo root with a single line:
   ```
   project_name: {chosen-name}
   ```
5. **Add to `.gitignore`** if step 3 was yes.
6. **Ensure the vault exists** at `~/Claude/{chosen-name}/`. Create it if missing.
7. **Resume the original request** — the project is now resolved on the next `!`bin/booping-project-name`` call.

## Notes

- Do not guess the project name silently; always confirm.
- Do not scaffold any vault subdirectories (`plans/`, `lessons/`, etc.) here — that is the responsibility of `/install` or the first skill that needs them.
