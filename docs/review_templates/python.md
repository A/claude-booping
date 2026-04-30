---
name: python
description: Python-specific checklist — type safety, style, testing patterns, exceptions, comments, idioms.
layer: language
---

# Quality Checklist

- [ ] Type safety — annotations are present and accurate; the project's configured type-checker passes without new ignores or weakened types.
- [ ] Style is linter-owned — formatting / import-order / naming concerns belong to the project's configured linter and formatter; review does not duplicate them.
- [ ] Tests favour DI and fakes over mocks — collaborators are injected and substituted with real fakes; mocking is reserved for true process edges (network, filesystem, clock) and not used to paper over tight coupling.
- [ ] Specific exception types — exceptions are typed to the failure they represent and surfaced at the right boundary; no bare `except`, no swallowed errors, no over-broad catch hiding bugs.
- [ ] Comments only for WHY — comments explain non-obvious intent, not what the code does; no restated code in prose.
- [ ] Idiomatic Python — context managers for resources, `pathlib` for paths, generators for streaming, no mutable default arguments, no manual index loops where iteration suffices.
