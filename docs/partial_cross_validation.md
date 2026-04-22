Mandatory for features and refactorings; optional for single-file bugs.

```bash
booping-validate-plan ~/Claude/{project}/plans/YYYYMMDD-{kebab-title}.md
```

`booping-validate-plan` ships in the plugin's `bin/` and is auto-added to PATH. It derives the project from the plans path, loads `~/Claude/{project}/lessons/` as the rubric, and handles its own API-key check.

**Security:** never inspect the environment for `GEMINI_API_KEY` (no `env | grep`, no `printenv`, no reading `.env` files). Call the validator blind.

Handle by exit code:

| Exit code | Meaning | Action |
|-----------|---------|--------|
| `0` | Validation ran | Paste full stdout to the user verbatim under a "Gemini cross-validation" heading. Address every **CRITICAL EXECUTION RISK** and **RULE VIOLATION** before finalizing. **ARCHITECTURAL BLIND SPOTS** may be deferred with explicit user acceptance — record in the Risk register. |
| `2` | Skipped (no `GEMINI_API_KEY`) | Report: "Gemini cross-validation skipped — `GEMINI_API_KEY` not set." Continue. Optionally fall back to the `double-check` skill if installed. |
| `1` | Error | Report stderr verbatim. Continue but flag that cross-validation did not complete. |

The validator's output **belongs to the user** — paste it as-is.
