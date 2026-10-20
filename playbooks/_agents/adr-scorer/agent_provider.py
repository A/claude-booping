"""promptfoo Python provider running one plugin agent as the session agent.

`claude -p --plugin-dir <repo> --agent <config.agent>` — the agent's own frontmatter decides
its tools and model, exactly as when a driver spawns it. `config.allowed_tools` (a list) is
passed as `--allowedTools`, pre-approving the commands a headless run cannot ask for. The prompt is built the way the
live caller builds it, each part under a `# {heading}`: `config.preamble`, then each
`config.paste` entry, then each `config.vars` var, then the test's `input` var under
`config.input_heading`.

A `config.paste` value is a repo-relative file, or `{file}#{heading}[,{heading}]` for only
those H2 sections of it, in the order named. A pasted text that already opens with its
`# {heading}` is not given a second one. `config.vars` maps a test var to its heading; a var
the test leaves empty reads `# {heading} — none named`.

Output: `<tool_calls>N</tool_calls>` (tool_use blocks the agent emitted), a `<tool_commands>`
block with one `{tool name} {input.command}` line per tool_use (the name alone when it has no
command), then the agent's reply in a `<return>` block. A test that also sets a `compare` var runs the agent a second
time on it — with `compare_{var}` in place of each `config.vars` var it sets — and adds that
reply in a `<compare>` block, for asserts that relate two replies.

stdlib-only; `call_api` never raises.
"""

import json
import os
import subprocess
import tempfile
from pathlib import Path

REPO = Path(__file__).parents[3]


def _sections(text, headings):
    found = {}
    current = None
    for line in text.splitlines():
        if line.startswith("## ") or line.startswith("# "):
            current = line[3:].strip() if line.startswith("## ") else None
            if current is not None:
                found[current] = [line]
            continue
        if current is not None:
            found[current].append(line)
    missing = [h for h in headings if h not in found]
    if missing:
        raise ValueError(f"no H2 section(s) {missing}")
    return "\n\n".join("\n".join(found[h]).strip() for h in headings)


def _paste(spec):
    rel, _, heads = spec.partition("#")
    text = (REPO / rel).read_text(encoding="utf-8")
    if heads:
        return _sections(text, [h.strip() for h in heads.split(",")])
    return text.strip()


def _part(heading, text):
    text = (text or "").strip()
    if not text:
        return f"# {heading} — none named"
    if text.startswith(f"# {heading}\n"):
        return text
    return f"# {heading}\n\n{text}"


def _prompt(config, variables, text):
    parts = [config.get("preamble", "").strip()]
    for heading, spec in (config.get("paste") or {}).items():
        parts.append(_part(heading, _paste(spec)))
    for var, heading in (config.get("vars") or {}).items():
        parts.append(_part(heading, variables.get(var)))
    parts.append(_part(config.get("input_heading", "Input"), text))
    return "\n\n".join(p for p in parts if p) + "\n"


def _run(prompt, agent, allowed_tools):
    cmd = ["claude", "-p", "--output-format", "stream-json", "--verbose",
           "--setting-sources", "project", "--plugin-dir", str(REPO), "--agent", agent]
    if allowed_tools:
        cmd += ["--allowedTools", *allowed_tools]
    # subscription OAuth only — a stray API key would bill
    env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
    with tempfile.TemporaryDirectory() as tmp:
        res = subprocess.run(cmd, input=prompt, capture_output=True, text=True,
                             cwd=tmp, env=env, timeout=900)
    if res.returncode != 0:
        return {"error": f"claude exited {res.returncode}: {res.stderr[:2000]}"}
    tool_commands = []
    result = None
    for line in res.stdout.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get("type") == "assistant":
            content = (event.get("message") or {}).get("content") or []
            for block in content:
                if block.get("type") == "tool_use":
                    command = (block.get("input") or {}).get("command")
                    name = block.get("name", "")
                    tool_commands.append(f"{name} {command}" if command else name)
        elif event.get("type") == "result":
            if event.get("is_error"):
                return {"error": f"claude error: {event.get('result')}"}
            result = event
    if result is None:
        return {"error": f"no result event; stdout: {res.stdout[:2000]}"}
    usage = result.get("usage") or {}
    prompt_tokens = usage.get("input_tokens", 0) or 0
    completion_tokens = usage.get("output_tokens", 0) or 0
    return {"tool_commands": tool_commands,
            "reply": (result.get("result") or "").strip(),
            "prompt": prompt_tokens, "completion": completion_tokens}


def _call(config, variables):
    allowed_tools = config.get("allowed_tools") or []
    runs = [_run(_prompt(config, variables, variables["input"]), config["agent"], allowed_tools)]
    if variables.get("compare"):
        compare_vars = {var: variables.get(f"compare_{var}", variables.get(var))
                        for var in (config.get("vars") or {})}
        runs.append(_run(_prompt(config, compare_vars, variables["compare"]), config["agent"],
                         allowed_tools))
    for run in runs:
        if "error" in run:
            return run
    tool_commands = [c for r in runs for c in r["tool_commands"]]
    commands = "\n".join(tool_commands)
    output = (f"<tool_calls>{len(tool_commands)}</tool_calls>\n\n"
              f"<tool_commands>\n{commands}\n</tool_commands>\n\n"
              f"<return>\n{runs[0]['reply']}\n</return>")
    if len(runs) > 1:
        output += f"\n\n<compare>\n{runs[1]['reply']}\n</compare>"
    prompt_tokens = sum(r["prompt"] for r in runs)
    completion_tokens = sum(r["completion"] for r in runs)
    return {"output": output,
            "tokenUsage": {"prompt": prompt_tokens, "completion": completion_tokens,
                           "total": prompt_tokens + completion_tokens}}


def call_api(prompt, options, context):
    try:
        config = (options or {}).get("config") or {}
        variables = (context or {}).get("vars") or {}
        if "input" not in variables:
            return {"error": "the test case sets no `input` var"}
        return _call(config, variables)
    except Exception as e:  # noqa: BLE001 — the provider must never raise
        return {"error": f"provider crashed: {e}"}
