from __future__ import annotations

import os
import subprocess
from pathlib import Path

from booping.commands.render_playbook import compose, compose_step
from booping.context import Context
from booping.context.playbook import Playbook
from tests.helpers import get_fixture_path

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
BOOPING_BIN = PLUGIN_ROOT / "bin" / "booping"


FIXTURE_HOME = get_fixture_path("render-playbook-home")


def _load(name: str) -> Playbook:
    pbs = Playbook.load_all(
        vault=None, home_dir=FIXTURE_HOME, plugin_root=Path("/nonexistent/plugin-root")
    )
    return next(pb for pb in pbs if pb.name == name)


def _render(name: str) -> str:
    return compose(_load(name))


def _composed() -> str:
    return _render("composed")


def _section(out: str, heading: str) -> str:
    """The slice of `out` from `heading` up to the next `## ` heading (or end)."""
    start = out.index(heading)
    rest = out.find("\n## ", start + 1)
    return out[start:] if rest == -1 else out[start:rest]


# --- happy path -------------------------------------------------------------


def test_section_order() -> None:
    out = _composed()
    order = [
        out.index("# Composed Procedure"),
        out.index("## Execution graph"),
        out.index("## Gather"),
        out.index("## Draft"),
        out.index("## Named Step"),
        out.index("## Plain"),
    ]
    assert order == sorted(order)


def test_verbatim_preamble_passes_through() -> None:
    out = _composed()
    # Body inserted verbatim: the literal Jinja token is NOT evaluated.
    assert "token: {{ leftover }} — no Jinja evaluation happens here." in out


def test_no_notices_on_happy_path() -> None:
    out = _composed()
    assert "**STOP" not in out
    assert "**Note" not in out


def test_mermaid_edges() -> None:
    graph = _section(_composed(), "## Execution graph")
    assert "flowchart TD" in graph
    assert "  gather --> draft" in graph
    assert "  gather --> named-step" in graph
    assert "  draft --> plain" in graph
    assert "  named-step --> plain" in graph


def test_wave_list_parallel_separator() -> None:
    graph = _section(_composed(), "## Execution graph")
    assert "1. `gather`" in graph
    assert "2. `draft` ∥ `named-step`" in graph
    assert "3. `plain`" in graph


def test_wave_one_read_link_no_after() -> None:
    gather = _section(_composed(), "## Gather")
    gather_step = next(s for s in _load("composed").steps if s.name == "gather")
    assert f"Read [Gather]({gather_step.path}) for content." in gather
    assert "Gather the raw model-agent inputs and return a bulleted list." not in gather
    assert "- After:" not in gather


def test_later_wave_read_link_and_after_and_parallel() -> None:
    out = _composed()
    draft = _section(out, "## Draft")
    step = _load("composed").steps
    draft_step = next(s for s in step if s.name == "draft")
    assert f"Read [Draft]({draft_step.path}) for content." in draft
    assert "Draft the artifact from the gathered inputs." not in draft
    assert "- After: gather" in draft
    assert "- Parallel with: named-step" in draft


def test_single_member_wave_has_after_no_parallel() -> None:
    plain = _section(_composed(), "## Plain")
    assert "- After: draft, named-step" in plain
    assert "- Parallel with:" not in plain


def test_summary_directive() -> None:
    # The step's own summary is surfaced to the driver: it is where a step declares
    # execution hints (e.g. "one agent per feature") in its own domain words.
    out = _composed()
    assert "- Summary: Gather inputs." in _section(out, "## Gather")
    assert "- Summary: Draft the artifact." in _section(out, "## Draft")
    assert "- Summary: A plain step with no agent and no gate." in _section(out, "## Plain")


def test_summary_leads_the_instructions_block() -> None:
    draft = _section(_composed(), "## Draft")
    assert draft.index("- Summary:") < draft.index("- After:")


def test_model_agent_directive() -> None:
    gather = _section(_composed(), "## Gather")
    assert "- Run in a sub-agent — model sonnet, effort medium." in gather


def test_named_agent_directive() -> None:
    named = _section(_composed(), "## Named Step")
    assert "- Run in sub-agent: booping-researcher." in named


def test_gate_directive_verbatim() -> None:
    draft = _section(_composed(), "## Draft")
    assert (
        '- Review gate: stop after this step — "confirm the draft before continuing";'
        " continue only on explicit user confirmation." in draft
    )


