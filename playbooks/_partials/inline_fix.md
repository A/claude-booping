{#- The small-fix criterion of vault rule/0019's exception, from `core.sprint`. Imported:

      {% from "_partials/inline_fix.md" import inline_fix %}
-#}
{%- set _cap = config.core.sprint.inline_fix_sp -%}
{%- set inline_fix -%}
at most **{{ _cap }} SP** on the sprint scale ({% for row in config.core.sprint.scale if row.sp <= _cap %}{{ row.sp }}: {{ row.meaning }}{% if not loop.last %}; {% endif %}{% endfor %}), every file it touches already read by the session that applies it, nothing left to find out — no file still to read, no research, no open question
{%- endset -%}
