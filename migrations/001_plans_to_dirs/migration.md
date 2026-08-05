---
id: 1
title: Plans become directories
summary: Convert every flat `plans/{slug}.md` into `plans/{slug}/index.md`.
---

# Plans become directories

A plan used to be a single markdown file directly under the vault's `plans/`. It is now a
directory named by the slug, with the plan document at `index.md` inside it — the directory
is also the plan's workspace, so anything a run produces beside the document lives next to it.

Convert every flat plan file in this vault, and nothing else:

`plans/20260714-09-12_add-search.md` → `plans/20260714-09-12_add-search/index.md`

The file's content — frontmatter included — is moved verbatim; nothing inside it changes.

## What to convert

- Only markdown files **directly** under `plans/`. Files nested deeper are already converted.
- A slug that already has a directory with an `index.md` in it is a **conflict**, not a
  duplicate to overwrite: stop and report it rather than merging or replacing.
- No `plans/` directory, or no flat files left in it, means there is nothing to do — report
  that as success. Re-running this migration on a converted vault changes nothing.

## Commands

Run from the vault root. First look at what is there:

```bash
ls -1 plans/*.md 2>/dev/null
```

Then move each one, refusing any slug whose destination is already taken:

```bash
for file in plans/*.md; do
  [ -e "$file" ] || continue
  dir="plans/$(basename "$file" .md)"
  if [ -e "$dir/index.md" ]; then
    echo "CONFLICT: $dir/index.md already exists — $file not moved"
    continue
  fi
  mkdir -p "$dir" && mv "$file" "$dir/index.md" && echo "moved $file -> $dir/index.md"
done
```

Confirm the result — this should list one `index.md` per plan and no flat files:

```bash
ls -1 plans/*.md 2>/dev/null; ls -1 plans/*/index.md 2>/dev/null
```

Any `CONFLICT:` line, or a flat `plans/*.md` still present at the end, is a failure: report which
slugs were left behind and what blocked them.
