---
type: idea
title: Groom depth scales with the task
summary: A small, already-decided request takes a light path to develop instead of a full groom, and groom runs its deeper work only when the task or the user asks for it.
created_by: claude
created_at: 2026-10-17
updated_at: 2026-10-17
status: open
sources: [vault/idea/0003-groom-depth-scales-with-task.md, vault/adr/0030-groom-drafts-the-whole-plan-in-one-pass.md]
---

## Idea

A small, already-decided request should not pay for a full groom (owner, 2026-10-16). Either groom routes it to a light path (request → one-pass develop brief) or the one-pass groom ([adr/0030](../adr/0030-groom-drafts-the-whole-plan-in-one-pass.md)) is shown to clear it in minutes. More broadly, groom picks how much work to do from the task's complexity: a simple task or a bug gets a minimal pass, and deeper research runs when the task is complex or when the user asks for it — directly ("plan tests") or indirectly ("do deep research for this task"). This is the follow-up left after the variant pick of [idea/0003](0003-groom-depth-scales-with-task.md).

## How to check

- Test case: corpus `s3-booping-specs-site-registries` in booping-benchmarks `groom/`, a site change the orchestrator first meant to groom and the owner sent straight to development; compare the current groom and the light path on time and on the develop outcome.
