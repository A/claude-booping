---
title: "Specs as a core feature — shipped format, specs CLI, tiers, rule injection"
type: "feature"
status: in-progress
sp: 34
related_to: null
created: 2026-10-14 17:32
planned: null
started: 2026-10-14 17:47
completed: null
code_reviews: []
sessions:
- 4fcdac60-259a-4a51-8481-b0c2629bb285
- 7f3bec31-4b2a-439f-ba9d-90c94c239644
retro: null
summary: Ship the specs format at src/specs, core.specs tier config and booping 
  specs check/ls/next; rule injection split off
commit: c604dfa30cb19334bf9277b145a87c2e5c8aad1f
tracker_provider: null
tracker_request: null
tracker_issue: null
return_to: null
agents:
  research-codebase: a5666b20e0e8382b1
  research-port-source: ad4b22bf0a5098dc7
  cross-review: a6996b104723c9cc9
reviewed_at: 2026-10-14 17:46
---

# Specs as a core feature — shipped format, specs CLI, tiers, rule injection

## Context

Booping's typed-records specs format (`value`, `rule`, `adr`, `conflict`, `story`, `idea`, `reference`, `runbook`) lives only inside booping's own vault: the format guide is `vault/specs/README.md`, the mdcheck schemas are `vault/specs/schemas/*.yaml`, and `just specs-check` is a bash loop running `mdcheck` per type with no cross-file checks. Booping itself knows nothing about specs — no tier paths in config, no namespace id, no CLI. The owner's global tier already exists (`<home_dir>/_specs/`, namespace `anton`) with no schemas of its own.

After this plan ships:

- The format is shipped by the plugin at `src/specs/` — `README.md` (the format guide) and `schemas/{type}.yaml` — and every tier is checked against it; `vault/specs/` holds only booping's own records.
- `core.specs` in config names each tier's specs root and the global tier's namespace, merged core → global → project like every other key ([adr/0004](../../specs/adr/0004-config-three-tier-merge.md)).
- `booping specs ls`, `booping specs next {type}` and `booping specs check` list, number and validate a tier's records, with cross-file checks and cross-tier namespaced refs; `just specs-check` calls `booping specs check` and stays in `just ci`.

This is the first of two plans for the feature agreed in [adr/0001](../../specs/adr/0001-specs-tiers.md). The full request (format, CLI, tier config, rule injection) estimates at ~42 SP, past the 35 SP split threshold, so it is split at the dependency seam: rule injection needs this plan's tier resolution and record model and is parked as the sibling stub [specs rule injection](../202610141732_specs-rule-injection/index.md).

## Decisions

- **Shipped format location**: `src/specs/README.md` + `src/specs/schemas/{type}.yaml`, moved (not copied) from `vault/specs/` — one source for the format ([value/0003](../../specs/value/0003-single-source.md)); `src/` is where booping already ships runtime data (`src/config.yaml`, `src/templates/`).
- **Type list**: derived from the file names in the shipped `schemas/` directory, never restated in code or config ([rule/0017](../../specs/rule/0017-structured-data-rendered-not-restated.md)).
- **Config shape**: one shared block `core.specs` (several playbooks and the CLI read it, so it sits directly under `core` per the placement rule):

  ```yaml
  core:
    specs:
      format: src/specs                 # plugin-root-relative; README.md + schemas/{type}.yaml
      tiers:
        core:    {namespace: booping, path: vault/specs}  # plugin-root-relative
        global:  {namespace: null, path: _specs}          # home_dir-relative; namespace null → $USER
        project: {path: null}                             # repo-relative; null → {vault}/specs when the vault is inside the repo, else specs
  ```

  An absolute or `~`-prefixed `path` is taken as is. [clarify] The project tier carries no namespace: no upper tier references a project record, and a project ref is always un-namespaced.
