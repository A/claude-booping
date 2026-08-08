---
id: 5
title: Session metrics reach the sprints view
summary: Add the `active_minutes` and `models` columns to the `sprints.md` Bases fence so the new plan metrics are visible.
---

# Session metrics reach the sprints view

A plan now records how much active work went into it: `active_minutes:` (whole minutes summed
across the plan's stamped Claude Code sessions) and `models:` (the distinct model ids that ran
them). Both are stamped by the develop playbook when a plan closes.

The vault's `sprints.md` Bases fence was seeded before those keys existed, so its table shows
neither. The vault scaffold now seeds them for new vaults; this migration adds them to the fence
an existing vault already has.

## What to convert

Only `sprints.md` at the vault root, and only the `order:` list of each view inside its `base`
fence. Nothing else in the file is touched — formulas, properties, filters, sort, and any prose
around the fence stay verbatim.

| Fence on entry | Conversion |
|---|---|
| a view whose `order:` has neither column | both appended, in the order `active_minutes`, `models` |
| a view whose `order:` has one of them | only the missing one appended |
| a view whose `order:` has both | untouched |

- No `sprints.md`, or no `base` fence in it, means there is nothing to do — report that as
  success. Re-running this migration on a converted vault changes nothing.
- A view without an `order:` list is left alone: an order-less Bases view shows every property
  already, so there is nothing to add.
- A vault that has hand-edited the fence keeps its own column order; the two new names are
  appended at the end, never re-sorted into place.

## Commands

Run from the vault root. First look at what is there:

```bash
cat sprints.md 2>/dev/null || echo "no sprints.md in this vault"
```

Then add the columns. The script is a `ruamel.yaml` round-trip over the fence body only, so
quoting and comments inside it survive; it writes nothing when every view already lists both:

```bash
uv run --quiet --with ruamel.yaml python - <<'PY'
import re
from io import StringIO
from pathlib import Path

from ruamel.yaml import YAML

COLUMNS = ["active_minutes", "models"]
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

    added = False
    for index, view in enumerate(views):
        if not isinstance(view, dict) or not isinstance(view.get("order"), list):
            continue
        name = view.get("name") or f"view {index}"
        for column in COLUMNS:
            if column in view["order"]:
                continue
            view["order"].append(column)
            report.append(f"{name}: added {column}")
            added = True

    if not added:
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
    print("every view already lists active_minutes and models - nothing to do")
    raise SystemExit(0)

path.write_text(converted)
for line in report:
    print(line)
PY
```

Confirm the result — the rewritten fence, then a check that both names are in it:

```bash
cat sprints.md 2>/dev/null
for column in active_minutes models; do
  grep -qF "$column" sprints.md 2>/dev/null \
    && echo "sprints.md lists $column" \
    || echo "STILL MISSING: $column is not in sprints.md"
done
```

Any `FAILED:` line, any `STILL MISSING:` line, or a `left as is` line is a failure to report: name
what blocked it so the user can add the columns by hand. A second run of the script must print
`every view already lists active_minutes and models - nothing to do`.
