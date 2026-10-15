---
type: idea
title: Booping as a web service with thin skills
summary: A web service owns playbook management, artefacts and execution; skills become thin clients, a tracker such as Linear is a driver, and a sandbox runs the workers.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: open
# also distilled from the owner's local, unpublished notes (vault/notes/ is gitignored): vault/notes/Web Booping.md
---

## Idea

Booping is wired to Claude Code and is hard to configure and share. A web service would
handle playbook management and execution, with skills as thin wrappers over it; better
still, the service also provides a sandbox where the workers run. Named parts:

- artefacts live in a web database (vault, vault entry, and a plan as a configured entry
  type with a state machine and templates), behind a REST API: CRUD on
  `/api/{vault}/` and `/api/{vault}/{entry}/`, `GET`/`PUT` on
  `/api/{vault}/states/{entry}/{id}`;
- render is an application that calls the service;
- a task-tracker driver (Linear, or the service itself) creates the request, mirrors
  clarifications and the plan, and starts develop when the user moves the task;
- a router model maps a request to a playbook and runs it;
- custom playbooks, seeded with the default sprint playbook.

MVP is groom and develop; retro and lessons come as increments after it. The source
leaves open where the state hooks are configured.

## How to check

- [clarify] The source names no check. Proposed: answer the source's open question first
  — where state hooks live when state is a `PUT` on the API — by sketching groom's
  `awaiting-clarification` round-trip through the API and a tracker driver on paper; if
  the hooks cannot stay in the playbook's `states:` block, the service changes the
  playbook contract, and the idea needs an ADR before any code.