def test_no_orphan_note_when_all_wired() -> None:
    assert "**Note" not in _composed()


# --- notices ----------------------------------------------------------------


def _assert_blocking(out: str) -> None:
    assert "## Execution graph" not in out
    assert "\n## " not in out  # no step sections


def test_missing_step_notice() -> None:
    out = _render("missing-step")
    assert (
        "**STOP — tell the user:** step 'ghost' is referenced in the graph but"
        " ghost/prompt.md does not exist. Do not execute this playbook." in out
    )
    _assert_blocking(out)


def test_unknown_dep_notice() -> None:
    out = _render("unknown-dep")
    assert (
        "**STOP — tell the user:** 'ghost' is listed as a dependency of 'b' but is"
        " not a step in the graph. Do not execute this playbook." in out
    )
    _assert_blocking(out)


def test_cycle_notice() -> None:
    out = _render("cycle")
    assert (
        "**STOP — tell the user:** the graph has a cycle: a → b → a."
        " Do not execute this playbook." in out
    )
    _assert_blocking(out)


def test_no_graph_notice() -> None:
    out = _render("no-graph")
    assert (
        "**STOP — tell the user:** playbook 'no-graph' has no graph: in its"
        " frontmatter. Do not execute this playbook." in out
    )
    _assert_blocking(out)


def test_inline_in_parallel_notice() -> None:
    out = _render("inline-in-parallel")
    assert (
        "**STOP — tell the user:** step 'one' runs inline (agent: null) but shares a"
        " wave with other steps; inline steps cannot run in parallel."
        " Do not execute this playbook." in out
    )
    _assert_blocking(out)


def test_orphan_note_non_blocking() -> None:
    out = _render("orphan")
    assert (
        "**Note — tell the user:** step 'extra' exists on disk but is not wired"
        " into the graph; it will not run." in out
    )
    # Non-blocking: the graph + wired step section still render.
    assert "## Execution graph" in out
    assert "## A" in out
    assert "**STOP" not in out


# --- opt-in Jinja -----------------------------------------------------------


def _ctx() -> Context:
    return Context.assemble()


def _threshold(ctx: Context) -> str:
    return str(ctx.config["sprint"]["default_threshold_sp"])


def test_non_jinja_playbook_output_unchanged() -> None:
    # A non-jinja playbook renders identically with or without context (paths normalised).
    golden = (FIXTURE_HOME.parent / "composed-prejinja.golden.md").read_text()
    actual = compose(_load("composed"), context=_ctx()).replace(str(FIXTURE_HOME), "{HOME}")
    assert actual == golden


def test_jinja_preamble_renders_expression_and_include() -> None:
    ctx = _ctx()
    out = compose(_load("jinja-composed"), context=ctx)
    assert f"Preamble threshold: {_threshold(ctx)}" in out
    assert "## Project Context" in out


def test_jinja_wave_one_step_shows_step_command() -> None:
    first = _section(compose(_load("jinja-composed"), context=_ctx()), "## First")
    assert "Run `booping render-playbook jinja-composed --step first` for content." in first
    assert "Wave-one body" not in first


def test_jinja_later_wave_step_shows_step_command() -> None:
    second = _section(compose(_load("jinja-composed"), context=_ctx()), "## Second")
    assert "Run `booping render-playbook jinja-composed --step second` for content." in second
    assert "Read [Second]" not in second


def test_non_jinja_step_keeps_read_link() -> None:
    draft = _section(compose(_load("composed"), context=_ctx()), "## Draft")
    assert "Read [Draft]" in draft
    assert "--step" not in draft


def test_jinja_without_context_stops() -> None:
    out = compose(_load("jinja-composed"))
    assert (
        "**STOP — tell the user:** playbook 'jinja-composed' sets jinja: true but was"
        " rendered without project context. Do not execute this playbook." in out
    )
    _assert_blocking(out)


def test_broken_step_body_does_not_break_compose() -> None:
    # Step bodies are never rendered at compose time — the error waits for the fetch.
    out = compose(_load("jinja-broken"), context=_ctx())
    assert "**STOP" not in out
    assert "## Execution graph" in out
    assert "# Broken" in out


def test_jinja_error_is_in_band_stop_notice_at_fetch_time() -> None:
    out = compose_step(_load("jinja-broken"), "only", _ctx())
    assert "**STOP — tell the user:** Jinja rendering of step 'only' failed:" in out
    assert "TemplateNotFound" in out
    assert "Traceback" not in out


