---
summary: Open the session with the short status and name what to act on.
review_gate: null
---

Run `booping status` and post its lines verbatim.

Then name what to act on, in this order:

1. Unacked finished, failed or lost runs.
2. Items waiting on the user — point at their item files.
3. Plans at `ready-for-dev` — develop next.
4. Plans `done` without a code review — review next.
5. Open items.

- `supervised` — propose the first action and wait for the user's message.
- `autonomous` — start `work` on that list without waiting.

A user message already present → `intake` first.
