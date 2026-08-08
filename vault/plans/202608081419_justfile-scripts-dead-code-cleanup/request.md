# Framing brief

**Request**

> groom: can you clean up justfile: move scripts like snapshots/accept etc into bin/ or scripts/ (idk if it should be along with product scripts). Also i want you to review codebase for orphaned/dead code, like create project script in bin, i guess it should be removed since we did the scaffold feature. I suggest you to spawn agents, like sonnet, which will read latest plans, understand track of the project, review codebase for dean and almost dead code, and do clean up to prepare for release.

**Task type**

`refactoring` — internal structure change with no user-visible behavior change: justfile recipes keep their names and semantics, script bodies move to files; dead code is removed, not changed. Not `feature`: no new user-facing capability is added. Not `bug`: nothing observed diverges from expected behavior — the justfile works, the dead code merely lingers.

**Problem**

The justfile carries three multi-line bash bodies inline (`mdcheck`, `snapshots`, `snapshots-render`), making it long and hard to scan; other recipes already delegate to `bin/*.sh` scripts. `bin/` mixes the product CLI wrapper (`booping`, `booping-create-project`) with dev-tooling scripts (`eval-*.sh`, `report-*.jq`), with no stated boundary. Suspected dead or orphaned code has accumulated across recent refactors (retro/code-review track splits, scaffold feature, learn-targets consolidation) — e.g. `bin/booping-create-project` may be superseded by the `booping scaffold` surface / setup playbook. The repo should be swept and cleaned before a release.

**Clarifications and Decisions**

- Inline justfile bash bodies (`mdcheck`, `snapshots`, `snapshots-render`) move into script files; recipes become thin delegating shells.
- New `scripts/` directory holds ALL dev tooling: the extracted bodies plus existing `eval-*.sh`, `eval-pr-comment.sh`, `report-*.jq` from `bin/`. `bin/` keeps only product entry points (`booping`).
- `bin/booping-create-project`: remove if research confirms the scaffold/setup surface covers it; its CLAUDE.md/docs mentions are cleaned in the same sprint.
- Dead-code sweep covers the whole repo: Python source, templates/partials, playbooks, docs references, bin scripts, config keys.
- Cleanup only — no release mechanics (no version bump, changelog, or release-skill involvement) in this plan.
- No post-implementation prose-shape reshape milestone needed (repo plumbing, gated by snapshots/mdcheck).
