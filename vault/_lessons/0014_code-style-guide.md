---
id: 14
title: Follow the project code style practices
targets:
  - agent:booping-developer
retro: null
created: 2026-08-10
---

Code style practices:

1. Do not use lazy (function-local) imports in Python; top-level imports only, unless there is genuinely no other way.
2. Prefer parametrized tests when testing the same surface with different inputs and expected results.
