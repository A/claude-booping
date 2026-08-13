---
id: "05"
title: "session-stats read path"
sp: 3
status: pending
plan: "vault/plans/202608131522_final-cli-commands-to-e2e/index.md"
---

# M05: session-stats read path

Artifact discovery, the JSON-on-stdout / diagnostics-on-stderr split, and both exit-1 refusals are pinned by txtar cases.

**Scope**: `booping session-stats <path> [--mask GLOB] [--projects-root PATH]` in its non-writing aspects. Files: new `booping-python/e2e/cases/session-stats/*.txtar`. The unit file is not touched here — the tier split is M07.

Transcripts are hand-written per case to the minimum shape the assertion needs — a header line plus the few events that produce the pinned numbers — and seeded at `fixtures/home/.claude/projects/{slug}/{id}.jsonl` so the default `--projects-root` resolves to them. One case seeds a cwd-rooted tree and passes `--projects-root` explicitly. The `tests/fixtures/session_stats/` tree is neither copied nor referenced; it stays for the library tests.

Derive every pinned minute and token total by hand from the seeded events. Never run the command first and paste its output as the expectation. Each case whose assertion carries a derived number opens with a comment showing the arithmetic — the events that contributed and the sum — so a reviewer can check the derivation without replaying the transcript, and so a wrong number is visible rather than merely consistent with itself.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | Write the discovery cases: a directory walked by the default `index.md` mask in sorted path order, a directory walked by an explicit `--mask`, a single file path ignoring `--mask` and yielding one entry, and an explicit `--projects-root` against a cwd-rooted transcript tree | `booping-python/e2e/cases/session-stats/*.txtar` | 1 | pending |
| 5.2 | Write the output-contract cases: stdout carrying exactly one JSON document while a note and both warning kinds go to stderr, an artifact with no `sessions:` key skipped with its stderr note at exit 0, a session id with no transcript warning and continuing, and a transcript with malformed lines counted and skipped | `booping-python/e2e/cases/session-stats/*.txtar` | 1 | pending |
| 5.3 | Write the refusal cases: a path that does not exist, a `--mask` matching nothing under an existing root, a `sessions:` key that is not a list, and unreadable frontmatter | `booping-python/e2e/cases/session-stats/*.txtar` | 1 | pending |

## Definition of Done

### Task 5.1

- [ ] A directory case seeds three artifacts whose sorted path order differs from their creation order and pins the `artifacts` array in sorted order.
- [ ] An explicit `--mask` case matches a filename the default mask would miss.
- [ ] A single-file case passes a `--mask` that cannot match and still yields exactly one entry.
- [ ] A `--projects-root` case resolves transcripts from a cwd-rooted tree, proving the flag overrides the `$HOME`-derived default.

### Task 5.2

- [ ] A case pins stdout as one JSON document with nothing else on it, while its stderr section carries the note and warning lines — no line appears on both streams.
- [ ] An artifact with no `sessions:` key is reported with `skipped`, empty `sessions` and `totals`, a stderr note naming it, and exit 0.
- [ ] A session id with no matching transcript emits `warning: no transcript found for session {id}` and the run still exits 0.
- [ ] A transcript carrying malformed lines emits `warning: skipped {n} malformed line(s) in {path}` with `{n}` derived by hand from the seeded file.

### Task 5.3

- [ ] A nonexistent path exits 1 with `path not found:` on stderr and empty stdout.
- [ ] A `--mask` matching nothing under a real directory exits 1 with the no-artifact message naming the mask and root.
- [ ] A `sessions:` key holding a scalar exits 1 with its own message.
- [ ] An artifact whose frontmatter cannot be parsed exits 1 with `cannot read frontmatter of {path}`.

## Verify

```
cd booping-python && uv run pytest e2e -k session-stats
```

Green, with every case in `e2e/cases/session-stats/` collected.
