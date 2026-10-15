---
title: "Project specs tier at the vault root — tier resolution, booping's records
  moved, migration"
type: "feature"
status: in-progress
sp: 29
related_to: null
created: 2026-10-15 17:27
planned: null
started: 2026-10-15 17:46
completed: null
code_reviews: []
sessions:
- 0de1a11b-6029-434b-9646-dec9c019459b
- 313e7b6b-ed34-4cef-9fbc-32cff672c444
retro: null
summary: Project specs tier defaults to the vault root; check reads type dirs 
  only; init links repo tiers; migration 005 moves vaults
commit: e609badcd1d877d0899e1d1eadd32eca2035d7b8
tracker_provider: null
tracker_request: null
tracker_issue: null
return_to: null
agents:
  research-codebase: ac9bca6adbbf5e8ab
  cross-review: ac2fc748a8cbc7c52
reviewed_at: 2026-10-15 17:41
---

# Project specs tier at the vault root — tier resolution, booping's records moved, migration

## Context

`booping specs` resolves the project tier from `core.specs.tiers.project.path`; null today means `{vault}/specs` for an in-repo vault, else repo `specs/`, and booping's own project records live in `vault/specs/{type}/`. [adr/0001](../../specs/adr/0001-specs-tiers.md) (amended 2026-10-15) and [adr/0028](../../specs/adr/0028-one-project-manager.md) move the project tier to the vault root: type directories beside `plans/`, no `specs/` in between, a repo directory as the opt-in exception linked into the vault. After this plan a null path resolves to the vault; `specs check`, `ls`, `next`, `site` and `open-items scan` at a vault-rooted tier read only type directories and ignore the rest of the vault; `specs init` creates nothing for the default tier and links a repo tier into the vault as `{vault}/specs`; migration 005 moves existing vaults; booping's own records sit at `vault/{type}/`. Separately, the migrate survey's rendered summary states the always-asked uncommitted-work question ([adr/0027](../../specs/adr/0027-autonomy-modes.md)).

This is the first slice of a larger request (`request.md`); the project-manager parts are parked below, under Out of scope.

## Decisions

- **Default root**: null `path` with a vault → the vault itself, in-repo or not; no vault attached → `{repo}/specs`, as today — C13.
- **Reading a vault-rooted tier**: only directories named after a schema stem are record directories; every other directory and root-level file is skipped. A tier with a root of its own keeps the strict `layout` check (unknown directories, stray root files) — C4.
- **`specs init`**: vault-rooted → no action, the root printed alone; a tier root outside the vault → directory, README and the `{vault}/specs` link, in either vault placement; the last stdout line stays the root — C5, C6.
- **Migration 005**: five cases in order — repo-pointed left alone; old out-of-repo default (`{vault}/specs` a link, or a repo `specs/` with no link) pinned with an explicit `path`; `{vault}/specs/{type}/` moved with in-record links re-pointed by code; otherwise nothing — C7, C8, C9.
- **Booping's own vault**: migrated by applying migration 005 itself (dogfood); `vault/specs/README.md` becomes `vault/README.md` — C10, C11.
- **Snapshots**: the runner may accept drift that is exactly what M01, M08 and M09 describe (migrate survey row, docs playbook record paths, setup example line); any other drift stops the run — C12.

### Values in play

- [value/0011 Everything in one place](../../specs/value/0011-everything-in-one-place.md) — the reason for the move: Obsidian shows the records directly; a repo tier is linked in.
- [value/0003 Single source](../../specs/value/0003-single-source.md) — the default lives in `tiers.py` and the config comment; types come from the schema stems everywhere, never a hand list (migration, `commit-docs`).
- [value/0015 Deterministic where it can be](../../specs/value/0015-deterministic-where-it-can-be.md) — the migration's link re-pointing is a code block, not model editing.
- [value/0010 Proven to work](../../specs/value/0010-proven-to-work.md) — strict `layout` kept wherever it does not collide with the vault; migration 005 proven on booping's own ~60 records; every behaviour held by a txtar case.
- [value/0004 Analysable history](../../specs/value/0004-analysable-history.md) — plans, retros and reviews keep their links as written; the migration lists inbound links, never rewrites them.

### Departures

- [rule/0019](../../specs/rule/0019-driver-owns-vault-workers-own-code.md) (driver owns the vault): M07 and M08 have a worker move and edit files under `vault/`. In this repo `vault/` is checked-in dogfood edited by workers before (plan 202610142247 M06), and the request asks the move as repo work — C11.
- [rule/0013](../../specs/rule/0013-snapshot-baselines-accepted-by-user.md) (baselines accepted by the user): the runner accepts the described drift under the owner's standing permission of 2026-10-14 for this feature, logging each accepted report in `develop-defaults.md` — C12.

