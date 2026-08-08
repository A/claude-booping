# Framing brief

## Request

> groom testing in this repo: i want: 1. ci, 2. snapshot tests for output, 3. md-checker tests (what do we need for it? Do we need to publish it? ~/Dev/@A/markdown-checker). So, i see it as a separate just snapshot-tests and just ci (runs all CI tests) commands.

## Task type

`feature` — new capability in the repo's tooling surface: test suites and CI stages that do not exist today (snapshot assertions over rendered output, mdcheck structural gates, an aggregate `just ci`).

- Not `bug` — nothing diverges from expected behaviour; there is no defect to reproduce. The gap is absence of coverage, not a wrong result.
- Not `refactoring` — the work adds new files, recipes and workflow jobs rather than restructuring existing ones with unchanged behaviour. The existing `just lint/typecheck/test` recipes are reused, not reshaped.

## Problem

Today the repo's automated checks stop at `booping-python/`: `.github/workflows/ci.yml` runs ruff, basedpyright and pytest, gated on `paths: booping-python/**`. Everything the plugin actually ships — rendered skill and agent artefacts under `skills/` and `agents/`, composed playbook procedures under `playbooks/*/_reports/output.md`, hand-authored `docs/` and `documentation/` — is verified only by a human running `just build` / `just playbook-reports` and eyeballing `git diff`. A template edit that silently changes every rendered playbook, or a build artefact left un-rebuilt, reaches `master` unnoticed.

Two classes of check are missing:

- **Snapshot** — does the rendered output still equal the committed bytes? Covers build-artefact drift (`skills/`, `agents/`) and playbook-report drift (`playbooks/*/_reports/output.md`), both already byte-reproducible by design (fixture vault + `--stub-macro`).
- **Structural** — does a markdown document still carry the shape its consumers assume (required sections, table columns, frontmatter keys, resolvable links)? This is what `mdcheck` (`~/Dev/@A/markdown-checker`, `github.com/A/markdown-checker`, Rust, `cargo install --git`, v0.1.0, unpublished to crates.io) does deterministically.

The delivery shape the user named: a `just snapshot-tests` recipe and a `just ci` recipe that runs every CI check, with the GitHub workflow calling the latter rather than duplicating stage lists.

## Clarifications and Decisions

- **Snapshot scope is playbook reports only** — re-render every core playbook against the fixture vault with stubbed macros and diff against the committed `playbooks/*/_reports/output.md`. Build-artefact drift (`skills/`, `agents/`), per-step render snapshots and Python-side render unit snapshots are all out.
- **mdcheck reaches CI via crates.io** — `cargo install`, no `--git` install, no prebuilt-binary download.
- **mdcheck is already published** — no crate metadata, release-workflow or `cargo publish` work in the `markdown-checker` repo belongs to this plan. The published crate name is confirmed against crates.io during research (the local checkout declares `name = "mdcheck"` at v0.1.0).
- **mdcheck targets rendered playbook reports only** — the shape `render-playbook` guarantees. Playbook sources, `docs/` templates and vault artefacts get no rule files in this plan.
- **`just ci` = lint + typecheck + test + snapshot-tests + md-check** — the docs build stays in `docs.yml` and is not folded in.
- **No post-implementation prose-shape reshape expected** — the work is tooling (recipes, workflow YAML, rule files, snapshot fixtures); no prompt bodies or rendered prose change.
