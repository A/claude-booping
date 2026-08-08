# Framing brief — Review-gate importance levels

## Request

> i want you to groom a playbook step review gate importance level: i want it to have high|medium|low level, and if user says he want to review each step, it takes all, if user want to review only main steps - it leaves only high ones. default = medium - importance is defined by user prompt prose. Can be filtered on rendering steps list. don't read any existing plan related to this, make a new one from scratch

## Task type

`feature` — new user-facing capability: playbook authors tag review gates with an importance level, and runners filter which gates fire based on the user's stated review appetite.

- Not `bug`: nothing diverges from documented behavior — gates today are untyped prose and always fire; that is the current design, not a defect.
- Not `refactoring`: the change is user-visible — a new frontmatter surface for authors and a new filtering behavior at run time.

## Problem

Today every step's `review_gate` frontmatter is a single prose string; when present, the driver always pauses and asks for confirmation. There is no way to express that some gates matter more than others, and no way for the user to say "only stop me at the important ones" or "stop me at everything" — the run's interruption density is fixed by the playbook author, not tunable by the runner.

The change: each review gate carries an importance level (`high` | `medium` | `low`, default `medium`). The user's prompt prose at run start sets the review appetite — "review each step" keeps all gates, "only main steps" keeps only `high`. Filtering is applied when the steps list is rendered.

## Clarifications and Decisions

- Frontmatter shape: key renamed to `review_gates:` — a **list** of `{gate: str, importance: high|medium|low}`; a step may carry several gates. Absent `importance` → `medium`.
- Old `review_gate: <string>` form → blocking STOP notice (like the legacy `agent:` key); all core + vault playbooks migrated in the same sprint.
- Filtering is render-time via a CLI flag on `render-playbook`; driver maps user prose to the flag. Levels include an autonomous value that skips all reviews.
- Default appetite (no prose about reviews) = `medium`: gates tagged `medium` and `high` fire, `low` skipped. "Review each step" → all gates; "only main steps" → `high` only.
- No post-implementation prose-reshape milestone needed.
