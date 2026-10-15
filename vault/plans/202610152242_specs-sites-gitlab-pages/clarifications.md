# Clarifications

Autonomous run — the owner was unavailable; every question below was settled by the run with a default.

## C1 — how a CI job gets booping — answered

**Asked:** 2026-10-15 — intake

**Question:** The request asks for the cheapest robust way for the `pages` job (and the index job) to get booping, documented.

**Options:**

- `uv tool install` of `booping-python` from git — fails: the CLI reads plugin-root files (`src/config.yaml`, `src/specs/`) that a wheel does not carry
- a booping container image — robust but needs a registry and a release pipeline booping does not have
- shallow `git clone` of the plugin repo and `bin/booping`

**Answer:**

Shallow `git clone --depth 1 --branch "$BOOPING_REF"` of `BOOPING_REPO` (default `https://github.com/A/claude-booping.git`, ref default `master`, documented to pin a release tag) into a scratch dir, then `bin/booping` — the same entry point every user runs. Image `ghcr.io/astral-sh/uv:python3.12-trixie`: derived from `python:3.12-trixie` (buildpack-deps), so uv, Python ≥ 3.12, git and curl are already there and no `apt-get` runs. `UV_CACHE_DIR` sits in the project dir under a CI `cache:` key so dependency installs are reused. Projects consume a template with `include: remote:` on its raw GitHub URL (public, no auth) — no copy to keep in sync.

## C2 — mdcheck in CI — answered

**Asked:** 2026-10-15 — intake

**Question:** How does the job get mdcheck?

**Answer:**

It does not need it. `booping specs site` never calls mdcheck (only `specs check`, in `specs/check.py`, shells out to it), and `site-index` does not either. The templates install no Rust toolchain; the docs say so, and name `cargo install markdown-checker --version 0.1.1 --locked` for a project that adds its own `specs check` job.

## C3 — site-index input and output — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** Exact input shape, validation and output content of `booping specs site-index` (rule booping:rule/0010 — output content locked in grooming).

**Answer:**

- Input: a list of mappings with keys `name` (required, non-empty string), `url` (required, `http://` or `https://`), `description` (optional string or null). `--projects FILE` parses FILE as YAML; `--projects -` (the default) parses stdin as JSON. Unknown keys, a non-list top level, a missing or empty name, a non-http(s) URL and a duplicate name each fail with exit 2 and one `booping specs: …` stderr line naming the entry index.
- Order: entries sorted by `(name.casefold(), name)`; the input order never shows.
- Description: whitespace runs collapsed to one space and stripped, so a multi-line description renders as one line; absent or null renders an empty cell.
- Output: `--out DIR` (default `specs-site-index`) gets `index.html`, `style.css` (the site's stylesheet, byte-identical) and the `.booping-site` marker, written by the site's own writer with its non-empty-out safety check. `--title TEXT` (default `Specs`) is the H1, the `<title>` (`{title} — specs`, the site's shape) and the single crumb.
- Page body: the H1, then a table `Project | Description`, one row per entry, the name linking to the URL. Zero entries renders the H1 and a paragraph `No projects.` and exits 0 — a group with no tagged project is not an error.
- Stdout: one line `specs site-index: {n} projects -> {out}`.

## C4 — where GitLab discovery lives — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** The index job lists the group's projects with topic `booping-specs` through the GitLab API. Is that a `booping` verb or part of the template?

**Answer:**

A stdlib-only Python script shipped beside the templates, `src/ci/gitlab/list-specs-projects.py`, run by the index job from the cloned plugin and piped into `booping specs site-index --projects -`. Value/0005 and adr/0029 keep GitLab specifics out of the core CLI ("GitLab-specific parts … are project and tracker concerns"); `booping-tracker` has no GitLab provider to host it. The script reads `CI_API_V4_URL`, `CI_PROJECT_NAMESPACE` (the group, URL-encoded), `SPECS_TOPIC` (default `booping-specs`), `SPECS_PAGES_BASE` (default `CI_PAGES_URL`, the index project's own Pages URL, which is the group's Pages root) and the token from `SPECS_INDEX_TOKEN`; calls `GET /groups/:id/projects?topic=…&archived=false&per_page=100&order_by=path`, following `x-next-page`; sends the token only as the `PRIVATE-TOKEN` header; prints JSON `[{name, url: {base}/{path}, description}]`. A missing token or an HTTP error exits non-zero with the status and the URL — never the token. Subgroups are not included (a project's Pages path under a subgroup differs); the docs say so.

## C5 — one plan or a split — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** Split the request?

**Answer:**

One plan: it stays well under the 35 SP threshold, and the templates are useless without site-index.

## C6 — departures from values and rules — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** Does any choice depart from a value or rule?

**Answer:**

- value/0005 (stack-agnostic core): the core ships GitLab CI templates and a GitLab script. adr/0029 decided exactly that; they are opt-in files under `src/ci/gitlab/`, carry no project or host name (no `lab`, no `zorya`), and the CLI itself stays GitLab-free.
- vault rule/0013 (snapshot baselines accepted by the user): the owner's standing permission for this feature (2026-10-14) lets the run accept drift the plan describes. This plan touches no playbook source, so no drift is expected.
