---
id: 2
title: Config settings move under `core`
summary: Rewrite a vault `config.yaml` onto the `core.*` namespace and drop the retired `skills:` and `plan:` blocks.
---

# Config settings move under `core`

Every setting the shipped playbook set owns now lives under one top-level `core:` key. `home_dir`
is the only other top-level key, because it resolves the vault before any namespace is reachable.
A key one playbook owns sits at `core.{name}_playbook`; a key several playbooks share sits directly
under `core`. The `skills:` block is gone with the skills it configured, and the shared `plan:`
lifecycle is gone with the `transition` command that read it.

A config left on the old paths is not an error — it merges as dead weight, and every key it meant
to override silently stops overriding. This migration rewrites those paths.

## What to convert

Only `config.yaml` at the vault root. Nothing else in the vault carries config paths.

| Old path | New path |
|---|---|
| `home_dir` | unchanged |
| `research_agent` | `core.research_agent` |
| `macros` | `core.macros` |
| `sprint` | `core.sprint` |
| `tasks` | `core.task_types` |
| `plans` | `core.plans` |
| `git` | `core.develop_playbook.git` |
| `migrations.pending` | `core.migrate_playbook.queries.pending` |
| `playbook.scaffold` | `core.playbook_authoring_playbook.scaffold` |
| `vault.scaffold` | `core.setup_playbook.scaffold` |
| `core.cross_review_agent` | `core.groom_playbook.cross_review_agent` |
| `skills.groom` | `core.groom_playbook` |
| `skills.develop` | `core.develop_playbook` |
| `skills.retro` | `core.retro_playbook` |
| `skills.learn` | `core.learn_playbook` |
| `skills.code-review` | `core.code_review_playbook` |

Dropped outright, because what read them is gone: `skills.chat`, `skills.help`, `skills.playbook`
and the whole `plan:` block. A container left empty by the move (`skills`, `migrations`,
`playbook`, `vault`) goes with it.

A `skills.<name>.agents.<id>` block registering an external agent survives the move intact — only
its path changes, e.g. `skills.code-review.agents.plannotator-reviewer` becomes
`core.code_review_playbook.agents.plannotator-reviewer`.

- No `config.yaml` in the vault, or one already on the new paths, means there is nothing to do —
  report that as success. Re-running this migration changes nothing.
- A key that already exists at its destination is **kept**, and the old value is reported as
  discarded rather than overwriting it.
- Values are moved verbatim; only the path and the indentation change. Comments are preserved by
  the round-trip, but one attached to a moved key can end up beside its old neighbour — read the
  rewritten file once and re-place any comment that landed wrong.

## Commands

Run from the vault root. First look at what is there:

```bash
cat config.yaml 2>/dev/null || echo "no config.yaml"
```

Then rewrite it. The script is a `ruamel.yaml` round-trip, so quoting, block scalars and comments
survive; it writes nothing when no old path is present:

```bash
uv run --quiet --with ruamel.yaml python - <<'PY'
from pathlib import Path

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

MOVES = [
    ("research_agent", "core.research_agent"),
    ("macros", "core.macros"),
    ("sprint", "core.sprint"),
    ("tasks", "core.task_types"),
    ("plans", "core.plans"),
    ("git", "core.develop_playbook.git"),
    ("migrations.pending", "core.migrate_playbook.queries.pending"),
    ("playbook.scaffold", "core.playbook_authoring_playbook.scaffold"),
    ("vault.scaffold", "core.setup_playbook.scaffold"),
    ("core.cross_review_agent", "core.groom_playbook.cross_review_agent"),
    ("skills.groom", "core.groom_playbook"),
    ("skills.develop", "core.develop_playbook"),
    ("skills.retro", "core.retro_playbook"),
    ("skills.learn", "core.learn_playbook"),
    ("skills.code-review", "core.code_review_playbook"),
]
DROPS = ["skills.chat", "skills.help", "skills.playbook", "plan"]
PRUNE = ["skills", "migrations", "playbook", "vault"]

path = Path("config.yaml")
if not path.is_file():
    print("no config.yaml in this vault - nothing to do")
    raise SystemExit(0)

yaml = YAML()
yaml.preserve_quotes = True
yaml.width = 4096
yaml.indent(mapping=2, sequence=4, offset=2)
data = yaml.load(path.read_text())
if not isinstance(data, dict):
    print(f"FAILED: {path} is not a YAML mapping")
    raise SystemExit(1)

report = []


def pop(node, dotted):
    head, _, rest = dotted.partition(".")
    if not isinstance(node, dict) or head not in node:
        return None, False
    if not rest:
        return node.pop(head), True
    return pop(node[head], rest)


def merge(dest, src, prefix):
    for key, value in src.items():
        if key not in dest:
            dest[key] = value
        elif isinstance(dest[key], dict) and isinstance(value, dict):
            merge(dest[key], value, f"{prefix}.{key}")
        else:
            report.append(f"kept existing {prefix}.{key} - moved value discarded")


def put(node, dotted, value):
    head, _, rest = dotted.partition(".")
    if rest:
        if not isinstance(node.get(head), dict):
            node[head] = CommentedMap()
        put(node[head], rest, value)
    elif head not in node:
        node[head] = value
    elif isinstance(node[head], dict) and isinstance(value, dict):
        merge(node[head], value, dotted)
    else:
        report.append(f"kept existing {dotted} - moved value discarded")


for old, new in MOVES:
    value, found = pop(data, old)
    if found:
        put(data, new, value)
        report.append(f"{old} -> {new}")

for dotted in DROPS:
    if pop(data, dotted)[1]:
        report.append(f"dropped {dotted}")

for key in PRUNE:
    if isinstance(data.get(key), dict) and not data[key]:
        del data[key]
        report.append(f"dropped empty {key}")

if not report:
    print("no renamed keys present - nothing to do")
    raise SystemExit(0)

yaml.dump(data, path)
for line in report:
    print(line)
PY
```

Confirm the result — the rewritten file, then a check that no old path survives:

```bash
cat config.yaml 2>/dev/null
grep -nE '^(research_agent|macros|sprint|tasks|plans|git|migrations|playbook|vault|skills|plan):' config.yaml 2>/dev/null \
  && echo "STILL OLD: the paths above were not converted" || echo "no old top-level paths remain"
```

Any `FAILED:` line, any `STILL OLD:` line, or a `kept existing` line the user has not been told
about is a failure to report.

## The global config is a manual step

A machine-level config at `${XDG_CONFIG_HOME:-~/.config}/booping/config.yaml` uses the same paths
and needs the same rewrite, but it is not part of any vault — the `.booping` watermark is
per-vault and cannot gate a machine-level file, and one migration run must not rewrite a file
shared by every other project on the machine. **Do not edit it.** Check it and tell the user:

```bash
GLOBAL="${XDG_CONFIG_HOME:-$HOME/.config}/booping/config.yaml"
[ -f "$GLOBAL" ] && grep -nE '^(research_agent|macros|sprint|tasks|plans|git|migrations|playbook|vault|skills|plan):' "$GLOBAL" \
  || echo "global config absent or already converted"
```

When that grep prints lines, report them and the mapping table above: the user must move those
keys by hand into `core.*` in `$GLOBAL`, exactly as this migration did for the vault. Until they
do, every one of those keys is inert.
