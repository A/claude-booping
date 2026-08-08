# Design the run's state machines

The input is the confirmed decomposition — graph, Steps table — plus the brief and the
state-machine verdict recorded in `_specs/DECISIONS.md` (or the user's override of it). Produce the `## States` section of the decomposition index: the
state chart `manifest` translates into `playbook.yaml` verbatim, so every cell must already
be in final vocabulary.

Honor the verdict first:

- **ephemeral**, and the user has not overridden it → change nothing, return the skip note.
- **minimal** → stamp the minimal pattern.
- **rich** → design in full: roles, superstates, hooks, per-instance machines as warranted.

{% include "state-machine.md" %}

## The edit to make

`<slug>/_specs/index.md`:

- append `## States` after `## Steps`: per machine a `### <name>` heading, an `artifact:`
  line, then its tables per the anatomy above.
- preserve the frontmatter — `status:` and stamps are harness-owned; the index re-enters
  review through the harness's transition, never through a frontmatter edit.

## Return format

```
## Changed:
- [UPDATED] <slug>/_specs/index.md

## Notes:
- <n> machine(s), tier <tier>
```

On an ephemeral verdict:

```
## Changed:

## Notes:
- skipped — ephemeral verdict, no state machine persisted
```
