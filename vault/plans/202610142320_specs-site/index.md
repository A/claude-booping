---
title: "Specs site — static HTML over one or several specs roots"
type: "feature"
status: in-progress
sp: 30
related_to: null
created: 2026-10-14 23:20
planned: null
started: 2026-10-14 23:34
completed: null
code_reviews: []
sessions:
- d0a2aeef-e06e-442c-adb3-1abbb2d6c765
- b129377e-4c8b-4ab9-b53f-9a552bb18fd0
retro: null
summary: booping specs site renders one or several specs roots to an offline 
  static HTML site; global-config roots for an aggregated site
commit: fb28dce0c47994cc2c75ce426a79215980be133e
tracker_provider: null
tracker_request: null
tracker_issue: null
return_to: null
reviewed_at: 2026-10-14 23:33
---

# Specs site — static HTML over one or several specs roots

## Context

`booping specs` today lists, checks and creates tiers, but a tier is readable only as raw markdown — one record per file, cross-tier refs (`booping:rule/0004`) not navigable, no view over several projects. `src/specs/README.md` already promises a site that "renders a type's records together, so splitting a set into records costs no readability" (value/0011 Everything in one place). After this plan ships, `booping specs site` renders one or several specs roots to a static, offline, deterministic HTML site: a top index over the roots, an index per root with every `[clarify]`/`[unknown]` mark, a page per type with every record in full, a page per record with resolved cross-links and backlinks; and `core.specs.site.roots` in the global config lets `home_dir` (the notes repo) build one site over every project's specs. Request: [request.md](request.md); every default this autonomous run chose is in [clarifications.md](clarifications.md).

## Decisions

- **Roots** (C2): `--root NAME=PATH` replaces everything; otherwise the existing tiers (core, global, project — named by namespace, project by project name) plus `core.specs.site.roots` from config; a root resolving to an already-selected directory is skipped. A root's name is its namespace on the site — single source for `ns:type/NNNN` resolution (value/0003).
- **Config key**: `core.specs.site.roots` — under `core.specs` because the specs surface is shared (placement rule); core default `[]`, set in the global tier; entries `{name, path}`, path home_dir-relative like `tiers.global`.
- **Output** (C3): `--out` default `specs-site` in the working directory; a `.booping-site` marker makes rewriting safe; never inside a rendered root (rule/0028 — the tier stays plain markdown).
- **Ported vs dropped** (C4): ported type pages in full, record pages, badges, marks with line anchors, backlinks, heading anchors, one stylesheet; dropped tags, `llms.txt`, raw `.md` copies, 404, repo-host URLs, `filter.js` — no JS at all.
- **Markdown** (C5): markdown-it-py 4.2 (`commonmark` + `table`, raw HTML escaped) — CommonMark, source line maps for `L{n}` anchors, one transitive dependency.
- **Links** (C6): resolved by filesystem path with symlinks followed, so links into another root (or through the `home_dir` symlinks value/0011 describes) land on that root's page; non-record targets render as unlinked text; only missing targets warn. `specs check` stays the validator — the site never fails on a link.
- **Frontmatter** (C7): header keys fixed (`title`, `summary`, `status`/`kind`, `reviewed` as the `unreviewed` badge), every other key rendered generically — a user tier's own keys need no code (value/0005, value/0006).
- **Templates**: Jinja2 with autoescape, already a dependency; no HTML string assembly in Python.
- **Determinism** (value/0010): no timestamps, no absolute paths in pages, explicit sort orders (roots as selected, types in schema order, records by number), sorted writes, sorted warnings.

## Architecture

```
booping specs site ──► commands/specs.py: _run_site
                         │ select roots: --root | tiers (resolve_tiers) + core.specs.site.roots
                         ▼
                       specs/site/model.py   load_site(roots, types) → Site
                         │ resolve_ref / resolve_link / backlinks
                         ▼
                       specs/site/markdown.py render_body (markdown-it-py) → html, marks, links
                         ▼
                       specs/site/pages.py   build_site(site) → {relpath: content}, warnings
                         │ templates/*.html.j2, style.css
                         ▼
                       specs/site/write.py   write_site(files, out, roots) → disk (+ .booping-site)
```

