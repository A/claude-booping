# Bug

A defect — observed behavior diverges from expected behavior.

## Triage

Before drafting a plan, work through three questions:

- **Code triage first — confirm the bug exists in code before planning the fix.** Locate the behavior in the codebase. If the cause is obvious on inspection (misread condition, off-by-one, wrong argument order), proceed to grooming with the root cause stated up front. If the cause is non-obvious, pause and ask the user for repro steps, environment, expected vs actual — a plan written on top of an unconfirmed bug is speculation.

- **Ask before drafting when the report is thin.** Missing repro steps, unstated version or environment, unclear severity, or behavior that could plausibly be intended are all blocking conditions. Ask the user for more detail rather than drafting with a fragile root-cause hypothesis.

- **Pick a test strategy up front.** Three options: (1) user manually verifies the fix — acceptable for UI-only changes with no regression surface; (2) an existing automated check already covers the bug's surface and will turn green post-fix — cite the command; (3) write a regression test that fails before the fix and passes after — the default when options 1 and 2 don't fit. The plan's Verify block must reflect whichever was chosen.

## Grooming

- No business goal needed — the implicit goal is "bug fixed and won't recur".
- The plan must include: triage, reproduction steps, root-cause hypothesis, minimal fix, and a regression test that fails before the fix and passes after.
- Skip product-manager-style elicitation unless the bug has product-impact ambiguity (e.g. unclear whether the current behavior is a bug or a feature).
