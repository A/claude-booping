---
id: 16
title: Plan tests per milestone and write them against real behavior
targets:
  - groom/draft-plan
  - agent:booping-developer
retro: null
created: 2026-08-10
---

**Grooming**: every milestone names what to test — the public surface it touches, the input cases that matter, and the tier it belongs at: integration by default, unit only for pure logic with tricky branches. One line, no test code. Example: "frontmatter-update extended with conditional quoting — test the CLI surface with parametrized inputs: plain, spaced, colon-bearing values."

**Practices**:

1. Name the break each test catches. A test that only fails on an intentional decision (a constant's value, exact wording, source text) is a change detector — assert the behavior that depends on the decision instead. Acid test: refactor the internals while keeping the public contract identical — a test that breaks is testing the wrong thing.
2. Name the test after the outcome observed, not the mechanism — `renders the first slide on load`, not `calls setIndex(0)`.
3. Derive expected values by hand — literals or checked fixtures, never the code under test or its helpers.
4. Test your own boundary contract, not framework mechanics.
5. Parametrize when the same surface takes different inputs and expected results.
6. Mock only at a true external boundary — network, disk, clock, subprocess, third-party — never a collaborator you own. Keep what the test depends on real, mirror real structures completely, and never assert on the mock itself. Test-only cleanup lives in test utilities, not production classes.
7. Before finishing, mutate the production code mentally — wrong constant, wrong branch, missing side effect, empty return, missing validation. Each mutation should fail a test.
