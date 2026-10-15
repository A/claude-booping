# Feedback — M01

**Blocked (1/2)**: the engine rejects the groomed `open_item` machine — `_parse_states` drops a state with `{instance}` in `artifact` that no subgraph references (`bad_state`, STOP notice on `render-playbook specs`), and an unreferenced state raises `orphan_state`; `playbook-transition specs … --state open_item` fails with `declares no states`.

Checked: worker report, `booping-python/src/booping/context/playbook.py` `_parse_states`. Tasks 1.1 and 1.2's files are in the working tree and stay — continue from them.

Next attempt: implement the new task 1.3 (develop-defaults D6) — an opt-in `standalone: true` key on a `states:` entry exempting it from both checks, set on `open_item`, documented in `documentation/playbook.md`, covered by cases for both the keyed and the unkeyed shape — then finish 1.2's transition case and continue with M02–M04. Keep the `plan=null` hook (`''` would leave an empty string; the item shape wants null) — accepted as develop-defaults D7.
