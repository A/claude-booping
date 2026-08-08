"""promptfoo Python provider wrapping the `claude -p` CLI on subscription auth.

Four modes, selected by the provider `config`:

- Step mode (`config.mode: step`): the promptfoo PROMPT is the step body — that is how a step
  dir's prompt set (`prompt.md`, `opus-5.md`, …) is run: each file is a labeled promptfoo
  prompt, sliced with `--filter-prompts`. The run's input comes from the test case's `input`
  var (prefixed with `**Target: <target>**` when that var is set), never from the prompt file,
  so the set's members differ only in their own text. Everything else matches consumer mode.
- Consumer mode (`config.entry` present): read the entry + `context` files (resolved
  absolute against the repo root, derived from this file's own location), wrap the
  promptfoo prompt (`{{input}}`) in the consumer instruction template, and run claude.
  With `output_mode: files` the run happens in an isolated temp cwd with edits accepted
  and Bash disallowed; the written tree is collected and serialized into the one output
  string the grader reads, followed by the consumer's reply (the step's return contract)
  in a trailing <return> block.
- Probe mode (`config.mode: probe`, no `entry`): the promptfoo-rendered prompt (a probe
  prompt file that embeds `{{input}}` itself) is passed straight to claude — no consumer
  template. `output_mode: files` is honored the same way as in consumer mode. Model/effort override via EVAL_CONSUMER_MODEL/EFFORT (the generation side,
  NOT the judge side, so swapping the model under test never swaps the judge).
- Grader mode (neither): the promptfoo-rendered `rubricPrompt` is passed straight to
  claude and its output returned verbatim. EVAL_JUDGE_MODEL/EFFORT override.

In both file-writing modes the prompt's <file path="…">…</file> blocks (if any) are the
run's CONTEXT CORPUS: they are written into the temp cwd and replaced in the prompt by a
path-only manifest, so the run must read them off disk the way a live step reads the
project's specs_dir. The judge is unaffected — its `{{input}}` var still carries the blocks
in full, so rubrics stay decidable. Seeded files count as output only when modified.

stdlib-only (json, os, re, subprocess, tempfile, pathlib) so plain `python3` runs it —
no uv/venv. `call_api` NEVER raises: every failure path returns `{"error": ...}` so
promptfoo always receives valid JSON.
"""

import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

# _playbooks/_lib/claude_provider.py -> parents[1] == _playbooks root. NOT process cwd:
# files-mode runs claude in a temp cwd, so entry/context must resolve against this fixed
# anchor. Suite entry:/context: paths are ROOT-relative (i.e. relative to _playbooks/).
ROOT = Path(__file__).parents[1]
LIB = Path(__file__).parent

# files-mode collection caps: past these the consumer misread the task, fail loud
MAX_FILES = 40
MAX_TOTAL_BYTES = 400_000
MAX_FILE_BYTES = 200_000

# An input may carry its context corpus as <file path="…">…</file> blocks (the same
# serialization the grader reads outputs in). In files mode those blocks are written to
# the consumer's cwd and replaced in the prompt by a path-only manifest line, so the
# consumer must READ them — the way a live step reads the project's specs_dir — while the
# judge still sees the full text in its `{{input}}` var.
SEED_BLOCK_RE = re.compile(r'^[ \t]*<file path="([^"]+)">\n(.*?)\n</file>[ \t]*$',
                           re.DOTALL | re.MULTILINE)


def _load_templates():
    """Parse consumer_prompt.txt into (template, text_rules, files_rules)."""
    text = (LIB / "consumer_prompt.txt").read_text(encoding="utf-8")
    parts = {}
    current = None
    buf = []
    for line in text.splitlines():
        if line.startswith("===") and line.endswith("===") and len(line) > 6:
            if current is not None:
                parts[current] = "\n".join(buf).strip("\n")
            current = line.strip("=")
            buf = []
        else:
            buf.append(line)
    if current is not None:
        parts[current] = "\n".join(buf).strip("\n")
    return parts["TEMPLATE"], parts["TEXT_RULES"], parts["FILES_RULES"]


