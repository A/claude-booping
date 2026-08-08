{#- The run's clock, from `core.macros.date`. Imported, not included: `{% set %}` in an
    included template does not reach the caller's scope, but `{% from ... import %}` does.

      {% from "_partials/timestamps.md" import slug_ts, human_ts -%}
-#}
{%- set slug_ts = macro('core.macros.date', '+%Y%m%d%H%M') -%}
{%- set human_ts = macro('core.macros.date', '+%Y-%m-%d %H:%M') -%}
