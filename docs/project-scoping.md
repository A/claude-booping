# Project scoping

booping artifacts live under `~/Claude/{project}/`. Every skill needs to know which project is "current" before it reads or writes anything.

## Resolution order

Every skill resolves the project in this order and stops at the first match:

1. **`.booping-project` marker file** in CWD or any ancestor directory. One line: the project name. This is the expected happy path — one repo → one project.
2. **`~/Claude/.booping/projects.json`** path entries. A list of `{cwd, project}` records; the skill picks the longest matching prefix. Populated by `booping-init` and by first-run prompts.
3. **Ask the user.** The skill lists existing projects (from `ls ~/Claude/`, directories only, excluding dotfiles) and offers "create new". The answer is persisted via step 2 (and optionally step 1 if the user allows a marker file in the CWD).

## `~/Claude/.booping/projects.json`

```json
{
  "projects": {
    "aurora-api": {"root": "~/Claude/aurora-api"}
  },
  "paths": [
    {"cwd": "/home/anton/Dev/zorya-development/aurora-api", "project": "aurora-api"}
  ]
}
```

The skill picks the longest matching `cwd` prefix. If two entries tie, the more recently added one wins (it is stored later in the array).

## First-run behavior

On the first run of any booping skill from a directory the system has never seen, the skill:

1. Runs the resolution chain above.
2. If step 3 is reached, it asks the user and shows existing projects.
3. On confirm, it calls the equivalent of `booping-init <name> <cwd>` to register and (optionally) write the marker file.

After that, subsequent runs from the same CWD skip the question.

## Cross-project work (deferred)

Running two projects in parallel (e.g. frontend + backend sessions simultaneously with isolated contexts) is out of scope for now. One CWD maps to exactly one project via the marker file or `projects.json`. If you later need umbrella projects or parallel sessions, this doc will grow.