- **$USER fallback**: a null `tiers.global.namespace` is read from the `USER` environment variable at runtime by code — not config interpolation, which stays forbidden.
- **Hermetic mode**: `--project` (where a command takes it) drops the global tier exactly as it drops global lessons today ([rule/0027](../../specs/rule/0027-renders-reproducible.md)).
- **CLI layout**: one nested argparse group `booping specs {check|ls|next}` — the first nested group in `booping-python`; each verb a function in one module `commands/specs.py`, the logic in a package `booping/specs/`.
- **Tier selection**: every verb takes `--tier core|global|project`, default `project`.
- **Check scope** (ported logic from shatterlings' `crates/specs`): per-file schema via `mdcheck`; `layout`, `filename`, `id` (unique number per type), `frontmatter` (parse error, `type:` ≠ directory), `targets` (a rule's `targets:` and `brief:` come together and every target parses as a lesson target does today), `link` (relative link targets exist), `ref` (`values`→`value`, `rules`→`rule`, `supersedes`→`adr`), `sources` (each path exists), `namespace` (cross-tier refs). Only `namespace` — a namespace that names no configured tier, or a tier whose directory does not exist on this machine — is a warning; everything else is an error.
- **`sources` base**: a `sources` entry resolves against its tier's anchor — core → plugin root, global → `home_dir`, project → repo root; an entry containing `://` is skipped. [clarify] booping's own records write `sources` repo-relative (`vault/…`, `playbooks/…`); this base matches them.
- **Not ported** from shatterlings: `tags.rs` (booping has no tag vocabulary), `review` verb and `ls` marker counts, ADR alternatives / conflict resolution correspondence checks, heading-anchor checks, `--format json`, `check {paths}`, `stamp`, `hook`, `site` — listed under Out of scope.
- **Markdown scanning**: a line scanner (fenced-code and inline-code aware) extracts links; no new Python dependency. Headings/tables stay mdcheck's job.
- **mdcheck**: invoked as `mdcheck {schema} - --format json` with the record on stdin, one call per record; exit 0/1 parsed, anything else or a missing binary is an internal error (exit 2).
- **Output content**: locked in [I/O contract](#io-contract) below ([rule/0010](../../specs/rule/0010-output-content-locked-in-grooming.md)). [clarify] Settled by the autonomous run, not with the owner.
- **Vault records edited by workers**: M01 moves `vault/specs/schemas/` and the format half of `vault/specs/README.md` into `src/specs/`. [clarify] `vault/specs/` is booping's shipped core tier, so this plan treats it as plugin content a worker may edit, an exception to [rule/0019](../../specs/rule/0019-driver-owns-vault-workers-own-code.md); booping's own record fixes needed for `just specs-check` to pass stay with the runner (Final Verification).

## Architecture

```
src/specs/README.md, schemas/{type}.yaml   ← shipped format (types = schema file names)
src/config.yaml core.specs                 ← tier paths + namespaces, merged core → global → project
        │
booping-python/src/booping/specs/
  tiers.py    resolve_tiers(ctx) → [Tier(name, namespace, root, anchor)]   (plugin root, home_dir, repo dir, vault)
  records.py  load_tier(tier, types) → [Record(type, number, slug, path, frontmatter, body)]
              parse_filename, parse_ref("booping:rule/0003") → Ref(namespace, type, number)
  links.py    relative link extraction (code-aware line scanner)
  check.py    Finding(path, line, level, check, message); per-record + cross-file checks; mdcheck subprocess
        │
booping-python/src/booping/commands/specs.py   argparse group: check | ls | next
        │
bin/booping specs …  ← just specs-check (repo root, default project tier = vault/specs here)
```

Callers: `just specs-check` (CI) only. No skill or playbook inlines these commands in this plan; the sibling plan's rule injection reuses `tiers.py` and `records.py`.

## Milestones

| id | title | sp | status |
| --- | --- | --- | --- |
| 01 | [Shipped specs format at src/specs](milestones/M01-shipped-format-location/M01-shipped-format-location.md) | 4 | done |
| 02 | [Specs tier config and record model](milestones/M02-specs-config-and-record-model/M02-specs-config-and-record-model.md) | 7 | done |
| 03 | [booping specs ls and next](milestones/M03-specs-ls-and-next/M03-specs-ls-and-next.md) | 5 | done |
| 04 | [booping specs check — per-record checks](milestones/M04-specs-check-per-record/M04-specs-check-per-record.md) | 6 | done |
| 05 | [booping specs check — links, refs and namespaces](milestones/M05-specs-check-cross-file/M05-specs-check-cross-file.md) | 8 | done |
| 06 | [specs-check on the CLI, docs and CLAUDE.md](milestones/M06-specs-check-in-ci-and-docs/M06-specs-check-in-ci-and-docs.md) | 4 | pending |

## Milestone files

One file per milestone under `milestones/M{nn}-{kebab}/`, each carrying its goal, tasks, DoD, references and Verify; this file holds only context.

## I/O contract

**Arguments / flags**

- `booping specs ls [--tier core|global|project] [--type {type}]` — every record of the tier, or of one type.
- `booping specs next {type} [--tier core|global|project]` — the next free ref of `{type}` in the tier.
- `booping specs check [--tier core|global|project]` — validate every record of the tier.

No stdin is read by any verb.

**stdout**

- `ls` — one line per record, sorted by type name then number, fields separated by two spaces, no padding: `{type}/{NNNN}  {status}  {summary}`. `{status}` is the frontmatter `status`, or `-` when absent (values). Nothing else is printed; an empty tier prints nothing.
- `next` — exactly one line: `{type}/{NNNN}` (highest existing number + 1, zero-padded to four; `0001` for an empty or missing type directory).
- `check` — one line per finding, sorted by path then line: `{path}:{line}  {level}  {check}  {message}`, `{level}` = `error` | `warning`, `{path}` relative to the current directory when the record is under it, else absolute; `{check}` is one of `layout`, `filename`, `id`, `frontmatter`, `targets`, `link`, `ref`, `sources`, `namespace`, or `schema` for an mdcheck finding (its `message` carried verbatim).

**stderr**

- `check` — always ends with one trailer line: `{n} record(s) checked: {e} error(s), {w} warning(s)`.
- Every failure — `error: {message}` on one line, nothing on stdout.

**Messages** (`check`, the `{message}` field):

| check | message |
| --- | --- |
| `layout` | ``a record lives at {type}/{NNNN}-{slug}.md`` |
| `filename` | ``file name is not {NNNN}-{slug}.md`` |
| `id` | ``{type}/{NNNN} is also used by {other path}`` |
| `frontmatter` | the YAML error text, or ``type is `{t}`, the directory is `{dir}` `` |
| `targets` | ``targets without brief`` / ``brief without targets`` / ``target `{entry}`: {reason}`` |
| `link` | ``link target `{dest}` does not exist`` |
| `ref` | ``{field}: must be a list`` / ``{field}: `{item}` is not a {type} ref`` / ``{field}: `{ref}` does not exist`` |
| `sources` | ``sources: must be a list`` / ``sources: `{entry}` does not exist`` |
| `namespace` | ``{field}: namespace `{ns}` names no tier`` / ``{field}: tier `{tier}` has no specs at {root}`` |

**Exit codes**

- `0` — success; for `check`, no error-level finding (warnings allowed).
- `1` — user error: `check` found an error; unknown `--type` / `{type}` (``unknown type `{t}`; known: {comma-separated list}``); the selected tier's directory does not exist (``no specs for tier `{tier}` at {root}``); the selected tier is not resolved here — no project attached, or the global tier under a vault override (``tier `{tier}` is not available here``).
- `2` — internal error: config load failure, `mdcheck` not on PATH (``mdcheck not found on PATH — cargo install markdown-checker``), mdcheck exit 2/3 or unparsable JSON.

## Risk register

- **Booping's own records fail the new checks** — `sources` paths and links in `vault/specs/` were never checked; the runner fixes them as vault work in Final Verification rather than loosening a check.
- **Local mdcheck drift** — the dev machine has `mdcheck 0.1.0`, crates.io's latest is `0.1.1`; the JSON shape (`findings[].{check,severity,line,message}`) was verified on 0.1.0. CI installs whatever `cargo install markdown-checker` yields.
- **`$USER` in e2e** — the txtar runner sets `HOME`/`XDG_CONFIG_HOME` only, so `USER` leaks from the machine; e2e cases pin `core.specs.tiers.global.namespace` in fixture config instead of relying on the fallback.
- **Core tier in e2e** — the core tier resolves to the real `vault/specs/`; e2e cases that resolve `booping:` refs reference `booping:value/0001` and `booping:rule/0001`, the two records foundational to the feature. Resolution needs only the target file to exist, not to pass its own checks, so record findings in `vault/specs/` never break these cases.

## Final Verification

- [ ] `just ci` passes (lint, typecheck, pytest, snapshots, mdcheck, specs-check, e2e).
- [ ] `bin/booping specs check` from the repo root exits 0 over `vault/specs/` — the runner fixes any finding in booping's own records (vault work) before closing, never by weakening a check.
- [ ] `bin/booping specs check --tier global` runs over the owner's global tier and reports only real findings.
- [ ] `bin/booping specs --help`, `… ls --help`, `… next --help`, `… check --help` describe the surface in the I/O contract.
- [ ] `rg -n 'vault/specs/schemas|vault/specs/README' --glob '!vault/plans/**' --glob '!vault/specs/**'` prints nothing.

## Out of scope

Follow-ups, each groomed in its own run:

- **Rule injection** — accepted rules with `targets:` + `brief:` from all three tiers injected into render-playbook, agent and skill bodies beside lessons: the parked sibling [specs rule injection](../202610141732_specs-rule-injection/index.md).
- The specs site (aggregating several roots into notes pages).
- `specs-setup` / `specs-upgrade` playbooks and the vault migration moving `_lessons/` into rules.
- `learn` writing rules instead of lessons.
- Adapting the vault `docs` playbook to the new records.
- Moving the hermes-pet and shatterlings copies onto the shipped format.
- Checker extensions not ported now: heading anchors, ADR alternatives and conflict-resolution correspondence, `[clarify]`/`[unknown]` marker counts and a `review` verb, `check {paths}`, `--format json`, a PreToolUse hook, `stamp`.

## CLAUDE.md impact

- **Commands** — `bin/booping` subcommand list gains `specs`; `just specs-check` described as `booping specs check`.
- **Layout** — new `src/specs/` entry (shipped format: guide + schemas).
- **Config** — new `core.specs` bullet (tier paths, namespaces, `format`).
- **Vault** — the `vault/specs/` sentence points at `src/specs/README.md` for the format instead of `vault/specs/README.md`.

All four land in M06.