def _resolve(env_var, config_val):
    """Env override wins over the config value; None when neither is set."""
    return os.environ.get(env_var) or config_val


def _run_claude(prompt, model, effort, extra_args=(), cwd=None):
    """Invoke `claude -p`, return (result_str, tokenUsage, cost, error).

    On any failure error is a non-empty string and the other fields are safe defaults.
    Never raises.
    """
    cmd = ["claude", "-p", "--output-format", "json", "--setting-sources", "project"]
    if model:
        cmd += ["--model", model]
    if effort:
        cmd += ["--effort", effort]
    cmd += list(extra_args)
    # subscription OAuth only — a stray API key would bill; strip it from the child env
    env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
    empty_usage = {"prompt": 0, "completion": 0, "total": 0}
    try:
        if cwd is not None:
            res = subprocess.run(cmd, input=prompt, capture_output=True, text=True,
                                 cwd=cwd, env=env, timeout=900)
        else:
            with tempfile.TemporaryDirectory() as tmp:
                res = subprocess.run(cmd, input=prompt, capture_output=True, text=True,
                                     cwd=tmp, env=env, timeout=900)
    except Exception as e:  # noqa: BLE001 — never raise out of the provider
        return "", empty_usage, 0.0, f"claude invocation failed: {e}"
    if res.returncode != 0:
        return "", empty_usage, 0.0, f"claude exited {res.returncode}: {res.stderr[:2000]}"
    try:
        data = json.loads(res.stdout)
    except (ValueError, TypeError) as e:
        return "", empty_usage, 0.0, f"claude JSON parse failed: {e}; stdout: {res.stdout[:2000]}"
    if data.get("is_error"):
        return "", empty_usage, 0.0, (f"claude API error {data.get('api_error_status')}: "
                                      f"{data.get('result')}")
    usage = data.get("usage") or {}
    prompt_tokens = usage.get("input_tokens", 0) or 0
    completion_tokens = usage.get("output_tokens", 0) or 0
    total_tokens = usage.get("total_tokens")
    if total_tokens is None:
        total_tokens = prompt_tokens + completion_tokens
    token_usage = {"prompt": prompt_tokens, "completion": completion_tokens,
                   "total": total_tokens}
    # subscription billing is notional; total_cost_usd may be missing or "N/A"
    try:
        cost = float(data.get("total_cost_usd"))
    except (TypeError, ValueError):
        cost = 0.0
    return data.get("result", ""), token_usage, cost, None


def _extract_seed(prompt):
    """Pull <file path="…">…</file> blocks out of the prompt. Returns (prompt, seed) where
    seed is [(posix relpath, text)] and each block is replaced in place by a `- <path>`
    manifest line. Returns (prompt, [], error) shape via the caller's check: a block whose
    path escapes the cwd is a fixture bug, so it fails loud."""
    seed = []
    bad = []

    def _sub(m):
        path, content = m.group(1).strip(), m.group(2)
        p = Path(path)
        if p.is_absolute() or ".." in p.parts:
            bad.append(path)
            return m.group(0)
        seed.append((p.as_posix(), content))
        return f"- {p.as_posix()}"

    stripped = SEED_BLOCK_RE.sub(_sub, prompt)
    if bad:
        return prompt, [], f"seed path escapes the run dir: {', '.join(bad)}"
    return stripped, seed, None


def _write_seed(cwd, seed):
    """Materialize the seed corpus into the run dir. Returns an error string or None."""
    root = Path(cwd)
    for rel, content in seed:
        dest = root / rel
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(content, encoding="utf-8")
        except OSError as e:
            return f"cannot seed {rel}: {e}"
    return None


