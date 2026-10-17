---
id: "05"
title: "Groom rewritten around one drafting step"
sp: 3
status: done
plan: "plans/202610161319_groom-one-pass-and-plan-split/index.md"
---

# M05: Groom rewritten around one drafting step

**Goal**: `/playbook groom` runs intake → draft-plan → cross-review → present, with draft-plan researching the code, drafting `draft.md`, splitting and checking it in one runner-performed step.

**Scope**: `playbooks/groom/playbook.yaml`, `playbooks/groom/draft-plan/prompt.md` + `opus-5.md`, delete `playbooks/groom/research-codebase/` and `playbooks/groom/research-web/`, `src/config.yaml` (`core.groom_playbook.split_fallback_agent`). Partials, present and the snapshot are M06. `playbooks/groom/_specs/` is design history — not touched.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | Graph `intake: []`, `draft-plan: [intake]`, `cross-review: [draft-plan]`, `present: [cross-review]`; delete the two research step directories. In `states.run`, keep every status, edge and hook; rewrite only `researching → drafting` `when` to "draft-plan's research stage posted its facts, with file paths, in chat" and `drafting → cross-reviewing` `when` to "draft-plan wrote `draft.md`, `booping plan split` exited 0 and `booping plan check` passed or its three fix rounds are spent" with gates "every call that is the user's is answered" and "`booping plan check` reports no `sp` finding". Add `split_fallback_agent: "sonnet:medium"` under `core.groom_playbook` with a comment: model:effort of the agent that rewrites a draft split cannot cut; null → the driver rewrites it itself. | `playbooks/groom/playbook.yaml`, `playbooks/groom/research-codebase/`, `playbooks/groom/research-web/`, `src/config.yaml` | 1 | done |
| 5.2 | Rewrite `draft-plan/opus-5.md` on the benchmark prompt (`variants/common.md` + `V3a-stages-no-review.md` + `V2-template.md`), adapted to the run: (1) research — read the code the request touches and what it depends on, delegating bulk reads to the research agent, and post the facts with file paths in chat, then advance to `drafting`; (2) draft — pick the template (`_partials/plan_templates.md`), write the whole plan to `{plan-dir}/draft.md`: every template section, milestones under `## Milestones` as `### M{nn} — {title}` blocks, each opened by `sp: {n}` (1–5) and `depends_on: [M{nn}, …]` lines and holding the `#### {name}` sub-headings rendered from `config.core.groom_playbook.split.sections`, one Verify command scoped to the milestone, the whole-repo check only in Final Verification; decide what the code and request settle and record each assumption; a call only the user can make goes to the user (supervised: asked in chat; otherwise `clarifications.md` and park, as today). (3) `booping plan split {plan-dir}/draft.md --replace`; exit 3 or 4 → spawn `config.core.groom_playbook.split_fallback_agent` (rendered, with a null branch) to rewrite the draft into the format at `/tmp/booping-split-{slug}/draft.md` writing nothing in the vault, copy it over `draft.md`, split again. (4) `booping plan check {plan-dir}`; exit 1 → fix the named milestones in `draft.md`, back to (3), at most three rounds, remaining findings carried to present. Then `booping frontmatter-update … summary=`. Keep: the 35 SP split offer (`config.core.sprint.default_threshold_sp`), `_partials/sprint_planning.md`. Drop: the scaffold-per-milestone section, the `booping query` table paste, `milestone_contract.md`, the "Draft design with the user — iterate until aligned" bullet, and every one of the 16 ablation cut rules. Update `prompt.md`'s `summary`. | `playbooks/groom/draft-plan/opus-5.md`, `playbooks/groom/draft-plan/prompt.md` | 2 | done |

Tests: surface `bin/booping render-playbook groom` and `--step draft-plan`; cases — graph table, no STOP/Note, the rendered format block lists the four configured section names, the fallback agent renders from config; tier render + snapshot.

## Definition of Done

### Task 5.1

- [x] `bin/booping render-playbook groom` shows four steps in the order above and no `**STOP` line.
- [x] `bin/booping render-playbook groom | grep -c 'researching\|drafting'` still finds both statuses in the `## State` table.

### Task 5.2

- [x] `bin/booping render-playbook groom --step draft-plan` contains `### M{nn} — {title}`, the four section names from config, `booping plan split`, `booping plan check` and the rendered fallback agent, and none of: "TBD", "Similar to", "either X or Y".

## References

- `~/Dev/@A/booping-benchmarks/groom/variants/common.md`, `V3a-stages-no-review.md`, `V2-template.md` — the body's basis.
- `playbooks/groom/cross-review/prompt.md` — how a config-gated agent renders with a null branch.
- `playbooks/develop/provision/base.md` — `config.core.sprint.max_sp` rendered into prose.

## Verify

```
bin/booping render-playbook groom --step draft-plan
```
