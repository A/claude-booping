---
title: Check the generated client into git after regenerating it
targets:
  - agent:booping-developer
retro: retrospectives/20260901-fixture-sprint.md
---

After running `just codegen`, commit the regenerated `client/` directory in the same
commit as the schema change that caused it; a schema change without its client breaks
every consumer build.