## Architecture

`tiers.py` resolves every tier and builds the `Tier` objects; the project tier gains `vault_rooted`. `records.load_tier` and `check.check_tier` are the only readers of a tier's directory tree, so every `booping specs` subcommand and the open-items scan follow them; rule injection (`rules.py`) reads `{root}/rule` and is untouched. `specs/init.py` is the only writer of the tier skeleton and the `{vault}/specs` link; the setup playbook's step 7 calls it unchanged. Migration 005 is plugin-shipped prose applied by `/playbook migrate`, which owns its commit and the watermark; the hermetic fixture's `.booping` watermark follows so committed reports stay current.

## Milestones

| id | title | sp | status |
| --- | --- | --- | --- |
| 01 | [Migrate survey summary always asks about uncommitted work](milestones/M01-migrate-survey-summary-always-asks/M01-migrate-survey-summary-always-asks.md) | 1 | done |
| 02 | [Project tier default resolves to the vault root](milestones/M02-project-tier-default-is-the-vault-root/M02-project-tier-default-is-the-vault-root.md) | 3 | done |
| 03 | [E2E fixtures seed project records at the vault root](milestones/M03-e2e-fixtures-at-the-vault-root/M03-e2e-fixtures-at-the-vault-root.md) | 3 | done |
| 04 | [A vault-rooted tier reads only type directories](milestones/M04-vault-rooted-tier-reads-only-type-directories/M04-vault-rooted-tier-reads-only-type-directories.md) | 4 | done |
| 05 | [specs init — nothing at the vault root, a repo tier linked into the vault](milestones/M05-specs-init-links-a-repo-tier-into-the-vault/M05-specs-init-links-a-repo-tier-into-the-vault.md) | 4 | in-progress |
| 06 | [Migration 005 — project specs move to the vault root](milestones/M06-migration-005-project-specs-to-vault-root/M06-migration-005-project-specs-to-vault-root.md) | 4 | pending |
| 07 | [Booping's own records move to the vault root](milestones/M07-booping-records-move-to-the-vault-root/M07-booping-records-move-to-the-vault-root.md) | 3 | pending |
| 08 | [Repo references follow the move](milestones/M08-repo-references-follow-the-move/M08-repo-references-follow-the-move.md) | 4 | pending |
| 09 | [Shipped specs guide and public docs](milestones/M09-shipped-guide-and-public-docs/M09-shipped-guide-and-public-docs.md) | 3 | pending |

## I/O contract

- **`booping specs init --tier project`**: stdout — one action line per change (`created dir {path}`, `created file {path}`, `linked {path} -> {target}`, as today), then the absolute tier root as the last line; default tier → the root line alone. stderr — the refusal message. Exit `0` success, non-zero on a refused `{vault}/specs` (unchanged codes).
- **`booping specs check|ls|next|site --tier project`**: output shapes unchanged; a vault-rooted tier simply yields no record or finding for non-type content.
- **Migration 005 report**: one line per action — `moved {vault}/specs/{type} -> {vault}/{type}`, `re-pointed {n} links in {file}`, `pinned: core.specs.tiers.project.path = {path}`, `left alone: path {value}`, `left in place: {path}`, `inbound link: {file}:{line}`, or `nothing to move`.

## Final Verification

- [ ] `just ci` green, run to completion.
- [ ] `just snapshots` drift limited to: the `survey` row of `playbooks/migrate/_reports/output.md` (M01), record paths in `vault/_playbooks/docs/_reports/output.md` (M08), the setup example line in `playbooks/setup/_reports/output.md` if rendered there (M09); accepted and listed in `develop-defaults.md`.
- [ ] `bin/booping specs init --tier project` in this repo prints `/home/…/vault` alone and writes nothing.
- [ ] `bin/booping render-playbook groom` prints no migration notice (marker at 5).
- [ ] Help text unchanged — no flag added or removed.

## Out of scope

- Parked siblings of this request, each groomed in its own run after this plan: (1) item model for user requests + `booping items add`; (2) computed status report; (3) run registry + `booping run groom|develop`; (4) the `project-manager` playbook, supervised and autonomous; (5) project-manager docs. Part (5)'s setup link lands here, through `specs init`.
- Rewriting links in plans, retros, reviews and other history artefacts.
- Moving a repo-pointed tier into the vault.
- Intake channels, duplicate merging, tracker integrations (adr/0028 — not core).

## CLAUDE.md impact

`Commands` (`just specs-check` line), `Config` (`core.specs` tiers — the project default), `Layout`/`Vault` (booping's project tier at `vault/`'s type directories) — M08 task 8.1.
