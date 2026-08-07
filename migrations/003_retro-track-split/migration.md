---
id: 3
title: Retro becomes its own track
summary: End the plan lifecycle at `done` and move every `plans/{slug}/retro.md` out to a standalone `retrospectives/{slug}.md`.
---

# Retro becomes its own track

A plan used to carry the retro states itself: `develop` handed it to `awaiting-retro`, `retro`
moved it to `awaiting-learning`, and `learn` closed it to `done`, with the retrospective document
sitting inside the plan directory at `retro.md`.

The plan lifecycle now **ends at `done`**, the moment `develop` finishes. The retro track lives on
its own artifact — a standalone `retrospectives/{slug}.md` — which is what `retro` drives from
`awaiting-retro` to `awaiting-learning` and what `learn` closes to `done`. The two are joined by a
pair of links: the plan's `retro:` points at the retrospective, the retrospective's `plan:` points
back at the plan.

This migration ends every in-flight plan at `done` and relocates every retrospective still living
inside a plan directory.

## What to convert

Only `plans/*/index.md` and the `retro.md` files beside them. One pass, per plan:

| Plan on entry | Conversion |
|---|---|
| `status: awaiting-retro` | `status: done`; `retro:` stays `null`; `code_review: null` added |
| `status: awaiting-learning` | `status: done`; its `retro.md` relocated with `status: awaiting-learning`; `retro:` repointed |
| `status: done` with a `retro.md` | its `retro.md` relocated with `status: done`; `retro:` repointed |
| `status: done`, `goal: skipped`, `retro: null` | `retro: skipped` — the sentinel that keeps it out of the retro queue |
| `status: done`, nothing else | untouched |

A relocated `plans/{slug}/retro.md` lands at `retrospectives/{slug}.md`, gains the `status:` its
plan implies and a `plan:` back-link holding the vault-relative plan path, and the plan's `retro:`
is repointed at the new path.

`code_review:` is added **only** to plans coming from `awaiting-retro`. Those are today's review
candidates, and the code-review queue is `{status: done, code_review: null}` — a row missing the
field fails the clause. Historical `done` plans therefore keep no `code_review:` key at all, which
is what keeps a year of finished work out of the review queue.

- No `plans/` directory, or nothing on the old lifecycle, means there is nothing to do — report
  that as success. Re-running this migration on a converted vault changes nothing.
- A `retrospectives/{slug}.md` that already exists is **kept**: the `retro.md` beside the plan is
  left where it is and the collision reported, never overwritten or merged.
- A `status:`, `plan:` or `retro:` value that is already set to something else is **kept** and
  reported, never overwritten. Only a `null`, an absent key, or a link still pointing at the old
  in-plan `retro.md` is rewritten.
- Bodies are moved verbatim; only frontmatter changes, through a `ruamel.yaml` round-trip, so
  quoting, block scalars, comments and key order survive.

## Commands

Run from the vault root. First look at what is there:

```bash
booping query --glob 'plans/*/index.md' --columns status,goal,retro,code_review 2>/dev/null \
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
        if "code_review" not in fm:
            fm["code_review"] = None
            changes.append("code_review: null added")
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
