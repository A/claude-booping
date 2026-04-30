---
name: craft
description: Generic software-craft checklist — SOLID, boundaries, DI seams, data access. Always loaded.
layer: generic
---

# Quality Checklist

- [ ] Single responsibility — each module / class / function has one reason to change; mixed concerns are split.
- [ ] Open/Closed & extensibility — where would the next feature land? New behaviour can be added without rewriting existing call sites.
- [ ] Dependency Inversion / DI seams — collaborators are injected, not constructed inline; tests can substitute fakes without monkey-patching.
- [ ] Layered architecture & boundaries — modules respect their layer (domain / application / infrastructure); no upward dependencies; no leaks of infrastructure types into the domain.
- [ ] Responsibility ownership — for any rule or invariant in this diff, exactly one component owns it; no duplicated enforcement, no orphaned checks.
- [ ] DRY in utility modules — repeated helpers across call sites are consolidated; ad-hoc inlined logic that belongs in a shared utility is flagged.
- [ ] Data access — N+1 patterns avoided regardless of ORM (batch / prefetch / join as appropriate); transaction boundaries are explicit and scoped to a single unit of work.
