---
id: "01"
title: "Questions on an item — booping items ask and answer"
sp: 4
status: done
plan: "plans/202610152006_project-manager-playbook/index.md"
---

# M01: Questions on an item — booping items ask and answer

`booping items ask` files a question on an item into `open-items/questions/{ID}.md` in the `docs/clarifications.md` format, and `booping items answer` records the answer and flips the question to `answered`.

**Scope**: create `booping-python/src/booping/specs/questions.py` — every read and write of a questions sidecar, nothing printed: `sidecar_path(ctx, item_id)` (`{vault}/{core.specs.open_items.dir}/questions/{id}.md`), a parser returning the questions in file order (`id`, `topic`, `state`, `answer` body), `is_answered(q)` implementing `docs/clarifications.md`'s answered test exactly (heading ends `answered` **and** the answer body has a non-blank line), `open_count(ctx, item_id)` (0 when no sidecar), `ask(...)` appending the next `C{n}` (numbered past the highest present, never reused) and `answer(...)` writing the body under `**Answer:**` and rewriting that heading's last segment. In `booping-python/src/booping/commands/items.py` add sub-verbs `ask` and `answer` with the flags, stdout and stderr the I/O contract in `index.md` locks; `ask` refuses an item whose status is `done` or `dropped` (`item {id} is {status}`); `--text -` reads stdin verbatim the way `add --text -` does; dates through `core.macros.date` as `add` renders `created_at`. Extend `docs/clarifications.md`'s opening paragraph by one sentence: the same format holds an item's questions at `open-items/questions/{id}.md`, written by `booping items ask|answer`.

Tests (integration tier, e2e corpus `booping-python/e2e/cases/items/`, expectations hand-derived, `core.macros.date` stubbed): ask on an open item creates the sidecar with the H1 and `C1`, options rendered as bullets; a second ask appends `C2`; answer from stdin keeps multi-line text verbatim and flips `C1` to answered; answer on an unknown question, an already-answered question, blank text, ask on a `done` item, unknown item → exit 1, the contract's message, files unchanged; `booping items list` still lists exactly the items (the `questions/` directory is not read as items).

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | `questions.py` sidecar module: parse, answered test, open count, ask, answer. | `booping-python/src/booping/specs/questions.py` | 2 | done |
| 1.2 | `items ask` / `items answer` sub-verbs; one sentence in the format doc. | `booping-python/src/booping/commands/items.py`, `docs/clarifications.md` | 1 | done |
| 1.3 | e2e cases above. | `booping-python/e2e/cases/items/ask-*.txtar`, `booping-python/e2e/cases/items/answer-*.txtar` | 1 | done |

## Definition of Done

### Task 1.1

- [x] The answered test treats `answered` over an empty body and a filled body under `open` both as open.
- [x] No sidecar path literal outside `sidecar_path`; the store directory comes from `core.specs.open_items.dir`.

### Task 1.2

- [x] `bin/booping items ask --help` and `bin/booping items answer --help` show the contract's arguments.
- [x] stdout and stderr lines equal the I/O contract.
- [x] `docs/clarifications.md` names the item sidecar in one sentence.

### Task 1.3

- [x] The cases above exist under `booping-python/e2e/cases/items/` and pass.

Return: the list of changed and created files, nothing else.

## References

- `booping-python/src/booping/defaults.py` — a sidecar writer with numbered entries and the date macro render.
- `booping-python/e2e/cases/items/add-request-from-stdin-keeps-the-text-verbatim.txtar` — case shape with stdin and a stubbed date.
- `docs/clarifications.md` — the format and the answered test.

## Verify

`cd booping-python && uv run pytest e2e/cases/items -q`
