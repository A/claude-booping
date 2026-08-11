---
id: "01"
title: "txtar parser and case-format spec"
sp: 3
status: pending
plan: "plans/202608111422_e2e-contract-corpus-pilot/index.md"
---

# M01: txtar parser and case-format spec

**Goal**: the corpus case format exists — a vendored txtar parse/serialize module and the format spec a future Rust runner is built from.

**Scope**: new files only, under `booping-python/e2e/`. No CLI behavior touched. `index.md`'s Decisions and I/O contract sections define the format this milestone writes down.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Vendor a txtar module: `parse(text) -> Archive` (leading comment + ordered `(name, content)` sections, `-- name --` markers, trailing-newline rules per Go's spec) and `serialize(archive) -> str`, byte-exact roundtrip for any well-formed archive. Plain functions + a small dataclass, stdlib only. | `booping-python/e2e/_txtar.py` | 2 | pending |
| 1.2 | Write the case-format spec: section vocabulary (`cmd`, `exit`, `stdout`, `stderr`, `fixtures/{home\|xdg\|cwd}/**`, `expected/{home\|xdg\|cwd}/**`), sandbox mapping and env (`HOME`, `XDG_CONFIG_HOME`, cwd), multi-line `cmd` semantics (all lines but last must exit 0, `stdout` = concatenation), normalization tokens `{CWD}`/`{HOME}`/`{XDG}` and the `[..]` in-line wildcard, absent-section-not-asserted rule, runner exit codes, and the `--update` authoring loop. Content mirrors `index.md`'s Decisions/I/O contract — no new rules invented here. | `booping-python/e2e/README.md` | 1 | pending |

## Definition of Done

### Task 1.1

- [ ] `parse(serialize(a))` and `serialize(parse(t))` are byte-exact roundtrips, including leading comment, section order, and files with no trailing newline.
- [ ] A section name may contain `/` (paths like `fixtures/cwd/a/b.md`); duplicate section names are a `ValueError` naming the section.
- [ ] Module is stdlib-only and passes `ruff` and `basedpyright` under the project config.

### Task 1.2

- [ ] Every section name the runner accepts is specified with its assert semantics; unknown sections are specified as a hard error, not ignored.
- [ ] A complete worked example case (fixture + cmd + expected) is included and is copy-paste runnable once M02 lands.
- [ ] Spec states the language-neutrality contract: the file defines behavior, `run.py` is the reference implementation.

## Verify

```
cd booping-python && uv run ruff check e2e/ && uv run basedpyright e2e/
cd booping-python && uv run python -c "
from pathlib import Path
from e2e._txtar import parse, serialize
import re
example = re.search(r'\`\`\`txtar\n(.*?)\`\`\`', Path('e2e/README.md').read_text(), re.S).group(1)
assert serialize(parse(example)) == example, 'roundtrip mismatch'
print('roundtrip ok')
"
```

(the README wraps its worked example in a ```txtar fence so this check can extract it.)
