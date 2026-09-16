---
title: "llama.cpp MTP spec-decode wedge — instrument, root-cause, patch"
type: "bug"
status: in-progress
sp: 31
related_to: null
created: 2026-08-19 13:33
planned: null
started: 2026-08-19 19:22
completed: null
code_reviews: []
sessions:
- 8b4bf164-f5e0-40ef-bf3c-1beadbd30728
- 57e194c7-0c23-41eb-8671-c321fed8226b
retro: null
summary: Find and patch the llama.cpp MTP spec-decode wedge that freezes 
  generation once per 15 min, without costing tg
commit: 4d851d53507e19c8b154e068eec70b06b00533a3
tracker_provider: null
tracker_request: null
tracker_issue: null
return_to: null
agents:
  research-codebase: a62cd848b829c9f0b
  cross-review: aca8675e412e369b5
  develop-loop-M01: aa2960b59edfd7be8
  develop-loop-M02-M03: ace87a2a4acb7bbe5
reviewed_at: 2026-08-19 19:21
---

# llama.cpp MTP spec-decode wedge — instrument, root-cause, patch

## Context

**Current state.** `llama-server` serving `Qwen3.8-27B-Q8` with `--spec-type draft-mtp --spec-draft-n-max 3` freezes mid-decode under sustained agentic load. Measured on the 2026-08-19 benchmark series: six freezes across three runs, about one per 15 minutes of generation, 150–200 s of wall clock each. The signature is exact — healthy `slot print_timing` heartbeats, then silence with no `slot release` ever; main thread at 99 % CPU in a busy-wait; both GPUs at 0 % utilisation while the draft card stays clocked up; `/health` returns 200 throughout; the in-flight `llama_decode()` cannot be cancelled. Only a process kill recovers it. The wedge detector, rewritten 2026-08-19, now bounds each incident to an unload plus a targeted SIGKILL, but nothing prevents one.

**Motivation.** Two mitigations are deployed and neither can work. `--batch-size 512 --ubatch-size 512` makes every decode a single ubatch, which removes the multi-ubatch precondition — at a cost of 15–20 % prefill throughput. The llama.cpp#26827 patch ships in a locally built image, but its guard is `cparams.ctx_type == LLAMA_CONTEXT_TYPE_MTP && mtp_multi_ubatch`, and those flags hold `mtp_multi_ubatch` false, so the patch has never executed on this host. Upstream's own description of #26827 confirms the mismatch: it targets long-prompt prefills of 100k+ tokens, while these wedges fire mid-decode at 40–60k context. The precondition both mitigations address is absent and the freeze persists, so the mechanism is something else.

Every wedge also corrupts a benchmark run's timing and agentic score, and the score is deliberately left to reflect that — the freezes are part of how the model's quality is actually experienced.

**Scope.** This plan instruments the wedge, captures a backtrace, tests one minimal source patch against `llama.cpp`, and measures it. It covers the infra repo `~/Dev/@A/infra/ansible-inference` — its image-build role, watchdog role and host vars — plus a local llama.cpp build tree on the inference host. It does NOT cover `bench-score` or the benchmark harness in the `claude-booping` repo, does not pursue an upstream pull request, and does not consider any workaround that costs token-generation throughput.

## Decisions

- **Debug vehicle**: a `RelWithDebInfo` llama.cpp build on the inference host, run bare, rather than a debug container — the stock image is `Release` and effectively unreadable in a backtrace, and a container rebuild is about 30 minutes against 2–5 minutes for an incremental host build with `ccache`. The proven patch is folded back into the image pipeline afterwards.
- **Patch target**: `common_speculative_process()` returns with `ctx_dft` GPU work outstanding, and the KV rollback that follows mutates that context's memory. The first candidate is a single `llama_synchronize(ctx_dft)` before `process()` returns — on a context that is read a step later anyway, so the expected cost is near zero.
- **Throughput is the constraint, not a variable**: dropping `--spec-type`, lowering `--spec-draft-n-max` and single-GPU serving are all rejected up front, at 28–50 % of token generation. Only a source change and tg-neutral configuration are admissible.
- **Measurement is statistical**: wedge rate per hour of generation, taken from benchmark series per candidate, never from a single clean run. A wrong fix that merely shifts timing is indistinguishable from a right one at n=1.
- **`-b 2048` is a diagnostic, not a fix**: it is the only configuration in which #26827 actually runs, and restoring it reclaims the 15–20 % prefill currently spent on an inert guard. It is tested after a patch lands, not before.
- **No tg-neutral configuration fix remains**, checked 2026-08-19: `-b`/`-ub` are spent (the precondition they remove is not the mechanism), `--flash-attn` is already on via `qwen_base_params`, `--parallel` is already 1 for this entry, `GGML_CUDA_P2P` is moot because `nvidia-smi topo -p2p rw` reports `NS` between the two cards, and f16 KV does not fit at 262144 ctx. A source change is what is left.
- **Evidence is persisted before it is hunted**: the engine's `slot` lines live only in llama-swap's in-memory ring and die with every recovery, so the capture work comes first and makes every later wedge readable.

