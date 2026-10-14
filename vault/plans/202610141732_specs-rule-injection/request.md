# Request

## Request

> Rule injection: `booping render-playbook` (and agent/skill bodies, where lessons are injected today) also inject every accepted rule from all three tiers whose `targets:` match, as its `brief` plus a link to the record. Lessons keep working unchanged in parallel until a later migration.

Split off from [specs as a core feature — first plan](../202610141731_specs-core-format-cli-injection/index.md) (item 4 of its request) because the full request passed the 35 SP split threshold. Depends on that plan's `core.specs` tier config and `booping.specs` record model. Not groomed yet — run `/playbook groom` on this stub.

## Notes carried from the first plan's grooming

- Estimated ~11 SP: rule loader across tiers with realpath dedupe (core and project tiers coincide in booping's own repo); `## Rules` section in the composed, `--step` and inline-step render surfaces; agent and skill partials; docs.
- Hermetic renders keep the core tier, so core rules targeting core playbooks will appear in the committed `_reports/output.md` snapshots — drift the owner accepts.
- Booping's own `vault/specs/rule/` duplicates several `vault/_lessons/` (0004–0007, 0010, 0013, 0015): both would inject in this repo's runs until the lessons migration.
- Rules 0013 (snapshot baselines) and 0015 (review covers code only) are booping-repo specifics in the core tier; once injection ships they reach every user's runs — retarget or move before release.
