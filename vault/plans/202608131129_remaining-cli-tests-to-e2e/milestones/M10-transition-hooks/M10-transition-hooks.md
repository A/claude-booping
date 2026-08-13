---
id: "10"
title: "playbook-transition hooks"
sp: 4
status: pending
plan: "vault/plans/202608131129_remaining-cli-tests-to-e2e/index.md"
---

# M10: playbook-transition hooks

Both hook verbs — `script` and `frontmatter-update` — are pinned by txtar cases: discovery, argv, environment, side effects and every fault exit.

**Scope**: hooks on `playbook-transition` edges and machine-level `hooks:`. Files: new `booping-python/e2e/cases/playbook-transition/*.txtar`; edited `booping-python/e2e/README.md`. Executable fixtures are the constraint this milestone solves: `pytest-txtar` writes content, not permissions, and `playbook_transition.py:268` refuses a script failing `os.access(X_OK)`, so every case whose hook must run opens with a `chmod +x ../home/Claude/_playbooks/{pb}/_scripts/{name}` cmd line — probed during grooming, hook side effects assert through `expected/`. The non-executable refusal needs no `chmod` and is a case in its own right.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 10.1 | Script-hook execution cases: a hook running and reporting `script {name}: ok`, its side-effect file asserted through `expected/`, the `BOOPING_ARTIFACT` / `BOOPING_INSTANCE` / `BOOPING_WORKDIR` environment and the cwd it runs in (asserted by a script that writes them out), trailing tokens passed through as argv, and an instance slug reaching the script | `booping-python/e2e/cases/playbook-transition/*.txtar` | 1 | pending |
| 10.2 | Script-discovery cases: the playbook's own `_scripts/` shadowing a same-named root copy, a discovery root's `_scripts/` used when the playbook carries none, a fallback to the next root, a missing script exiting 2 with every probed path named, and a present-but-not-executable script exiting 2 | `booping-python/e2e/cases/playbook-transition/*.txtar` | 1 | pending |
| 10.3 | Hook-fault cases: a script exiting non-zero exits 2 with its own stderr relayed verbatim ahead of the `error:` line, an unknown hook verb exits 2, and a failed hook leaves the artifact's status unmoved | `booping-python/e2e/cases/playbook-transition/*.txtar` | 1 | pending |
| 10.4 | `frontmatter-update` hook cases: a hook with no target writing the artifact itself, a file target writing a sibling file, an `{instance}`-bearing target interpolated, that target without `--instance` exiting 2, a missing target file exiting 2, a target file with no frontmatter block getting one bootstrapped, and the README gaining the `chmod` pattern note | `booping-python/e2e/cases/playbook-transition/*.txtar`, `booping-python/e2e/README.md` | 1 | pending |

## Definition of Done

### Task 10.1

- [ ] A case's stdout pins `script {name}: ok` in the report, and `expected/cwd/run/{file}` carries what the hook wrote.
- [ ] A fixture script writing `$BOOPING_ARTIFACT`, `$BOOPING_INSTANCE`, `$BOOPING_WORKDIR` and `$PWD` into a file proves all four, with sandbox paths normalized to `{CWD}` in the expected section.
- [ ] A hook declared as `script {name} arg1 arg2` reaches the script as `$1` and `$2`.
- [ ] An instance transition passes the slug through `BOOPING_INSTANCE`, empty on a plain machine.

### Task 10.2

- [ ] Two near-identical fixtures — one with a playbook-local `_scripts/{name}`, one without — show the local copy winning and the root copy used otherwise, asserted by distinct marker output.
- [ ] The missing-script case exits 2 and its stderr lists every probed path in order, with sandbox paths normalized.
- [ ] A script fixture written without a `chmod` line exits 2 with the not-executable message naming the path.

### Task 10.3

- [ ] A hook exiting non-zero exits 2, the script's own stderr appears verbatim, and the `error:` line names the hook and its exit code.
- [ ] An unknown hook verb exits 2 naming the verb.
- [ ] Both fault cases assert through `expected/` that the artifact's `status:` is still the pre-edge value.

### Task 10.4

- [ ] A `frontmatter-update` hook with no target writes the keys onto the artifact, asserted by the expected artifact and the `frontmatter:` report lines.
- [ ] A file-target hook writes a sibling file; an `{instance}`-bearing file target lands at the interpolated path.
- [ ] The instance-bearing target invoked without `--instance` exits 2; a missing target file exits 2; a target file with no frontmatter block gains one, with its body preserved below.
- [ ] `booping-python/e2e/README.md` documents the `chmod` cmd-line pattern for executable hook fixtures, and states that permissions are otherwise not expressible in a fixture section.

## Verify

```
cd booping-python && uv run pytest e2e -k playbook-transition
```

Every case passes without `--txtar-update`, and a follow-up `--txtar-update` run leaves the working tree clean.
