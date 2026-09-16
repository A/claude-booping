---
id: "05"
title: "Ship the patch through the image pipeline"
sp: 4
status: pending
plan: "vault/plans/202608191332_llamacpp-mtp-wedge-rootcause-patch/index.md"
---

# M05: Ship the patch through the image pipeline

Goal: the proven patch runs in production through the existing image-build role, and the repo's documentation states what was found either way.

Scope: `roles/llama_swap_image/`, `host_vars/llm.yml` and `README.md` in the infra repo. Runs only if M04's verdict says the patch is worth shipping; if M04 found no change in the wedge rate, this milestone reduces to its documentation task alone.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | Add the patch as `0002-{slug}.patch` in the role's patch directory, generated from the M02 build tree so it applies at the pinned commit, and bump `llama_swap_image_tag` so the new patch set is picked up. Converge the image and the deployment, and confirm from the role's own patch-manifest output that the running image carries both patches. | `roles/llama_swap_image/files/patches/0002-{slug}.patch`, `roles/llama_swap_image/defaults/main.yml` | 2 | pending |
| 5.2 | Read the Q8 entry's current `--batch-size` out of `host_vars/llm.yml` and record it as the revert target, then set `--batch-size 2048` keeping `--ubatch-size 512`, and confirm across one benchmark series that the wedge rate has not moved. This reclaims the 15–20 % prefill that `-b 512` currently spends on a precondition the patch now handles, and it is the first configuration in which llama.cpp#26827's guard actually executes. Revert if the wedge rate rises. | `host_vars/llm.yml` | 1 | pending |
| 5.3 | Update the README's wedge-detector section: what the evidence showed, whether the patch worked, the before-and-after wedge rate, and the `-b 2048` outcome. Correct the two claims the investigation falsified — that llama.cpp#26827 protects this host, and that `-b 512` is belt-and-braces rather than the only thing that was ever active. | `README.md` | 1 | pending |

## Definition of Done

### Task 5.1

- [ ] `git apply --verbose` accepts both patches in filename order at `llama_swap_image_llama_commit`; the image build reaches its final stage.
- [ ] The role's "Show which patches the image carries" output lists both patch filenames.
- [ ] `docker inspect -f '{{.Config.Image}}' llama-swap` on the host reports the new tag.

### Task 5.2

- [ ] The batch size in effect before the change is recorded in the task's notes, so the revert target is the real prior value rather than an assumed 512.
- [ ] The Q8 serve command in the live `/opt/llama-swap/config.yaml` shows `--batch-size 2048 --ubatch-size 512`.
- [ ] One benchmark series after the change reports a wedge rate no higher than M04's post-patch number, or the change is reverted and that is recorded.
- [ ] Prompt-processing throughput is re-measured with `scripts/benchmark.sh` and the gain is recorded against the previous `docs/benchmarks.md` row.

### Task 5.3

- [ ] The README states the wedge rate before and after, on the same per-hour-of-generation basis.
- [ ] The paragraph claiming `--batch-size 512` is belt-and-braces is corrected to record that it held #26827's guard false, so the patch never ran on this host.
- [ ] A null result is documented as plainly as a success would be.

## References

- `roles/llama_swap_image/tasks/main.yml` — how a patch-file change forces a rebuild at an unchanged tag, and the note that removed patches are not mirrored off the host.
- `roles/llama_swap_image/files/patches/0001-mtp-serialize-multi-ubatch-decode.patch` — the naming and format the new patch follows.
- `README.md`, sections "Recovery ladder, rewritten 2026-08-19", "The suspected root cause — llama.cpp#26827 (unmerged)" and "Both halves of the fix shipped 2026-08-18" — the three places carrying claims this milestone corrects.
- `host_vars/llm.yml`, the `Qwen3.8-27B-Q8` serve block — where the batch size is set.

## Verify

```
ansible-playbook site.yml --tags llama_swap_image,llama_swap -l llm --check --diff
```
