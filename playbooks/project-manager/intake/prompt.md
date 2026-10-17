---
summary: File every request in the user's message as an item, in the user's own words.
review_gate: null
---

Split the message into requests — each distinct ask, asides included. A message that only answers a pending question or confirms a gate is no request.

Per request, one:

```bash
booping create core.specs.open_items.template {vault}/open-items --set source=request --set title="{short title}" --set body="$(cat <<'TEXT'
{the user's own words for that request}
TEXT
)"
```

The heredoc carries the user's words for that request character for character — never paraphrased, summarised or corrected. The printed diff names the filed id.

An answer to an item's question goes on the item, again in the user's words, and moves it back to `open`:

```bash
cat >> {vault}/open-items/{id}.md <<'TEXT'

## Answer

{the user's own words}
TEXT
booping transition {vault}/open-items/{id}.md open
```

Then post the filed ids, one line each: `{id} {title}`.
