## Plan Structure

The plan is the run's `index.md`: frontmatter, then the title, then the body.

### Frontmatter

```yaml
{% include "_partials/plan_frontmatter.md" %}
```

`sp` and `summary` are yours to write. `title` and `type` are intake's — correct them only where
the design changed them. `status`, `plan_status`, and every date and outcome key belong to the run
machine and its hooks: whatever intake left `null` stays `null`.

### Title

One H1 matching `title:`, and the only H1 in the file.

### Body + Quality Checklist

Each plan template is one file with two top-level sections:

- `# Plan Body` — the structure the plan is written against, section for section, in its order.
  None dropped, none extra.
- `# Quality Checklist` — walked item by item against the plan as written, before the plan is
  returned. An unsatisfied item is fixed, not reported as satisfied.

Read the chosen file before drafting: neither section can be guessed from its catalogue line.

When no entry fits, author one at `{project}/plan_templates/{name}.md` first, then draft against
it — frontmatter (`name`, `description`) plus both top-level sections, generic for its surface
class: placeholders throughout, no path, milestone or story-point value from this run baked in.
Never draft into a bad-fit template, never improvise a shape and name a template after it.
