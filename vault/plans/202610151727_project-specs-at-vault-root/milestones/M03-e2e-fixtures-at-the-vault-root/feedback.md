# Feedback

**Blocked (1/2)**: `## Verify` red — `just e2e -k 'not init- and not check-layout'` → 452 passed, 1 failed.

- Checked: worker report plus the working tree. The sed pass over the 40 listed cases and the two hand fixes (core tier pointed at `~/../cwd/vault`) are in place.
- Wrong: `booping-python/e2e/cases/specs/ls-on-a-missing-tier-directory-is-rejected.txtar` still expects `error: no specs for tier project at {CWD}/vault/specs`, exit 1. Under M02's default the project tier is the vault itself, which exists, so `ls` exits 0 with no output. The case seeds nothing under `vault/specs`, so it was not in the grep list, but it is one of this milestone's fixtures following the default.
- Next attempt: keep the case asserting what its name says — `ls` on a missing tier directory is rejected. Pin `core.specs.tiers.project.path` in the case's vault config to a directory that does not exist (e.g. `specs`, a repo-pointed tier) and update the expected error path to match. Do not delete the case or drop the assertion. Then re-run M03's `## Verify` and also `just e2e` in full; both must be green.
