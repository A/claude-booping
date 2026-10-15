---
type: value
title: Deterministic where it can be
summary: Whatever can be computed is computed by code; the model spends tokens only on judgement, so a result does not depend on which model produced it.
kind: value
created_by: owner
created_at: 2026-10-15
updated_at: 2026-10-15
---

Whatever can be computed is computed by code, algorithmically; the model spends tokens
only where judgement is needed. A result that code produces is the same on every model
and every run.

## In practice

The `/playbook` skill renders known playbooks by code, so the model never assembles
them; rules, config values and queries are injected by code; state transitions and
their hooks run as code.

## Trade-off

More code and tests to keep; strict formats instead of flexible prose.
