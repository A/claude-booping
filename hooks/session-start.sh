#!/usr/bin/env bash
# SessionStart hook: inject the booping session-start block inside a booping project.
# Never blocks a session — every failure exits 0 with no output.

dir="$PWD"
while [ ! -e "$dir/.booping" ]; do
  [ "$dir" = "/" ] && exit 0
  dir="$(dirname "$dir")"
done

out="$("$CLAUDE_PLUGIN_ROOT/bin/booping" render src/templates/hooks/session_start.md.j2 2>/dev/null)" || exit 0
printf '%s\n' "$out"
exit 0
