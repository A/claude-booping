# Refactoring

A change to internal structure with no user-visible behavior change.

## Grooming

- Ask the user what they want to achieve **after this refactoring lands** — easier extension point, removed coupling, fewer foot-guns, faster onboarding, etc.
- If the user request doesn't already state a clear goal, challenge the user to articulate it. No goal → no `ready-for-dev`.
- Capture the agreed outcome in the plan's **Context** section, and write the one-line plan intent into the `summary:` frontmatter (yes, even though it's internal — the intent still names what changes).
- If the original user request file doesn't mention the goal, update it so the request reflects the agreed outcome.
- The plan must include current-vs-target design and migration steps. DoD is "no behavior change" — observable behavior identical before and after.
