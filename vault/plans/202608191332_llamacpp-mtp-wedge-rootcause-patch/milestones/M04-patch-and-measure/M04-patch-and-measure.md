---
id: "04"
title: "Candidate patch and measurement"
sp: 8
status: pending
plan: "vault/plans/202608191332_llamacpp-mtp-wedge-rootcause-patch/index.md"
---

# M04: Candidate patch and measurement

Goal: one minimal source change to llama.cpp, tested against the bare build, with a wedge rate and a token-generation number on both sides of it.

Scope: the llama.cpp build tree at `/home/anton/src/llama.cpp` from M02, and two measurement runs. **Entry condition**: M03 completed task 3.3 with a located call site. If M03 stopped at task 3.2 because the wedge did not reproduce against the bare build, this milestone does not run — there is nothing to baseline and nothing to patch. Nothing is shipped here — the patch reaches `roles/llama_swap_image/files/patches/` in M05, only if the numbers justify it. The change M03's evidence points at takes precedence over the candidate written below; the candidate is what to write when the evidence confirms the standing hypothesis.

The candidate: add `llama_synchronize(ctx_dft)` before `common_speculative_impl_draft_mtp::process()` returns, so the catch-up decode at `common/speculative.cpp:1514` cannot still be executing when `seq_rm` mutates that context's KV cache at `tools/server/server-context.cpp:3852` or `:3899`. The expected cost is near zero, because `ctx_dft` is synchronized one step later anyway by `common_sampler_sample` (`common/sampling.cpp:595`) — but expected is not measured, which is what task 4.3 is for.

Measurement is statistical and the plan's central discipline: a wedge fires roughly once per 15 minutes of generation, so a single clean run proves nothing and must not be reported as a result.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Establish the pre-patch baseline: run one benchmark series against the unpatched bare build and record wedges per hour of generation, counting wedges from the detector's confirmations and from the M02 hang wrapper. Record generation hours from the run's own timing, not wall clock, so idle time between turns does not dilute the rate. | `docs/wedge-evidence.md` | 2 | pending |
| 4.2 | Write the candidate patch against the M02 build tree and rebuild. The change is one synchronisation call at the point M03's evidence identifies, defaulting to the end of `process()` when the evidence confirms the standing hypothesis. Keep it to the smallest change that closes the ordering — no refactor, no second call site. | host build tree, `docs/wedge-evidence.md` | 2 | pending |
| 4.3 | Measure the patched build: one benchmark series for the wedge rate, and `scripts/benchmark.sh` with `API` pointed at the bare server for prompt processing and token generation. Compare both against 4.1 and against the `Qwen3.8-27B-Q8` row of `docs/benchmarks.md`, and state the verdict in one paragraph. | `docs/wedge-evidence.md` | 4 | pending |

## Definition of Done

### Task 4.1

- [ ] The baseline states wedges per hour of generation, with the wedge count and the generation hours it was computed from.
- [ ] The benchmark series is driven with `/playbook model-benchmark local-llama Qwen3.8-27B-Q6 medium reasoning with direct orchestration`, and stopping it early is followed by `killall pi` — otherwise the run continues in the background and contaminates the next measurement.

### Task 4.2

- [ ] The diff is a single synchronisation call plus any comment explaining the ordering it enforces; `git diff --stat` shows one file changed.
- [ ] The patched tree builds clean and `llama-server --version` still reports the pinned build number.
- [ ] A short comment above the call names the race it closes and the two line references it orders, so the patch is reviewable by someone who has not read this plan.

### Task 4.3

- [ ] Post-patch wedges per hour is stated on the same basis as the baseline.
- [ ] Token generation is within 2 % of the pre-patch number, or the regression is stated in the verdict as a cost.
- [ ] The verdict paragraph says plainly whether the patch is worth shipping, and a null result — the wedge rate unchanged — is stated as such rather than presented as inconclusive.
- [ ] If the wedge rate is unchanged, the milestone ends here and the finding is reported in chat; no second candidate is attempted under this plan.

## References

- `docs/wedge-evidence.md` — M03's evidence document, which decides where the call goes; this milestone appends to it.
- `common/speculative.cpp` lines 1434-1550 in the M02 build tree — `process()`, the function being changed.
- `roles/llama_swap_image/files/patches/0001-mtp-serialize-multi-ubatch-decode.patch` — the shape a patch in this repo takes, and the guard that made it inert here.
- `scripts/benchmark.sh` and `docs/benchmarks.md` — the throughput harness and the committed baseline it is compared against.

## Verify

```
ssh anton@10.0.0.106 'cd ~/src/llama.cpp && git diff --stat && build/bin/llama-server --version'
```
