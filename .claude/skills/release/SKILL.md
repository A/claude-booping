---
name: release
description: Cut a booping plugin release — verify the version bump against the last published tag, draft public-voiced release notes, merge the release branch into master, tag, and publish the GitHub release. Use when cutting a vX.Y.Z release of this repo.
user-invocable: true
allowed-tools:
  - Read
  - Write
  - Bash(git:*)
  - Bash(gh:*)
  - Bash(jq:*)
---

# release — cut a booping plugin release

Releases the `booping` plugin from a `release/X.Y.Z` branch: verifies the version, drafts public release notes, merges to `master`, tags `vX.Y.Z`, and publishes the GitHub release.

Run from the repo root with the `release/X.Y.Z` branch checked out. Default branch is **`master`**. Version is single-source in `.claude-plugin/plugin.json`.

## Preflight — gather facts

Run these read-only; report the resolved values back before doing anything that writes:

```bash
git rev-parse --abbrev-ref HEAD                       # current branch — expect release/X.Y.Z
jq -r .version .claude-plugin/plugin.json             # the version to ship
gh release list --limit 1                             # last published release
git status --porcelain                                # working tree must be clean
git remote                                            # remote name — this repo uses `gh`, NOT origin
```

Resolve: `VERSION` (from plugin.json), `TAG = v$VERSION`, `LAST_TAG` (newest existing `v*` tag), `BRANCH`, and `REMOTE` (the single remote — do not assume `origin`; use whatever `git remote` reports). Substitute `$REMOTE` into every push/fetch/log-range below.

## Phase 0 — Verify version + previous release

Gate every check; if any fails, stop and report — do not proceed to merge.

1. **Clean tree** — `git status --porcelain` is empty. Dirty tree → stop.
2. **On the release branch** — `BRANCH` is `release/$VERSION`. If it is `master` or a mismatched `release/*`, stop and ask the user to switch.
3. **Version bumped** — `$VERSION` is strictly greater than `LAST_TAG` (semver). The bump commit follows the convention `chore(booping): bump plugin version <prev> → $VERSION`; confirm it exists in `git log master..HEAD`. If plugin.json still equals `LAST_TAG`, stop — the bump is missing.
4. **Tag is free** — `git tag -l "$TAG"` and `gh release view "$TAG"` both return nothing. An existing tag/release → stop (already released).
5. **Branch is ahead of master** — fetch first (`git fetch $REMOTE`), then `git log $REMOTE/master..HEAD --oneline` is non-empty (there is something to release).

Report the verification result as a short checklist before continuing.

## Phase 1 — Draft release notes

Compute the release contents from the commit range, then write them in the **public voice** described below.

```bash
git fetch $REMOTE
git log $REMOTE/master..HEAD --oneline        # commits being released
git diff --stat $REMOTE/master..HEAD | tail -1
```

Read the previous release for voice and structure before drafting:

```bash
gh release view "$LAST_TAG"
```

### Audience tiering (the core rule)

Notes are for **public plugin users**, not contributors. Classify every commit by who touches it, then order the notes user-first:

1. **Lead paragraph** — one or two sentences: what this release is mainly about.
2. **⚠️ Breaking change** *(only if any)* — what broke, with a **Migration notes** section at the end.
3. **User-facing feature sections** (`## Title` each) — capabilities the user interacts with: new/changed skills (`/groom`, `/develop`, `/install`, …), vault/setup behaviour, workflow changes. Explain these properly — what it does and why it matters to them.
4. **`## Other changes`** — a compact bullet list (one line each) for everything internal: refactors, schema/engine internals, docs, test/build plumbing. No deep explanations here.

### Privacy rules

- The **`booping` CLI** (`render`, `transition`, `build`, `vault-commit`, … and `booping-python/` internals) is **private** — users never invoke it directly. Never give CLI work a feature section or a long write-up. A single compact line under **Other changes** ("refactored the transition engine", "improved render performance") is the most it gets — unless a change is a large, user-visible performance or reliability win, in which case a brief mention in a feature section is acceptable.
- Build-time plumbing (`src/files/`, `just build`, config_files, CI) is internal — **Other changes** one-liners only.
- Do not enumerate per-milestone commit messages. Group related commits into one human-readable point.

### Output

Write the drafted notes to `/tmp/release-notes-$VERSION.md` and present them in chat. Iterate with the user until they explicitly approve. Do not merge or publish before approval.

## Phase 2 — Merge the release branch to master

Only after the user approves the notes. Detect whether a PR is open and pick the path:

```bash
gh pr list --head "release/$VERSION" --base master --state open --json number,title
```

- **PR open** → merge it: `gh pr merge <number> --merge` (creates the merge commit on master). Then `git checkout master && git pull $REMOTE master`.
- **No PR** → direct merge:

  ```bash
  git checkout master
  git pull $REMOTE master
  git merge --no-ff "release/$VERSION" -m "merge release/$VERSION into master"
  git push $REMOTE master
  ```

Confirm the push succeeded and `master` now contains the release commits (`git log $REMOTE/master..HEAD` is empty afterward).

## Phase 3 — Tag and publish

On `master`, after the merge landed:

```bash
git tag "$TAG"
git push $REMOTE "$TAG"
gh release create "$TAG" --title "$TAG" --notes-file "/tmp/release-notes-$VERSION.md" --latest
```

This publishes immediately (per the chosen workflow). Report the release URL `gh release view "$TAG" --json url -q .url` back to the user.

## Hard rules

- **Never publish or push without the version-verify gate passing** (Phase 0). A missing or non-incremented bump aborts the release.
- **Never merge or publish before the user approves the drafted notes.**
- **The CLI is private** — it never earns a release-notes feature section.
- Default branch is `master`, not `main`. The git remote is **not** named `origin` — resolve it with `git remote` and use `$REMOTE`. Tags are `vX.Y.Z`. Version source of truth is `.claude-plugin/plugin.json` only.
- If any git/gh command fails mid-flow, stop and surface the exact error — do not retry blindly or force-push.
