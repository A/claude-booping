---
id: "03"
title: "playbook-state target addressing and error exits"
sp: 3
status: pending
plan: "vault/plans/202608131522_final-cli-commands-to-e2e/index.md"
---

# M03: playbook-state target addressing and error exits

`--target` and `--workdir` addressing, degenerate artifact shapes, and every exit-1 refusal are pinned by txtar cases.

**Scope**: `booping playbook-state <playbook> [--target PATH] [--workdir PATH]`, its four refusal paths and its two degenerate-frontmatter paths. The `{instance}` placeholder named below is the per-instance state machine's `artifact:` path segment that identifies one instance — its mechanics are in `documentation/playbook.md`. Files: new `booping-python/e2e/cases/playbook-state/*.txtar`. Fixture playbooks are inlined per case with the `fx-` prefix, as in M02. `--workdir` defaulting to cwd is expressed by simply omitting the flag, since the sandbox already runs every cmd line from the `cwd` root.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Write the addressing cases: `--workdir` omitted falling back to cwd, a relative `--target` resolving against the workdir and reporting that file's frontier, an absolute `--target` honoured as given, a `--target` naming a file that does not exist reporting `not-started`, a machine with no declared `artifact:` refusing without `--target`, and the same machine reporting when `--target` is supplied | `booping-python/e2e/cases/playbook-state/*.txtar` | 2 | pending |
| 3.2 | Write the refusal and degenerate-artifact cases: a missing workdir, an unknown playbook name whose stderr lists the known names, a playbook declaring no `states:`, a file whose frontmatter carries no `status:` key, and a file with no frontmatter block at all | `booping-python/e2e/cases/playbook-state/*.txtar` | 1 | pending |

## Definition of Done

### Task 3.1

- [ ] A case omits `--workdir` entirely and reports the run seeded in the `cwd` root, with `workdir` in the pinned YAML normalized to `{CWD}`.
- [ ] A relative `--target` case reports the named file's status, not the machine's declared `artifact:`.
- [ ] An absolute `--target` case passes a `{CWD}`-rooted absolute path and reports that file.
- [ ] A `--target` naming a nonexistent file reports `not-started` with the bootstrap edge, at exit 0.
- [ ] A machine declaring no `artifact:` invoked without `--target` exits 1, with stderr naming the state and telling the caller to pass `--target`.
- [ ] The same machine with `--target` supplied reports normally at exit 0.

### Task 3.2

- [ ] A missing workdir exits 1 with `workdir not found:` and the normalized path on stderr.
- [ ] An unknown playbook name exits 1 and its stderr lists the known names; the shipped names in that list are covered by `[..]` so the case survives a new core playbook.
- [ ] A playbook with a graph but no `states:` exits 1 with its own message.
- [ ] An artifact whose frontmatter block parses but carries no `status:` key reports `not-started`.
- [ ] An artifact with no frontmatter block at all reports `not-started`.

## Verify

```
cd booping-python && uv run pytest e2e -k playbook-state
```

Green, including every case added in M02.
