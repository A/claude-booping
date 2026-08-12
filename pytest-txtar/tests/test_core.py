from __future__ import annotations

import sys
from pathlib import Path

import pytest

from pytest_txtar import txtar
from pytest_txtar.case import CaseError, TxtarSpec, load_case
from pytest_txtar.compare import compare, line_matches, normalizer, report, text_matches
from pytest_txtar.sandbox import run_case
from pytest_txtar.update import updated_archive

SPEC = TxtarSpec(
    commands={"py": Path(sys.executable)},
    roots=("home", "xdg", "cwd"),
    cwd_root="cwd",
    env={"HOME": "home", "XDG_CONFIG_HOME": "xdg"},
)


def write_case(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "case.txtar"
    path.write_text(text, encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Spec
# ---------------------------------------------------------------------------

def test_tokens_default_to_the_upper_cased_root_in_braces():
    assert SPEC.token_map == {"home": "{HOME}", "xdg": "{XDG}", "cwd": "{CWD}"}


def test_explicit_tokens_win_over_the_derived_ones():
    spec = TxtarSpec(
        commands={},
        roots=("work",),
        cwd_root="work",
        tokens={"work": "<WORK>"},
    )

    assert spec.token_map == {"work": "<WORK>"}


# ---------------------------------------------------------------------------
# Normalization
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("/box/cwd/note.md", "{CWD}/note.md"),
        ("home is /box/home", "home is {HOME}"),
        ("/box/cwd and /box/xdg", "{CWD} and {XDG}"),
        ("/box/other/thing", "/box/other/thing"),
    ],
)
def test_root_paths_are_replaced_by_their_tokens(text: str, expected: str):
    roots = {root: Path("/box") / root for root in SPEC.roots}

    assert normalizer(roots, SPEC.token_map)(text) == expected


def test_a_nested_root_is_not_shadowed_by_its_parent():
    roots = {"outer": Path("/box"), "inner": Path("/box/inner")}
    normalize = normalizer(roots, {"outer": "{OUTER}", "inner": "{INNER}"})

    assert normalize("/box/inner/note.md") == "{INNER}/note.md"


def test_the_resolved_form_of_a_root_is_normalized_too(tmp_path: Path):
    real = tmp_path / "real"
    real.mkdir()
    link = tmp_path / "link"
    link.symlink_to(real)
    normalize = normalizer({"cwd": link}, {"cwd": "{CWD}"})

    assert normalize(f"{real}/note.md") == "{CWD}/note.md"
    assert normalize(f"{link}/note.md") == "{CWD}/note.md"


# ---------------------------------------------------------------------------
# Matching
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    ("expected", "actual", "matches"),
    [
        ("plain line", "plain line", True),
        ("plain line", "plain  line", False),
        ("[..]", "anything at all", True),
        ("[..]", "", True),
        ("wrote [..]", "wrote /tmp/x/note.md", True),
        ("wrote [..]", "wrote ", True),
        ("wrote [..]", "read /tmp/x/note.md", False),
        ("id: [..] done", "id: 4f2a done", True),
        ("id: [..] done", "id:  done", True),
        ("id: [..] done", "id: 4f2a done later", False),
        ("a[..]b[..]c", "axxbyyc", True),
        ("a[..]b[..]c", "axxc", False),
        ("cost is [..]$", "cost is 5$", True),
    ],
)
def test_wildcard_matching_of_a_single_line(expected: str, actual: str, matches: bool):
    assert line_matches(expected, actual) is matches


@pytest.mark.parametrize(
    ("expected", "actual", "matches"),
    [
        ("one\ntwo\n", "one\ntwo\n", True),
        ("one\ntwo\n", "one\ntwo", True),
        ("one\n[..]\n", "one\nsecond\n", True),
        ("one\n", "one\ntwo\n", False),
        ("one\ntwo\n", "one\n", False),
        ("", "", True),
        ("", "one\n", False),
    ],
)
def test_wildcard_matching_across_lines(expected: str, actual: str, matches: bool):
    assert text_matches(expected, actual) is matches


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def test_a_case_loads_its_sections_into_the_model(tmp_path: Path):
    path = write_case(
        tmp_path,
        "a case\n"
        "-- cmd --\n"
        "py --version\n"
        "\n"
        "py -c pass\n"
        "-- exit --\n"
        "3\n"
        "-- stdout --\n"
        "out\n"
        "-- stderr --\n"
        "err\n"
        "-- fixtures/home/note.md --\n"
        "seed\n"
        "-- expected/cwd/out.md --\n"
        "written\n",
    )

    case = load_case(path, SPEC)

    assert case.cmd == ["py --version", "py -c pass"]
    assert case.exit_code == 3
    assert case.stdout == "out\n"
    assert case.stderr == "err\n"
    assert case.fixtures == [("fixtures/home/note.md", "seed\n")]
    assert case.expected == [("expected/cwd/out.md", "written\n")]


