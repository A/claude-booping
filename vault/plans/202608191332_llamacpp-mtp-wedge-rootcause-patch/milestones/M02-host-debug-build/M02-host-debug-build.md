---
id: "02"
title: "Debug vehicle on the inference host"
sp: 6
status: done
plan: "vault/plans/202608191332_llamacpp-mtp-wedge-rootcause-patch/index.md"
---

# M02: Debug vehicle on the inference host

Goal: a `RelWithDebInfo` llama.cpp built on the inference host, runnable bare with the production serve command, whose token generation matches the shipped image.

Scope: the inference host `10.0.0.106` and a build tree at exactly `/home/anton/src/llama.cpp` on it — every task below and every later milestone means that path when it says "the build tree" — plus one committed runbook in the infra repo. No role changes, no image changes, no llama-swap configuration change — llama-swap is stopped while the bare server runs and started again afterwards.

Why bare and why on the host: the shipped image is built `--config Release`, so a backtrace off it carries no usable symbols, and every image rebuild costs about 30 minutes at `sm_86`. A host build with `ccache` rebuilds a one-line change in 2–5 minutes. Runtime speed is not expected to differ from the container — matching token generation is the check that the bare build is the same binary in every way that matters, not a separate result.

Constraints the worker must respect: `/` on that host is 86 % full with about 79 GB free and has a history of a filesystem-full incident, so the build tree is kept under that budget and `ccache` is capped. The model occupies roughly 44 GB across two 24 GB cards, so llama-swap must be stopped before the bare server starts — the two cannot coexist.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Install the missing toolchain on the host: `gcc-14`, `g++-14`, `ccache`, `gdb`, and the `perf` package for this kernel. Set a `ccache` maximum size that fits the remaining disk budget. Record what was installed and the resulting free space. | host `10.0.0.106`, `docs/debugging-the-wedge.md` | 1 | done |
| 2.2 | Clone llama.cpp at the commit `roles/llama_swap_image/defaults/main.yml` pins in `llama_swap_image_llama_commit`, apply every patch in `roles/llama_swap_image/files/patches/` in filename order with `git apply --verbose`, and build `-DCMAKE_BUILD_TYPE=RelWithDebInfo -DGGML_CUDA=ON -DGGML_BACKEND_DL=ON -DGGML_CPU_ALL_VARIANTS=ON -DCMAKE_CUDA_ARCHITECTURES=86` with `ccache` enabled. The build must reproduce the image's flags apart from the build type. | host build tree, `docs/debugging-the-wedge.md` | 3 | done |
| 2.3 | Write the bare-run recipe: the exact `llama-server` invocation, derived from the Q8 entry in `/opt/llama-swap/config.yaml` with `${server_cmd}` and `${qwen_base_params}` expanded, on a port that does not collide with llama-swap. Include the stop-llama-swap and restart-llama-swap steps around it, and a hang-detection wrapper that fires the M01 capture after 30 s of silence on the server's log rather than killing the process. | `docs/debugging-the-wedge.md`, `scripts/wedge-bare-run.sh` | 2 | done |

## Definition of Done

### Task 2.1

- [x] `gcc-14`, `g++-14`, `ccache`, `gdb` and `perf` all resolve on the host.
- [x] `ccache --max-size` is set to a value that leaves at least 60 GB free on `/`, and `df -h /` after the first full build confirms it.

### Task 2.2

- [x] `git apply --verbose` reports every patch in `files/patches/` applied, with no rejects.
- [x] `build/bin/llama-server --version` reports the same build number as the image's `system_fingerprint` (`b1-25ae3a9` at the pinned commit).
- [x] `file build/bin/llama-server` reports "with debug_info, not stripped".
- [x] A second build after touching one source file completes in under 5 minutes.

### Task 2.3

- [x] `scripts/wedge-bare-run.sh` starts the bare server, and `curl` against its port returns a completion.
- [x] The recipe's invocation matches the production Q8 command flag for flag, apart from `--port`; a diff of the two flag lists is recorded in the runbook.
- [x] Token generation measured against the bare server with `API` pointed at its port is within 2 % of the `Qwen3.8-27B-Q8` row in `docs/benchmarks.md`.
- [x] The wrapper fires the M01 capture on 30 s of log silence and leaves the process running, so the wedged state is still attachable afterwards.
- [x] The runbook states how to stop llama-swap before a bare run and start it after, and warns that the two cannot hold VRAM simultaneously.

## References

- `roles/llama_swap_image/files/Dockerfile` — the build flags to mirror, and the reason `--target llama-server` must not be used with `GGML_BACKEND_DL`.
- `roles/llama_swap_image/defaults/main.yml` — `llama_swap_image_llama_commit`, the commit to check out.
- `scripts/benchmark.sh` — measurement harness; `API` is an environment variable, so it points at the bare server without modification.
- `/opt/llama-swap/config.yaml` on the host — the source of the production serve command and of the `server_cmd` and `qwen_base_params` macros.

## Verify

```
ssh anton@10.0.0.106 'file ~/src/llama.cpp/build/bin/llama-server && ~/src/llama.cpp/build/bin/llama-server --version'
```
