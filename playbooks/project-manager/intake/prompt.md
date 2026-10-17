---
summary: File every request in the user's message as an item, in the user's own words.
review_gate: null
---

Split the message into requests — each distinct ask, asides included. A message that only answers a pending question or confirms a gate is no request.

Per request, one:

```bash
booping items add --source request --title "{short title}" --text - <<'TEXT'
{the user's own words for that request}
TEXT
```

stdin carries the user's words for that request character for character — never paraphrased, summarised or corrected.

An answer to an item's question goes on the item, again in the user's words, and moves it back to `open`:

```bash
cat >> {vault}/open-items/{id}.md <<'TEXT'

## Answer

{the user's own words}
TEXT
booping transition {vault}/open-items/{id}.md open
```

Then post the filed ids, one line each: `{id} {title}`.
