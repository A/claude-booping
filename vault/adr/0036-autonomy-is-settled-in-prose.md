---
type: adr
title: Autonomy is settled in prose
summary: A run is autonomous because the user or its launch prompt says so, not because a config key does; there is no core.autonomy.
created_by: owner
created_at: 2026-10-18
updated_at: 2026-10-18
status: accepted
values: [value/0009, value/0002, value/0015]
issues: []
sources: []
---

## Context

The owner works two ways: supervised in work projects, where every gate waits for review, and
autonomous in pet projects and experiments, where the manager grooms and builds on its own. Whether a
run waits for the user is a property of the session that runs it. A session told "work autonomously"
already works that way, and `booping run … --autonomous` already hands every child run that instruction
through `core.run.preamble`, including the escalation path: a question only the owner can answer parks
the run, and the manager reports it as waiting on the user.

## Decision

Autonomy is settled in prose. A run is autonomous when the user says so to the session, or when it was
launched with `booping run … --autonomous`; otherwise it is supervised. The project manager reads the
mode from the user's words and passes it on through `--autonomous`, the only switch. The driving
protocol and the step bodies carry both branches as prose ("in an autonomous run … , otherwise …").
No config key chooses the mode (owner, 2026-10-18).

## Alternatives

| Option | Status | Complexity | Reversibility | Verdict |
|---|---|---|---|---|
| [Prose](#prose) | accepted | low | high | One switch, already proven by the launch preamble |
| [A config key](#a-config-key) | rejected | medium | high | A second switch that did not hold anyway |

### Prose

The user's words or the launch preamble decide; the bodies describe both behaviours.

- **Pros:** one switch; the mode follows the conversation, not a file; nothing to validate or render per mode.
- **Cons:** both branches sit in every driving context; the model, not code, reads which applies (a departure from value/0015).
- **Complexity:** low.
- **Reversibility:** high.

### A config key

`core.autonomy: supervised | autonomous` per project, picking the protocol's branch at render and
stopping on any other value.

- **Pros:** the mode is chosen by code; a project keeps its default without restating it.
- **Cons:** a second switch beside `--autonomous`; a supervised project's child runs already got the supervised text plus the autonomous preamble, and the preamble won, so the key bought nothing the prose did not.
- **Complexity:** medium.
- **Reversibility:** high.

## Consequences

- `core.autonomy`, its invalid-value STOP, the `autonomy:` project-context line and their e2e cases are removed.
- `_playbook_driving.j2`, the project-manager and specs playbooks render no mode branch; they say what an autonomous run does in prose.
- migrate's question about uncommitted work is asked in every run, autonomous or not.
- Every gate and question an autonomous run settles is still logged with `booping defaults add`.
