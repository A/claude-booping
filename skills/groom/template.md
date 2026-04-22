---
type: feature | bug | refactoring
title: {{Descriptive Title}}
created: YYYY-MM-DD
source: {{URL / ad-hoc / conversation ref}}
status: groomed
sp: {{total}}
---

# {{Title}}

## Context

Why this work now. 2-4 sentences. Link to prior retros/lessons if they motivate this item.

## Business goal

*(features only)* The user-facing outcome. Distinct from the sprint title — phrase this as the problem the user has today and what changes for them after.

## Definition of Done

Bullet list of observable outcomes that, once all true, mean the work is finished. Each bullet must be testable.

- [ ] ...
- [ ] ...

## Design

### Architecture

How this fits into the existing system. Integration points. Reference concrete files.

### Decisions

| # | Decision | Alternative considered | Why this one |
|---|----------|------------------------|--------------|
| D1 | ... | ... | ... |

### Applies lessons

- `lessons/0007_no-mocked-db.md` — integration tests use real DB
- ...

## Milestones

### M1: {{Milestone name}} — {{SP}} SP | pending

**Goal**: One sentence — what changes in the codebase after this milestone.

**Verify**: Exact command(s) to run to confirm this milestone is done.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | ... | `path/to/file.py` | 2 | pending |
| 1.2 | ... | `path/to/other.py` | 1 | pending |

#### Task 1.1 DoD

- [ ] ...
- [ ] ...

#### Task 1.2 DoD

- [ ] ...
- [ ] ...

---

### M2: ...

...

---

## Final Verification

Commands to run at end of sprint:

```
just test
just lint
```

## Risk register

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| ... | low/med/high | ... |

## Out of scope

Explicit list of things intentionally not done in this sprint. Prevents scope creep.
