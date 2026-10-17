---
id: "04"
title: "booping specs check — per-record checks"
sp: 6
status: done
plan: "plans/202610141731_specs-core-format-cli-injection/index.md"
---

# M04: booping specs check — per-record checks

`booping specs check [--tier]` validates every record of a tier against its shipped schema and the per-record and number checks, printing findings, the trailer and the exit code exactly as the plan's I/O contract states.

**Scope**: new `booping-python/src/booping/specs/check.py` holding `Finding(path, line, level, check, message)`, the per-record checks and the mdcheck call; the `check` verb in `booping-python/src/booping/commands/specs.py`. Checks in this milestone: `schema` (mdcheck), `layout`, `filename`, `id`, `frontmatter`, `targets`. The cross-file `link`, `ref`, `sources` and `namespace` checks are M05 — leave a single place in `check.py` where M05 appends its checks. mdcheck runs as `mdcheck {format}/schemas/{type}.yaml - --format json`, `{format}` being `core.specs.format` resolved against the plugin root, with the record on stdin; each JSON finding becomes `Finding(level="error", check="schema", line=finding.line, message=finding.message)`; exit 0/1 parsed, anything else, unparsable JSON or a missing binary → `error: …` on stderr, exit 2 (plan I/O contract). A record in a directory under the tier root whose name is not a shipped type (M02 `types()`), or a `.md` file directly under the root other than `README.md`, gets one `layout` finding and no schema run. `targets` reuses `booping.context.lesson.parse_target` — rejections become ``target `{entry}`: {reason}``. Findings sort by path then line; the trailer goes to stderr. Line numbers: 1 for file-level findings; the `type:` key's line for a type mismatch (naive `key:` line scan over the frontmatter, frontmatter starting at file line 2). Tests: txtar e2e cases under `booping-python/e2e/cases/specs/` — a clean two-type tier (exit 0, trailer only), one case per check with a fixture record breaking exactly that check (exit 1, exact finding line), duplicate numbers across two files of one type (a finding on each), a mdcheck schema finding passed through verbatim. A unit test for the missing-binary path runs the verb with `PATH` pointing at an empty directory (subprocess is the true boundary).

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | `check` verb with `--tier`: `Finding`, sorting, output line, stderr trailer, exit codes, the `schema` check via mdcheck; e2e clean-tier and schema-finding cases; the missing-binary unit test. | `booping-python/src/booping/specs/check.py`, `booping-python/src/booping/commands/specs.py`, `booping-python/e2e/cases/specs/check-*.txtar`, `booping-python/tests/specs/check_test.py` | 3 | done |
| 4.2 | `layout`, `filename`, `id`, `frontmatter`, `targets` checks with the plan's message texts; one e2e case per check. | `booping-python/src/booping/specs/check.py`, `booping-python/e2e/cases/specs/check-*.txtar` | 3 | done |

## Definition of Done

### Task 4.1

- [x] `bin/booping specs check --help` shows `--tier`.
- [x] A clean tier → empty stdout, stderr exactly `{n} record(s) checked: 0 error(s), 0 warning(s)`, exit 0.
- [x] A schema violation → `{path}:{line}  error  schema  {mdcheck message}`, exit 1.
- [x] `mdcheck` absent from PATH → stderr `error: mdcheck not found on PATH — cargo install markdown-checker`, exit 2.

### Task 4.2

- [x] Each of `layout`, `filename`, `id`, `frontmatter`, `targets` has a passing e2e case pinning its exact output line and exit 1.
- [x] A rule with both `targets:` and `brief:` and parseable targets yields no `targets` finding.

Return: the list of changed files, nothing else.

## References

- `booping-python/src/booping/commands/specs.py` (from M03) — the group the verb joins.
- `scripts/mdcheck.py` — the existing mdcheck invocation and its exit-code handling.
- `booping-python/src/booping/context/lesson.py` — `parse_target` and its rejection reasons.

## Verify

```
just e2e -k specs
```

All selected cases pass.
