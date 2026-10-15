---
id: 5
title: Project specs move to the vault root
summary: Move a vault's project spec records from `{vault}/specs/{type}/` to `{vault}/{type}/` and re-point the links inside them; a project tier the old default placed elsewhere is pinned there with an explicit `path`.
---

# Project specs move to the vault root

The project specs tier's default root is now the vault itself: record type directories sit beside
`plans/`, with no `specs/` directory in between. A tier kept in the repo is the opt-in exception,
set by `core.specs.tiers.project.path` and linked into the vault as `{vault}/specs`. This migration
moves records the old default kept under `{vault}/specs/`, or pins the tier where the old default
put it outside the vault.

## Setup

Run every command from the repo root — the directory holding the `.booping` marker; `booping`
resolves the config from it. The blocks run in bash or zsh alike — word lists are split with
`$(echo $LIST)`, never a bare `$LIST`. `<vault>` is the vault path from your run-time context,
`<migration-dir>` this migration's directory.

```bash
export PLUGIN_ROOT="$(cd <migration-dir>/../.. && pwd)"
export VAULT="$(cd <vault> && pwd)"
export REPO="$(pwd)"
export TYPES="$(ls -1 "$PLUGIN_ROOT"/src/specs/schemas/*.yaml | xargs -n1 basename | sed 's/\.yaml$//' | tr '\n' ' ')"
booping config-get core.specs.tiers.project.path
ls -ld "$VAULT/specs" 2>/dev/null || echo "no $VAULT/specs"
```

A **type directory** is a directory named after one of `$TYPES`. Judge the cases below in order; the
first that matches is the only one applied.

## 1. A repo-pointed tier — left alone

`booping config-get core.specs.tiers.project.path` printed a value other than `None` / `null` /
empty: the user chose the tier's place. Change nothing.

Report: `left alone: path {value}`.

## 2. `{vault}/specs` is a link — pinned

`$VAULT/specs` is a symlink — the old default for a vault outside the repo, made by `specs init`.
The records stay where the link points; the tier is pinned there so the new default does not move
it.

```bash
realpath --relative-to="$REPO" "$(readlink -f "$VAULT/specs")"
```

Set `core.specs.tiers.project.path` to that printed path in `$VAULT/config.yaml`: create the file
when absent, merge into an existing `core:` / `specs:` / `tiers:` / `project:` mapping when present,
keep every other key and comment as written. Keep the link.
`booping config-get core.specs.tiers.project.path` now prints the path.

Report: `pinned: core.specs.tiers.project.path = {path}`.

## 3. A repo `specs/` with no link — pinned

`$VAULT/specs` is absent, the vault sits outside the repo, and `$REPO/specs/` holds a type
directory — the old default for an out-of-repo vault that never got its link.

```bash
case "$VAULT/" in "$REPO"/*) echo "vault inside the repo" ;; *) echo "vault outside the repo" ;; esac
for t in $(echo $TYPES); do [ -d "$REPO/specs/$t" ] && echo "type directory: specs/$t"; done
```

Pin `core.specs.tiers.project.path` to `specs` in `$VAULT/config.yaml`, exactly as in case 2.

Report: `pinned: core.specs.tiers.project.path = specs`.

## 4. Records under `{vault}/specs/` — moved

`$VAULT/specs` is a directory holding at least one type directory.

First, collisions. Any `$VAULT/{type}` that already exists for a type to move fails the migration
before anything moves: stop and report each collision as `collision: {vault}/{type} exists`.

```bash
MOVED=""; COLLISIONS=""
for t in $(echo $TYPES); do
  [ -d "$VAULT/specs/$t" ] || continue
  if [ -e "$VAULT/$t" ]; then COLLISIONS="$COLLISIONS $t"; else MOVED="$MOVED $t"; fi
done
for t in $(echo $COLLISIONS); do echo "collision: $VAULT/$t exists"; done
```

With no collision, move every type directory:

```bash
for t in $(echo $MOVED); do mv "$VAULT/specs/$t" "$VAULT/$t" && echo "moved $VAULT/specs/$t -> $VAULT/$t"; done
export MOVED
```

