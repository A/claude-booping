---
summary: Drive the benchmark plan through `/playbook develop` inline in this conversation under the guide's autonomy rules, answering every gate yourself, and end the sprint either finished or given up — both are results.
review_gate: null
---

# Run the sprint

The sprint is the measurement. It runs here, in this conversation: invoke `/playbook develop` on the entry's `plan` inside the workspace `prepare` cloned, on the branch it cut there, and drive it to its end. Every path the sprint touches is inside that workspace — its plan, its milestone bookkeeping and its commits all belong to the clone's own `vault/` and are thrown away with it; nothing here writes to the source repo. Never hand the sprint to a sub-agent and never re-implement any part of the develop playbook — this step only supplies the answers develop would otherwise ask the user for.

## Autonomy

The user is unavailable for the whole sprint. `guide.md`'s **Autonomy** section is the answer sheet — follow it as written rather than deciding afresh: it fixes what to answer at review gates and drift checks, that the branch is already settled, that abort approval is granted, and that `AskUserQuestion` is never called. Record every gate you auto-answered, with the answer given, for the return.

## Delegation

Every milestone and every retry goes to the entry's `worker` agent with the model, **the run's log path** and **this milestone's segment label** pinned in the briefing, per `guide.md`'s **Worker delegation** section. No other agent writes code — not the runner, not a default developer agent. One model, end to end, or the run measures nothing.

Stamp the log path once, before the first milestone: `~/.tmp/pi-developer/{ts}-{model_slug}.ndjson` with `{ts}` from `date +%Y%m%d-%H%M%S`. Every briefing after it — every later milestone, every retry — repeats that same path verbatim and varies only the `-S {milestone}` label. The whole run lands in that one file, and `measure` splits it into attempts by those labels; an invocation briefed without its label, or against a second path, is invisible to the process and cost layers.

## When the sprint gives up

A model that exhausts its attempts on a milestone has produced a result. Take develop's `fail` edge as `guide.md`'s **Failed sprints** section prescribes, note the milestone it died on as `fail@Mnn`, and continue — `measure` and `publish` run over the branch exactly as they would after a finished sprint. Never re-run the sprint from scratch, finish the milestone by hand, or discard the branch.

## Closing the step

Leave the workspace in place with the branch checked out, whatever work it carries, and the run's log where it was written — `measure` reads it. Nothing is pushed and nothing is written to the source repo's vault here.

## Return format

```markdown
## Notes:

- outcome: `pass` | `fail@Mnn` — {one line on how the sprint ended}
- milestones: {per milestone — attempts spent, commit sha, whether the DoD held first time}
- auto-answered gates: {one clause per gate — which gate, which answer}, or `none`
- log: `{the run's shared ndjson path}` — {n} segments, one per milestone invocation
- sprint report: {what develop's own wrap-up reported, in one line}
```
