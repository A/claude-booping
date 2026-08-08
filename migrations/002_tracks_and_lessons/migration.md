---
id: 2
title: Retro becomes its own track; extension files become targeted lessons
summary: End the plan lifecycle at `done` and move every `plans/{slug}/retro.md` out to a standalone `retrospectives/{slug}.md`; convert every `_booping/skill_*.md` and `_booping/agent_*.md` into a targeted `_lessons/NNNN_*.md`, and move the invocation log to the vault root.
---

# Retro becomes its own track; extension files become targeted lessons

Two independent conversions of how a vault records finished work and teaches booping. Either
part can be a no-op on its own; run both, in order.

## Part 1 — retro becomes its own track

A plan used to carry the retro states itself: `develop` handed it to `awaiting-retro`, `retro`
moved it to `awaiting-learning`, and `learn` closed it to `done`, with the retrospective document
sitting inside the plan directory at `retro.md`.

The plan lifecycle now **ends at `done`**, the moment `develop` finishes. The retro track lives on
its own artifact — a standalone `retrospectives/{slug}.md` — which is what `retro` drives from
`awaiting-retro` to `awaiting-learning` and what `learn` closes to `done`. The two are joined by a
pair of links: the plan's `retro:` points at the retrospective, the retrospective's `plan:` points
back at the plan.

This part ends every in-flight plan at `done` and relocates every retrospective still living
inside a plan directory.

### What to convert

Only `plans/*/index.md` and the `retro.md` files beside them. One pass, per plan:

| Plan on entry | Conversion |
|---|---|
| `status: awaiting-retro` | `status: done`; `retro:` stays `null`; `code_reviews: null` added |
| `status: awaiting-learning` | `status: done`; its `retro.md` relocated with `status: awaiting-learning`; `retro:` repointed |
| `status: done` with a `retro.md` | its `retro.md` relocated with `status: done`; `retro:` repointed |
| `status: done`, `goal: skipped`, `retro: null` | `retro: skipped` — the sentinel that keeps it out of the retro queue |
| `status: done`, nothing else | untouched |

A relocated `plans/{slug}/retro.md` lands at `retrospectives/{slug}.md`, gains the `status:` its
plan implies and a `plan:` back-link holding the vault-relative plan path, and the plan's `retro:`
is repointed at the new path.

`code_reviews: null` is added **only** to plans coming from `awaiting-retro`, matching the
frontmatter new plans are seeded with. The key holds the plan's review history — the code-review
playbook appends each closing review's path to it. Historical `done` plans keep no `code_reviews:`
key at all; the review queue is every `done` plan either way, so nothing falls out of it.

- No `plans/` directory, or nothing on the old lifecycle, means there is nothing to do — report
  that as success. Re-running this part on a converted vault changes nothing.
- A `retrospectives/{slug}.md` that already exists is **kept**: the `retro.md` beside the plan is
  left where it is and the collision reported, never overwritten or merged.
- A `status:`, `plan:` or `retro:` value that is already set to something else is **kept** and
  reported, never overwritten. Only a `null`, an absent key, or a link still pointing at the old
  in-plan `retro.md` is rewritten.
- Bodies are moved verbatim; only frontmatter changes, through a `ruamel.yaml` round-trip, so
  quoting, block scalars, comments and key order survive.

### Commands

Run from the vault root. First look at what is there:

```bash
booping query --glob 'plans/*/index.md' --columns status,goal,retro,code_reviews 2>/dev/null \
  || ls -1 plans/*/index.md 2>/dev/null || echo "no plans in this vault"
ls -1 plans/*/retro.md 2>/dev/null || echo "no in-plan retrospectives"
```

Then convert. The script writes nothing when there is nothing on the old lifecycle:

