Mandatory for features and refactorings; optional for single-file bugs.

Run `booping-external-llm-call --prompt=validate-plan` **once per plan** during grooming, after addressing the user's initial feedback on the draft. Do not re-run on every iteration. Cross-validation is an advisory review, not a CI gate — re-running burns tokens without proportional value. If the user makes substantive scope changes after the first validation, re-running is acceptable; iterative wording tweaks are not grounds to re-run.

```bash
booping-external-llm-call --prompt=validate-plan \
  --context.plan=~/Claude/{project}/plans/YYYYMMDD-{kebab-title}.md \
  --context.lessons=~/Claude/{project}/lessons/
```

`booping-external-llm-call` ships in the plugin's `bin/` and is auto-added to PATH. Templates live under `bin/llm-call-templates/`. The CLI handles its own API-key check.

**Security:** never inspect the environment for `GEMINI_API_KEY` (no `env | grep`, no `printenv`, no reading `.env` files). Call the validator blind.

Handle by exit code:

| Exit code | Meaning | Action |
|-----------|---------|--------|
| `0` | Validation ran | Paste full stdout to the user verbatim under a "Gemini cross-validation" heading. Address every **CRITICAL EXECUTION RISK** and **RULE VIOLATION** before finalizing. **ARCHITECTURAL BLIND SPOTS** may be deferred with explicit user acceptance — record in the Risk register. |
| `2` | Skipped (no `GEMINI_API_KEY`) | Report: "Gemini cross-validation skipped — `GEMINI_API_KEY` not set." Continue. Optionally fall back to the `double-check` skill if installed. |
| `1` | Error | Report stderr verbatim. Continue but flag that cross-validation did not complete. |

The validator's output **belongs to the user** — paste it as-is.
