# Install extension file skeletons

Skeletons for the `_booping/` extension files `/install` Phase 4 may seed. Seed a file only when it carries project-local signal the repo `CLAUDE.md` does not already own; otherwise skip it (Phase 4 prints the locked skip message). Never copy a command catalogue from the repo into a vault file.

## File: `~/Claude/{project}/_booping/agent_booping-developer.md`

Stack + conventions only; no commands. Always seeded (subject to the attach-mode skip-if-exists rule).

```markdown
# booping-developer (project extension)

Project-local stack and conventions for the developer agent.

## Stack
{{language}}

## Conventions
{{conventions — e.g. "ruff for lint, mypy for typing, pytest for tests; prefer protocol over base class; no mocked DB in integration tests"}}

## Notes

- If a task touches areas outside the stack above, stop and escalate to the orchestrator before implementing.
- Always prefer the project's own commands over ad-hoc invocations. If the task specifies a Verify command, run that — don't substitute.
```

## File: `~/Claude/{project}/_booping/skill_groom.md`

Seed **only** when the user supplies a real groom override (e.g. a sprint-cap SP value). Do not seed a validations catalogue, and do not write a config-path sizing stub — `sprint.default_threshold_sp` is already rendered into the groom skill body. With no real override, skip the file.

```markdown
# groom (project extension)

Project-local facts for grooming.

## Sizing calibration

Sprint cap: {{value}} SP.
```

## File: `~/Claude/{project}/_booping/skill_develop.md`

Seed **only** when there is dev signal the repo `CLAUDE.md` lacks (e.g. required services / env setup it does not document). Do not copy a command list — `CLAUDE.md` owns the command catalogue. If nothing remains once `CLAUDE.md`'s coverage is removed, skip the file.

```markdown
# develop (project extension)

Project-local facts for development.

## Dev environment

{{env_notes — signal CLAUDE.md does not already document, e.g. "Docker Compose up + Redis required before tests"}}
```
