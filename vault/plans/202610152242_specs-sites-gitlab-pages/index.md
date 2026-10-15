---
title: "Specs sites on GitLab Pages — booping specs site-index and the CI templates"
type: "feature"
status: presenting
sp: null
related_to: null
created: 2026-10-15 22:43
planned: null
started: null
completed: null
code_reviews: []
sessions:
- 908d42c7-d080-4f88-89c0-c354e8d7d15a
retro: null
summary: booping specs site-index renders a group index page; shipped GitLab CI 
  templates publish specs sites and the index on Pages
commit: 0d0a7e372f85e537b80b21f672a0b6da2794f0d0
tracker_provider: null
tracker_request: null
tracker_issue: null
return_to: null
---

# Specs sites on GitLab Pages — booping specs site-index and the CI templates

## Context

`booping specs site` renders a project's specs roots to a static directory; nothing publishes it or ties several projects' sites together. adr/0029 decides each repo-local-vault project publishes its site on GitLab Pages through a booping-shipped `pages` job, and an index project at the group's Pages root lists every project carrying the topic `booping-specs`, rebuilt on a schedule. After this plan: a new verb `booping specs site-index` renders that index page in the site's look from a project list; booping ships `src/ci/gitlab/` with a project template, an index template and the discovery script the index job runs; `documentation/specs.md` documents both. No GitLab project or remote is touched — wiring the owner's group is the orchestrator's job afterwards. Request and framing: [request.md](request.md); every default settled by this autonomous run: [clarifications.md](clarifications.md).

Values in play: value/0015 (deterministic where it can be — sorted, timestamp-free index output, discovery by code not by the model), value/0005 (stack-agnostic core — GitLab lives only in opt-in shipped files, never in the CLI), value/0010 (proven to work — txtar cases for the verb, a fake-server test for discovery, template tests tying script paths to the repo), value/0012 (cheapest robust CI: no image to build, no mdcheck). Departures: value/0005 is bent by shipping GitLab files at all — adr/0029 decided it, the files name no host or project (C6); vault rule/0013 is overridden for this run by the owner's standing snapshot permission, and no playbook source changes, so no drift is expected (C6).

## Decisions

- **Verb**: `booping specs site-index` beside `site`, sharing its stylesheet, base template and marker-safe writer — "same look" by construction, not by copy (value/0003).
- **Input**: list of `{name, url, description}`; `--projects -` (default) is stdin JSON, a path is YAML; strict validation, http(s) URLs only, unique names — C3.
- **Output content**: locked in C3 — sorted rows, collapsed one-line descriptions, `Project | Description` table, `No projects.` for an empty list, one stdout summary line (booping:rule/0010).
- **Exit codes**: 0 written; 1 unreadable/invalid list or refused out dir, `error: …` on stderr; 2 config not loadable — the `specs` verbs' existing contract.
- **Getting booping in CI**: shallow `git clone` at `BOOPING_REF` + `bin/booping` on `ghcr.io/astral-sh/uv:python3.12-trixie` (uv, Python, git preinstalled); templates consumed by `include: remote:` — C1.
- **mdcheck**: not installed — `site` and `site-index` never call it — C2.
- **Discovery**: stdlib-only `src/ci/gitlab/list-specs-projects.py`, not a CLI verb; token only in the `PRIVATE-TOKEN` header, never printed — C4.
- **Pages job shape**: classic job `pages` with `artifacts: paths: [public]` — works on every GitLab version, unlike the newer `pages.publish` keyword.

## Architecture

```
project repo (repo-local vault)          index project ({group}.{pages-domain})
  include: specs-site.gitlab-ci.yml        include: specs-index.gitlab-ci.yml
  pages job, default branch                pages job, schedule | web
    git clone booping @ BOOPING_REF          git clone booping @ BOOPING_REF
    bin/booping specs site --out public      list-specs-projects.py  ── GitLab API (SPECS_INDEX_TOKEN)
          │                                      │ JSON [{name,url,description}]
          ▼                                      ▼
  {group pages root}/{project}             bin/booping specs site-index --out public
                                                 ▼
                                           {group pages root}/
```

In `booping-python`: `commands/specs.py` registers `site-index`; `specs/site/index.py` holds `Project`, `load_projects`, `build_index`; the template `specs/site/templates/site_index.html.j2` extends `base.html.j2`; writing reuses `specs/site/write.py`. No caller inlines the verb; no config key is added.

## Milestones

| id | title | sp | status |
| --- | --- | --- | --- |
| 01 | site-index — the index page from a YAML project file | 4 | pending |
| 02 | site-index — stdin JSON and input validation | 3 | pending |
| 03 | GitLab discovery script — the group's booping-specs projects as site-index input | 3 | pending |
| 04 | GitLab CI templates — the project pages job and the index job | 2 | pending |
| 05 | Docs — site-index, publishing on GitLab Pages, CLAUDE.md | 2 | pending |

## Milestone files

One file per milestone under `milestones/M{nn}-{kebab}/`; each carries its goal, scope, tasks, DoD, references and Verify.

## I/O contract

- **Arguments / flags**: `booping specs site-index [--projects PATH|-] [--out DIR] [--title TEXT]` — `--projects` the list (default `-`), `--out` the output dir (default `specs-site-index`), `--title` H1/title/crumb (default `Specs`).
- **stdin**: with `--projects -`, a JSON array of `{name, url, description?}`.
- **stdout**: one line `specs site-index: {n} projects -> {out}`.
- **stderr**: one `error: {message}` line on failure, entries named `projects[{i}]`; nothing on success.
- **Exit codes**: `0` index written; `1` unreadable or invalid project list, or out dir refused; `2` config could not be loaded.
- **Files**: `{out}/index.html`, `{out}/style.css`, `{out}/.booping-site`; byte-identical for the same input.
- **Discovery script** (`src/ci/gitlab/list-specs-projects.py`): env in, JSON array (the stdin shape above) out, `list-specs-projects: {reason}` + exit 1 on failure — C4.

## Final Verification

- [ ] Help text updated and accurate (`booping specs site-index --help`).
- [ ] Happy-path + failure-path invocations verified by the M01/M02 txtar cases.
- [ ] Exit codes match the documented contract.
- [ ] `just ci` green.

## Out of scope

- Touching any GitLab project, schedule, variable or remote — the orchestrator wires `lab/lab.pages.zorya.dev` after this plan.
- Subgroup projects in the index, a GitLab provider in `booping-tracker`, a booping container image, a `specs check` CI template.
- Changing `booping specs site` output.

## CLAUDE.md impact

`## Commands` — `site-index` added to the `specs` subcommand list; `## Layout` — `src/ci/` added (M05).
