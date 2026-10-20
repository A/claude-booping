---
id: 6
title: Stories become feature-sized
summary: Keep an existing project tier's old-shape stories green — when a story fails the new feature-sized schema and the tier has no story schema of its own, pin the old schema as the tier's `_schemas/story.yaml` override.
---

# Stories become feature-sized

The shipped `story` schema now describes one whole feature: the "As **who**, I want …, so that …"
opening, then `## Scenarios`, `## Edge cases`, an optional `## Out of scope` and `## Criteria`,
with a required `priority: P0|P1|P2|P3`. A story written in the old shape — one sentence and one
to five criteria — fails it. This migration never rewrites a story: when the project tier holds a
failing story, it pins the old schema as the tier's own override, so the check stays green until
the user rewrites the stories.

## Setup

Run every command from the repo root — the directory holding the `.booping` marker; `booping`
resolves the config from it. `<vault>` is the vault path from your run-time context. This
migration covers the project tier only; stories in the global tier are left to the user.

```bash
export VAULT="$(cd <vault> && pwd)"
export REPO="$(pwd)"
booping config core.specs.tiers.project.path
```

The **tier root** is that printed path, anchored at the repo root (`$REPO/{path}`); when it printed
`None` / `null` / empty, the tier root is the vault root, `$VAULT`.

```bash
export TIER="<tier root>"
ls -d "$TIER/story" 2>/dev/null || echo "no story directory"
ls "$TIER/_schemas/story.yaml" 2>/dev/null || echo "no story schema override"
```

Judge the cases below in order; the first that matches is the only one applied.

## 1. The tier has its own story schema — left alone

`$TIER/_schemas/story.yaml` exists: the user already shapes stories for this tier. Change nothing.

Report: `left alone: _schemas/story.yaml exists`.

## 2. No story fails the shipped schema — nothing to do

The tier has no `story/` directory, or every story passes the shipped schema — the check reports
no finding under `story/`:

```bash
booping specs check --tier project | grep -E '^([^:]*/)?story/[^/:]+\.md:' || echo "no story finding"
```

Change nothing. A second run of this migration lands here, in case 1 or in case 3, so re-running
changes nothing.

Report: `nothing to do`.

## 3. No failing story is in the old shape — reported

The check above printed at least one finding under `story/`, but no failing story is in the old
shape — each has a `## Scenarios` H2, or its first paragraph is not the "As **who**, I want …,
so that …" sentence. Pinning would not help them. Change nothing.

Report: `not pinned: no old-shape story`, followed by each story finding the check printed.

## 4. An old-shape story fails the shipped schema — pinned

At least one failing story is in the old shape: no `## Scenarios` H2, and its first paragraph is
the "As **who**, I want …, so that …" sentence. Write the pre-change story schema, verbatim, as
the tier's override:

```bash
mkdir -p "$TIER/_schemas"
cat > "$TIER/_schemas/story.yaml" <<'SCHEMA'
# story: specs/story/<NNNN>-<slug>.md — one sentence "As **who**, I want …,
# so that …" and 1-5 criteria.
doc: story

rules:
  - select: FRONTMATTER
    has:
      type: story
      title: '^.+$'
      summary: '^.{1,200}$'
      created_by: { enum: [owner, claude] }
      created_at: '^\d{4}-\d{2}-\d{2}$'
      updated_at: '^\d{4}-\d{2}-\d{2}$'
      status: { enum: [done, planned, deferred] }

  - select: H2
    ordered: [Criteria]
    strict: true

  - select: DOCUMENT > P[0]
    match: '(?s)^As\s+\*\*.+\*\*,\s+I\s+want\s.+,\s+so\s+that\s.+'

  - select: SECTION("Criteria") > UL > LI
    min: 1
    max: 5
SCHEMA
```

Re-run the check; the old-shape stories now pass against the override:

```bash
booping specs check --tier project | grep -E '^([^:]*/)?story/[^/:]+\.md:' || echo "no story finding"
```

A finding still printed is a story that fails the old shape too; report it as it is, never fix it.

Report: `pinned: _schemas/story.yaml — rewrite the stories to the feature shape and delete it`.

## Report

One line, the matched case's:

```
left alone: _schemas/story.yaml exists
nothing to do
not pinned: no old-shape story
pinned: _schemas/story.yaml — rewrite the stories to the feature shape and delete it
```

followed, in case 3, by each story finding the check printed, and in case 4, by each story
finding the re-run check still printed.
