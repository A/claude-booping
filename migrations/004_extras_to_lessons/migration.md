---
id: 4
title: Extension files become targeted lessons
summary: Convert every `_booping/skill_*.md` and `_booping/agent_*.md` into a targeted `_lessons/NNNN_*.md`, and move the invocation log to the vault root.
---

# Extension files become targeted lessons

A project used to teach booping through two channels: extension files in `_booping/`, whose
*filename* said what they reached (`skill_groom.md` rode the groom skill, `agent_booping-developer.md`
rode the developer agent), and targeted lessons in `_lessons/`, whose `targets:` frontmatter says the
same thing as data.

Only the lesson survives. Nothing reads `_booping/skill_*.md` or `_booping/agent_*.md` any more, so
every rule still living there is inert. Most of the skills those files extended are playbooks now, so
an extension for a retired skill becomes a lesson targeting the playbook of the same name.

The invocation log moved in the same change — from `_booping/.booping.log` to `.booping.log` at the
vault root — and the vault's `.gitignore` seed moved with it.

## What to convert

Only markdown files **directly** under `_booping/`. Each one becomes one file in `_lessons/`, and the
source is then deleted.

| Extension file | Lesson `targets:` |
|---|---|
| `agent_<id>.md` (e.g. `agent_booping-developer.md`) | `agent:<id>` — e.g. `agent:booping-developer` |
| `skill_playbook.md` | `skill:playbook` |
| `skill_<name>.md` where `<name>` is a shipped playbook (`groom`, `develop`, `code-review`, `retro`, `learn`, `setup`, `migrate`, `playbook-authoring`) | `<name>` — the playbook of the same name |

`skill:playbook` is the only skill target that exists; every other `skill_<name>.md` is a retired
skill and routes to its playbook.

## How to convert

The rewrite is judged, not mechanical — read each file and write the lesson yourself.

- **One lesson per source file.** Split into two only when a file mixes unrelated rules aimed at
  different targets; each resulting file then carries its own `targets:`.
- **Name it `_lessons/NNNN_<slug>.md`**, `NNNN` continuing the vault's existing four-digit sequence
  (highest present + 1, zero-padded; `0001` in an empty `_lessons/`). `<slug>` is a few lowercase
  words joined by underscores, naming the rule.
- **Frontmatter** is `title:` (a short name for the rule) and `targets:` (the list from the table).
- **Body** carries the rules themselves, as standing imperative sentences. Drop only framing that
  restated what the filename already said — "Extra instructions for the groom skill", "This file is
  loaded into …". Every project fact, command, path and convention survives; this is a re-homing, not
  an edit of substance.
- **A file with no rule in it** — empty, a lone heading, a placeholder or commented-out stub — is
  deleted like any other converted source, and named in the report as *no convertible content*.
  Never silently skipped.
- **A `skill_<name>.md` that names neither the `playbook` skill nor a shipped playbook** (`skill_chat.md`,
  `skill_help.md`, a name from an even older layout) has no target in the table. Judge whether its
  content still applies to something live: convert it when it does, naming the target you chose, and
  otherwise **leave the file in place** and report it for the user to decide. Never guess a target.
- **Delete each source only once its lesson exists on disk.** A lesson that already exists under the
  intended name is **kept** and the collision reported — the source stays where it is, never
  overwritten or merged.
- **`_booping/` itself stays.** The log, subdirectories and anything unrecognised are still in it;
  removing the directory is the user's call, not this migration's.

No `_booping/` directory, or no extension files left in it, means there is nothing to convert —
report that as success. Re-running this migration on a converted vault changes nothing.

## Commands

Run from the vault root. First look at what is there:

```bash
ls -1 _booping/*.md 2>/dev/null || echo "no extension files in this vault"
ls -1 _lessons/*.md 2>/dev/null || echo "no lessons in this vault yet"
```

Read every file the first command listed, then take the next free lesson number:

```bash
ls -1 _lessons 2>/dev/null | awk 'match($0, /^[0-9]+/) { n = substr($0, 1, RLENGTH) + 0; if (n > max) max = n } END { printf "%04d\n", max + 1 }'
```

Write each lesson with your own file tools — the shape is:

```markdown
---
title: Run the suite through the project's own wrapper
targets:
  - agent:booping-developer
---

Never call `pytest` directly; the suite only resolves through `just pytest`.
```

Then delete each converted source, one `rm` per file, after its lesson is on disk:

```bash
rm _booping/skill_groom.md
```

## The log and the `.gitignore`

Deterministic, and independent of whether any extension file existed:

```bash
if [ -f _booping/.booping.log ]; then
  if [ -e .booping.log ]; then
    echo "kept existing .booping.log - _booping/.booping.log left in place"
  else
    mv _booping/.booping.log .booping.log && echo "moved _booping/.booping.log -> .booping.log"
  fi
fi

if [ -f .gitignore ] && grep -qF '_booping/*.log' .gitignore; then
  grep -vF '_booping/*.log' .gitignore > .gitignore.tmp && mv .gitignore.tmp .gitignore
  echo "dropped _booping/*.log from .gitignore"
fi
grep -qxF '.booping.log' .gitignore 2>/dev/null \
  || { echo '.booping.log' >> .gitignore; echo "added .booping.log to .gitignore"; }
```

## Verify

```bash
ls -1 _booping/skill_*.md _booping/agent_*.md 2>/dev/null \
  && echo "STILL OLD: the extension files above were not converted" \
  || echo "no extension files remain"
ls -1 _lessons/*.md 2>/dev/null
for f in _lessons/*.md; do [ -e "$f" ] || continue; grep -q '^targets:' "$f" || echo "NO TARGETS: $f"; done
ls -1 _booping/.booping.log 2>/dev/null && echo "log still under _booping/"
cat .gitignore 2>/dev/null
```

Any `STILL OLD:`, `NO TARGETS:`, `kept existing` or *no convertible content* line goes in the report,
naming the file and what happened to it. A file left in place because its target could not be judged
is reported the same way, with what it contains, so the user can route it by hand.
