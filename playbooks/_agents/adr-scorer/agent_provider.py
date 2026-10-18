"""promptfoo Python provider running one plugin agent as the session agent.

`claude -p --plugin-dir <repo> --agent <config.agent>` — the agent's own frontmatter decides
its tools and model, exactly as when a driver spawns it. The prompt is built the way the
live caller builds it: `config.preamble`, then each `config.paste` file's text under its
heading, then the test's `input` var under `config.input_heading`.

Output: `<tool_calls>N</tool_calls>` (tool_use blocks the agent emitted), then the agent's
reply in a `<return>` block, so `_lib/asserts/return.js` checks the reply's contract.

stdlib-only; `call_api` never raises.
"""

import json
import os
import subprocess
import tempfile
from pathlib import Path

REPO = Path(__file__).parents[3]
PLAYBOOKS = REPO / "playbooks"


def _prompt(config, variables):
    parts = [config.get("preamble", "").strip()]
    for heading, rel in (config.get("paste") or {}).items():
        parts.append(f"## {heading}\n\n{(PLAYBOOKS / rel).read_text(encoding='utf-8').strip()}")
    parts.append(f"## {config.get('input_heading', 'Input')}\n\n{variables['input'].strip()}")
    return "\n\n".join(p for p in parts if p) + "\n"


def _run(prompt, agent):
    cmd = ["claude", "-p", "--output-format", "stream-json", "--verbose",
           "--setting-sources", "project", "--plugin-dir", str(REPO), "--agent", agent]
    # subscription OAuth only — a stray API key would bill
    env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
    with tempfile.TemporaryDirectory() as tmp:
        res = subprocess.run(cmd, input=prompt, capture_output=True, text=True,
                             cwd=tmp, env=env, timeout=900)
    if res.returncode != 0:
        return {"error": f"claude exited {res.returncode}: {res.stderr[:2000]}"}
    tool_calls = 0
    result = None
    for line in res.stdout.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get("type") == "assistant":
            content = (event.get("message") or {}).get("content") or []
            tool_calls += sum(1 for block in content if block.get("type") == "tool_use")
        elif event.get("type") == "result":
            if event.get("is_error"):
                return {"error": f"claude error: {event.get('result')}"}
            result = event
    if result is None:
        return {"error": f"no result event; stdout: {res.stdout[:2000]}"}
    usage = result.get("usage") or {}
    prompt_tokens = usage.get("input_tokens", 0) or 0
    completion_tokens = usage.get("output_tokens", 0) or 0
    output = (f"<tool_calls>{tool_calls}</tool_calls>\n\n"
              f"<return>\n{(result.get('result') or '').strip()}\n</return>")
    return {"output": output,
            "tokenUsage": {"prompt": prompt_tokens, "completion": completion_tokens,
                           "total": prompt_tokens + completion_tokens}}


def call_api(prompt, options, context):
    try:
        config = (options or {}).get("config") or {}
        variables = (context or {}).get("vars") or {}
        if "input" not in variables:
            return {"error": "the test case sets no `input` var"}
        return _run(_prompt(config, variables), config["agent"])
    except Exception as e:  # noqa: BLE001 — the provider must never raise
        return {"error": f"provider crashed: {e}"}
