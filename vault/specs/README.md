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

## Format

The format these records follow — tiers, types, files, frontmatter, body, marks —
is the shipped guide: [src/specs/README.md](../../src/specs/README.md).

## Check

```
just specs-check
```

Runs `booping specs check` over this directory, the project tier of this repo: each
record against its type's shipped schema (mdcheck), layout, file names, unique
numbers, frontmatter, rule targets, relative link targets, typed refs and `sources`
paths, with a warning for a namespace no tier answers to. The full list is the
shipped guide's [Check](../../src/specs/README.md#check) section.