def test_a_case_without_an_exit_section_expects_success(tmp_path: Path):
    case = load_case(write_case(tmp_path, "-- cmd --\npy --version\n"), SPEC)

    assert case.exit_code == 0
    assert case.stdout is None
    assert case.stderr is None


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("-- stdout --\nout\n", "missing section: cmd"),
        ("-- cmd --\n\n", "empty section: cmd"),
        ("-- cmd --\npy -c pass\n-- exit --\nlater\n", "exit is not an integer"),
        ("-- cmd --\npy -c pass\n-- setup --\nx\n", "unknown section: setup"),
        ("-- cmd --\npy -c pass\n-- fixtures/tmp/x.md --\nx\n", "must start with one of"),
        ("-- cmd --\npy -c pass\n-- expected/cwd --\nx\n", "must start with one of"),
        ("-- cmd --\npy -c pass\n-- fixtures/cwd/../x.md --\nx\n", "escapes its root"),
        ("-- cmd --\none\n-- cmd --\ntwo\n", "duplicate section: cmd"),
    ],
)
def test_a_malformed_case_is_rejected(tmp_path: Path, text: str, message: str):
    with pytest.raises(CaseError, match=message):
        load_case(write_case(tmp_path, text), SPEC)


def test_roots_a_case_may_address_come_from_the_spec(tmp_path: Path):
    spec = TxtarSpec(commands={}, roots=("work",), cwd_root="work")

    case = load_case(
        write_case(tmp_path, "-- cmd --\npy -c pass\n-- fixtures/work/note.md --\nseed\n"),
        spec,
    )

    assert case.fixtures == [("fixtures/work/note.md", "seed\n")]


# ---------------------------------------------------------------------------
# Running
# ---------------------------------------------------------------------------

def test_a_run_reports_stdout_stderr_and_exit_code(tmp_path: Path):
    case = load_case(
        write_case(
            tmp_path,
            "-- cmd --\n"
            'py -c "import sys; print(\'out\'); print(\'err\', file=sys.stderr); sys.exit(4)"\n',
        ),
        SPEC,
    )

    outcome = run_case(case, SPEC)

    assert outcome.stdout == "out\n"
    assert outcome.stderr == "err\n"
    assert outcome.exit_code == 4
    assert outcome.early_exit is None


def test_a_fixture_is_readable_from_the_root_it_names(tmp_path: Path):
    case = load_case(
        write_case(
            tmp_path,
            "-- cmd --\n"
            "py -c \"import os,pathlib; "
            "print(pathlib.Path(os.environ['HOME'], 'note.md').read_text())\"\n"
            "-- fixtures/home/note.md --\n"
            "seed\n",
        ),
        SPEC,
    )

    assert run_case(case, SPEC).stdout == "seed\n\n"


def test_a_file_the_command_writes_is_read_back_normalized(tmp_path: Path):
    case = load_case(
        write_case(
            tmp_path,
            "-- cmd --\n"
            "py -c \"import os,pathlib; pathlib.Path('out.md').write_text(os.getcwd())\"\n"
            "-- expected/cwd/out.md --\n"
            "{CWD}\n",
        ),
        SPEC,
    )

    outcome = run_case(case, SPEC)

    assert outcome.files == {"expected/cwd/out.md": "{CWD}"}
    assert compare(case, outcome) == []


def test_an_expected_file_that_was_never_written_is_reported_missing(tmp_path: Path):
    case = load_case(
        write_case(
            tmp_path,
            "-- cmd --\npy -c pass\n-- expected/cwd/out.md --\nsomething\n",
        ),
        SPEC,
    )

    outcome = run_case(case, SPEC)

    assert outcome.files == {"expected/cwd/out.md": None}
    assert [mismatch.label for mismatch in compare(case, outcome)] == ["expected/cwd/out.md"]
    assert compare(case, outcome)[0].actual == "<file does not exist>\n"


def test_the_process_runs_in_the_spec_cwd_root(tmp_path: Path):
    case = load_case(
        write_case(tmp_path, '-- cmd --\npy -c "import os; print(os.getcwd())"\n'),
        SPEC,
    )

    assert run_case(case, SPEC).stdout == "{CWD}\n"


