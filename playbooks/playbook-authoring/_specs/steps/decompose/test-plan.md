---
{}
---

[← index](../../index.md)

# decompose — Tests

## Fixtures

| Fixture         | Requirements                                                                                     |
| --------------- | ------------------------------------------------------------------------------------------------ |
| mod-review-brief | confirmed brief for a module-review playbook (goal, success, `_review/` home, two wishes) plus the user's procedure description |

## Tests

| Fixture          | Tier    | Title           | Check logic                                                                                  |
| ---------------- | ------- | --------------- | -------------------------------------------------------------------------------------------- |
| mod-review-brief | smoke   | FILE-AT-SLUG    | index written at `mod-review/_specs/index.md`, no frontmatter of its own authored             |
| mod-review-brief | smoke   | SECTIONS        | intro paragraph, then Graph, Steps, optional Decisions, optional Questions — in order        |
| mod-review-brief | smoke   | GRAPH-FENCE     | Graph section carries a yaml fence with a `graph:` mapping                                   |
| mod-review-brief | smoke   | TABLE-COLS      | Steps table columns exactly Step, Summary, Artifact, Gate, Model, Spec                       |
| mod-review-brief | smoke   | MODEL-FORMAT    | every Model cell is `model:effort`                                                           |
| mod-review-brief | smoke   | SPEC-LINKS      | every Spec cell links `steps/<step>/index.md`                                                |
| mod-review-brief | regress | DECOMP-FAITHFUL | steps, artifacts and gates reflect the described procedure and wishes — per-file findings ungated, one gated report; no invented scope |
| mod-review-brief | regress | GRAPH-SOUND     | graph orders sweeping before composing and expresses the per-file fan-out                    |
