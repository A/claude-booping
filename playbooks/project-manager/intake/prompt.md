---
summary: File each request that must outlive the session as an item, in the user's own words.
review_gate: null
---

Split the message into requests and file only what must outlive the session: work for later — a feature, a bug, a fix, a scope question — or a question waiting on the owner. The rest files nothing: an instruction for this session ("ping me", "wait", "do it now") is done or kept in the session; an answer to a gate or a UAT confirmation stays in the session; a standing policy goes to a rule through the `specs` playbook; a decision goes to an ADR.

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

Then post the filed items, one line each, in the user's language: `Создан {id}: {title}` / `Created {id}: {title}`.
