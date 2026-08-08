```base
filters:
  and:
    - file.inFolder(this.file.folder + "/plans")
    - file.name == "index"
formulas:
  plan: file.asLink(title)
  tokens_in: ((metrics_tokens_input + metrics_tokens_cache_creation + metrics_tokens_cache_read) / 1000000).round(1) + "M"
  tokens_out: (metrics_tokens_output / 1000).round(0) + "k"
  cached: (metrics_tokens_cache_read / 1000000).round(1) + "M"
properties:
  formula.plan:
    displayName: Title
  formula.tokens_in:
    displayName: In
  formula.tokens_out:
    displayName: Out
  formula.cached:
    displayName: Cached
  note.metrics_active_minutes:
    displayName: Active min
  note.metrics_models:
    displayName: Models
views:
  - type: table
    name: Plans
    order:
      - status
      - sp
      - formula.plan
      - summary
      - created
      - completed
      - metrics_active_minutes
      - metrics_models
      - formula.tokens_in
      - formula.tokens_out
      - formula.cached
    sort:
      - property: created
        direction: DESC
      - property: metrics_tokens_cache_read
        direction: ASC
    columnSize:
      note.summary: 719
      note.created: 162
      note.metrics_models: 224
      formula.cached: 128

```
