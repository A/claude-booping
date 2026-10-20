# vault/

Booping's project tier: the specs about developing booping itself, in the format
booping ships — why booping exists and what it is like (values), the constraints
every decision obeys (rules), the decisions with their rejected alternatives (ADRs),
and the rest of what the code cannot show. This set is also the dogfood of the format
itself — the rules on how records are written live here as records.

The records sit in the type directories at the vault root (`vault/value/`,
`vault/rule/`, `vault/adr/`, …).

What lives where:

- **`vault/{type}/`** — why and where the boundaries are: values, rules, decisions.
  A rule here reaches only runs in this repo.
- **`specs/`** at the repo root — the core tier: rules shipped with the plugin and
  injected into every user's runs. Cited from here as `booping:rule/NNNN`.
- **Vault artefacts** (`plans/`, `retrospectives/`, `codereviews/`, `notes/`) — work
  and its history; a decision made in a run goes up into an ADR here. This public
  release does not carry them.
- **Code** (`booping-python/`, `booping-tracker/`, `playbooks/`, `src/`) — how things
  work. Anything recoverable from code, config or tests is documented only there.
- **`documentation/`** — the public docs site, for users; `docs/` — fragments the
  skills lazy-load at runtime.

## Format

The format these records follow — tiers, types, files, frontmatter, body, marks —
is the shipped guide: [src/specs/README.md](../src/specs/README.md).

## Check

```
just specs-check
```

Runs `booping specs check` over the core tier (`specs/`) and the type directories
here, the project tier of this repo: each record against its type's shipped schema
(mdcheck), file names, unique numbers, frontmatter, rule targets, relative link
targets, typed refs and `sources` paths, with a warning for a namespace no tier
answers to. Everything else in the vault is not a record and is not checked. The
full list is the shipped guide's [Check](../src/specs/README.md#check) section.
