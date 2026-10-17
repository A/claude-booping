---
type: rule
title: Tests run through the project's wrapper
summary: The test suite is run through the project's own task runner, never by calling the test binary directly.
created_by: owner
created_at: 2026-09-01
updated_at: 2026-09-01
status: accepted
targets: [agent:booping-developer]
brief: "Run the suite through the project's task runner (`just test`), never the test binary directly."
---

## Rule

Run the test suite through the project's task runner — `just test` — never by calling
the test binary directly; the runner sets the environment the suite needs.

## Follows from

- [The fixture's convention](../README.md) — the owner's preference.
