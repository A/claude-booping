---
id: "07"
title: "render-playbook --set overrides and the parse_set_overrides move"
sp: 2
status: pending
plan: "vault/plans/202608131129_remaining-cli-tests-to-e2e/index.md"
---

# M07: render-playbook --set overrides and the parse_set_overrides move

`--set` is pinned at the CLI by txtar cases, and its parser keeps unit coverage in the file that owns `booping.utils`.

**Scope**: the `--set KEY=VALUE` flag on `render-playbook`, and `parse_set_overrides` in `booping/utils.py`. Files: new `booping-python/e2e/cases/render-playbook/*.txtar`; edited `booping-python/tests/utils_test.py`; edited `booping-python/tests/test_render_playbook.py` (its `--set config overrides` section is emptied — the file itself is deleted in M08). This is the one place the migration draws the tier line inside a section: the parser is shared by `render`, `render-playbook` and `scaffold`, so its `ValueError` contract belongs to the library, while precedence over the config tiers is only observable through a render.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 7.1 | Move the five `parse_set_overrides` tests to `tests/utils_test.py` verbatim in intent — dotted key into a nested mapping, flat key whose value stays a string, value containing `=`, repeated pairs where the later wins, malformed pair raising — and delete them from the render-playbook file | `booping-python/tests/utils_test.py`, `booping-python/tests/test_render_playbook.py` | 1 | pending |
| 7.2 | Write the CLI cases: an override beating the core config value, repeated pairs where the later wins, an override reaching the `--step` surface, a malformed pair exiting 1, an absent flag leaving the merged config untouched, and `--help` documenting the flag | `booping-python/e2e/cases/render-playbook/*.txtar` | 1 | pending |

## Definition of Done

### Task 7.1

- [ ] `tests/utils_test.py` carries the five parser tests, importing `parse_set_overrides` from `booping.utils`, with no import of `booping.commands.render_playbook`.
- [ ] The malformed-pair test asserts the `ValueError` and its message, not an exit code.
- [ ] `uv run pytest tests/utils_test.py` passes and the `--set config overrides` section is gone from `tests/test_render_playbook.py`.

### Task 7.2

- [ ] A case whose fixture playbook renders a config value shows the core default, and its sibling with `--set` shows the overridden value — the same fixture, two cases.
- [ ] Repeated `--set` pairs on one invocation render the later value.
- [ ] `--set` reaches a `--step` render.
- [ ] A `--set` argument with no `=` exits 1, stdout empty, with a message naming the malformed pair.
- [ ] `booping render-playbook --help` output pins the `--set` entry.

## Verify

```
cd booping-python && uv run pytest e2e -k render-playbook && uv run pytest tests/utils_test.py
```

Both green; the corpus needs no `--txtar-update`.
