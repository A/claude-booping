# Request — specs site

## Request

> Request — specs site (value/0011 Everything in one place, the owner wants readability through a site):
> - `booping specs site [--out DIR] [--root NAME=PATH ...]` renders the records of one or several specs roots (tiers and/or projects) to a static HTML site: an index per root, one page per type listing every record of the type in full (so a split set reads as a whole), record pages with working cross-links (relative links, namespaced refs across roots), status and [clarify]/[unknown] marks visible. Port the logic, not the code, from `/home/anton/Dev/@A/shatterlings/crates/specs/src/site.rs`; plain HTML+CSS, no JS framework, no network at render time. txtar e2e cases on a small fixture; deterministic output.
> - A global-config key listing the roots for the aggregated site (so `<home_dir>` — the notes repo — can build one site over every project's specs), documented in documentation/specs.md.

## Task type

`feature` — a new user-facing capability: a CLI subcommand and a config key the owner runs and reads. Not `bug`: no existing behaviour diverges from an expectation — there is no site today. Not `refactoring`: user-visible behaviour is added, not preserved.

## Problem

Today a specs tier is readable only as raw markdown files (or through Obsidian); `src/specs/README.md` already promises "the site renders a type's records together, so splitting a set into records costs no readability", but no site exists. Records split one-per-file read poorly as a set, cross-tier refs (`booping:rule/0003`) are not navigable, and there is no single view over every project's specs. After this ships, the owner runs `booping specs site` in a project (or in `<home_dir>` with a global-config roots list) and opens a static HTML site: per-root index, per-type pages with every record in full, record pages with working relative and namespaced cross-links, statuses and `[clarify]`/`[unknown]` marks visible.

## Clarifications and Decisions

Autonomous run — the owner is unavailable; every default below is also recorded in `clarifications.md` (answered by default, marked for the owner's review).

- Goal (after ship): one readable site over one or many specs roots, built offline from plain files; the source of truth stays the markdown records (value/0011, rule/0028).
- Scope in: `booping specs site` subcommand, global-config roots key, documentation in `documentation/specs.md`, txtar e2e cases, a small fixture.
- Scope out: serving/watching (no dev server), publishing/deploy (gh-pages), search, JS of any kind, editing records from the site, a playbook wrapping the command.
- The site is a derived artefact: never written into a tier root, never committed by the command.
