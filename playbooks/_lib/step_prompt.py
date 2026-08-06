"""promptfoo prompt function returning a step's body exactly as the driver fetches it.

Declared by a suite as:

    prompts:
      - id: file://../../_lib/step_prompt.py:render
        label: rendered
        config:
          step: groom/intake

`render` shells out to `booping render-playbook <playbook> --step <step> --project
<fixture vault> --no-lessons` — the same command the driver runs, against the committed
fixture vault, so the prompt under test is the live body with every include expanded and
no Jinja left. A hand-maintained flattened copy drifts; this cannot.

The result is wrapped in `{% raw %}`: promptfoo runs every prompt — a function's return
value included — through nunjucks, which would otherwise choke on a body quoting `{{ … }}`
or `{% … %}` as example text.

Use a plain `file://<name>.md` prompt instead when the text under test is a *candidate*
rewrite (an optimizer's output) rather than the step body itself.

stdlib-only, like claude_provider.py — plain `python3` runs it.
"""

import os
import shutil
import subprocess
from pathlib import Path

# _lib/ -> playbooks/ (or the vault's _playbooks/, when _lib is reached through the symlink)
PLAYBOOKS = Path(__file__).resolve().parents[1]
FIXTURE_VAULT = PLAYBOOKS / "_fixtures" / "vault"


def _booping() -> str:
    """The CLI: $BOOPING_BIN, then the plugin checkout above this file, then PATH."""
    override = os.environ.get("BOOPING_BIN")
    if override:
        return override
    local = PLAYBOOKS.parent / "bin" / "booping"
    if local.is_file():
        return str(local)
    found = shutil.which("booping")
    if not found:
        raise RuntimeError(
            "booping CLI not found — set BOOPING_BIN, or run the suite from a plugin checkout"
        )
    return found


def render(context: dict) -> str:
    # Not derived from cwd: promptfoo runs the function with the cwd of the `promptfoo`
    # invocation, not the suite directory, so a `just smoke` from the repo root would
    # resolve the repo's own path as <playbook>/<step>.
    target = (context.get("config") or {}).get("step")
    if not target or "/" not in target:
        raise ValueError(
            f"step must be '<playbook>/<step>', got {target!r} — declare it under the "
            "prompt's `config:` in promptfooconfig.yaml"
        )

    playbook, step = target.split("/", 1)
    if not FIXTURE_VAULT.is_dir():
        raise RuntimeError(f"fixture vault missing at {FIXTURE_VAULT}")

    argv = [
        _booping(), "render-playbook", playbook,
        "--step", step,
        "--project", str(FIXTURE_VAULT),
        "--no-lessons",
    ]
    result = subprocess.run(argv, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"{' '.join(argv)} exited {result.returncode}: {result.stderr.strip()}"
        )

    body = result.stdout
    # Graph problems are in-band at exit 0 — a STOP notice would otherwise be evaluated
    # as if it were the step body.
    if "**STOP — tell the user:**" in body:
        raise RuntimeError(f"render of {target} carries a STOP notice:\n{body}")
    if "{% endraw %}" in body:
        raise RuntimeError(
            f"render of {target} contains a literal `{{% endraw %}}`, which would break "
            "the raw wrapper this function relies on"
        )
    return "{% raw %}" + body + "{% endraw %}"
