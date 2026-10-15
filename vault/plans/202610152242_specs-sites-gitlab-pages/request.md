# Request

**Request**

> Request — specs sites on GitLab Pages under one index (vault/adr/0029-specs-sites-on-gitlab-pages.md — read it first). In booping: (1) `booping specs site-index` renders one static index page from a list of projects (name, url, one-line description; input a YAML file or stdin JSON) with the same look as `booping specs site`; deterministic output; (2) a shipped GitLab CI template for a project's `pages` job (`booping specs site --out public` on the default branch; how the job gets booping and mdcheck — pick the cheapest robust way and document it) and a template for the index project's scheduled job that lists the group's projects with topic `booping-specs` through the GitLab API (token from a masked CI variable, never printed) and runs site-index; both documented in documentation/specs.md; (3) txtar e2e for site-index. Do not touch any GitLab project or remote; the orchestrator wires lab/lab.pages.zorya.dev afterwards.

(Run directives — autonomous, worktree, snapshot policy — are in the session prompt and not repeated here.)

**Task type** — `feature`: a new CLI verb (`booping specs site-index`) and two new shipped CI templates appear. Not `bug`: `booping specs site` works as documented; nothing diverges. Not `refactoring`: new commands and files appear, so the no-behaviour-change test fails.

**Problem** — Today `booping specs site` renders one project's specs roots to a static directory, and nothing publishes it or ties several projects' sites together. adr/0029 decides each repo-local-vault project publishes its site on GitLab Pages through a booping-shipped `pages` job, and one index project at the group's Pages root lists every project carrying the topic `booping-specs`, rebuilt on a schedule. After this plan booping ships: `booping specs site-index`, rendering one index page in the site's look from a project list; a project `pages` template; an index template whose scheduled job discovers the projects through the GitLab API and runs site-index; docs for both; txtar contract cases. No GitLab project or remote is touched.

**Clarifications and Decisions** (autonomous run — each a default, logged in `clarifications.md`)

- C1 — how a job gets booping: shallow `git clone` of the plugin repo at a `BOOPING_REF` variable, run through `bin/booping` on the `ghcr.io/astral-sh/uv:python3.12-trixie` image (uv + git preinstalled); templates consumed via `include: remote`.
- C2 — mdcheck in CI: none — `specs site` and `site-index` never call mdcheck; only `specs check` does.
- C3 — input shape: a list of `{name, url, description}` mappings; `--projects FILE` parsed as YAML, `--projects -` reads JSON from stdin; strict keys, http(s) URLs only, unique names.
- C4 — where GitLab discovery lives: a stdlib-only Python script shipped beside the index template, not a `booping` verb — the core CLI stays GitLab-free (value/0005, adr/0029).
- C5 — one plan, no split.
