---
id: "11"
title: "playbook-transition --target addressing"
sp: 3
status: pending
plan: "vault/plans/202608131129_remaining-cli-tests-to-e2e/index.md"
---

# M11: playbook-transition --target addressing

`--target` — what it overrides, what workdir it implies, what it bootstraps and what it refuses — is pinned by txtar cases.

**Scope**: `--target` and its interaction with `--workdir`, `--instance` and machines declaring no `artifact:`. Files: new `booping-python/e2e/cases/playbook-transition/*.txtar`. Ported from the `--target` and `bootstrap onto an existing file` sections of `tests/commands/playbook_transition_test.py` (lines 506–end). Workdir implication is the subtle half: an absolute target ending in the declared `artifact:` implies its workdir, and the cases pin which directory hooks then run in.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 11.1 | Override cases: a relative target resolving against the workdir and overriding the declared artifact, an absolute target honoured as given, a machine declaring no `artifact:` refusing without `--target` and moving with one, and `--target` together with `--instance` exiting 1 | `booping-python/e2e/cases/playbook-transition/*.txtar` | 1 | pending |
| 11.2 | Workdir-implication cases: an absolute target ending in the declared artifact implying its workdir, an explicit `--workdir` beating the implied one, an absolute target that does not end in the declared artifact keeping the invocation directory, a relative target never re-anchored under an implied workdir, and a hook receiving the resolved target as `BOOPING_ARTIFACT` | `booping-python/e2e/cases/playbook-transition/*.txtar` | 1 | pending |
| 11.3 | Target-bootstrap cases: a missing target file bootstrapped at the initial status, the same with a non-initial target refused, an existing file stamped with `status:` without losing its other keys or body, and an existing file with no frontmatter block gaining one | `booping-python/e2e/cases/playbook-transition/*.txtar` | 1 | pending |

## Definition of Done

### Task 11.1

- [ ] A relative `--target other.md` moves that file and leaves the declared artifact absent, asserted by two `expected/` sections — one for the moved file, one showing the declared path unwritten.
- [ ] An absolute `--target` under the sandbox is honoured, with the path normalized to `{CWD}` in the pinned output.
- [ ] A machine with no `artifact:` exits 1 without `--target`, naming what is missing, and moves cleanly with one.
- [ ] `--target` plus `--instance` exits 1 with the mutual-exclusion message.

### Task 11.2

- [ ] An absolute target ending in the declared `artifact:` runs its hooks in the implied workdir, asserted by a hook that writes into `$BOOPING_WORKDIR` and an `expected/` section at that path.
- [ ] The same invocation with an explicit `--workdir` writes into the explicit one instead.
- [ ] An absolute target not ending in the declared artifact leaves the workdir at the invocation directory.
- [ ] A relative target under an invocation that also implies a workdir resolves against the workdir argument, not the implication — asserted by where the moved file lands.
- [ ] A hook run under `--target` sees the resolved target in `BOOPING_ARTIFACT`.

### Task 11.3

- [ ] `--target` at a path that does not exist creates it at the machine's initial status when the target status is that initial one.
- [ ] The same invocation with a non-initial target status exits 1 and creates nothing.
- [ ] An existing target file carrying other frontmatter keys and a body gains `status:` with both preserved, asserted byte-for-byte in the expected section.
- [ ] An existing target file with no frontmatter block gains one above its body.

## Verify

```
cd booping-python && uv run pytest e2e -k playbook-transition
```

Every case passes without `--txtar-update`, and a follow-up `--txtar-update` run leaves the working tree clean.
