---
title: Cache warm-up on deploy
type: feature
status: ready-for-dev
sp: null
created: null
planned: 19700104 08:00
started: null
completed: null
retro: null
code_review: null
goal: First request after a deploy is not a cold read.
summary: Warm the read cache as part of the deploy step.
commit: null
---

# Cache warm-up on deploy

Fixture plan — a null `sp` and a null `created`, so every renderer's missing-value branch is exercised.
