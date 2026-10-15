---
id: 4
title: Lessons become rules
summary: Turn every lesson in `{home_dir}/_lessons/` and `{vault}/_lessons/` into a rule record of its tier, or drop it as a duplicate of an existing rule; rewrite references to the removed files and remove both directories.
---

# Lessons become rules

Targeted guidance used to travel two ways: lesson files in `{home_dir}/_lessons/` and
`{vault}/_lessons/`, injected whole, and rule records in the specs tiers, injected as a brief plus a
link. Rules are now the only carrier — nothing reads `_lessons/` any more. This migration moves
what is left in either directory into rules, then removes the directories.

The legacy untargeted `{vault}/lessons/` directory (no underscore) is a different carrier and is not
touched.

## Setup

Run every command from the repo root — the directory holding the `.booping` marker; `booping`
resolves the project tier from it. `<vault>` is the vault path from your run-time context,
`<migration-dir>` this migration's directory.

```bash
export PLUGIN_ROOT="$(cd <migration-dir>/../.. && pwd)"
export VAULT="$(cd <vault> && pwd)"
export REPO="$(pwd)"
HOME_DIR="$(booping config-get home_dir)"; HOME_DIR="${HOME_DIR/#\~/$HOME}"; export HOME_DIR="${HOME_DIR%/}"
export CORE_ROOT="$PLUGIN_ROOT/$(booping config-get core.specs.tiers.core.path)"
# A tier's root when the tier exists, else empty; never creates one.
tier_root() { booping specs ls --tier "$1" >/dev/null 2>&1 && booping specs init --tier "$1" | tail -n 1; }
ls -1 "$HOME_DIR"/_lessons/*.md 2>/dev/null || echo "no global lessons"
ls -1 "$VAULT"/_lessons/*.md 2>/dev/null || echo "no project lessons"
```

Tier anchors — what `sources` entries and every path in the report are relative to: core → the
plugin root, global → `$HOME_DIR`, project → `$REPO`. When the project tier root is the core tier
root (a vault whose specs directory is the core tier), its records count as **core**: the first tier wins, as in rule injection.

## Order

Two passes, global first, then project, so a project lesson can be judged against a rule the global
pass just wrote. Each pass:

| Pass | Lessons | Writes into | Tier root |
|---|---|---|---|
| global | `$HOME_DIR/_lessons/*.md` | the global tier | last stdout line of `booping specs init --tier global` |
| project | `$VAULT/_lessons/*.md` | the project tier | last stdout line of `booping specs init --tier project` |

A pass with no lesson files does nothing — no `specs init`, no write — and reports `nothing to
convert`. Re-running on a migrated vault therefore changes nothing; a second vault migrating later
finds the global pass already done.

Within a pass, judge every lesson first (step 1), then run the script once (step 2). A lesson file is
deleted only after its rule exists on disk or its duplicate is named.

## 1. Judge each lesson

Read the lesson: `title`, `targets` (absent or empty → untargeted), `retro` (a path relative to the
directory holding `_lessons/`, or absent / `null`) and the body. List the rules it could duplicate
with `booping specs ls --type rule --tier core|global|project` and read every candidate in full.

**Duplicate** — an `accepted` or `retired` rule in the core, global or project tier stating the same
constraint. Judge substance, not wording. A global lesson is judged against core and global rules
only; a project lesson against all three.

- A **retired** duplicate drops the lesson: the retirement stands, the lesson is not revived, its
  targets go nowhere.
- An accepted duplicate in the **tier the pass writes**, lacking some of the lesson's targets, gains
  them: merge them into its `targets:` list, write a `brief:` when it had none (one or two lines —
  what an agent at those targets needs, without restating what it already knows), set
  `updated_at:` to today.
- An accepted duplicate in **another tier** — core for any lesson, global for a project lesson — is
  never edited. The targets it lacks are reported as not carried.

**Not a duplicate** — convert it into a new rule record in the pass's tier, at
`{tier root}/rule/{NNNN}-{slug}.md`: `{NNNN}` from `booping specs next rule --tier global|project`,
`{slug}` a few kebab-case latin words naming the rule. Shape per the specs guide
(`$PLUGIN_ROOT/src/specs/README.md`, `## Frontmatter`, `## Body`):

