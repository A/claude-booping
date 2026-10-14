Before drafting the review table, check whether each candidate duplicates or conflicts with existing coverage:

The lookup set is:

- The rule records of all three specs tiers — `booping specs ls --tier {core,global,project} --type rule`, one call per tier; a tier that does not exist is skipped silently. Only the project tier is ever written.
- `{vault}/_lessons/` — this project's lessons, shadowing a global lesson of the same filename.
- `{home_dir}/_lessons/` — global lessons, shared across projects (the vault-home base is `booping config-get home_dir`).
- The attached repo's `CLAUDE.md` — the non-rule destination.

Skip silently when a directory is empty or a file is absent. Lessons are read here, never written: no row routes to a lesson file.

Record a sweep verdict per candidate as one of:

- `new` — no prior coverage anywhere in the lookup set.
- `update existing at rule/NNNN` — duplicate or refinement of a project rule; the candidate becomes an edit of that record in place.
- `update existing at _lessons/{file}` — duplicate of a lesson in `{vault}/_lessons/`; the candidate is converted on write into a new project rule carrying the merged content.
- `covered by {ref}` — already covered by a core or global rule, or a global lesson; shown in the review table and never written.
- `conflict with {ref}` — contradicts an existing rule; surface it in the review table as a visible flag.