def test_step_body_only_non_jinja() -> None:
    pb = _load("composed")
    step = next(s for s in pb.steps if s.name == "draft")
    out = compose_step(pb, "draft", _ctx())
    assert out == step.body
    assert "## Draft" not in out
    assert "Review gate:" not in out
    assert "Parallel with:" not in out


def test_step_body_only_jinja_rendered() -> None:
    ctx = _ctx()
    out = compose_step(_load("jinja-composed"), "first", ctx)
    assert out.startswith(f"Wave-one body, threshold {_threshold(ctx)}.")
    assert "## Project Context" in out
    assert "## First" not in out
    assert "Run in a sub-agent" not in out


# --- include search chain ---------------------------------------------------


def _includes() -> str:
    return compose(_load("jinja-includes"), context=_ctx())


def _includes_step(name: str) -> str:
    return compose_step(_load("jinja-includes"), name, _ctx())


def test_include_from_playbook_dir_by_bare_name() -> None:
    # Preamble pulls `_references/rules.md` sitting next to playbook.md.
    assert "RULES-OK" in _includes()


def test_include_from_step_dir_by_bare_name() -> None:
    assert "STEP-FIXTURE-OK" in _includes_step("first")


def test_include_from_playbook_root_by_root_relative_name() -> None:
    assert "ROOT-LIB-OK" in _includes_step("first")


def test_plugin_partials_still_reachable() -> None:
    first = _includes_step("first")
    assert first.index("## Project Context") > first.index("STEP-FIXTURE-OK")


def test_relative_includes_resolve_against_including_file() -> None:
    # rules.md → ./deep/one.md → ../plain.md (depth 3, both `./` and `../`).
    out = _includes()
    assert "DEEP-ONE-OK" in out
    assert "PLAIN-OK" in out


def test_later_wave_step_fetch_resolves_playbook_dir_include() -> None:
    assert "RULES-OK" in compose_step(_load("jinja-includes"), "second", _ctx())


def _plant_roots(tmp_path: Path, *scopes: str) -> tuple[Path, Path, Path]:
    """Core / global / local roots, each carrying `_lib/shared.md` for the named
    scopes, plus a jinja playbook in the local root that includes it.
    """
    core, home, vault = tmp_path / "core", tmp_path / "home", tmp_path / "vault"
    roots = {
        "core": core / "playbooks",
        "global": home / "_playbooks",
        "local": vault / "_playbooks",
    }
    for scope, root in roots.items():
        (root / "_lib").mkdir(parents=True)
        if scope in scopes:
            (root / "_lib" / "shared.md").write_text(f"MARKER-{scope}\n")
    pb_dir = roots["local"] / "inc"
    (pb_dir / "only").mkdir(parents=True)
    (pb_dir / "playbook.md").write_text(
        "---\nname: inc\ntitle: Inc\njinja: true\ngraph:\n  only: []\n---\nPreamble.\n"
    )
    (pb_dir / "only" / "prompt.md").write_text(
        '---\nsummary: only\nagent: sonnet:medium\n---\n{% include "_lib/shared.md" %}\n'
    )
    return core, home, vault


def _render_inc(tmp_path: Path, *scopes: str) -> str:
    core, home, vault = _plant_roots(tmp_path, *scopes)
    pbs = Playbook.load_all(vault=vault, home_dir=home, plugin_root=core)
    pb = next(p for p in pbs if p.name == "inc")
    return compose_step(pb, "only", _ctx())


def test_root_relative_include_prefers_local(tmp_path: Path) -> None:
    assert "MARKER-local" in _render_inc(tmp_path, "core", "global", "local")


def test_root_relative_include_falls_back_to_global(tmp_path: Path) -> None:
    assert "MARKER-global" in _render_inc(tmp_path, "core", "global")


def test_root_relative_include_falls_back_to_core(tmp_path: Path) -> None:
    assert "MARKER-core" in _render_inc(tmp_path, "core")


def test_missing_include_is_blocking_notice(tmp_path: Path) -> None:
    out = _render_inc(tmp_path)
    assert "**STOP — tell the user:** Jinja rendering of step 'only' failed:" in out
    assert "TemplateNotFound" in out
    assert "Traceback" not in out


# --- CLI-level --------------------------------------------------------------