def _collect_files(cwd, seed=()):
    """Walk the consumer's cwd -> [(posix relpath, text)]. Returns (files, error).
    Seeded context files are the input, not the output: they are collected only when the
    consumer changed them (steps that rewrite an artifact in place), never when untouched."""
    root = Path(cwd)
    seeded = dict(seed)
    files = []
    total = 0
    for p in sorted(root.rglob("*"), key=lambda p: p.relative_to(root).as_posix()):
        rel = p.relative_to(root)
        if not p.is_file() or any(part.startswith(".") for part in rel.parts):
            continue  # skip dirs and dot-prefixed paths (.claude/ etc.)
        key = rel.as_posix()
        if key in seeded:
            try:
                if p.read_text(encoding="utf-8") == seeded[key]:
                    continue  # untouched context file — not an output
            except (OSError, UnicodeDecodeError):
                return None, f"cannot re-read seeded file {key}"
        try:
            size = p.stat().st_size
        except OSError as e:
            return None, f"cannot stat {rel.as_posix()}: {e}"
        if size > MAX_FILE_BYTES:
            return None, f"consumer file too large: {rel.as_posix()} ({size} bytes)"
        total += size
        try:
            files.append((rel.as_posix(), p.read_text(encoding="utf-8")))
        except UnicodeDecodeError:
            return None, f"consumer wrote a non-UTF-8 file: {rel.as_posix()}"
    if len(files) > MAX_FILES:
        return None, f"consumer wrote {len(files)} files (cap {MAX_FILES})"
    if total > MAX_TOTAL_BYTES:
        return None, f"consumer wrote {total} bytes total (cap {MAX_TOTAL_BYTES})"
    return files, None


def _serialize_files(files):
    return "\n\n".join(f'<file path="{path}">\n{content}\n</file>' for path, content in files)


def _input_from_vars(context):
    """Step mode: the harness — not the prompt file — supplies the run's input.

    Mirrors what the live driver prepends above a step's input (`**Target: <X>**`), so a
    prompt body carries no `{{input}}` plumbing and two prompt files differ only in their
    own text. Vars still reach the judge untouched; this only builds the consumer side.
    """
    variables = (context or {}).get("vars") or {}
    text = variables.get("input")
    if text is None:
        return None, "step mode needs an `input` var; none was set on the test case"
    target = variables.get("target")
    if target:
        return f"**Target: {target}**\n\n{text}", None
    return text, None


def _consumer(prompt, config, context=None):
    """Consumer mode: a step + context + input -> produced document(s).

    The step is either `config.entry` (a file, ROOT-relative) or — with `mode: step` — the
    promptfoo prompt itself, which is how a step dir's prompt SET is run: each member is a
    promptfoo prompt with its own label, sliced with `--filter-prompts`.
    """
    template, text_rules, files_rules = _load_templates()
    output_mode = config.get("output_mode", "text")
    step_mode = config.get("mode") == "step"

    # entry + context resolve absolute against the repo root, not the process cwd
    if step_mode:
        atom_md = prompt
        input_md, err = _input_from_vars(context)
        if err:
            return {"error": err}
    else:
        try:
            atom_md = (ROOT / config["entry"]).read_text(encoding="utf-8")
        except OSError as e:
            return {"error": f"cannot read entry {config.get('entry')}: {e}"}
        input_md = prompt
    for ctx in config.get("context") or []:
        try:
            atom_md += f"\n\n---\n\n{(ROOT / ctx).read_text(encoding='utf-8')}"
        except OSError as e:
            return {"error": f"cannot read context {ctx}: {e}"}

    rules = files_rules if output_mode == "files" else text_rules
    full_prompt = (template.replace("<<OUTPUT_RULES>>", rules)
                   .replace("<<ATOM>>", atom_md)
                   .replace("<<INPUT>>", input_md))

    model = _resolve("EVAL_CONSUMER_MODEL", config.get("model"))
    effort = _resolve("EVAL_CONSUMER_EFFORT", config.get("effort"))

    if output_mode == "files":
        return _files_run(full_prompt, model, effort,
                          allow_no_files=bool(config.get("allow_no_files")))
    output, usage, cost, error = _run_claude(full_prompt, model, effort)
    if error:
        return {"error": error}
    return {"output": output, "cost": cost, "tokenUsage": usage, "error": None}


