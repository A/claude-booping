---
type: rule
title: Tests are planned per milestone and written against real behaviour
summary: Each milestone names what to test and at which tier; a test asserts observable behaviour, mocks only true external boundaries and would fail on a plausible break.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: accepted
targets: [groom/draft-plan, agent:booping-developer]
brief: "Grooming: each milestone names in one line the surface to test, the cases, the tier (integration by default). Tests: assert behaviour not mechanism, mock only external boundaries, hand-derived expectations."
sources: [vault/_lessons/0016_test-practices.md]
---

## Rule

**Grooming.** Every milestone names what to test in one line, no test code: the
public surface it touches, the input cases that matter, and the tier — integration
by default, unit only for pure logic with tricky branches.

**Writing tests.**

1. Each test names the break it catches. A test that fails only on an intentional
   decision (a constant's value, exact wording, source text) is a change detector;
   assert the behaviour that depends on the decision instead. A refactor that keeps
   the public contract must not break a test.
2. A test is named after the observed outcome, not the mechanism.
3. Expected values are derived by hand — literals or checked fixtures, never the
   code under test or its helpers.
4. A test covers its own boundary contract, not framework mechanics.
5. The same surface with different inputs and results is parametrized.
6. Mocks sit only at a true external boundary — network, disk, clock, subprocess,
   third party — never on a collaborator the project owns; what the test depends
   on stays real, real structures are mirrored completely, and no assertion targets
   the mock itself. Test-only cleanup lives in test utilities, not production code.
   [clarify] The owner prefers fakes and DI over mocks, while the lesson allows mocks
   at external boundaries; whether a fake replaces the mock there too is unsettled.
7. Before finishing, the production code is mutated mentally — a wrong constant or
   branch, a missing side effect or validation, an empty return; each mutation
   fails a test.

## Follows from

- [Proven to work](../values/0001-booping.md#proven-to-work) — a behaviour that matters is held by a check
  that would fail if it broke.
- [Lesson 0016](../../_lessons/0016_test-practices.md) — the source names no retro.
