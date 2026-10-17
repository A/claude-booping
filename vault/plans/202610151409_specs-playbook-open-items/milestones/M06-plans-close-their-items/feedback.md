# Feedback — M06

**Blocked (1/2)**: Tests names three behaviours; the third — "the transition still succeeds and stderr carries the warning" — is asserted only for its first half: `playbook-transition` swallows a hook's stderr when it exits 0.

Checked: the worker's report. Everything else (script, five edges, intake bullet, the groom cancel case's updated output) stands.

Next attempt: assert the warning where it is observable — a txtar case that runs the script itself (`sh`/exec of `playbooks/_scripts/open-items-follow-plan open` with `BOOPING_ARTIFACT` set and `BOOPING_BIN` a command exiting 1), asserting exit 0 and the `warning: open-items follow-plan failed (exit 1)` line on stderr. Keep the existing through-a-transition case. If a txtar case cannot run the script directly, say why and leave the existing case as is.
