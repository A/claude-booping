---
type: runbook
title: Cut a plugin release
summary: A release is a release/X.Y.Z branch bumping plugin.json and CHANGELOG.md, merged by PR into master, then tagged vX.Y.Z with a GitHub release on the merge commit.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: live
sources: [CHANGELOG.md, .claude-plugin/plugin.json, .github/workflows/docs.yml, vault/_playbooks/docs/changelog/opus-5.md]
---

## When

User-visible changes have landed on `master` and should reach users, who pick them up
with `/plugin update booping`.

## Before you start

- `master` is up to date with the GitHub remote, which is named `gh`, not `origin`.
- `just ci` is green on `master`.
- The version follows semver: a patch for fixes only, no new feature and no config change.

## Steps

1. Cut `release/X.Y.Z` from `master`.
2. Set `"version"` in `.claude-plugin/plugin.json` to `X.Y.Z`; `marketplace.json` carries
   no version.
3. Write the `## vX.Y.Z — YYYY-MM-DD` entry at the top of `CHANGELOG.md`: one lead line,
   then `### Added` / `### Changed` / `### Fixed` bullets of user-visible effects in the
   past tense. The `docs` user playbook's changelog step writes the same shape when it has
   run since the last release; earlier entries are never reworded.
4. Commit both files as `release: vX.Y.Z`.
5. Push the branch to `gh` and open a PR into `master` titled `release: vX.Y.Z`; its body
   names the base commit, the two files changed, the PRs included and why the bump is
   patch, minor or major.
6. Merge the PR with a merge commit.
7. Create the GitHub release `vX.Y.Z` on `master` (`gh release create vX.Y.Z --target
   master`), which tags the merge commit. The notes open with the changelog's lead line
   and give each change its own `##` section, in more depth than the changelog.

## Check

- `gh release list` shows `vX.Y.Z` as Latest, and `git tag` has `vX.Y.Z` on the merge
  commit after a fetch.
- `.claude-plugin/plugin.json` on `master` reads `X.Y.Z`.
- The docs workflow ran green on the push to `master` (it publishes the site to `gh-pages`).

## Rollback

- No release has been rolled back and there is no rollback procedure; the owner
  finds that acceptable for now (2026-10-14). A broken release is fixed by the next
  patch release.
