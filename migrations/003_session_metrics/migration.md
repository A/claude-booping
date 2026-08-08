---
id: 3
title: Session metrics live in flat `metrics_` frontmatter and the sprints view
summary: Rename `active_minutes` → `metrics_active_minutes` and `models` → `metrics_models` on every plan, and rewrite the `sprints.md` Bases fence to the six `metrics_*` columns.
---

# Session metrics live in flat `metrics_` frontmatter and the sprints view

`booping session-stats` replaces `session-time` and records four token totals beside the two keys a
plan already carried. All six live in flat, `metrics_`-prefixed frontmatter — Obsidian Properties
and Bases cannot address a nested YAML mapping as a column, which is the whole reason the keys
exist:

`metrics_active_minutes`, `metrics_models`, `metrics_tokens_input`, `metrics_tokens_output`,
`metrics_tokens_cache_creation`, `metrics_tokens_cache_read`.

This migration renames the two keys already stamped and puts all six in the sprints view. It does
not compute anything: the four token keys appear on a plan only when `session-stats` next runs
over it.

## What to convert

Two things, independently:

| Where | Conversion |
|---|---|
| `plans/*/index.md` frontmatter | `active_minutes:` → `metrics_active_minutes:`, `models:` → `metrics_models:`, values preserved verbatim; an old key whose prefixed twin is already present is dropped instead of renamed |
| `sprints.md`, the `order:` list of each view in the `base` fence | `active_minutes` / `models` renamed in place, then any of the six `metrics_*` columns still missing appended |

- A plan already carrying only `metrics_active_minutes` / `metrics_models` is left alone, and so is
  a plan that never carried either. Only the frontmatter block is touched — body prose that happens
  to mention the old names is not.
- A plan carrying **both** an old key and its prefixed twin — what `booping session-stats` leaves
  behind when it runs before this migration — keeps the prefixed key and drops the old one, line
  and multi-line value together, rather than renaming into a duplicate YAML key. The stamped
  `metrics_*` value is the authoritative one: it was computed by the new algorithm.
- A view whose `order:` already lists the six columns is untouched. A view without an `order:` list
  is left alone: an order-less Bases view shows every property already.
- A vault that has hand-edited the fence keeps its own column order — renames happen in place and
  the missing token columns are appended at the end, never re-sorted.
- No `plans/`, no `sprints.md`, or no `base` fence in it means there is nothing to do — report that
  as success. Re-running this migration on a converted vault changes nothing.

## Commands

Run from the vault root. First look at what is there:

```bash
grep -l -E '^(active_minutes|models):' plans/*/index.md 2>/dev/null || echo "no plan carries the old keys"
cat sprints.md 2>/dev/null || echo "no sprints.md in this vault"
```

Then rename the plan keys. The rewrite is anchored to the frontmatter block and to a line start, so
list values, quoting and every other key survive byte for byte:

```bash
uv run --quiet python - <<'PY'
import re
from pathlib import Path

RENAMES = {"active_minutes": "metrics_active_minutes", "models": "metrics_models"}
FRONTMATTER = re.compile(r"\A---\n(?P<body>.*?)(?P<close>\n---\n)", re.S)


def index_of(lines, key):
    for position, line in enumerate(lines):
        if line.startswith(f"{key}:"):
            return position
    return None


def drop(lines, position):
    # A value may span lines: take the continuation too, stopping at the next key at column 0.
    end = position + 1
    while end < len(lines) and lines[end][:1] in (" ", "\t", "-"):
        end += 1
    del lines[position:end]


report = []
for path in sorted(Path("plans").glob("*/index.md")) if Path("plans").is_dir() else []:
    text = path.read_text()
    match = FRONTMATTER.match(text)
    if not match:
        report.append(f"NO FRONTMATTER: {path}")
        continue
    lines = match.group("body").split("\n")
    changed = []
    for old, new in RENAMES.items():
        position = index_of(lines, old)
        if position is None:
            continue
        if index_of(lines, new) is None:
            lines[position] = f"{new}:" + lines[position][len(old) + 1 :]
            changed.append(f"{old} -> {new}")
        else:
            drop(lines, position)
            changed.append(f"dropped duplicate {old}")
    if not changed:
        continue
    path.write_text("---\n" + "\n".join(lines) + match.group("close") + text[match.end() :])
    report.append(f"{path}: {', '.join(changed)}")

if not report:
    print("no plan carries the old keys - nothing to do")
else:
    for line in report:
        print(line)
PY
```

