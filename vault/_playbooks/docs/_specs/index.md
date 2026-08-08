---
status: building-steps
reviewed_at: 2026-08-08 13:18
playbook_yaml_reviewed_at: 2026-08-08 13:46
---
# docs — Decomposition

Keep the project's documentation matched to what the repo actually is. A cheap `survey` opens the
run record and reports both the spec set's completeness and the delivered work not yet documented;
the spec set — briefing, roles, surfaces, feature index — is established or refreshed from there,
each file written by its own agent and confirmed by the runner. `research` then reads the
undocumented deliveries in parallel sub-agents and returns a typed change table the user extends
and confirms; `sync-specs` folds the confirmed deltas back into the spec set, `targeting` turns
them into a role × surface plan, and the `update` loop runs one instance per destination document —
write, compact, verify — so no two instances ever touch the same file. The changelog entry and the
closed run record end the run. Every destination is a markdown surface — source files are never
edited, code-level docs stay with `develop`. Artifacts live under `{vault}/docs/`: the stable spec set in
`_specs/` (`index.md`, `roles.md`, `targets.md`, `features.md`), the ledger of already-documented
work in `_specs/documented.md`, and one `{YYYYMMDDHHmm}-{title}.md` record per run.

## Graph

```yaml
graph:
  survey: []
  briefing: [survey]
  roles: [briefing]
  targets: [briefing]
  feature-index: [briefing]
  research: [roles, targets, feature-index]
  sync-specs: [research]
  targeting: [sync-specs]
  update:
    dependencies: [targeting]
    repeat: once per destination document in the confirmed targeting plan; instances may run in parallel
    graph:
      write: []
      compact: [write]
      verify: [compact]
  changelog: [update]
  record: [changelog]
```

## Steps

| Step | Summary | Inputs | Artifact | Gate | Delegation | Model | Spec |
| --- | --- | --- | --- | --- | --- | --- | --- |
| survey | report which spec-set files are missing or incomplete and which delivered work is not yet documented; open the run record | which spec files exist and whether each is complete; the delivered work items and their statuses; the record of what has already been documented | `{vault}/docs/{YYYYMMDDHHmm}-{title}.md` — run record opened with the spec-set state and the undocumented set | confirm the run scope — which spec files to refresh, which delivered items to cover | detached | opus-5:medium | [spec](steps/survey/index.md) |
| briefing | write the shaping briefing — what the project is, who it serves, where it is heading — and catch vision migration against the previous one | the repo's self-description and architecture; the direction the user states; the previous briefing | `{vault}/docs/_specs/index.md` | confirm the briefing, especially any vision shift | detached | fable-5:high | [spec](steps/briefing/index.md) |
| roles | characterise the audiences that read this project's documentation and the tone and depth each one needs | the briefing; the surfaces the project exposes and who consumes them; the previous roles file | `{vault}/docs/_specs/roles.md` | confirm or refine — presented together with surfaces | detached | fable-5:medium | [spec](steps/roles/index.md) |
| targets | enumerate the markdown documentation surfaces — those the repo has plus the changelog this playbook introduces — with each one's format, audience and depth | the briefing; the documentation surfaces present in the repo and their conventions; the previous surfaces file | `{vault}/docs/_specs/targets.md` | confirm or refine — presented together with roles | detached | fable-5:medium | [spec](steps/targets/index.md) |
| feature-index | build the feature index — features, their capabilities, their groups; the groups are the documentation structure | the briefing; the capabilities the project actually ships; the previous index | `{vault}/docs/_specs/features.md` | confirm features, capabilities and groups | detached | fable-5:medium | [spec](steps/feature-index/index.md) |
| research | read each delivered item in its own sub-agent and return a typed change table tied to the spec set | the delivered items in scope; the briefing, roles, surfaces and feature index | run record — typed change table (vision shift / new feature / refactoring / feature drop / chore) | extend, refine and confirm the change table | assisted | opus-5:high | [spec](steps/research/index.md) |
| sync-specs | apply the confirmed change table back to the spec set — vision, roles, surfaces, capabilities | the confirmed change table; the current briefing, roles, surfaces and feature index | the four `_specs/` spec files, updated in place | none — executes the already-confirmed table | detached | opus-5:medium | [spec](steps/sync-specs/index.md) |
| targeting | decide per change which role × surface combinations must be written and what each one must say | the confirmed change table; each role's tone and depth needs; each surface's format and audience; the feature index | run record — targeting plan, one row per destination document | confirm the targeting plan before anything is written | assisted | opus-5:high | [spec](steps/targeting/index.md) |
| write | write one destination document's assigned changes, in the depth and tone its audience needs; markdown only, never source files | one destination document and its current content; the changes assigned to it and what each must say; the roles it addresses | the destination markdown document, updated | none — authorised by the targeting plan | detached | fable-5:medium | [spec](steps/write/index.md) |
| compact | split the document by sections, run a radical and a gentle compaction per section, merge the result | a freshly written document; the depth and tone its audience needs | the same document, compacted | none | detached | opus-5:high | [spec](steps/compact/index.md) |
| verify | check the document against facts, audience fit and legacy narration; correct what fails — reads source to check, never edits it | the document; the code and behaviour it describes; the roles it addresses; the surface's purpose | the same document, corrected; unresolved findings on the run record | none | detached | opus-5:high | [spec](steps/verify/index.md) |
| changelog | write the run's user-visible entry in the project's chronological history — the one surface where past tense is correct; seed the file on first run | what landed this run and its user-visible effect; the history's existing format and latest entries | `CHANGELOG.md` at the repo root, created if absent | none | detached | opus-5:medium | [spec](steps/changelog/index.md) |
| record | close the run record with what landed where, and mark the covered work items documented | the changes covered and where each landed; the work items now documented | run record closed — `## Landed` + `documented:` list; the ledger write in `_specs/documented.md` is the `close-documented` hook's | none | detached | opus-5:low | [spec](steps/record/index.md) |

## States

See [states.md](states.md).