def test_every_root_is_created_even_when_no_fixture_names_it(tmp_path: Path):
    case = load_case(
        write_case(
            tmp_path,
            "-- cmd --\n"
            "py -c \"import os; print(os.path.isdir(os.environ['XDG_CONFIG_HOME']))\"\n",
        ),
        SPEC,
    )

    assert run_case(case, SPEC).stdout == "True\n"


def test_output_of_every_command_in_a_case_is_concatenated(tmp_path: Path):
    case = load_case(
        write_case(
            tmp_path,
            "-- cmd --\npy -c \"print('one')\"\npy -c \"print('two')\"\n",
        ),
        SPEC,
    )

    outcome = run_case(case, SPEC)

    assert outcome.stdout == "one\ntwo\n"
    assert outcome.exit_code == 0


def test_a_non_final_command_that_fails_stops_the_case(tmp_path: Path):
    case = load_case(
        write_case(
            tmp_path,
            "-- cmd --\npy -c \"import sys; print('one'); sys.exit(7)\"\npy -c \"print('two')\"\n",
        ),
        SPEC,
    )

    outcome = run_case(case, SPEC)

    assert outcome.stdout == "one\n"
    assert outcome.early_exit == ('py -c "import sys; print(\'one\'); sys.exit(7)"', 7)
    assert [mismatch.label for mismatch in compare(case, outcome)] == ["cmd", "exit"]


def test_a_command_word_outside_the_spec_is_run_as_written(tmp_path: Path):
    case = load_case(write_case(tmp_path, "-- cmd --\necho hello\n"), SPEC)

    assert run_case(case, SPEC).stdout == "hello\n"


def test_a_mismatch_renders_as_a_unified_diff(tmp_path: Path):
    case = load_case(
        write_case(tmp_path, "-- cmd --\npy -c \"print('actual')\"\n-- stdout --\nwanted\n"),
        SPEC,
    )

    mismatches = compare(case, run_case(case, SPEC))

    assert [mismatch.label for mismatch in mismatches] == ["stdout"]
    assert report(mismatches[0]).splitlines() == [
        "=== stdout ===",
        "--- expected",
        "+++ actual",
        "@@ -1 +1 @@",
        "-wanted",
        "+actual",
    ]


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------

def test_update_fills_in_the_assertions_of_a_bare_case(tmp_path: Path):
    text = (
        "a case\n"
        "-- cmd --\n"
        "py -c \"import os,pathlib,sys; print(os.getcwd()); "
        "print('warned', file=sys.stderr); pathlib.Path('out.md').write_text('body\\n')\"\n"
        "-- fixtures/home/note.md --\n"
        "seed\n"
        "-- expected/cwd/out.md --\n"
        "stale\n"
    )
    case = load_case(write_case(tmp_path, text), SPEC)

    archive = updated_archive(case, run_case(case, SPEC))

    assert archive.comment == "a case\n"
    assert archive.files == [
        ("cmd", case.archive.files[0][1]),
        ("fixtures/home/note.md", "seed\n"),
        ("expected/cwd/out.md", "body\n"),
        ("exit", "0\n"),
        ("stdout", "{CWD}\n"),
        ("stderr", "warned\n"),
    ]


def test_update_keeps_a_silent_case_free_of_a_stderr_section(tmp_path: Path):
    case = load_case(write_case(tmp_path, "-- cmd --\npy -c \"print('out')\"\n"), SPEC)

    archive = updated_archive(case, run_case(case, SPEC))

    assert [name for name, _ in archive.files] == ["cmd", "exit", "stdout"]


def test_update_keeps_an_expected_file_the_run_never_wrote(tmp_path: Path):
    case = load_case(
        write_case(tmp_path, "-- cmd --\npy -c pass\n-- expected/cwd/out.md --\nkept\n"),
        SPEC,
    )

    archive = updated_archive(case, run_case(case, SPEC))

    assert ("expected/cwd/out.md", "kept\n") in archive.files


def test_updating_an_already_updated_case_rewrites_nothing(tmp_path: Path):
    path = write_case(
        tmp_path,
        "-- cmd --\n"
        "py -c \"import os,pathlib,sys; print(os.getcwd()); "
        "print('warned', file=sys.stderr); pathlib.Path('out.md').write_text('body\\n')\"\n"
        "-- expected/cwd/out.md --\n"
        "stale\n",
    )
    first = load_case(path, SPEC)
    once = txtar.serialize(updated_archive(first, run_case(first, SPEC)))
    path.write_text(once, encoding="utf-8")

    second = load_case(path, SPEC)
    outcome = run_case(second, SPEC)

    assert compare(second, outcome) == []
    assert txtar.serialize(updated_archive(second, outcome)) == once
