# Clarifications

## C1 — scope boundaries — answered

**Asked:** 2026-10-14 — intake

**Question:** Which surfaces are in and out of the specs-site feature?

**Answer:**

Default chosen by the agent (autonomous run, owner unavailable) — [clarify] the owner confirms or narrows. In: `booping specs site`, a global-config roots key, `documentation/specs.md`, txtar e2e cases on a small fixture. Out: a dev server or watch mode, publishing (gh-pages), search, any JavaScript, editing records from the site, a playbook wrapping the command. The site is a derived artefact: never written into a tier root, never committed by the command.

## C2 — which roots a run renders — answered

**Asked:** 2026-10-14 — draft-plan

**Question:** Without `--root`, which roots does `booping specs site` render, and how does the global-config key combine with the tiers?

**Options:**

- Tiers plus configured roots — every resolved tier whose directory exists, then the `core.specs.site.roots` entries
- Configured roots replace the tiers when set
- Tiers only; configured roots only in a `--aggregate` mode

**Answer:**

Default chosen by the agent — [clarify] the owner confirms. Tiers plus configured roots. `--root NAME=PATH` given (repeatable) → exactly those roots, nothing else. Otherwise: the resolved tiers whose root directory exists, in order core, global, project — named by their namespace (core `booping`, global the global namespace, project the project's name, since the project tier declares no namespace) — then each `core.specs.site.roots` entry `{name, path}` in listed order, `path` resolved like a global-tier path (`~` expanded, absolute as is, else relative to `home_dir`). Any root (tier or configured) whose resolved path equals an earlier root's is skipped silently — a project run would otherwise list itself twice, and in this repo the core and project tiers are the same `vault/specs`; a configured root whose directory is missing is a warning and skipped (another machine); a missing `--root` path is an error. A root's name is its namespace on the site, so `booping:rule/0004` resolves into the root named `booping`.

## C3 — output directory and its safety — answered

**Asked:** 2026-10-14 — draft-plan

**Question:** Where does the site go by default, and what happens to an existing directory there?

**Answer:**

Default chosen by the agent — [clarify] the owner confirms. `--out` defaults to `specs-site` relative to the working directory. The command writes a marker file `.booping-site` into the out directory; on the next run it clears and rewrites a directory carrying the marker, and refuses (exit 1) an existing non-empty directory without it, an out path that is a file, and an out path inside any rendered root — the site is never written into a tier. No config key for the out directory: the request names only the roots key.

## C4 — what the site renders and what it leaves out of site.rs — answered

**Asked:** 2026-10-14 — draft-plan

**Question:** Which parts of shatterlings' `site.rs` are ported?

**Answer:**

Default chosen by the agent — [clarify] the owner confirms. Ported: a page per type listing every record in full, a record page, a status badge, highlighted `[clarify]`/`[unknown]` marks with a per-root list of every mark linking to its line, backlinks ("Referenced by") on the record page, heading anchors, rewritten record-to-record links, one standalone `style.css` with light/dark themes. Added for booping: a top index over all roots, namespaced refs across roots, an `unreviewed` badge for a record without `reviewed` (value/0009). Left out: tags (booping records have none), `llms.txt`, republished raw `.md`, the review page as a separate page (its list moves onto the root index), `404.html`, repo-host blob/history URLs and site-URL env vars, `filter.js` (the request forbids a JS framework; the owner's "no network, plain HTML+CSS" reads as no JS at all), the post-build broken-link scan of written HTML (resolution warnings are emitted while rendering instead), Russian labels.

## C5 — markdown renderer — answered

**Asked:** 2026-10-14 — research-web

**Question:** Which markdown library renders record bodies?

**Options:**

- markdown-it-py — CommonMark, built-in table rule, tokens carry source line maps, one dependency (`mdurl`)
- mistune — fast, no source line maps
- python-markdown — not CommonMark

**Answer:**

Default chosen by the agent — [clarify] the owner confirms. markdown-it-py (4.2.0 on PyPI, Python ≥ 3.10), `commonmark` preset with `table` enabled, raw HTML off (escaped). Line maps give the `L{line}` mark anchors without a second parser.

## C6 — links that do not land on a record — answered

**Asked:** 2026-10-14 — draft-plan

**Question:** How is a body link or a frontmatter ref rendered when it does not resolve to a rendered record?

**Answer:**

Default chosen by the agent — [clarify] the owner confirms. Body link to a local path: resolved against the record's directory with symlinks followed; lands on a record of any rendered root → relative link to that record's page (anchor kept); lands on an existing non-record file (a retro, `CLAUDE.md`) → the link text with no `href`, class `offsite`, no warning (`specs check` owns link validity); target missing → link text, class `unresolved`, one warning. URL, `mailto:` and absolute links pass through unchanged. Frontmatter list item that parses as `[ns:]type/NNNN` → link when it resolves, `unresolved` code plus a warning when its root is rendered but the record is missing, plain code with no warning when the namespace names no rendered root. Bare refs in body prose are not linked. Exit stays 0 on warnings.

## C7 — frontmatter shown on a record — answered

**Asked:** 2026-10-14 — draft-plan

**Question:** Which frontmatter keys does a record page show?

**Answer:**

Default chosen by the agent — [clarify] the owner confirms. `title`, `summary`, `status` (and `kind` for a value) go into the record header; every other key is shown in a facts list in frontmatter order, so a user tier's own keys appear without code knowing them (value/0005, value/0006). A list value renders item by item, each item a ref link when it parses as one.

## C8 — snapshot drift — answered

**Asked:** 2026-10-14 — draft-plan

**Question:** May this run accept snapshot drift, given rule/0013?

**Answer:**

The owner's standing permission for this feature (2026-10-14) overrides rule/0013 for this run only: `just snapshots-accept` is allowed when every drifted hunk is a change this plan describes, listed with its reason in `develop-defaults.md`; any other drift stops the run. The plan touches no playbook source, so no drift is expected.

## C9 — full-page HTML baselines vs hand-derived expectations — answered

**Asked:** 2026-10-14 — draft-plan

**Question:** anton:rule/0003 asks for hand-derived expectations; a full HTML page in a txtar `expected/` section is impractical to write by hand. How do the e2e cases assert pages?

**Answer:**

Default chosen by the agent — [clarify] the owner confirms. Split by tier: the hand-derived behaviour checks live in M02's tests (every relative href lands on a written page and every fragment on an id, the cross-root href, the mark anchor, backlinks, warnings — literals written by hand). The txtar cases hand-write stdout, stderr, exit and the marker file, and hold full pages as contract baselines: written once with `--txtar-update`, then read line by line against `index.md` → I/O contract before they are kept, so a later change to page output shows up as a reviewed diff (value/0010).
