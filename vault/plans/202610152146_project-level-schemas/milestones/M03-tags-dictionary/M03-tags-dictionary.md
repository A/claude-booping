---
id: "03"
title: "Tags dictionary — record tags checked against the tier's tags.yaml"
sp: 3
status: in-progress
plan: "plans/202610152146_project-level-schemas/index.md"
---

# M03: Tags dictionary — record tags checked against the tier's tags.yaml

`booping specs check` checks every record's `tags:` against the tier's `{tier root}/tags.yaml` when the tier has one.

**Scope**: new `booping-python/src/booping/specs/tags.py` — load `{tier.root}/tags.yaml` (absent → no check; not a mapping of string → string → one `tags` error on the file, line 1, `tags.yaml must map each tag to a one-line description`) and check one record's `tags:` frontmatter (absent → nothing; not a list of strings → `tags` error `tags must be a list of strings`). Per tag, first failure wins, errors in this order (C4): `tag {t} is not area[:sub] kebab-case` (regex `^[a-z0-9]+(-[a-z0-9]+)*(:[a-z0-9]+(-[a-z0-9]+)*)?$`), `tag {t} is not in tags.yaml`, `tag {t} needs its area {a} in tags.yaml`. `check.py` `check_tier` calls it per record, findings check kind `tags`, level error, line of the `tags:` key (or 1). Any tier, any type — whether a type requires `tags` stays its schema's business.

Tests (integration tier, `booping-python/e2e/cases/specs/`, hand-derived): a tier with `tags.yaml` `{ui: …, ui:hud: …, net: …}` and records tagged `[ui:hud]` (pass), `[audio]` (not in dictionary), `[Ui]` (not kebab), `[net:sync]` (not in dictionary), and a dictionary holding `combat:melee` without `combat` with a record tagged `[combat:melee]` (needs its area) — one case, the expected stdout listing each finding; a tier without `tags.yaml` passes the same `[audio]` record.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Dictionary load and per-record tag check. | `booping-python/src/booping/specs/tags.py`, `booping-python/src/booping/specs/check.py` | 2 | pending |
| 3.2 | The two e2e cases above. | `booping-python/e2e/cases/specs/check-tags-*.txtar` | 1 | pending |

## Definition of Done

### Task 3.1

- [ ] Each of the three messages and the malformed-dictionary error is produced exactly as worded above, finding format `{path}:{line}  error  tags  {message}`.
- [ ] A tier without `tags.yaml` produces no `tags` finding.

### Task 3.2

- [ ] The cases exist and pass.

Return: the list of changed and created files, nothing else.

## References

- `booping-python/src/booping/specs/check.py` — an existing per-record frontmatter check (`targets`) to copy the finding shape from.
- `/home/anton/Dev/@A/hermes-pet/specs/tags.yaml` and `/home/anton/Dev/@A/hermes-pet/specs/README.md` (read-only) — the dictionary shape and the `area:sub` convention.

## Verify

`cd booping-python && uv run pytest e2e/cases/specs -q -k tags`
