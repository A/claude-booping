---
id: "01"
title: "Persist the wedge evidence"
sp: 5
status: done
plan: "vault/plans/202608191332_llamacpp-mtp-wedge-rootcause-patch/index.md"
---

# M01: Persist the wedge evidence

Goal: every confirmed wedge writes a readable evidence bundle to disk before any recovery action destroys it.

Scope: the watchdog role only — `roles/inference_watchdog/templates/wedge-detector.py.j2`, `roles/inference_watchdog/defaults/main.yml`, and the README section that documents the detector's variables. No other role, no llama.cpp, no serve-command change. The detector already resolves the wedged model's PIDs via `wedged_pids_for(model)` and already logs an evidence line; this milestone makes that evidence survive.

The problem being solved: the engine's `slot` lines exist only in llama-swap's in-memory ring at `/logs/stream/{model}` — verified 2026-08-19, a healthy request emitted `launch_slot_`, five `print_timing` and one `release` there while `journalctl -t llama-swap` carried 155 lines and zero `slot` lines. Every recovery that restarts the container erases exactly the window that explains the freeze.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Write an evidence bundle on wedge confirmation, before the recovery ladder runs: the detector's evidence line, the tail of `/logs/stream/{model}`, `nvidia-smi -q`, and `/proc/{pid}/status` plus `/proc/{pid}/stack` for every wedged PID. Add a `--capture-now {model}` CLI flag that runs the same capture against a live model so it is testable without waiting for a freeze. Add `wedge_capture_dir` and `wedge_capture_log_lines` to the role defaults and create the directory from the role. | `roles/inference_watchdog/templates/wedge-detector.py.j2`, `roles/inference_watchdog/defaults/main.yml`, `roles/inference_watchdog/tasks/main.yml` | 3 | done |
| 1.2 | Add a backtrace to the bundle: `gdb -p {pid} -batch -ex "thread apply all bt"` per wedged PID, behind a `wedge_capture_backtrace` default that is on, skipping with a logged warning when `gdb` is absent rather than failing the capture. Document `wedge_capture_dir`, `wedge_capture_log_lines` and `wedge_capture_backtrace` in the README's wedge-detector variable table. | `roles/inference_watchdog/templates/wedge-detector.py.j2`, `roles/inference_watchdog/defaults/main.yml`, `README.md` | 2 | done |

## Definition of Done

### Task 1.1

- [x] `--capture-now Qwen3.8-27B-Q8` against a loaded model writes a directory under `wedge_capture_dir` containing the log tail, `nvidia-smi -q` output and one `/proc` dump per PID.
- [x] Capture runs before the first recovery call in `recover()` — verified by reading the function, the capture call precedes `unload(model)`.
- [x] A capture failure is logged and does not abort recovery: recovery still runs when the capture raises.
- [x] The log tail is bounded by `wedge_capture_log_lines`, so a captured bundle cannot grow without limit on a host that has filled its root filesystem before.
- [x] `ansible-playbook site.yml --tags watchdog -l llm --check --diff` shows the new defaults and the capture directory, and no unrelated drift.

### Task 1.2

- [x] The bundle contains one backtrace file per wedged PID when `gdb` is present.
- [x] With `gdb` absent the capture still completes, and the detector logs one warning naming the missing binary.
- [x] The README's variable table lists all three new variables with their defaults.

## References

- `roles/inference_watchdog/templates/wedge-detector.py.j2` — the file being extended; `recover()` is the ladder, `wedged_pids_for()` already resolves the target PIDs by `/proc/{pid}/cmdline`.
- `roles/inference_watchdog/defaults/main.yml` — the shape every `wedge_*` variable follows.
- `README.md`, section "Wedge detector (armed 2026-08-17)" — the variable table to extend.

## Verify

```
ansible-playbook site.yml --tags watchdog -l llm && ssh anton@10.0.0.106 'sudo /usr/local/bin/llama-swap-wedge-detector.py --capture-now Qwen3.8-27B-Q8 && find /var/log/llama-swap-wedge -type f | head -20'
```