- Frontmatter: `type: rule`, `title`, `summary` (one line up to 200 characters — what is claimed),
  `created_by: claude`, `created_at` and `updated_at` today, `status: accepted`; `targets:` = the
  lesson's, with a written, quoted `brief:`; `sources:` = `[{the lesson's retro, relative to the tier
  anchor}]` when the retro exists inside the anchor, else omitted. An untargeted lesson gets neither
  `targets` nor `brief`. Never write `reviewed`.
- Body: `## Rule` — the lesson's constraint as a compact paragraph, every command, path and example
  kept; `## Follows from` — one item per reason, each holding a link: a value of the tier that names
  it, the retro as a relative link when it has one inside the anchor, and otherwise
  `` - [migration 004](https://github.com/A/claude-booping/blob/master/migrations/004_lessons_to_rules/migration.md) — converted from `_lessons/{file}`, which names no retro. ``
- Two lessons of one pass stating the same constraint: the second is a duplicate of the rule the
  first became.

## 2. Rewrite references and delete

Deterministic. Run once per pass with lesson files to remove, passing the pass name, its lessons
directory and tier roots, and every lesson file step 1 dropped or converted. It rewrites references
in the records of the tier root the pass writes — and never a `targets:` line — reports references
held by other tiers as dangling without editing them, deletes the lesson files and removes the
emptied directory.

- A `sources:` entry resolving (against the tier anchor) to a removed lesson is replaced by the
  lesson's retro, re-expressed against the same anchor, when it has one, it exists inside the anchor,
  and it is not already listed; otherwise it is dropped. An emptied list drops the key.
- A relative body link resolving to a removed lesson is re-pointed at the lesson's retro when it has
  one, else replaced by the text `` `_lessons/{file}` (removed by [migration 004](…)) `` — the
  surrounding sentence stays as written, and the link to this migration keeps a `## Follows from`
  item linked.

```bash
PASS=project LESSONS_DIR="$VAULT/_lessons" \
  PASS_ROOT="$(booping specs init --tier project | tail -n 1)" \
  GLOBAL_ROOT="$(tier_root global)" PROJECT_ROOT="$(tier_root project)" \
  uv run --quiet python - 0004_some-lesson.md 0007_another.md <<'PY'
import os
import re
import sys
from pathlib import Path
from urllib.parse import unquote

MIGRATION = "https://github.com/A/claude-booping/blob/master/migrations/004_lessons_to_rules/migration.md"
FRONTMATTER = re.compile(r"\A---\n(?P<body>.*?\n)---\n", re.S)
FENCE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
CODE_SPAN = re.compile(r"((`+).+?(?<!`)\2(?!`))")
LINK = re.compile(r"\[(?P<text>[^\]]*)\]\(\s*(?P<dest><[^>]*>|[^)\s]+)(?P<title>\s+[^)]*)?\)")


def env_path(name):
    value = os.environ.get(name, "").strip()
    return Path(value).absolute() if value else None


def inside(path, anchor):
    return path.resolve().is_relative_to(anchor.resolve())


def rel(path, anchor):
    return os.path.relpath(path, anchor)


pass_name = os.environ["PASS"]
lessons_dir = env_path("LESSONS_DIR")
anchors = {"core": env_path("PLUGIN_ROOT"), "global": env_path("HOME_DIR"), "project": env_path("REPO")}
roots = {"core": env_path("CORE_ROOT"), "global": env_path("GLOBAL_ROOT"), "project": env_path("PROJECT_ROOT")}
roots[pass_name] = env_path("PASS_ROOT")
pass_root, pass_anchor = roots[pass_name], anchors[pass_name]
other_tiers = [
    name
    for name in ("core", "global", "project")
    if name != pass_name and roots[name] is not None and roots[name].is_dir()
    and roots[name].resolve() != pass_root.resolve()
]


def lesson_display(path):
    return rel(path, pass_anchor) if inside(path, pass_anchor) else f"_lessons/{path.name}"


removed = {}
for name in sys.argv[1:]:
    path = lessons_dir / name
    if not path.is_file():
        sys.exit(f"{name}: no such lesson in {lessons_dir}")
    match = FRONTMATTER.match(path.read_text())
    retro_line = re.search(r"^retro:[ \t]*(.*)$", match.group("body") if match else "", re.M)
    retro_value = retro_line.group(1).strip().strip("'\"") if retro_line else ""
    retro = None
    if retro_value and retro_value not in ("null", "~"):
        candidate = (lessons_dir.parent / retro_value).absolute()
        if candidate.is_file() and inside(candidate, pass_anchor):
            retro = candidate
    removed[path.resolve()] = (path, retro)


def removed_lesson(target):
    return removed.get(target.resolve())


def split_frontmatter(text):
    match = FRONTMATTER.match(text)
    if not match:
        return None, text
    return match.group("body").split("\n")[:-1], text[match.end():]


def read_sources(lines):
    """(start, end, entries, flow) of the `sources:` key, or None."""
    for start, line in enumerate(lines):
        if not line.startswith("sources:"):
            continue
        value = line[len("sources:"):].strip()
        if value.startswith("["):
            entries = [e.strip().strip("'\"") for e in value.strip("[]").split(",") if e.strip()]
            return start, start + 1, entries, True
        end = start + 1
        entries = []
        while end < len(lines) and re.match(r"^\s+-\s", lines[end]):
            entries.append(lines[end].split("-", 1)[1].strip().strip("'\""))
            end += 1
        return start, end, entries, False
    return None