## Architecture

Two `llama_context` objects exist per speculative step: the target (`ctx_tgt`) and the MTP draft (`ctx_dft`), created in `common/speculative.cpp:2406` or `:2418`. `cparams.ctx_other` is set unconditionally for the MTP context at `speculative.cpp:2391`, but `llama_context`'s constructor honours it only for `LLM_ARCH_GEMMA4_ASSISTANT`, `LLM_ARCH_EAGLE3` and `LLM_ARCH_DFLASH` (`src/llama-context.cpp:145-161`). For every other architecture it stays null and each context builds its own KV cache (`src/llama-context.cpp:392-395`). Which architecture this model loads as is unresolved from source and is read off the load log in M02.

The per-step flow, and where synchronisation does and does not happen:

```
server-context.cpp:3588   llama_decode(ctx_tgt, batch_view)      target verify
server-context.cpp:3590   llama_synchronize(ctx_tgt)             ONLY if has_output
server-context.cpp:3653   common_speculative_process(...)
  speculative.cpp:1482      llama_get_embeddings_nextn(ctx_tgt)  -> ctx->synchronize()  (ctx_tgt)
  speculative.cpp:1514      llama_decode(ctx_dft, batch)         catch-up, NOT synchronized
  speculative.cpp:1541      ..._nextn_ith(ctx_tgt, ...)          -> synchronize()       (ctx_tgt)
                          returns with ctx_dft work outstanding
server-context.cpp:3820   common_sampler_sample_and_accept_n     synchronizes ctx_tgt
server-context.cpp:3852   slot.mem.seq_rm(...)                   partial accept
server-context.cpp:3899   slot.mem.seq_rm(...)                   full accept
  common/common.cpp:1623-1628  seq_rm calls common_context_seq_rm on BOTH ctx_tgt AND ctx_dft
```

So the KV cache of `ctx_dft` is mutated while that context's catch-up decode may still be executing on the device. Nothing in this chain orders the two. The draft loop at `speculative.cpp:1603` is safe by accident — the `common_sampler_sample` that follows it calls `llama_synchronize` internally (`common/sampling.cpp:595`) — but the catch-up decode has no such follower.

The hang is a device synchronise that never returns, not a host read of stale data: `llama_get_embeddings_nextn` is `ctx->synchronize()` followed by the read (`src/llama-context.cpp:3797-3801`), and an independent report on a Vulkan/RADV host has the main thread blocked forever in `ggml_vk_wait_for_fence` beneath exactly that symbol. Two different backends hanging in the same MTP path is what makes a driver-logic defect more likely than a CUDA-specific race, and it is why the fix is sought in `common/speculative.cpp` rather than in `ggml-cuda`.

Ruled out during research: CUDA graphs. `GGML_CUDA_GRAPHS` defaults to OFF (`ggml/CMakeLists.txt:117-119, 209`) and the image Dockerfile never enables it, so that code is not compiled in and `GGML_CUDA_DISABLE_GRAPHS` is not a variable this tree reads.

The delivery path already exists: `roles/llama_swap_image` fetches llama.cpp at a pinned commit, applies every file in `files/patches/` in filename order with `git apply --verbose` — failing the build if one does not apply — and layers the rebuilt binary and `.so` set over the stock llama-swap image.

## Milestones

| id | title | sp | status |
| --- | --- | --- | --- |
| 01 | [Persist the wedge evidence](milestones/M01-persist-wedge-evidence/M01-persist-wedge-evidence.md) | 5 | done |
| 02 | [Debug vehicle on the inference host](milestones/M02-host-debug-build/M02-host-debug-build.md) | 6 | done |
| 03 | [Capture and read the wedge](milestones/M03-capture-and-read-the-wedge/M03-capture-and-read-the-wedge.md) | 8 | done |
| 04 | [Candidate patch and measurement](milestones/M04-patch-and-measure/M04-patch-and-measure.md) | 8 | pending |
| 05 | [Ship the patch through the image pipeline](milestones/M05-ship-the-patch/M05-ship-the-patch.md) | 4 | pending |

## Implementation Order

```
M01 ──┐
      ├── M03 ── M04 ── M05
M02 ──┘
```