```bash
uv run --quiet --with ruamel.yaml python - <<'PY'
from io import StringIO
from pathlib import Path

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap
from ruamel.yaml.representer import RoundTripRepresenter


class NullPreserving(RoundTripRepresenter):
    def represent_none(self, data):
        return self.represent_scalar("tag:yaml.org,2002:null", "null")


NullPreserving.add_representer(type(None), NullPreserving.represent_none)

yaml = YAML(typ="rt")
yaml.Representer = NullPreserving
yaml.preserve_quotes = True
yaml.width = 4096
yaml.indent(mapping=2, sequence=4, offset=2)

report = []


def read_doc(path):
    """Return (frontmatter, tail) where tail starts at the closing `---`."""
    text = path.read_text()
    if not text.startswith("---\n"):
        return None, text
    close = text.find("\n---", 3)
    if close == -1:
        return None, text
    return yaml.load(text[4 : close + 1]) or CommentedMap(), text[close + 1 :]


def write_doc(path, data, tail):
    buf = StringIO()
    yaml.dump(data, buf)
    path.write_text("---\n" + buf.getvalue() + tail)


def relocate(src, dest, plan_rel, status):
    data, tail = read_doc(src)
    if data is None:
        data, tail = CommentedMap(), "---\n" + tail
    for key, want in (("status", status), ("plan", plan_rel)):
        if data.get(key) in (None, ""):
            data[key] = want
        elif data[key] != want:
            report.append(f"kept existing {key}: {data[key]} in {src} - left as is")
    dest.parent.mkdir(parents=True, exist_ok=True)
    write_doc(dest, data, tail)
    src.unlink()
    report.append(f"{src} -> {dest} (status: {data['status']}, plan: {data['plan']})")


plans = sorted(Path(".").glob("plans/*/index.md"))
if not plans:
    print("no plans in this vault - nothing to do")
    raise SystemExit(0)

for plan in plans:
    slug = plan.parent.name
    plan_rel = f"plans/{slug}/index.md"
    fm, tail = read_doc(plan)
    if fm is None:
        report.append(f"SKIPPED {plan} - no frontmatter")
        continue

    status = fm.get("status")
    changes = []

    if status == "awaiting-retro":
        fm["status"] = "done"
        changes.append("status: awaiting-retro -> done")
        if fm.get("retro") is None:
            fm["retro"] = None
        if "code_reviews" not in fm:
            fm["code_reviews"] = None
            changes.append("code_reviews: null added")
    elif status == "awaiting-learning":
        fm["status"] = "done"
        changes.append("status: awaiting-learning -> done")

    src = plan.parent / "retro.md"
    dest = Path("retrospectives") / f"{slug}.md"
    if src.is_file():
        if dest.exists():
            report.append(f"kept existing {dest} - {src} not moved")
        else:
            relocate(src, dest, plan_rel, "awaiting-learning" if status == "awaiting-learning" else "done")
            current = fm.get("retro")
            if current in (None, "", f"plans/{slug}/retro.md", "retro.md", "./retro.md"):
                fm["retro"] = str(dest)
                changes.append(f"retro -> {dest}")
            elif current != str(dest):
                report.append(f"kept existing retro: {current} on {plan} - left as is")

    if status == "done" and fm.get("goal") == "skipped" and fm.get("retro") is None:
        fm["retro"] = "skipped"
        changes.append("retro -> skipped")

    if changes:
        write_doc(plan, fm, tail)
        report.append(f"{plan}: " + "; ".join(changes))

if not report:
    print("no plans on the old lifecycle - nothing to do")
    raise SystemExit(0)

for line in report:
    print(line)
PY
```

Confirm the result — no plan left on a retro status, no `retro.md` left inside a plan directory:

```bash
grep -l -E '^status: (awaiting-retro|awaiting-learning)$' plans/*/index.md 2>/dev/null \
  && echo "STILL OLD: the plans above were not converted" || echo "no plan left on a retro status"
ls -1 plans/*/retro.md 2>/dev/null \
  && echo "STILL OLD: the retrospectives above were not relocated" || echo "no in-plan retrospectives remain"
ls -1 retrospectives/*.md 2>/dev/null
```

Any `SKIPPED`, `STILL OLD:` or `kept existing` line is a failure to report: name the files and what
blocked them. A second run of the script must print `no plans on the old lifecycle - nothing to do`.

## Part 2 — extension files become targeted lessons

A project used to teach booping through two channels: extension files in `_booping/`, whose
*filename* said what they reached (`skill_groom.md` rode the groom skill, `agent_booping-developer.md`
rode the developer agent), and targeted lessons in `_lessons/`, whose `targets:` frontmatter says the
same thing as data.

Only the lesson survives. Nothing reads `_booping/skill_*.md` or `_booping/agent_*.md` any more, so
every rule still living there is inert. Most of the skills those files extended are playbooks now, so
an extension for a retired skill becomes a lesson targeting the playbook of the same name.

The invocation log moved in the same change — from `_booping/.booping.log` to `.booping.log` at the
vault root — and the vault's `.gitignore` seed moved with it.

### What to convert

Only markdown files **directly** under `_booping/`. Each one becomes one file in `_lessons/`, and the
source is then deleted.

| Extension file | Lesson `targets:` |
|---|---|
| `agent_<id>.md` (e.g. `agent_booping-developer.md`) | `agent:<id>` — e.g. `agent:booping-developer` |
| `skill_playbook.md` | `skill:playbook` |
| `skill_<name>.md` where `<name>` is a shipped playbook (`groom`, `develop`, `code-review`, `retro`, `learn`, `setup`, `migrate`, `playbook-authoring`) | `<name>` — the playbook of the same name |

`skill:playbook` is the only skill target that exists; every other `skill_<name>.md` is a retired
skill and routes to its playbook.

### How to convert

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
report that as success. Re-running this part on a converted vault changes nothing.

### Commands

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

### The log and the `.gitignore`

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

### Verify

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
