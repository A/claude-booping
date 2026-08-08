---
title: Discover the actual git remote name before pushing
targets:
  - develop
---

Before any `git push`, run `git remote -v` to discover the actual remote name. Do not assume `origin` — this user's repos often use a different remote name, and pushing to a guessed name fails or pushes to the wrong place.
