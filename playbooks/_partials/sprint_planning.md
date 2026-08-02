## Sprint planning

A plan is estimated as a single sprint: every task carries story points, task points sum into the
milestone total, milestone totals sum into the plan's `sp`.

Story points measure the **complexity and review burden** of getting a task to a merged, accepted
state: design judgment, blast radius, ambiguity, integration surface, and how much careful reading
the diff demands. AI does implementation cheaply; this is what remains.

### Scale

| SP | Meaning |
|----|---------|
{% for row in config.sprint.scale -%}
| {{ row.sp }} | {{ row.meaning }} |
{% endfor %}
{%- if config.sprint.max_milestones_per_agent %}

Development bundles **up to {{ config.sprint.max_milestones_per_agent }} consecutive milestone(s)** into a single agent briefing — size
milestones against that combined review burden.
{%- endif %}

### Thresholds

{% if config.sprint.redecompose_threshold -%}
- **{{ config.sprint.redecompose_threshold }} SP re-decompose threshold** — a task at or over it is split before the plan is
  returned. Cut at a seam in its own work, never at its midpoint; each half stands alone with its
  own DoD and Verify, and the milestone and sprint totals are re-summed from the new leaves.
{% endif -%}
- **{{ config.sprint.default_threshold_sp }} SP split threshold** — not a velocity: the point past which a sprint is too large to
  hold together as one coherent iteration.

Estimate the work as it honestly stands: never shave a task to land under a threshold, never
inflate one, and never re-estimate a task down to dodge a split.

Project-specific sizing overrides live in `{project}/_booping/skill_groom.md` and take precedence.