M01 and M02 are independent and may run in parallel. M03 needs both: M01 makes a production wedge readable, M02 gives a build whose backtrace has symbols.

## Key Files Reference

| File | Role |
|------|------|
| `roles/llama_swap_image/files/patches/` | where the candidate patch lands; applied in filename order, a patch that does not apply fails the build |
| `roles/llama_swap_image/files/Dockerfile` | pins `LLAMA_COMMIT`, builds `--config Release` for `sm_86`, layers over the stock image |
| `roles/llama_swap_image/defaults/main.yml` | `llama_swap_image_base` and `llama_swap_image_llama_commit` must agree; `llama_swap_image_rebuild` forces a rebuild at an unchanged tag |
| `roles/inference_watchdog/templates/wedge-detector.py.j2` | already resolves the wedged PID; the capture hook attaches here |
| `roles/llama_swap/templates/docker-compose.yml.j2` | journald log driver — carries llama-swap's own output only |
| `host_vars/llm.yml` | the Q8 serve command, where `-b 512` versus `-b 2048` is decided |
| `scripts/benchmark.sh` | existing pp/tg measurement; `API` is env-overridable so it also points at a bare server |
| `docs/benchmarks.md` | the baseline those numbers are compared against |

## Final Verification

- [ ] A backtrace of a wedged `llama-server`, taken with symbols, is committed under `docs/` and names the function the main thread is blocked in.
- [ ] A candidate patch exists in `roles/llama_swap_image/files/patches/`, applies cleanly at the pinned commit, and the image builds.
- [ ] Wedge rate before and after the patch is stated as wedges per hour of generation, each from at least one full benchmark series.
- [ ] Token generation after the patch is within 2 % of the pre-patch baseline in `docs/benchmarks.md`.
- [ ] `ansible-playbook site.yml --tags llama_swap_image,llama_swap -l llm --check --diff` reports no unexpected drift.
- [ ] README's wedge-detector section states the outcome, whichever way it went.

## Testing Strategy

Correctness here is statistical — the defect fires probabilistically, so no single run proves anything.

1. **Business-goal acceptance.** A human confirms the fix by comparing wedges per hour of generation across benchmark series, not by observing one clean run. The criterion is zero wedges across a series that previously averaged one per 15 minutes, with token generation unchanged within 2 %.
2. **Fast debug loop.** The bare host build plus a hang-detection wrapper: `llama-server` started from the M02 recipe, driven by a benchmark series, with the capture script firing on 30 s of log silence. Rebuild after a one-line patch is 2–5 minutes with `ccache`; a wedge is expected within about 15 minutes of load.
3. **User-facing validation.** `scripts/benchmark.sh` writes a full markdown report of pp and tg per id, directly comparable against the committed `docs/benchmarks.md`, so the throughput side of the trade is inspectable without reading any code.

## Deployment / config impact

| Env var / config | docker-compose / deploy | terraform / infra | CI workflow |
|------------------|-------------------------|-------------------|-------------|
| `llama_swap_image_tag` | bumped for the new patch set | n/a | n/a |
| `wedge_capture_dir` | new watchdog variable, host path for captured backtraces | n/a | n/a |
| `wedge_capture_log_lines` / `wedge_capture_backtrace` | new watchdog variables bounding the captured log tail and enabling the backtrace | n/a | n/a |

## Out of scope

- `bench-score` and the benchmark harness in `claude-booping` — freezes stay inside the score by explicit decision.
- An upstream pull request to `ggml-org/llama.cpp`. The evidence is written so one is cheap later, but filing it is not in this sprint.
- Any workaround costing token generation: dropping `--spec-type`, lowering `--spec-draft-n-max`, single-GPU serving. Measured trade, from `docs/benchmarks.md:76-78` on `Qwen3.6-27B`: 21.3 t/s without `--spec-type` against 39.8 with `draft-mtp`, so turning drafting off costs about 47 % of token generation — roughly 25 minutes per benchmark run against the 7 minutes the wedges actually cost.
- `--ubatch-size 2048`. It removes the same precondition `-b 512 -ub 512` already removes, at a VRAM cost instead of a prefill cost, and that precondition is demonstrably not the mechanism.
- Bumping `llama_swap_image_base` to a newer llama.cpp build. Changing the baseline mid-hunt would invalidate every before-and-after measurement.
- A second patch candidate. If the first fails, the run reports in chat rather than iterating further under this plan.

## CLAUDE.md impact

The infra repo's `CLAUDE.md` is currently untracked (`?? ../CLAUDE.md` at the repo root). No changes are required to it: the wedge-detector ladder, the patch-set mechanism and the measurement baseline are all documented in `README.md`, which M05 updates.
