---
status: done
reviewed_at: 20260731 19:14
fixtures_reviewed_at: 20260731 19:27
suite_reviewed_at: 20260731 19:47
---

[← index](../../index.md)

# research-web

## Contract

- **Delegation** — assisted: the runner renders and owns the step and decides what is
  researched; the configured researcher agent performs the web reads and returns the findings
  with their sources; the runner posts them in chat.
- **Needs** —
  - the confirmed framing brief — the restated problem, the task type, and the decisions the
    user settled
  - the blast-radius map — in particular the open external questions and the external
    references (packages, images, APIs, flags, config options) the work names
- **Value** — settles the external ground the design rests on before the architecture is
  called. Where the work is complex, novel, or non-obvious, current best practice, competing
  approaches and known pitfalls are researched, so `draft-plan` argues from dated sources
  rather than model memory. Every external reference the plan will name — package version,
  image tag, API endpoint, CLI flag, config option — is checked against current docs, never
  assumed. Where the work is routine and no reference is in doubt, the step's whole output is
  one line saying so, so `draft-plan` never has to work out whether research happened; facts
  answerable from local ground truth are not fetched.
- **Output files** —
  - none — the findings are posted in chat, not written to the plan directory: the candidate
    approaches with their trade-offs and fit, the pitfalls that constrain the design, the
    verified references, and a source table carrying a URL and a retrieval date per claim.
    Research is sized to the open questions the framing and the blast radius carry — one
    primary source per question, stopping once the design call is constrained.
- **Step report** — the findings themselves, closed by `## Notes:` carrying the
  recommendation, the pitfall count and the reference verdicts — or the one skip line.
- **Review gate** —
  - none — the step never pauses the run; its findings reach the user through the design
    conversation in `draft-plan`

## Example findings

Posted in chat, when the work warranted research:

```markdown
# research — rate-limit-public-api

## Approaches

### Token bucket in gateway middleware

Per-key bucket refilled at a fixed rate, checked before the handler runs.

- Fits: limits are per API key, which the gateway already resolves.
- Costs: bucket state must be shared across processes — needs the cache tier, which the
  deployment already runs.
- Retire cost: low — the middleware is one layer, removable without touching handlers.

### Sliding-window counter in the datastore

Counts requests per key per window directly in the primary datastore.

- Fits: no new infrastructure.
- Costs: a write per request on the hot path; the window boundary allows a 2x burst.

## Pitfalls

- Returning `429` without `Retry-After` makes well-behaved clients retry immediately; the header
  is expected, not optional.
- Counting on the cache tier without a failure policy turns a cache outage into a total outage —
  fail-open vs fail-closed is a design call, not an implementation detail.
- Per-process in-memory buckets silently multiply the effective limit by the process count.

## Sources

| Source                                                | Backs                            | Checked  |
| ----------------------------------------------------- | -------------------------------- | -------- |
| https://www.rfc-editor.org/rfc/rfc6585                | `429` + `Retry-After` semantics  | 20260731 |
| https://redis.io/docs/latest/develop/use-cases/rate-limiting/ | token bucket on a shared cache | 20260731 |
```

## Return Format

When the work warranted research:

```markdown
## Notes:

- recommended: token bucket in gateway middleware — lowest retire cost, keys on what the
  gateway already resolves
- 3 pitfall(s) the design must answer, one of them a fail-open vs fail-closed call
- references: `redis-py` floor verified at 5.0 against current docs
```

When nothing was uncertain and no reference was in doubt:

```markdown
## Notes:

- routine work, no external references in doubt — no web research performed
```
