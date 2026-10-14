# specs/

Booping's own specs, written in the format booping will ship as a core feature: why
booping exists and what it is like (values), the constraints every decision obeys
(rules), the decisions with their rejected alternatives (ADRs), and the rest of what
the code cannot show. This set is also the dogfood of the format itself — the rules
on how records are written live here as records.

What lives where:

- **`vault/specs/`** — why and where the boundaries are: values, rules, decisions.
- **Vault artefacts** (`plans/`, `retrospectives/`, `codereviews/`, `notes/`) — work
  and its history; a decision made in a run goes up into an ADR here.
- **Code** (`booping-python/`, `booping-tracker/`, `playbooks/`, `src/`) — how things
  work. Anything recoverable from code, config or tests is documented only there.
- **`documentation/`** — the public docs site, for users; `docs/` — fragments the
  skills lazy-load at runtime.

`vault/docs/_specs/` (briefing, roles, features, targets, glossary, documented) is
deprecated: its content moves here; it stays until the `docs` playbook reads from
here. `vault/_lessons/` likewise stays until lesson injection reads rules
([rule/0001](rule/0001-lessons-are-rules.md)).

## Format

The format these records follow — tiers, types, files, frontmatter, body, marks —
is the shipped guide: [src/specs/README.md](../../src/specs/README.md).

## Check

```
just specs-check
```

Checks every record here against its type's shipped schema (mdcheck).
