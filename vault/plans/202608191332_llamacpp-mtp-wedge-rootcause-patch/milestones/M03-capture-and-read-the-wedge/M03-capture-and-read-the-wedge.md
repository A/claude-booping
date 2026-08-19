---
id: "03"
title: "Capture and read the wedge"
sp: 8
status: pending
plan: "vault/plans/202608191332_llamacpp-mtp-wedge-rootcause-patch/index.md"
---

# M03: Capture and read the wedge

Goal: a backtrace of a wedged `llama-server`, taken with symbols, that names the function the main thread is blocked in — turning the freeze from a hypothesis into a located fact.

Scope: reproduction and observation only. No source change to llama.cpp, no patch, no role change beyond what M01 and M02 already landed. The output is an evidence document committed to `docs/` in the infra repo. Both M01 (capture on wedge) and M02 (a build with symbols) must be done first.

The standing hypothesis, to be confirmed or refuted rather than assumed: `common_speculative_process()` returns at `common/speculative.cpp:1550` with the catch-up `llama_decode(ctx_dft, batch)` from `:1514` still outstanding, and the KV rollback at `tools/server/server-context.cpp:3852` or `:3899` then mutates that context's memory through `seq_rm`, which touches both contexts (`common/common.cpp:1623-1628`). A backtrace blocked inside `llama_context::synchronize()` or a backend fence wait, reached from the MTP path, supports it. A backtrace anywhere else refutes it, and the refutation is the milestone's result just as much as a confirmation.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Resolve the two facts the source could not settle: which `LLM_ARCH_*` the model loads as, read from the server's load log, and therefore whether `cparams.ctx_other` is honoured for it (`src/llama-context.cpp:145-161`) — that is, whether the target and MTP contexts share one KV cache or hold two. Record both with the log line they came from. | `docs/wedge-evidence.md` | 2 | pending |
| 3.2 | Reproduce the wedge against the bare build from M02 by driving a benchmark series at it, and capture the state: `perf top -p {pid}` for the spinning symbol, then `gdb -p {pid} -batch -ex "thread apply all bt full"`, then `cuda-gdb` attached to establish whether a kernel is resident on the device or the host is waiting on an event that never fires. Leave the process alive between captures. | `docs/wedge-evidence.md` | 4 | pending |
| 3.3 | Write the evidence document: the full backtrace, the `perf` symbol, the `cuda-gdb` verdict, the exact flags and the model architecture, and one paragraph stating whether the standing hypothesis is confirmed or refuted and on what evidence. | `docs/wedge-evidence.md` | 2 | pending |

## Definition of Done

### Task 3.1

- [ ] The architecture name appears in the document, quoted from the `llm_load_print_meta: arch` line of a real load.
- [ ] The document states whether `ctx_tgt` and `ctx_dft` share a KV cache, citing `src/llama-context.cpp:145-161` and the architecture just established.

### Task 3.2

- [ ] A wedge is reproduced against the bare build, and the capture bundle exists.
- [ ] `thread apply all bt full` output is captured with resolved symbols — no frame in the main thread's stack reads `??`.
- [ ] The `cuda-gdb` observation distinguishes a resident kernel from a host-side wait, and the document says which it is.
- [ ] If a wedge does not reproduce against the bare build within two benchmark series, that is recorded as the finding — it would mean the container or llama-swap is part of the precondition — and the milestone stops there rather than continuing to task 3.3 as if it had. **M04 does not start in that case**: it has no reproduction to baseline against and no located call site to patch. Report the non-reproduction in chat and stop the sprint there.

### Task 3.3

- [ ] `docs/wedge-evidence.md` names the function the main thread is blocked in, with the call chain above it.
- [ ] The document states confirmed or refuted for the standing hypothesis, and what evidence decides it.
- [ ] The exact `llama-server` flags and the build commit are recorded, so the evidence is reproducible by someone who was not there.

## References

- `docs/debugging-the-wedge.md` — the runbook M02 wrote; the bare-run recipe and hang wrapper come from it.
- `common/speculative.cpp` in the M02 build tree, function `common_speculative_impl_draft_mtp::process()` at lines 1434-1550 — the code the hypothesis is about.
- `tools/server/server-context.cpp` lines 3588, 3653, 3852, 3899 — the target decode, the `process()` call, and the two rollback sites.
- `README.md`, section "The incident it was built from (2026-08-17, Qwen3.8-27B-Q8, task 19045)" — the previously recorded observations this evidence extends.

## Verify

```
ssh anton@10.0.0.106 'grep -c "llama_context::synchronize\|ggml_backend_sched_synchronize\|??" /var/log/llama-swap-wedge/*/backtrace-*.txt'
```