def _files_run(full_prompt, model, effort, allow_no_files=False):
    """Run claude in an isolated temp cwd (edits accepted, Bash disallowed), collect the
    written tree, and serialize it followed by the reply — the step's RETURN value (its
    "Return …" contract; manifest fallback) — as a <return> block so graders can check
    the return contract alongside the files. Text/grader runs have no such block.

    Any <file path="…"> block in the prompt is seeded into that cwd instead of being sent
    inline, so the run reads its context off disk exactly as a live step reads specs_dir."""
    full_prompt, seed, serr = _extract_seed(full_prompt)
    if serr:
        return {"error": serr}
    with tempfile.TemporaryDirectory() as cwd:
        werr = _write_seed(cwd, seed)
        if werr:
            return {"error": werr}
        result, usage, cost, error = _run_claude(
            full_prompt, model, effort, cwd=cwd,
            extra_args=("--permission-mode", "acceptEdits", "--disallowedTools", "Bash"))
        if error:
            return {"error": error}
        files, ferr = _collect_files(cwd, seed)
    if ferr:
        return {"error": ferr}
    # zero written files usually means the consumer misread the task — fail loud. Optimizer-style
    # steps legitimately edit nothing (undecidable red → question only); they opt out with
    # `allow_no_files: true` in the provider config.
    if not files and not allow_no_files:
        return {"error": f"files-mode consumer wrote no files; stdout: {result[:2000]}"}
    output = _serialize_files(files) + f"\n\n<return>\n{result.strip()}\n</return>"
    return {"output": output, "cost": cost, "tokenUsage": usage, "error": None}


def _passthrough(prompt, config, model_env, effort_env):
    """Send the promptfoo-rendered prompt to claude unchanged. With `output_mode: files`
    (probe configs for file-writing steps) the run gets the same isolated-cwd file
    plumbing as the consumer — otherwise a probe that asks to write a file stalls on a
    permission prompt and replies with chatter instead of the document."""
    model = _resolve(model_env, config.get("model"))
    effort = _resolve(effort_env, config.get("effort"))
    if config.get("output_mode") == "files":
        return _files_run(prompt, model, effort)
    output, usage, cost, error = _run_claude(prompt, model, effort)
    if error:
        return {"error": error}
    return {"output": output, "cost": cost, "tokenUsage": usage, "error": None}


def _tick_progress():
    """Append one line to $SWEEP_PROGRESS_FILE (sweep.sh's per-suite case counter).
    Consumer calls only — judge calls would inflate the count past the case total."""
    path = os.environ.get("SWEEP_PROGRESS_FILE")
    if not path:
        return
    try:
        with open(path, "a") as f:
            f.write(".\n")
    except OSError:
        pass


def call_api(prompt, options, context):
    try:
        config = (options or {}).get("config") or {}
        is_consumer = bool(config.get("mode") in ("step", "probe") or config.get("entry"))
        try:
            if config.get("mode") == "step" or config.get("entry"):
                return _consumer(prompt, config, context)
            if config.get("mode") == "probe":
                # generation-side passthrough: the probe prompt file IS the whole prompt
                return _passthrough(prompt, config, "EVAL_CONSUMER_MODEL", "EVAL_CONSUMER_EFFORT")
            return _passthrough(prompt, config, "EVAL_JUDGE_MODEL", "EVAL_JUDGE_EFFORT")
        finally:
            if is_consumer:
                _tick_progress()
    except Exception as e:  # noqa: BLE001 — the provider must never raise
        return {"error": f"provider crashed: {e}"}
