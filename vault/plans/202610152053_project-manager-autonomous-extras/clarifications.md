# Clarifications

Autonomous run — the owner was unavailable; every question below was settled by the run with a default.

## C1 — part (2), linking a repo-pointed specs tier — answered

**Asked:** 2026-10-15 — intake

**Question:** setup should link a repo-directory specs tier into the vault (adr/0001). What is missing?

**Answer:**

Nothing in code. `booping-python/src/booping/specs/init.py` `plan()` plans the `{vault}/specs` symlink whenever the project tier resolves outside the vault, `playbooks/setup/setup-project/` runs `booping specs init --tier project` (step 7), `src/specs/README.md`'s tier table documents it, and e2e cases `init-project-tier-outside-vault-creates-repo-specs-and-links-it` and `init-a-repo-tier-beside-an-in-repo-vault-is-linked` hold it. The parent plan reached the same finding (its C2). Part (2) needs no milestone; the docs milestone only checks the setup page names the link.

## C2 — one plan or a split — answered

**Asked:** 2026-10-15 — intake

**Question:** Part (1) plus docs in one plan, or split?

**Answer:**

One plan — part (2) carries no work (C1) and part (3) is the docs of part (1). A split is reconsidered at draft-plan if the total passes 35 SP.
