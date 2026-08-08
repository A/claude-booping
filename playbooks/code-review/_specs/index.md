---
status: building-steps
agents:
  record-decision: af37d670c00e4b360
  interview: a3d64596be77a6349
  decompose: a4f053ab5a8df0aff
  states: ac925b17eea07f821
  manifest: a0ed20fb0f023bea6
reviewed_at: 20260804 11:22
playbook_yaml_reviewed_at: 20260804 17:18
---
# code-review — Decomposition

Port the stateless `/code-review` skill into a playbook that runs in the same conversation as a
`develop` sprint, so a review starts where the work just landed. Four steps in a line: **scope**
settles what to review — offering the plan `develop` just delivered when one is in hand, otherwise
proposing the latest coherent piece of work judged off `git log --oneline`, asked through
`AskUserQuestion` with a free-text route so the user can name an arbitrary target outright;
**review** hands the whole craft to a detached sub-agent — stack discovery, checklist selection,
blast-radius mapping, the static checklists and the plan- and lesson-aware dynamic checks — which
returns findings classified `BLOCKER` / `SUGGESTION` / `NIT` and nothing else, so the diff and the
checklists never enter the runner's context; **present** hands those findings to the
`plannotator-reviewer` agent for an in-browser review of code and AI comments together and relays
the human's feedback back, or the signal that the surface is unavailable; **resolve** acts on that
feedback — trivial nits applied inline, non-trivial fixes delegated to the developer agent, nothing
committed or pushed, and the chat-only presentation performed here when Plannotator was
unavailable. The run is ephemeral: no workdir, no persisted state, no review artefact, no
plan-status move, single pass — a second look after fixes is a new run. The stateless
`/code-review` skill stays in place for what this playbook cannot serve: an arbitrary diff, file
list or working tree with no plan and no sprint behind it.

## Graph

```yaml
graph:
  scope: []
  review: [scope]
  present: [review]
  resolve: [present]
```

A flat chain: each step consumes the previous one's output whole, so there is no wave to
parallelise and no repetition to make a subgraph of.

## Steps

| Step    | Summary                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | Inputs                                                                                                                                                                                                                                                                                                                             | Artifact                                                                                                                                                                                                                                    | Gate                                                                                              | Delegation                                             | Model         | Spec                           |
| ------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- | ------------------------------------------------------ | ------------- | ------------------------------ |
| scope   | settle what to review and resolve it into a concrete target: put every candidate on one `AskUserQuestion` call — the plan the session just delivered when there is one, the latest coherent piece of work judged off the recent commit history (the latest plan delivery on this branch, a feature's worth of commits, whatever the commits actually suggest), the vault's plans sitting at the configured code-review status, and a free-text route for an arbitrary scope — then resolve the answer into a diff range or file list and surface it back before any review work is spent                                                                                                  | whether this session just delivered a plan and which; the vault's plans at the configured code-review status with their titles and commit baselines; the repo's recent commit history, current branch and uncommitted work; the user's answer naming the scope                                                                     | the confirmed review scope — a diff range or file list, plus the plan behind it when there is one — carried in conversation                                                                                                                 | none — the scope question is asked in-step and the resolved target reported back in the same turn | inline                                                 | opus-5:medium | [spec](steps/scope/index.md)   |
| review  | perform the skill's craft over the confirmed scope in one detached pass: discover the stack from the repo's manifests and tooling, pick the review checklists that match it (every generic one, language and framework ones only on a real signal), map blast radius for wide diffs, walk each loaded checklist against the changed code, then the dynamic checks — lesson compliance, plan-DoD alignment and plan-intent match — and return every finding classified `BLOCKER` / `SUGGESTION` / `NIT` with its file and line anchor, offending snippet, proposed fix and the checklist item or lesson it cites; style the project's linter or formatter already enforces is filtered out | the confirmed review scope; the plan in scope with its DoD, mandated approach and architectural decisions when there is one; the project's lessons; the available review checklists and their descriptions; the repo's stack signals — manifests, framework, linter, formatter, type-checker, test runner; the changed code itself | the severity-classified findings, returned inline in the step's own return block under a richer contract than the harness default — one entry per finding, anchor · severity · snippet · proposed fix · rationale; nothing written anywhere | none — the findings are what the human reviews next                                               | detached                                               | opus-5:high   | [spec](steps/review/index.md)  |
| present | put the findings in front of the human and collect their verdict: post them in chat grouped by severity — anchor · snippet · proposed fix · the checklist item or lesson cited — and ask which of them to apply, taking back which the human approved, which they rejected and any correction of their own; a project that has registered a review-presenting agent in config can have the step hand the findings to that agent instead, that agent's own description carrying the rest                                                                                                                                                                                                   | the severity-classified findings with their anchors, snippets, fixes and rationales, as they arrived in the review's return — nothing is re-read, re-derived or re-classified; the review scope, for the heading                                                                                                                   | the human's verdict on the findings, carried in conversation                                                                                                                                                                                | none — this step *is* the human review                                                            | inline                                                 | opus-5:medium | [spec](steps/present/index.md) |
| resolve | close the run on the human's verdict: trivial nits the human approved applied inline, non-trivial approved fixes delegated to the worker agent with the finding, its files and the proposed fix, findings the human rejected dropped without argument — and report what was applied, what was delegated and what was left; no commits, no pushes, no plan-status move, no review file left behind                                                                                                                                                                                                                                                                                         | the human's verdict, already collected in `present`; the findings as classified, still in hand from the review's return; which fixes are trivial inline edits and which are not; the project's conventions the fixing agent must follow                                                                                            | approved trivial nits applied in the working tree; non-trivial fixes applied by the delegated agent; the closing report in chat                                                                                                             | none — the human's own feedback is the approval                                                   | assisted — worker agent for approved non-trivial fixes | opus-5:medium | [spec](steps/resolve/index.md) |

## Constraints

- The playbook is `jinja: true` + `requires_project: true`: `review`'s body renders the review-checklist
  table and the vault's lessons through the partials the skill already uses, and both need project
  context. Reviewing a repo with no booping project remains the stateless skill's job.
- The playbook is **surface-agnostic**: no step body names a review surface, a transport or an
  annotation format. `present` posts the findings in chat. A project that wants a richer surface
  wires an external agent through its own config tier, and that agent's description carries what it
  does — the playbook offers only the generic config-driven extension point. A targeted lesson
  cannot reach such an external agent; a lesson for that surface targets `code-review/present`.
- Nothing is written to the vault or the repo: no review report is produced on any route.
- The review is read-only against plan state — no plan-lifecycle status moves, in either direction.
- The skill's hard rules carry over into the preamble, not into each step: no commits or pushes,
  linter-handled style filtered out, lesson violation is always a `BLOCKER`, no persistent report,
  no runner edits beyond approved trivial nits.

## Questions

- [x] ~~How do the findings travel from `review` to the runner — inline in the return block or via a
      temp file?~~ — **inline in the step's return block**, under a richer return contract than the
      harness default. No temp file: `present` posts the findings to the human and `resolve` acts on
      them without re-reading or re-deriving anything.
- [x] ~~Besides the just-delivered plan and the commit-history judgement, should `scope` also offer
      the vault's plans at the configured code-review status?~~ — **yes**, as extra options on the
      same `AskUserQuestion` call, alongside the just-delivered plan, the commit-history judgement
      and the free-text route.