Then the sprints view. The script is a `ruamel.yaml` round-trip over the fence body only, so
quoting and comments inside it survive; it writes nothing when every view already lists the six:

```bash
uv run --quiet --with ruamel.yaml python - <<'PY'
import re
from io import StringIO
from pathlib import Path

from ruamel.yaml import YAML

RENAMES = {"active_minutes": "metrics_active_minutes", "models": "metrics_models"}
COLUMNS = [
    "metrics_active_minutes",
    "metrics_models",
    "metrics_tokens_input",
    "metrics_tokens_output",
    "metrics_tokens_cache_creation",
    "metrics_tokens_cache_read",
]
# Spelled from a variable so this script can itself live inside a fenced block.
TICKS = "`" * 3
FENCE = re.compile(
    rf"^(?P<open>[ \t]*{TICKS}base[ \t]*\n)(?P<body>.*?)(?P<close>^[ \t]*{TICKS}[ \t]*$)",
    re.S | re.M,
)

path = Path("sprints.md")
if not path.is_file():
    print("no sprints.md in this vault - nothing to do")
    raise SystemExit(0)

yaml = YAML()
yaml.preserve_quotes = True
yaml.width = 4096
yaml.indent(mapping=2, sequence=4, offset=2)

report = []


def convert(match):
    body = match.group("body")
    try:
        data = yaml.load(body)
    except Exception as exc:
        report.append(f"FAILED: base fence is not valid YAML - {exc}")
        return match.group(0)
    if not isinstance(data, dict):
        report.append("FAILED: base fence is not a YAML mapping")
        return match.group(0)

    views = data.get("views")
    if not isinstance(views, list):
        report.append("no views in the base fence - left as is")
        return match.group(0)

    touched = False
    for index, view in enumerate(views):
        if not isinstance(view, dict) or not isinstance(view.get("order"), list):
            continue
        name = view.get("name") or f"view {index}"
        order = view["order"]
        for position in range(len(order) - 1, -1, -1):
            column = order[position]
            if column not in RENAMES:
                continue
            target = RENAMES[column]
            if target in order:
                del order[position]
                report.append(f"{name}: dropped duplicate {column}")
            else:
                order[position] = target
                report.append(f"{name}: renamed {column} -> {target}")
            touched = True
        for column in COLUMNS:
            if column in order:
                continue
            order.append(column)
            report.append(f"{name}: added {column}")
            touched = True

    if not touched:
        return match.group(0)

    buf = StringIO()
    yaml.dump(data, buf)
    return match.group("open") + buf.getvalue() + match.group("close")


text = path.read_text()
converted, count = FENCE.subn(convert, text)
if not count:
    print("no base fence in sprints.md - nothing to do")
    raise SystemExit(0)

if any(line.startswith("FAILED:") for line in report):
    for line in report:
        print(line)
    raise SystemExit(1)

if converted == text:
    print("every view already lists the six metrics_ columns - nothing to do")
    raise SystemExit(0)

path.write_text(converted)
for line in report:
    print(line)
PY
```

## Verify

```bash
grep -n -E '^(active_minutes|models):' plans/*/index.md 2>/dev/null \
  && echo "STILL OLD: the lines above keep an unprefixed key" \
  || echo "no plan carries the old keys"
grep -c -E '^metrics_(active_minutes|models):' plans/*/index.md 2>/dev/null
awk 'FNR==1{n=0} /^---$/{n++; next} n==1 && /^metrics_(active_minutes|models):/{seen[FILENAME" "$1]++} END{d=0; for (k in seen) if (seen[k] > 1) {print "DUPLICATE: " k; d=1} if (!d) print "every plan carries each metrics_ key at most once"}' plans/*/index.md 2>/dev/null
cat sprints.md 2>/dev/null
for column in metrics_active_minutes metrics_models metrics_tokens_input metrics_tokens_output metrics_tokens_cache_creation metrics_tokens_cache_read; do
  grep -qF "$column" sprints.md 2>/dev/null \
    && echo "sprints.md lists $column" \
    || echo "STILL MISSING: $column is not in sprints.md"
done
```

Any `FAILED:`, `STILL OLD:`, `STILL MISSING:`, `DUPLICATE:`, `NO FRONTMATTER:` or `left as is` line
is a failure to report: name what blocked it so the user can finish by hand. A plan that carried
both an old key and its prefixed twin ends with exactly one of each prefixed key. A second run of
both scripts must print `no plan carries the old keys - nothing to do` and `every view already
lists the six metrics_ columns - nothing to do`, writing nothing.