def test_requires_project_without_project_exits_1(tmp_path: Path) -> None:
    # HOME is isolated (autouse fixture); plant a requires_project playbook in its
    # default global root. tmp cwd has no `.booping` — no project attached.
    pb_dir = Path(os.environ["HOME"]) / "Claude" / "_playbooks" / "gated"
    (pb_dir / "steps").mkdir(parents=True)
    (pb_dir / "playbook.md").write_text(
        "---\nname: gated\ntitle: Gated\nrequires_project: true\n"
        "graph:\n  only: []\n---\nPreamble.\n"
    )
    (pb_dir / "steps" / "only.md").write_text("---\nname: only\n---\nstep body\n")
    result = subprocess.run(
        [str(BOOPING_BIN), "render-playbook", "gated"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert result.stdout == ""
    assert "requires a booping project" in result.stderr


def test_missing_playbook_exits_1(tmp_path: Path) -> None:
    # tmp cwd has no `.booping` and HOME is isolated (autouse fixture) — no playbooks.
    result = subprocess.run(
        [str(BOOPING_BIN), "render-playbook", "definitely-nonexistent"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert result.stdout == ""
    assert "definitely-nonexistent" in result.stderr


def test_output_to_file(tmp_path: Path) -> None:
    # Plant the composed fixture in the isolated HOME's global root, render to a file.
    src = get_fixture_path("render-playbook-home") / "_playbooks" / "composed"
    dst = Path(os.environ["HOME"]) / "Claude" / "_playbooks" / "composed"
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["cp", "-r", str(src), str(dst)], check=True)
    out_file = tmp_path / "out.md"
    result = subprocess.run(
        [str(BOOPING_BIN), "render-playbook", "composed", "--output", str(out_file)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert result.stdout == ""
    text = out_file.read_text()
    assert "## Execution graph" in text
    assert "token: {{ leftover }}" in text


def _plant_vault(tmp_path: Path, *names: str) -> Path:
    """A bare vault dir (no `.booping` marker) carrying the named fixture playbooks."""
    vault = tmp_path / "vault"
    (vault / "_playbooks").mkdir(parents=True)
    for name in names:
        src = FIXTURE_HOME / "_playbooks" / name
        subprocess.run(["cp", "-r", str(src), str(vault / "_playbooks" / name)], check=True)
    return vault


def test_project_flag_satisfies_requires_project(tmp_path: Path) -> None:
    vault = _plant_vault(tmp_path, "requires-project")
    result = subprocess.run(
        [str(BOOPING_BIN), "render-playbook", "requires-project", "--project", str(vault)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "## Execution graph" in result.stdout
    assert "Only body." not in result.stdout


def test_step_prints_body_only_and_logs(tmp_path: Path) -> None:
    vault = _plant_vault(tmp_path, "composed")
    body = next(s for s in _load("composed").steps if s.name == "draft").body
    result = subprocess.run(
        [
            str(BOOPING_BIN), "render-playbook", "composed",
            "--step", "draft", "--project", str(vault),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert result.stdout == body
    assert "## Draft" not in result.stdout
    log = (vault / "_booping" / ".booping.log").read_text()
    assert "[render-playbook] composed --step draft" in log


def test_step_renders_jinja_body(tmp_path: Path) -> None:
    vault = _plant_vault(tmp_path, "jinja-composed")
    result = subprocess.run(
        [
            str(BOOPING_BIN), "render-playbook", "jinja-composed",
            "--step", "first", "--project", str(vault),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "{{" not in result.stdout
    assert "## Project Context" in result.stdout


def test_unknown_step_exits_1(tmp_path: Path) -> None:
    vault = _plant_vault(tmp_path, "composed")
    result = subprocess.run(
        [
            str(BOOPING_BIN), "render-playbook", "composed",
            "--step", "nope", "--project", str(vault),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert result.stdout == ""
    assert "step not found" in result.stderr


def test_cli_renders_to_stdout(tmp_path: Path) -> None:
    src = get_fixture_path("render-playbook-home") / "_playbooks" / "composed"
    dst = Path(os.environ["HOME"]) / "Claude" / "_playbooks" / "composed"
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["cp", "-r", str(src), str(dst)], check=True)
    result = subprocess.run(
        [str(BOOPING_BIN), "render-playbook", "composed"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "## Execution graph" in result.stdout