Input: specs tier directories (read only). Output: the out directory. No network, no subprocess, no caller inlines the output. Record loading reuses `booping/specs/records.py`; types come from `core.specs.format` schemas, as for `ls` and `check`.

## Milestones

| id | title | sp | status |
| --- | --- | --- | --- |
| 01 | [Site model and markdown rendering](milestones/M01-site-model-and-markdown/M01-site-model-and-markdown.md) | 10 | done |
| 02 | [Site pages, stylesheet and writer](milestones/M02-site-pages-and-writer/M02-site-pages-and-writer.md) | 9 | done |
| 03 | [booping specs site command, roots config and e2e cases](milestones/M03-specs-site-command/M03-specs-site-command.md) | 8 | done |
| 04 | [Document the specs site](milestones/M04-document-specs-site/M04-document-specs-site.md) | 3 | pending |

## I/O contract

- **Arguments / flags**: `booping specs site [--out DIR] [--root NAME=PATH ...]` — `--out` the output directory (default `specs-site`, relative to the working directory); `--root` repeatable, each a root name (`[A-Za-z0-9][A-Za-z0-9._-]*`) and a directory holding type directories; given at least once, it replaces tier and config roots.
- **Config**: `core.specs.site.roots: [{name, path}]`, path `~`-expanded / absolute / home_dir-relative.
- **stdin**: not read.
- **stdout** (success, exactly one line): `specs site: {R} roots, {N} records, {P} pages, {W} warnings -> {out}`.
- **stderr**: per warning, sorted by path then line — `{path}:{line}  warning  site  unresolved link {dest}`, `{path}:{line}  warning  site  unresolved ref {ref}`, `{path}  warning  site  root {name} not found, skipped`. On failure, one `error: {message}` line.
- **Files written**: `{out}/.booping-site` (`booping specs site\n`), `{out}/style.css`, `{out}/index.html`, `{out}/{root}/index.html`, `{out}/{root}/{type}/index.html`, `{out}/{root}/{type}/{NNNN-slug}.html`.
- **Page content** (locked; detail in M02's Scope): top index — table Root | Records | per-type counts | `[clarify]` | `[unknown]` | Unreviewed. Root index — table Type | Records | `[clarify]` | `[unknown]` | Unreviewed, then Marks per kind, each `type/NNNN title — {block text ≤ 160 chars…}` linking to `#L{n}`. Type page — contents list, then every record in full. Record page — record block (title; `type/NNNN`, status badge, `unreviewed` badge, mark chips; summary; facts of every other frontmatter key; body), then Referenced by. Every page: relative stylesheet link, breadcrumb, no script.
- **Exit codes**: `0` site written (warnings may be printed); `1` malformed `--root`, a `--root` path not a directory, a bad configured entry, duplicate root names, no roots, out directory refused (a file, inside a root, non-empty without marker); `2` config could not be loaded.

## Final Verification

- [ ] `booping specs site --help` shows both flags accurately.
- [ ] Happy path: `bin/booping specs site --out /tmp/specs-site-check` in this repo renders the core root once (the project tier resolves to the same `vault/specs` directory and is skipped as a duplicate path) and prints the summary line; opening `/tmp/specs-site-check/index.html` shows every type with working links.
- [ ] Failure path: rerunning into a non-empty dir without the marker exits 1 with `error: …`.
- [ ] Two runs over the same input produce byte-identical trees (`diff -r`).
- [ ] `just ci` green.
- [ ] `just snapshots` shows no drift (none expected — no playbook source changes); any drift handled per C8.

## Out of scope

- Dev server, watch mode, publishing (gh-pages or other hosting).
- Search, filtering, any JavaScript.
- Tags, `llms.txt`, raw `.md` republishing, a 404 page, repo-host links.
- Linking bare `ns:type/NNNN` refs written in body prose.
- Failing on broken links — `booping specs check` owns link validity.
- A playbook or `just` recipe around the command.

## CLAUDE.md impact

`## Commands` → the `bin/booping` subcommand list gains `site` among the `specs` verbs (M04, task 4.2). No other CLAUDE.md change — the specs surface and `core.specs` placement already covered.

## Risk register

- Two roots resolving to one directory (this repo's core and project tiers are both `vault/specs`) — the first selected wins and later ones are skipped silently (C2), so `booping:` refs resolve and nothing renders twice.