Then re-point the links inside every moved record. Deterministic — run this block once, right after
the move; it prints the report lines for re-pointed links and for targets it could not find.

```bash
python3 - <<'EOF'
import os
import os.path
import re
from pathlib import Path

vault = Path(os.environ["VAULT"])
old_root = vault / "specs"
moved = os.environ["MOVED"].split()
fence_re = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
code_span_re = re.compile(r"((`+).+?(?<!`)\2(?!`))")
link_re = re.compile(r"\]\((?P<dest>[^)\s]+)")


def remap(path: Path) -> Path:
    for t in moved:
        old = old_root / t
        if path == old or old in path.parents:
            return vault / t / path.relative_to(old)
    return path


for t in moved:
    for record in sorted((vault / t).rglob("*.md")):
        new_dir = record.parent
        old_dir = old_root / t / record.parent.relative_to(vault / t)
        count = 0
        missing = []

        def repoint(match: re.Match[str]) -> str:
            global count
            dest = match.group("dest")
            if "://" in dest or dest.startswith(("#", "/")):
                return match.group(0)
            target, sep, anchor = dest.partition("#")
            if not target:
                return match.group(0)
            resolved = Path(os.path.normpath(old_dir / target))
            mapped = remap(resolved)
            if not mapped.exists():
                missing.append(dest)
                return match.group(0)
            new_dest = os.path.relpath(mapped, new_dir) + sep + anchor
            if new_dest == dest:
                return match.group(0)
            count += 1
            return f"]({new_dest}"

        out = []
        fence = None
        for line in record.read_text().split("\n"):
            opener = fence_re.match(line)
            if fence is not None:
                if opener and opener.group(1)[0] == fence[0] and len(opener.group(1)) >= len(fence):
                    fence = None
                out.append(line)
                continue
            if opener:
                fence = opener.group(1)
                out.append(line)
                continue
            parts = code_span_re.split(line)
            rebuilt = []
            index = 0
            while index < len(parts):
                if index % 3 == 0:
                    rebuilt.append(link_re.sub(repoint, parts[index]))
                    index += 1
                else:
                    rebuilt.append(parts[index])
                    index += 2
            out.append("".join(rebuilt))
        if count:
            record.write_text("\n".join(out))
            print(f"re-pointed {count} links in {record.relative_to(vault)}")
        for dest in missing:
            print(f"left as is: {record.relative_to(vault)} -> {dest} (target missing before the move)")
EOF
```

Then what is left. Anything remaining in `$VAULT/specs/` (a README, other files or directories)
stays where it is; `$VAULT/specs` is removed only when empty.

```bash
find "$VAULT/specs" -mindepth 1 -maxdepth 1 | sed 's/^/left in place: /'
rmdir "$VAULT/specs" 2>/dev/null || true
```

Links from other vault files into the moved directories are listed, never rewritten — plans,
retrospectives and reviews stay as they were written.

```bash
alts="$(echo $MOVED | tr -s ' ' '\n' | grep . | paste -sd'|')"
grep -rnE --include='*.md' "specs/($alts)/" "$VAULT" | grep -vE "^$VAULT/($alts)/" \
  | cut -d: -f1,2 | sed "s|^$VAULT/|inbound link: |"
```

## 5. Otherwise — nothing to move

No case above matched: the vault already keeps its records at the root, or holds none. Change
nothing. A second run of this migration lands here (or in case 1 after a pin), so re-running
changes nothing.

Report: `nothing to move`.

## Verify

```bash
booping specs check --tier project
```

The check must report no `link` finding in a moved record; a finding there is fixed before
reporting. Findings of other kinds, or in records this migration did not move, are reported as
they are.

## Report

One line per action, as printed or stated above:

```
moved {vault}/specs/{type} -> {vault}/{type}
re-pointed {n} links in {file}
left as is: {file} -> {link} (target missing before the move)
pinned: core.specs.tiers.project.path = {path}
left alone: path {value}
left in place: {path}
inbound link: {file}:{line}
collision: {vault}/{type} exists
nothing to move
```
