---
id: 14
title: Use top-level imports; resort to lazy imports only when there is no other way
targets:
  - agent:booping-developer
retro: null
created: 2026-08-10
---

Place imports at the top of the module. A lazy (function-local) import is an anti-pattern reached for only when a genuine constraint — a circular dependency that cannot be restructured, an optional heavy dependency — leaves no alternative.

**Example**: Importing a module inside a function body to dodge a circular import hides the real coupling; restructure the modules instead, and only fall back to the local import when no restructuring works.
