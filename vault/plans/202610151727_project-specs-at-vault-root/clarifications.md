# Clarifications

## C1 — splitting the request — answered

**Asked:** 2026-10-15 — intake

**Question:** The request spans parts (0)–(6), well past the 35 SP split threshold. Which slice does this plan carry?

**Answer:**

Default (autonomous run): parts (0) and (6) — the seam the request names ("Do this part FIRST"). Parts (1)–(5) are parked siblings listed in `index.md` Out of scope, each groomed in its own run.

## C2 — setup linking the specs into the vault — answered

**Asked:** 2026-10-15 — intake

**Question:** Part (5)'s "setup links `<vault>/specs` to the repo's specs" and part (6)'s "setup links it into the vault" are one mechanism. Where does it land?

**Answer:**

Default: here, in `booping specs init` (M05), which setup step 7 already calls — code, not model steps (value/0015). Part (5)'s project-manager docs stay parked.

## C3 — task type — answered

**Asked:** 2026-10-15 — intake

**Question:** Feature or refactoring?

**Answer:**

Default: `feature` — users' records move and the resolved tier path changes, so "no user-visible behaviour change" fails.

## C4 — strict layout check outside the vault — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** Should every tier read only known type directories, or only a tier rooted at the vault?

**Answer:**

Default: only a vault-rooted tier. Core, global and repo-pointed tiers keep reporting unknown directories and stray root files — the check that catches a mistyped type directory stays wherever it does not collide with the vault (value/0010).

## C5 — specs init on the default tier — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** What does `specs init --tier project` create when the tier is the vault root — a README at the vault root?

**Answer:**

Default: nothing. The vault root's README is the project's own business; init prints the root alone so callers reading the last line keep working.

## C6 — when the vault link is made — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** Today the `{vault}/specs` link exists only for an out-of-repo vault. With a repo-pointed tier, when is it made?

**Answer:**

Default: whenever the tier root lies outside the vault — in-repo vault or not — under the existing name `{vault}/specs`.

## C7 — vaults on the old out-of-repo default — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** A vault outside its repo had its project tier at repo `specs/` by default. Move those records into the vault, or keep them where they are?

**Answer:**

Default: keep them — migration 005 pins `core.specs.tiers.project.path` in the vault config to where the old default put them, making it the repo-pointed tier the request says to leave alone; the existing link keeps Obsidian's view.

## C8 — a type directory already at the vault root — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** What if `{vault}/{type}` already exists when migration 005 would move `{vault}/specs/{type}` there?

**Answer:**

Default: the migration fails before moving anything and names each collision — no merge of two record sets by a migration.

## C9 — leftovers and inbound links — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** What happens to non-type content left in `{vault}/specs/`, and to links from other vault files into the moved records?

**Answer:**

Default: leftovers stay in place and are listed; `{vault}/specs` is removed only when empty. Inbound links are listed, not rewritten — history artefacts stay as written (value/0004). Links inside the moved records are re-pointed by code.

## C10 — booping's vault/specs/README.md — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** Where does `vault/specs/README.md` go once the type directories leave `vault/specs/`?

**Answer:**

Default: `vault/README.md`, rewritten for its place (the tier is the vault root's type directories; links one level shallower).

## C11 — workers editing booping's own vault — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** rule/0019 gives the vault to the driver. Who moves booping's records and fixes the vault-side references?

**Answer:**

Default: a worker, by applying migration 005 (M07) and editing the docs playbook (M08) — booping's `vault/` is checked-in dogfood edited by workers before (plan 202610142247 M06), and the move is repo work the request asks for. Flagged as a departure in `index.md`.

## C12 — accepting snapshot drift — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** rule/0013 reserves baseline acceptance for the user. Does the develop runner accept this plan's drift?

**Answer:**

Per the owner's standing permission for this feature (2026-10-14, restated in the request): the runner accepts drift only when every hunk is one the plan describes — the migrate survey row, docs-playbook record paths, the setup example line — and lists each accepted report in `develop-defaults.md`. Any other drift stops the run.

## C13 — no vault attached — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** What does a null project path resolve to with no vault attached?

**Answer:**

Default: `{repo}/specs`, unchanged — the vault-root default needs a vault.
