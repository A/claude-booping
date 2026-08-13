---
id: "08"
title: "debug-context cases"
sp: 1
status: pending
plan: "vault/plans/202608131522_final-cli-commands-to-e2e/index.md"
---

# M08: debug-context cases

`booping debug-context` gets its first coverage: an assembly guard asserting exit and stderr, with stdout deliberately unasserted and each case saying why.

**Scope**: the `debug-context` subcommand, which takes no flags. Files: new `booping-python/e2e/cases/debug-context/*.txtar`.

The stdout dump enumerates every core playbook, skill and agent, and the runner's `text_matches` rejects on unequal line counts before any wildcard applies — so `[..]` cannot absorb a list whose length changes when a playbook is added, and there is no way to narrow the output: cmd lines run raw argv with no shell, only `argv[0]` is rewritten, stdout never reaches disk for a later cmd line to read, and the command has no `--output`. What remains is worth having: `debug-context` assembles the whole `Context`, so a case that reaches exit 0 over a given vault shape catches the class of the `git_commit under project` regression, which is exactly how that bug surfaced.

Asserting the dump is valid YAML is explicitly not in scope — `yaml.dump` cannot emit invalid YAML, so such an assertion tests PyYAML rather than booping.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 8.1 | Write the assembly-guard cases — one over a cwd-rooted vault with a `.booping` marker, plans, lessons and a local playbook seeded, one with no marker anywhere — each asserting exit 0 and empty stderr with no `stdout` section, and each opening with a comment naming what it does not pin and why | `booping-python/e2e/cases/debug-context/*.txtar` | 1 | pending |

## Definition of Done

### Task 8.1

- [ ] The attached-vault case seeds a `.booping` marker, at least one plan, one lesson and one `fx-`-prefixed local playbook, and asserts exit 0 with an empty `stderr` section.
- [ ] The detached case runs from a `cwd` root with no marker on any parent and likewise asserts exit 0 and empty stderr.
- [ ] Neither case carries a `stdout` section.
- [ ] Each case file opens with a comment stating that stdout is unasserted because the dump's line count tracks the shipped playbook, skill and agent lists, and that the case guards assembly rather than output content.

## Verify

```
cd booping-python && uv run pytest e2e -k debug-context
```

Green, with both cases collected.
