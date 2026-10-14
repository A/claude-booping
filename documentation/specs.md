# Specs

Specs are typed records of what the code cannot show: why a project exists and what it is like (values), the constraints every decision obeys (rules), the decisions with their rejected alternatives (ADRs), and the conflicts, stories, ideas, references and runbooks around them. Plain markdown with YAML frontmatter, one record per file.

## Format in brief

A tier root holds one directory per type — `value/`, `rule/`, `adr/`, `conflict/`, `story/`, `idea/`, `reference/`, `runbook/` — and each record is a file `<type>/<NNNN>-<slug>.md`: a four-digit number running within the type and a kebab-case slug. A record is referred to as `<type>/<NNNN>` (`adr/0001`); in a body, references are ordinary relative markdown links.

The full format — frontmatter keys, the body sections each type requires, marks for open questions — is the shipped guide: [`src/specs/README.md`](https://github.com/A/claude-booping/blob/master/src/specs/README.md). Each type's shape is an [mdcheck](https://github.com/A/markdown-checker) rule file beside it under `src/specs/schemas/`.

## Tiers

Specs come in three tiers, each a tier root of its own:

| Tier      | Where                                                                                     | Holds                                            |
|-----------|-------------------------------------------------------------------------------------------|--------------------------------------------------|
| `core`    | shipped with the plugin, at `vault/specs/`                                                | booping's own values and rules                   |
| `global`  | `<home_dir>/_specs/`                                                                      | your values and rules for every project          |
| `project` | `specs/` in the attached repo, or `<vault>/specs/` when the vault lives inside the repo   | the project's own records                        |

Where each tier lives and what it is called is the [`core.specs`](project_config.md#corespecs) config key.

## Namespaced refs

A reference without a namespace points into its own tier: `rule/0003`. A reference into another tier names that tier's namespace in front: `booping:rule/0003` for core, `<user>:rule/0003` for the global tier, where the namespace defaults to your `$USER`. A project that departs from a rule of a tier above records that in its own ADR or conflict, citing the rule by its namespaced ref.

## Injection

An accepted rule carrying `targets:` and `brief:` is injected into the playbooks, steps, agents and skills it targets, from all three tiers: each surface gets a `## Rules` section listing the brief of every matching rule with a link to its record, right before the lessons. Target forms, the section shape, the ref and link per tier and the `--no-rules` opt-out are in [Playbooks → Rules](playbook.md#rules).

## Commands

All three verbs take `--tier core|global|project`, default `project`.

### `booping specs ls`

```
booping specs ls [--tier TIER] [--type TYPE]
```

Lists the tier's records, one per line: `{type}/{NNNN}  {status}  {summary}`, sorted by type and number. `--type` keeps one type.

### `booping specs next`

```
booping specs next TYPE [--tier TIER]
```

Prints the next free ref of a type in the tier — the highest number plus one, e.g. `adr/0004`. Use it to name a new record.

### `booping specs check`

```
booping specs check [--tier TIER]
```

Validates every record of the tier: its type's schema, the directory layout and file names, unique numbers, frontmatter, rule targets, relative link targets, typed refs and `sources` paths. Each finding prints as `{path}:{line}  {level}  {check}  {message}`, followed by a count on stderr. A cross-tier ref whose namespace no configured tier answers to, or whose tier is absent on this machine, is a warning, not an error.

The check needs the `mdcheck` binary on `PATH`:

```
cargo install markdown-checker --version 0.1.1 --locked
```

### Exit codes

| Code | `ls`, `next`                                                   | `check`                                                        |
|------|----------------------------------------------------------------|----------------------------------------------------------------|
| 0    | printed                                                        | no errors (warnings may be printed)                            |
| 1    | unknown type, or the tier is unavailable or has no directory   | at least one error, or the tier is unavailable or has no directory |
| 2    | config could not be loaded                                     | the check could not run: config not loaded, `mdcheck` missing or failing |
