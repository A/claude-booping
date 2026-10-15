# Specs

Specs are typed records of what the code cannot show: why a project exists and what it is like (values), the constraints every decision obeys (rules), the decisions with their rejected alternatives (ADRs), and the conflicts, stories, ideas, references and runbooks around them. Plain markdown with YAML frontmatter, one record per file.

## Format in brief

A tier root holds one directory per type — `value/`, `rule/`, `adr/`, `conflict/`, `story/`, `idea/`, `reference/`, `runbook/` — and each record is a file `<type>/<NNNN>-<slug>.md`: a four-digit number running within the type and a kebab-case slug. A record is referred to as `<type>/<NNNN>` (`adr/0001`); in a body, references are ordinary relative markdown links.

The full format — frontmatter keys, the body sections each type requires, marks for open questions — is the shipped guide: [`src/specs/README.md`](https://github.com/A/claude-booping/blob/master/src/specs/README.md). Each type's shape is an [mdcheck](https://github.com/A/markdown-checker) rule file beside it under `src/specs/schemas/`.

## Tiers

Specs come in three tiers, each a tier root of its own:

| Tier      | Where                                                                                     | Holds                                            |
|-----------|-------------------------------------------------------------------------------------------|--------------------------------------------------|
| `core`    | shipped with the plugin, at `specs/`                                                      | booping's rules for every project                |
| `global`  | `<home_dir>/_specs/`                                                                      | your values and rules for every project          |
| `project` | `specs/` in the attached repo, or `<vault>/specs/` when the vault lives inside the repo   | the project's own records                        |

Where each tier lives and what it is called is the [`core.specs`](project_config.md#corespecs) config key. The [setup playbook](install.md#scaffold-the-project-vault) creates the global and project tiers and asks for your global namespace; [`booping specs init`](#booping-specs-init) creates either one on demand.

## Namespaced refs

A reference without a namespace points into its own tier: `rule/0003`. A reference into another tier names that tier's namespace in front: `booping:rule/0003` for core, `<user>:rule/0003` for the global tier, where the namespace is the one you gave setup — your `$USER` when none is set. A project that departs from a rule of a tier above records that in its own ADR or conflict, citing the rule by its namespaced ref.

## Injection

An accepted rule carrying `targets:` and `brief:` is injected into the playbooks, steps, agents and skills it targets, from all three tiers: each surface gets a `## Rules` section listing the brief of every matching rule with a link to its record. Target forms, the section shape, the ref and link per tier and the `--no-rules` opt-out are in [Playbooks → Rules](playbook.md#rules).

## Open items

A gap between the records and the code — an unconfirmed ADR, a `[clarify]` mark, a check finding — is filed as an open item, a file under `open-items/` in the vault that a plan can pick up and close. The [specs playbook](specs_playbook.md#open-items) files and works them, and `booping specs open-items` drives them directly.

## Commands

Every verb but `site` takes `--tier core|global|project`, default `project`.

### `booping specs init`

```
booping specs init [--tier global|project]
```

Creates the tier root and its `README.md` when absent. When the vault lives outside the repo, the project tier is `specs/` in the repo and `init` also links `<vault>/specs` to it, so the records sit with the code and stay reachable from the vault. Safe to re-run: it changes only what is missing.

Prints one line per change, in the order made, then the absolute tier root as the last line — on a re-run with nothing to do, only that last line:

```
created dir /home/me/Dev/app/specs
created file /home/me/Dev/app/specs/README.md
linked /home/me/Claude/app/specs -> /home/me/Dev/app/specs
/home/me/Dev/app/specs
```

The `core` tier ships with the plugin and is never created. An error prints `specs init: {message}` on stderr — the core tier asked for, a path in the way that is not a directory, or a `<vault>/specs` that is not a link to the tier — and nothing is written.

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

### `booping specs site`

```
booping specs site [--out DIR] [--root NAME=PATH ...]
```

Renders one or several specs roots to a static HTML site you open in a browser straight from disk: no server, no network, no JavaScript. The same input always produces a byte-identical tree.

- **`--out DIR`** — the output directory, default `specs-site` in the working directory.
- **`--root NAME=PATH`** — a root to render, repeatable: a name (`[A-Za-z0-9][A-Za-z0-9._-]*`) and a directory holding type directories. `~` is expanded.

**Root selection.** Given `--root` at least once, exactly those roots are rendered, in the order given. Otherwise the roots are the three [tiers](#tiers) — core, global, project, each named by its namespace, the project tier by the project's name — followed by every entry of [`core.specs.site.roots`](project_config.md#corespecs). A tier whose directory does not exist is left out silently; a configured root whose directory does not exist is skipped with a warning. A root resolving to a directory already selected is skipped, so a tier that is also a configured root renders once. A root's name is its namespace on the site: `name:type/NNNN` refs resolve against it, so give a configured root the namespace its records are cited by.

To build one site over every project's specs, list them in the global config and run the command from `home_dir`:

```yaml
# ~/.config/booping/config.yaml
home_dir: ~/Claude
core:
  specs:
    site:
      roots:
        - {name: app, path: ../Dev/app/specs}
        - {name: api, path: /home/me/Dev/api/specs}
```

A `path` is absolute, `~`-prefixed, or relative to `home_dir`.

**Pages.**

- `index.html` — one row per root: its record count, the count per type, the open `[clarify]` and `[unknown]` marks, and how many records are unreviewed.
- `{root}/index.html` — one row per type with the same counts, then every `[clarify]` and `[unknown]` mark in the root, each linking to its line in the record.
- `{root}/{type}/index.html` — a contents list, then every record of the type in full.
- `{root}/{type}/{NNNN-slug}.html` — one record: title, ref, status or kind badge, an `unreviewed` badge when `reviewed` is not set, mark counts, summary, every other frontmatter key, the body, then **Referenced by** — every record linking to this one, across roots.

Relative links and typed refs between records become links to the target's page, across roots too. A link to something that is not a record renders as plain text; a link or ref whose target is missing renders as plain text and prints a warning. The site never fails on a link — `booping specs check` is the validator.

**Output directory.** Every build writes a `.booping-site` marker into the out directory. The command refuses — and writes nothing — when the out path is a file, lies inside one of the rendered roots, or is a non-empty directory without the marker. A directory carrying the marker is cleared and rewritten, so re-running into the same `--out` is safe.

**Output.** On success, stdout gets one line:

```
specs site: 3 roots, 42 records, 51 pages, 2 warnings -> specs-site
```

Warnings go to stderr, sorted by path then line:

```
/home/me/Dev/old/specs  warning  site  root old not found, skipped
vault/specs/adr/0002-ports.md:5  warning  site  unresolved ref booping:rule/0099
vault/specs/adr/0002-ports.md:14  warning  site  unresolved link ../rule/0099-gone.md
```

An error prints one `error: {message}` line on stderr.

### Exit codes

| Code | `init`                                                     | `ls`, `next`                                                   | `check`                                                        | `site` |
|------|------------------------------------------------------------|----------------------------------------------------------------|----------------------------------------------------------------|------|
| 0    | tier in place                                              | printed                                                        | no errors (warnings may be printed)                            | site written (warnings may be printed) |
| 1    | the tier is `core` or unavailable, or a path is in the way | unknown type, or the tier is unavailable or has no directory   | at least one error, or the tier is unavailable or has no directory | a malformed `--root` or one that is not a directory, a bad configured root entry, duplicate root names, no roots, or the out directory refused |
| 2    | config could not be loaded                                 | config could not be loaded                                     | the check could not run: config not loaded, `mdcheck` missing or failing | config could not be loaded |
