Sprint branches live in the **attached repo** (not the vault). Create the branch before any worker writes code, and never run worker agents against `main` or `master`.

```bash
cd <repo-path>
git checkout -b <prefix>/<kebab-sprint-title>
```

Pick the prefix from the plan's `type`:

| Plan `type` | Branch prefix |
|-------------|---------------|
| feature     | `feat/`       |
| bug         | `fix/`        |
| refactoring | `refactor/`   |
| other       | `chore/`      |

One branch per sprint. A sprint that spans multiple repos uses the same kebab title in each repo. Project-specific prefix overrides (e.g. `hotfix/`) live in `~/Claude/{project_name}/_booping/skill_develop.md`.
