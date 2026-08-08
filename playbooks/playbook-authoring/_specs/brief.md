---
reviewed_at: 20260731 08:43
---

# playbook-authoring — Brief

## Goal

Turn a user's procedure description into a working, evaluated playbook: specs confirmed file
by file, then manifest, per-step prompts and promptfoo suites — each step smoke-green before
it counts as built.

## Success result

A `<slug>/` playbook dir under the playbook root: `playbook.md` manifest, one dir per step
with `prompt.md` + model variants, `promptfooconfig.yaml` + `tests.yaml` + `_fixtures/`;
every step's smoke tier green, judged tier tuned or explicitly skipped by the user; the
`_specs/` behind it confirmed in full.

## Artifact home

`<slug>/_specs/`

## Wishes

- Files mode everywhere — every review point is an on-disk artifact; runs restart from disk.
- User gate per artifact, in-file (`confirmed: Yes`), not chat-only.
- The confirmed example IS the contract — suites derive from it; wrong checks lose to it.
- Per-step depth: one `step-pipeline` carries a step from contract to green suite.
