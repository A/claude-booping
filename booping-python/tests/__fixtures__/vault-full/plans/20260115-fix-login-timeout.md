---
title: Fix login timeout bug
type: bug
status: ready-for-dev
effort: 2
planned: 20260115 10:30
---

# Goal

Session tokens expire prematurely when the user's clock drifts slightly.

# Tasks

- [ ] 2 SP: Normalise token expiry check to server time
