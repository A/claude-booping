# Request

> our goal - get best tg and don't waste time on reloads/watchdog, so draft n, and other options are bad. What i offer is to update cpp code to fix issue, mb apply some config changes doesnt affect t/s

> 1. we added persistent logs, 2. is there any way to debug it live, i mean mb we spin of llama.cpp on host, and there test if it makes it faster? plus add extra logs to see better evidences

> why -u 2048 may fix it? can you groom plan with /playbook groom ? For running benchmark you can run `/playbook model-benchmark local-llama Qwen3.8-27B-Q6 medium reasoning with direct orchestration.` if you stop it, do `killall pi` too, otherwise it will continue to work.

## Task type

`bug` — a defect with a reproducible symptom: `llama-server` stops advancing mid-generation, the request never completes, and only a process kill recovers it. Observed behaviour diverges from expected behaviour, which is the definition of this type.

- Not `feature`: no new user-facing capability is asked for. Test — would a user gain something they could not do before? No; they regain generation that already works most of the time.
- Not `refactoring`: the outcome is explicitly a behaviour change (the hang stops happening). Test — is the DoD "no user-visible behaviour change"? The opposite.

The defect is in a vendored upstream dependency (`llama.cpp`), not in this repo's own code. That does not change the type; it changes where the fix lands — a patch file in `roles/llama_swap_image/files/patches/`, the mechanism that already carries llama.cpp#26827.

## Problem

Today, under sustained agentic load, `llama-server` serving `Qwen3.8-27B-Q8` with `--spec-type draft-mtp` freezes mid-decode. Measured on the 2026-08-19 benchmark series: six freezes across three runs, roughly one per 15 minutes of generation. Each one costs 150–200 s of wall clock and corrupts the run's timing and agentic score.

The freeze signature is exact and repeatable: healthy `print_timing` heartbeats every ~3 s up to some `n_gen`, then silence — no further heartbeat, no `release` line ever; main thread pinned at 99 % CPU in a busy-wait; both GPUs at 0 % utilisation while the draft card stays clocked up; `/health` returns 200 throughout; an in-flight `llama_decode()` cannot be cancelled. Only a kill recovers it.

Two mitigations are already deployed and neither removes the freeze:

- `--batch-size 512 --ubatch-size 512` makes every decode a single ubatch, which removes the multi-ubatch race precondition that llama.cpp#26827 targets. It costs 15–20 % prefill throughput.
- The llama.cpp#26827 patch itself ships in a locally built image. Its guard is `cparams.ctx_type == LLAMA_CONTEXT_TYPE_MTP && mtp_multi_ubatch`, and the flags above hold `mtp_multi_ubatch` at false, so the patch never executes on this host.

So the precondition both mitigations address is already absent and the freeze persists — the mechanism is something else. The next lead named in the infra README is llama.cpp#23268, spec-decode streams intermittently hanging, reported for `draft-mtp` and `ngram-mod` alike, which points at the speculative-decode driver rather than the MTP graph.

What must change: the freeze stops, without giving up token-generation throughput. Every throughput-costing workaround is out of scope by the user's constraint — dropping `--spec-type` (−28…50 % tg), lowering `--spec-draft-n-max`, single-GPU serving. That leaves two admissible levers: a source change to `llama.cpp`, and configuration that does not move tg.

The current recovery path is the wedge detector, patched and deployed 2026-08-19: it now unloads, verifies against the wedged PIDs, SIGKILLs only those PIDs, and restarts the container only as a last lever. That bounds the damage per freeze but does not prevent one.

## Clarifications and Decisions

- Throughput-costing workarounds are rejected up front: no dropping `--spec-type`, no lowering `--spec-draft-n-max`, no single-GPU serving.
- `--ubatch-size 2048` is not a candidate. It removes the same multi-ubatch precondition that `-b 512 -ub 512` already removes, at a VRAM cost instead of a prefill cost, and that precondition is demonstrably not the mechanism.
- `-b 2048` with `-ub 512` is a diagnostic, not a fix: it is the only configuration in which llama.cpp#26827 actually runs, and it returns the 15–20 % prefill that `-b 512` currently spends on an inert guard.
- Debugging runs against a bare `llama-server` on the host rather than the container: the win is symbols (`RelWithDebInfo`), a ~2–5 min incremental rebuild instead of a ~30 min image build, and free access to `CUDA_LAUNCH_BLOCKING`, `GGML_CUDA_DISABLE_GRAPHS` and `GGML_SCHED_DEBUG`. Runtime speed is not expected to differ; matching t/s is the check that the bare build matches the image.
- Persistent logging landed 2026-08-19 as the journald log driver plus `logLevel: debug`. It captures llama-swap's own output; whether the engine's `slot` lines reach it is unverified and is a prerequisite for using it as evidence.
- The benchmark doubles as the load generator and the measurement instrument: `/playbook model-benchmark local-llama Qwen3.8-27B-Q6 medium reasoning with direct orchestration`. Stopping a run requires `killall pi` or it keeps working.
- Scope answers, 2026-08-19: the sprint runs against the infra repo `~/Dev/@A/infra/ansible-inference` — `claude-booping`'s vault holds the plan only.
- `bench-score` is explicitly out of scope. Freezes stay inside the benchmark score: they are part of how the model's quality is actually experienced, so a wedge column would hide signal rather than clean it up.
- Terminal outcome is a local patch, measured: a patch under `roles/llama_swap_image/files/patches/` running on the box, with a before/after wedge rate and a no-tg-regression check. An upstream PR is not in the DoD.
- Wedge rate is measured with benchmark series per candidate — `/playbook model-benchmark local-llama Qwen3.8-27B-Q6 medium reasoning with direct orchestration` — not a purpose-built load generator. Stopping a run needs `killall pi`.
- If root cause does not yield, the plan does not branch into a fallback deliverable: report the finding in chat and stop.
