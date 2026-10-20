#!/usr/bin/env bash
# Asserts the end state of migration 004 applied to a copy of this fixture.
#
#   cp -r migrations/004_lessons_to_rules/_fixtures /tmp/m004
#   (apply migration.md from /tmp/m004/repo with XDG_CONFIG_HOME=/tmp/m004/home/.config)
#   bash migrations/004_lessons_to_rules/_fixtures/check.sh /tmp/m004
#
# The copy must sit at /tmp/m004: home/.config/booping/config.yaml pins home_dir there.
set -uo pipefail

COPY="$(cd "${1:?usage: check.sh <migrated copy>}" && pwd)"
FIXTURE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_ROOT="$(cd "$FIXTURE/../../.." && pwd)"
BOOPING="$PLUGIN_ROOT/bin/booping"
export XDG_CONFIG_HOME="$COPY/home/.config"

HOME_RULES="$COPY/home/_specs/rule"
RULES="$COPY/repo/vault/specs/rule"
RETRO="vault/retrospectives/20260901-fixture-sprint.md"

fail() { echo "FAIL: $*" >&2; exit 1; }
one() { local hits=("$@"); [ ${#hits[@]} -eq 1 ] && [ -f "${hits[0]}" ] || fail "expected exactly one file for $*"; echo "${hits[0]}"; }
frontmatter() { awk 'NR==1 && /^---$/ {open=1; next} open && /^---$/ {exit} open' "$1"; }
has() { frontmatter "$1" | grep -qE "$2" || fail "$(basename "$1"): frontmatter lacks /$2/"; }
lacks() { ! frontmatter "$1" | grep -qE "$2" || fail "$(basename "$1"): frontmatter has /$2/"; }
same() { cmp -s "$1" "$2" || fail "$(basename "$1") was edited"; }

[ "$(cd "$COPY/home" && pwd -P)" = "$(cd /tmp/m004/home 2>/dev/null && pwd -P)" ] \
  || fail "the copy must be /tmp/m004 — config.yaml pins home_dir there"

# Every lesson file is gone and both emptied directories are removed (C6).
[ ! -e "$COPY/home/_lessons" ] || fail "home/_lessons still exists"
[ ! -e "$COPY/repo/vault/_lessons" ] || fail "repo/vault/_lessons still exists"

# Global — a duplicate of the global rule: dropped, the rule untouched (same tier, no target lacking).
same "$HOME_RULES/0001-tests-run-through-the-wrapper.md" "$FIXTURE/home/_specs/rule/0001-tests-run-through-the-wrapper.md"

# Global — a new lesson: converted into the global tier as rule/0002 (C4 rule shape).
G2="$(one "$HOME_RULES"/0002-*.md)" || exit 1
has "$G2" '^type: rule$'
has "$G2" '^created_by: claude$'
has "$G2" '^status: accepted$'
has "$G2" '^targets: \[develop\]$|^  - develop$'
has "$G2" '^brief: .+'
lacks "$G2" '^sources:'
lacks "$G2" '^reviewed:'
[ "$(ls "$HOME_RULES" | wc -l)" -eq 2 ] || fail "the global tier holds other than two rules"

# Project — a duplicate of a core booping: rule: dropped, the core rule never edited (C4).
git -C "$PLUGIN_ROOT" diff --quiet -- vault/specs/rule/0022-conventional-commits-with-scope.md \
  || fail "core rule booping:rule/0022 was edited"
! grep -q '^targets:' "$PLUGIN_ROOT/vault/specs/rule/0022-conventional-commits-with-scope.md" \
  || fail "core rule booping:rule/0022 gained targets"

# Project — a duplicate of the retired rule: dropped, the retirement stands, the rule untouched.
same "$RULES/0002-pin-the-node-version.md" "$FIXTURE/repo/vault/specs/rule/0002-pin-the-node-version.md"

# Project — a duplicate of the project rule lacking a target: the target merged, updated_at bumped.
P1="$RULES/0001-changelog-entry-per-change.md"
has "$P1" '^targets: \[.*groom/draft-plan.*\]$|^  - groom/draft-plan$'
has "$P1" '^targets: \[.*develop.*\]$|^  - develop$'
has "$P1" '^brief: .+'
lacks "$P1" '^updated_at: 2026-09-01$'

# Project — the rule whose sources and body link name lessons: both rewritten (C5).
P3="$RULES/0003-migrations-on-a-clean-tree.md"
has "$P3" "^sources: \[$RETRO\]$"
grep -qF '](../../retrospectives/20260901-fixture-sprint.md)' "$P3" || fail "0003: the link to lesson 0004 is not re-pointed at its retro"
grep -qF '`_lessons/0001_commit-scope.md` (removed by [migration 004](' "$P3" || fail "0003: the link to lesson 0001 is not replaced by the removal text"
lacks "$P3" '^targets:'

# Project — a new lesson with retro: converted, its retro as sources.
P4="$(one "$RULES"/0004-*.md)" || exit 1
has "$P4" '^type: rule$'
has "$P4" '^created_by: claude$'
has "$P4" '^status: accepted$'
has "$P4" '^targets: \[agent:booping-developer\]$|^  - agent:booping-developer$'
has "$P4" '^brief: .+'
has "$P4" "^sources: \[$RETRO\]$|^  - $RETRO$"
grep -qF '](../../retrospectives/20260901-fixture-sprint.md)' "$P4" || fail "0004: Follows from does not link the retro"

# Project — a new untargeted lesson without retro: converted with neither targets, brief nor sources.
P5="$(one "$RULES"/0005-*.md)" || exit 1
has "$P5" '^status: accepted$'
has "$P5" '^created_by: claude$'
lacks "$P5" '^targets:'
lacks "$P5" '^brief:'
lacks "$P5" '^sources:'
[ "$(ls "$RULES" | wc -l)" -eq 5 ] || fail "the project tier holds other than five rules"

# No project record links to or sources a removed lesson (C5).
! grep -rnE '\]\([^)]*_lessons/|^sources:.*_lessons/|^  - .*_lessons/' "$COPY/repo/vault/specs" \
  || fail "a project record still references a removed lesson"

# Both fixture tiers pass the specs check.
(cd "$COPY/repo" && "$BOOPING" specs check --tier project >/dev/null 2>&1) || fail "specs check --tier project reports an error"
(cd "$COPY/repo" && "$BOOPING" specs check --tier global >/dev/null 2>&1) || fail "specs check --tier global reports an error"

echo "ok: migration 004 end state holds in $COPY"