def body_links(body, on_link):
    out = []
    fence = None
    for line in body.split("\n"):
        opener = FENCE.match(line)
        if fence is not None:
            if opener and opener.group(1)[0] == fence[0] and len(opener.group(1)) >= len(fence):
                fence = None
            out.append(line)
            continue
        if opener:
            fence = opener.group(1)
            out.append(line)
            continue
        parts = CODE_SPAN.split(line)
        rebuilt = []
        index = 0
        while index < len(parts):
            part = parts[index]
            if index % 3 == 0:
                rebuilt.append(LINK.sub(on_link, part))
                index += 1
            else:
                rebuilt.append(part)
                index += 2
        out.append("".join(rebuilt))
    return "\n".join(out)


def link_target(record, dest):
    dest = dest[1:-1] if dest.startswith("<") and dest.endswith(">") else dest
    if "://" in dest or dest.startswith(("mailto:", "/", "#")):
        return None
    path = unquote(dest.split("#", 1)[0])
    return (record.parent / path) if path else None


def records(root):
    return sorted(p for p in root.glob("*/*.md") if p.is_file())


report = []

for record in records(pass_root):
    text = record.read_text()
    lines, body = split_frontmatter(text)
    record_display = rel(record, pass_anchor)
    changed = False

    if lines is not None:
        found = read_sources(lines)
        if found:
            start, end, entries, flow = found
            kept = []
            for entry in entries:
                hit = None if "://" in entry else removed_lesson(pass_anchor / entry)
                if hit is None:
                    kept.append(entry)
                    continue
                lesson, retro = hit
                replacement = rel(retro, pass_anchor) if retro is not None else None
                if replacement is not None and replacement not in entries and replacement not in kept:
                    kept.append(replacement)
                report.append(
                    f"rewrote {record_display} — sources {lesson.name} → {replacement or 'removed'}"
                )
                changed = True
            if changed:
                if not kept:
                    new_lines = []
                elif flow:
                    new_lines = [f"sources: [{', '.join(kept)}]"]
                else:
                    new_lines = ["sources:"] + [f"  - {e}" for e in kept]
                lines[start:end] = new_lines

    def on_link(match):
        global changed
        target = link_target(record, match.group("dest"))
        hit = removed_lesson(target) if target is not None else None
        if hit is None:
            return match.group(0)
        lesson, retro = hit
        changed = True
        if retro is not None:
            report.append(f"rewrote {record_display} — link {lesson.name} → {rel(retro, pass_anchor)}")
            return f"[{match.group('text')}]({rel(retro, record.parent)}{match.group('title') or ''})"
        report.append(f"rewrote {record_display} — link {lesson.name} → removed")
        return f"`_lessons/{lesson.name}` (removed by [migration 004]({MIGRATION}))"

    new_body = body_links(body, on_link)
    if changed:
        head = "" if lines is None else "---\n" + "".join(f"{line}\n" for line in lines) + "---\n"
        record.write_text(head + new_body)

for tier in other_tiers:
    anchor = anchors[tier]
    for record in records(roots[tier]):
        text = record.read_text()
        lines, body = split_frontmatter(text)
        hits = []
        found = read_sources(lines) if lines is not None else None
        for entry in found[2] if found else []:
            hit = None if "://" in entry else removed_lesson(anchor / entry)
            if hit is not None:
                hits.append(hit[0])

        def note(match):
            target = link_target(record, match.group("dest"))
            hit = removed_lesson(target) if target is not None else None
            if hit is not None:
                hits.append(hit[0])
            return match.group(0)

        body_links(body, note)
        for lesson in dict.fromkeys(hits):
            report.append(
                f"dangling {rel(record, anchor)} → {lesson_display(lesson)} ({tier}, not edited)"
            )

for lesson, _ in removed.values():
    lesson.unlink()
if lessons_dir.is_dir() and not any(lessons_dir.iterdir()):
    lessons_dir.rmdir()

for line in report:
    print(line)
PY
```

For the global pass: `PASS=global LESSONS_DIR="$HOME_DIR/_lessons"`, `PASS_ROOT` from
`booping specs init --tier global`, and the same `GLOBAL_ROOT` / `PROJECT_ROOT` lines.

## Verify

```bash
ls -d "$HOME_DIR/_lessons" "$VAULT/_lessons" 2>/dev/null && echo "STILL OLD: a lessons directory above remains"
booping specs check --tier project
```

Add `booping specs check --tier global` when the global pass wrote. Each check must report no error;
an error in a record this migration wrote or rewrote is fixed before reporting.

## Report

One line per action, grouped under `global:` then `project:`, paths relative to the tier anchor:

```
dropped {lesson path} — duplicate of {ref}
converted {lesson path} → {rule path}
merged targets {targets} into {ref} from {lesson path}
not carried {lesson path} targets {targets} — {ref} is {tier}, never edited
rewrote {record path} — {sources|link} {lesson file} → {retro path|removed}
dangling {record path} → {lesson path} ({tier}, not edited)
nothing to convert
```

`{ref}` is namespaced across tiers (`booping:rule/0013`, `anton:rule/0001`), bare within the pass's
tier. `{targets}` is comma-separated. The `rewrote` and `dangling` lines are the script's output,
copied as printed.
