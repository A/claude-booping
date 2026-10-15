# corrections.md format

Sidecar beside the run artefact, holding every correction the user made during a run: in the plan directory for groom and develop, in the review's `codereviews/{dir}/` for code-review — shared by that directory's reviews. Plain markdown, no frontmatter, seeded with `# Corrections` on the first entry.

`booping correction add` is its only writer; `booping correction list --plan` is its reader — a plan's own sidecar, then those of its code reviews.

## Shape

One H2 per entry, in the order logged:

```
## R{n} — {step} — {YYYY-MM-DD HH:MM}
```

- `R{n}` — the entry id, numbered from `R1` across the whole file; the next is the highest plus one, never reused.
- `{step}` — the `{playbook}/{step}` the correction happened in, verbatim.
- `{YYYY-MM-DD HH:MM}` — local date and time of logging.

Under the heading, in this order:

- `**Did:**` — what the driver did that the user corrected.
- `**Said:**` — the user's words, every line blockquoted, never reworded. When the session transcript is found, the quote must appear in one of its user messages.
- `**Why:**` — the reason the user stated, or `not stated`.
- `**Dialogue:**` — `` `{session}` line {n} · `{uuid}` ``: the session id, the 1-based transcript line and the uuid of the last user message holding the quote. Without a session id or a transcript: `not found — no session id` | `not found — no transcript for {session}`.
- `**Record:**` — only when the correction names a spec record: the ref, an arrow and a link to the open item filed for it.
- `**Artifact:**` — a link to the run artefact, relative to the sidecar.

## Example

```markdown
# Corrections

## R1 — groom/draft-plan — 2026-10-15 15:40

**Did:** proposed one plan over the 35 SP threshold

**Said:**

> split it, corrections first

**Why:** not stated

**Dialogue:** `6a68e361-5db5-43f6-9580-ac2e1ae7254d` line 212 · `4f2c9a1e-0b7d-4c55-9e0a-6d1f3b2a8c90`

**Record:** value/0007 → [OI-0004](../../open-items/OI-0004.md)

**Artifact:** [index.md](index.md)
```
