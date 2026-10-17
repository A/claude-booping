---
type: story
title: Specs first, then code
summary: A decision made in the specs becomes tracked work the code follows, closed with its plan; code that ran ahead of the specs becomes work for the specs.
created_by: claude
created_at: 2026-10-18
updated_at: 2026-10-18
status: done
sources: [vault/adr/0025-open-items-are-an-index.md, playbooks/specs/guide/prompt.md]
---

As **the owner**, I want a decision made in the specs to become tracked work that the code follows, so that the code never runs ahead of a decision and nothing decided is forgotten.

## Criteria

- A decision that needs code becomes an open item running specs to code: from an ADR's confirmation line, or from a sync of the specs against the code.
- Groom links the item to the plan it grooms, and develop carries that plan out.
- The item closes when its plan is done and reopens when the plan fails or is cancelled.
- Code that ran ahead of the specs becomes an open item running code to specs.
