---
id: "04"
title: "Playbooks, docs and CLAUDE.md on booping items"
sp: 4
status: done
plan: "plans/202610151825_user-request-items/index.md"
---

# M04: Playbooks, docs and CLAUDE.md on booping items

Every prompt, manifest, fixture and doc that drives or describes the item store names `booping items`, and the public docs tell a user how to file a request item from any channel.

**Scope**: text only, no code.

- Playbooks: `playbooks/specs/playbook.md` (line 29), `playbooks/specs/playbook.yaml` (the comment and the five `when:` strings), `playbooks/specs/guide/prompt.md` (every `open-items` verb, and `--body` → `--text`), the guide's eval fixtures `playbooks/specs/guide/_fixtures/{autonomous-open-items,record-decision,what-is-open}.md` and `playbooks/specs/guide/tests.yaml` wherever they name the command or a flag; `playbooks/groom/intake/fable-5.md` (line 30, `booping items plan {ids} --plan {plan-dir}/index.md`).
- Public docs (audience: a booping user — the commands they type and what an item holds; no internal module names, no history of the rename): `documentation/specs_playbook.md` (the open-items section: the command is `booping items`; an item's `source` adds `request` and `backlog`; a request item holds the user's words verbatim with no direction; `booping items add --text -` reads stdin, so any channel — a script, a bridge — can file one; the `source` column in `list`), `documentation/specs.md:35`, `documentation/project_config.md:287` (index columns now include `source`), `README.md:155`.
- `CLAUDE.md`: line 17 — `items` (`add`, `list`, `plan`, `close`, `reopen`, `scan`) joins the subcommand list and `specs` loses `open-items`; line 48 — `open_items` is the item store `booping items` lists; line 78 — the open-items track is moved only by `booping items`, and the reconcile is `booping items close|reopen --plan`; the track names user requests beside spec gaps.

The vault record `vault/adr/0025-open-items-are-an-index.md` and the committed reports `playbooks/{groom,specs}/_reports/output.md` are the runner's, not this milestone's.

Tests: none — prose only; the grep in Verify is the check.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Playbook manifests, prompts, eval fixtures and suite. | `playbooks/specs/playbook.md`, `playbooks/specs/playbook.yaml`, `playbooks/specs/guide/prompt.md`, `playbooks/specs/guide/_fixtures/*.md`, `playbooks/specs/guide/tests.yaml`, `playbooks/groom/intake/fable-5.md` | 2 | done |
| 4.2 | Public docs, README and CLAUDE.md. | `documentation/specs_playbook.md`, `documentation/specs.md`, `documentation/project_config.md`, `README.md`, `CLAUDE.md` | 2 | done |

## Definition of Done

### Task 4.1

- [x] No playbook file names `specs open-items` or `--body`.
- [x] `bin/booping render-playbook specs` and `bin/booping render-playbook groom` print no `STOP` notice.

### Task 4.2

- [x] `documentation/specs_playbook.md` documents `booping items add` with `--text -`, the `request` and `backlog` sources and the null direction, in user terms only.
- [x] `CLAUDE.md` lines 17, 48 and 78 read as Scope states.

Return: the list of changed files, nothing else.

## References

- `documentation/specs_playbook.md` — the section being rewritten; keep its voice.

## Verify

`! grep -rn -e "specs open-items" -e "open-items add.*--body" playbooks documentation README.md CLAUDE.md src --include='*.md' --include='*.yaml' --include='*.j2' | grep -v "/_reports/"`
