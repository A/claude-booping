---
id: "09"
title: "playbook-transition bootstrap, edges and the report"
sp: 3
status: pending
plan: "vault/plans/202608131129_remaining-cli-tests-to-e2e/index.md"
---

# M09: playbook-transition bootstrap, edges and the report

`booping playbook-transition` has a txtar case directory covering artifact bootstrap, edge validation, the mutation report and instance addressing.

**Scope**: the `playbook-transition` subcommand without hooks. Files: new `booping-python/e2e/cases/playbook-transition/*.txtar`. Ported from the `bootstrap` and `report` sections of `tests/commands/playbook_transition_test.py`; nothing is deleted here. This milestone establishes the transition fixture conventions: a hookless states-bearing playbook at `fixtures/home/Claude/_playbooks/{name}/` with `playbook.yaml`, and the run workdir seeded as `fixtures/cwd/run/.keep` because the command errors on a missing workdir instead of creating one.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 9.1 | Bootstrap cases: a first transition creating the artifact at the initial status and reporting it, a nested artifact path whose parent directories are created, a missing artifact with a non-initial target exiting 1, and a workdir defaulting to the invocation directory | `booping-python/e2e/cases/playbook-transition/*.txtar` | 1 | pending |
| 9.2 | Report and instance cases: the exact report lines of a normal move — `{from} → {to}` plus one `frontmatter:` line per key — a rerun of the same edge reported as idempotent, and an instance artifact whose `{instance}` path is interpolated and moved with `--instance` | `booping-python/e2e/cases/playbook-transition/*.txtar` | 1 | pending |
| 9.3 | Refusal cases: an illegal edge exiting 1 with the allowed targets listed, `--instance` required for an instance artifact and rejected for a plain one, an artifact with no frontmatter block and one with no `status:` key both exiting 1, an unknown playbook, an unknown state, and a playbook declaring no `states:` | `booping-python/e2e/cases/playbook-transition/*.txtar` | 1 | pending |

## Definition of Done

### Task 9.1

- [ ] A single-`cmd` case bootstraps the artifact: stdout pins `created {artifact}`, the `not-started → {initial}` line and the `frontmatter: status={initial}` line, and `expected/cwd/run/index.md` carries the stamped frontmatter.
- [ ] A machine whose `artifact:` sits under a subdirectory creates those parents, asserted by the expected file rather than by a stdout line.
- [ ] Targeting a non-initial status with no artifact on disk exits 1 with a message naming the artifact path.
- [ ] A case omitting `--workdir` resolves the artifact against the sandbox cwd.

### Task 9.2

- [ ] A two-`cmd` case (bootstrap, then move) pins the full report of the second line, including one `frontmatter: k=v` line per key the edge writes.
- [ ] Re-running the same edge a third time reports the idempotent outcome and writes no second timestamp — asserted by the expected artifact.
- [ ] An instance machine moved with `--instance {slug}` writes `steps/{slug}/index.md`, asserted by an `expected/` section at the interpolated path.

### Task 9.3

- [ ] Each refusal case pins its `error:` line on stderr, its exit code, and — where an artifact exists — that the artifact on disk is unchanged.
- [ ] The illegal-edge message lists every allowed target from the current status.
- [ ] `--instance` missing on an instance machine and supplied on a plain one both exit 1 with distinct messages.
- [ ] The unknown-playbook, unknown-state and no-`states:` cases each exit 1 with a message naming what was missing.

## Verify

```
cd booping-python && uv run pytest e2e -k playbook-transition
```

Every case passes without `--txtar-update`, and a follow-up `--txtar-update` run leaves the working tree clean.
