# Install extension file skeletons

Skeletons populated by `/install` Phase 4 in the project vault.

## File: `~/Claude/{project}/_booping/agent_booping-developer.md`

Stack + conventions only; no commands.

```markdown
# booping-developer (project extension)

Project-local stack and conventions for all active developer-agent tiers.

## Stack
{{language}}

## Conventions
{{conventions — e.g. "ruff for lint, mypy for typing, pytest for tests; prefer protocol over base class; no mocked DB in integration tests"}}

## Notes

- If a task touches areas outside the stack above, stop and escalate to the orchestrator before implementing.
- Always prefer the project's own commands over ad-hoc invocations. If the task specifies a Verify command, run that — don't substitute.
```

## File: `~/Claude/{project}/_booping/skill_groom.md`

Catalogue of validations + optional sizing calibration.

```markdown
# groom (project extension)

Project-local facts for grooming.

## Available validations

Commands available in this project to validate changes. When writing a milestone's `Verify` block or the plan's `Final Verification` section, pick the subset that actually exercises what the milestone changed — don't blanket-run everything.

{{validations — one bullet per command with a short role description, e.g.:
- `just test` — unit + integration suite
- `just lint` — ruff check + ruff format --check
- `just typecheck` — basedpyright
- `pre-commit run --all-files` — full hook suite
— or `(none detected — populate this file manually when commands exist)` }}

## Sizing calibration

{{"Sprint cap: {{value}} SP." if user supplied — else "(default — see `src/config.yaml` → `sprint.default_threshold_sp`)"}}
```

## File: `~/Claude/{project}/_booping/skill_develop.md`

Quality-check classification + env notes.

```markdown
# develop (project extension)

Project-local facts for development.

## Quality-check classification

Hook-enforced (runs automatically at commit, no skill action required):
{{hook_enforced_commands — one per line, or "(none)" if empty}}

Configured-but-manual (skill picks the relevant ones per milestone per docs/development_quality_checks.md — not all need to run on every milestone):
{{configured_manual_commands — one per line, or "(none)" if empty}}

## Dev environment

{{env_notes — e.g. "Docker Compose up + Redis required before tests" — or "(none)"}}
```
