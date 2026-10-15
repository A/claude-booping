"""`src/ci/gitlab/list-specs-projects.py` as a subprocess against a fake GitLab API."""

from __future__ import annotations

import json
import os
import subprocess
import threading
from collections.abc import Iterator
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest

SCRIPT = Path(__file__).resolve().parents[3] / "src" / "ci" / "gitlab" / "list-specs-projects.py"
TOKEN = "glpat-secret-token-value"


@dataclass
class Request:
    path: str
    query: dict[str, list[str]]
    token: str | None


@dataclass
class FakeGitLab:
    """Serves `pages[n-1]` for `page=n`; `status` replaces every response when set."""

    url: str = ""
    pages: list[list[dict[str, object]]] = field(default_factory=lambda: [[]])
    status: int = 200
    requests: list[Request] = field(default_factory=lambda: [])


@pytest.fixture
def gitlab() -> Iterator[FakeGitLab]:
    fake = FakeGitLab()

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            split = urlsplit(self.path)
            query = parse_qs(split.query)
            fake.requests.append(Request(split.path, query, self.headers.get("PRIVATE-TOKEN")))
            if fake.status != 200:
                self.send_response(fake.status)
                self.end_headers()
                self.wfile.write(b'{"message": "401 Unauthorized"}')
                return
            page = int(query["page"][0])
            body = json.dumps(fake.pages[page - 1]).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("x-next-page", str(page + 1) if page < len(fake.pages) else "")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format: str, *args: object) -> None:
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    fake.url = f"http://127.0.0.1:{server.server_address[1]}/api/v4"
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield fake
    server.shutdown()
    server.server_close()


def _run(env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    base = {k: v for k, v in os.environ.items() if not k.startswith(("CI_", "SPECS_"))}
    return subprocess.run(
        [str(SCRIPT)], env={**base, **env}, capture_output=True, text=True, check=False
    )


def _ci_env(fake: FakeGitLab, **extra: str) -> dict[str, str]:
    return {
        "CI_API_V4_URL": fake.url,
        "CI_PROJECT_NAMESPACE": "lab/sub",
        "SPECS_INDEX_TOKEN": TOKEN,
        **extra,
    }


def test_two_pages_merge_sorted_with_pages_urls(gitlab: FakeGitLab) -> None:
    gitlab.pages = [
        [
            {"name": "zeta", "path": "zeta-svc", "description": "Zeta specs."},
            {"name": "Beta", "path": "beta", "description": None},
        ],
        [{"name": "alpha", "path": "alpha", "description": "Ålpha."}],
    ]

    result = _run(_ci_env(gitlab, SPECS_PAGES_BASE="https://lab.pages.example.org/"))

    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    assert result.stdout == (
        "[\n"
        "  {\n"
        '    "name": "alpha",\n'
        '    "url": "https://lab.pages.example.org/alpha",\n'
        '    "description": "Ålpha."\n'
        "  },\n"
        "  {\n"
        '    "name": "Beta",\n'
        '    "url": "https://lab.pages.example.org/beta",\n'
        '    "description": null\n'
        "  },\n"
        "  {\n"
        '    "name": "zeta",\n'
        '    "url": "https://lab.pages.example.org/zeta-svc",\n'
        '    "description": "Zeta specs."\n'
        "  }\n"
        "]\n"
    )
    assert [r.query["page"] for r in gitlab.requests] == [["1"], ["2"]]
    first = gitlab.requests[0]
    assert first.path == "/api/v4/groups/lab%2Fsub/projects"
    assert first.token == TOKEN
    assert first.query["topic"] == ["booping-specs"]
    assert first.query["archived"] == ["false"]


def test_pages_base_defaults_to_ci_pages_url(gitlab: FakeGitLab) -> None:
    gitlab.pages = [[{"name": "alpha", "path": "alpha", "description": "A."}]]

    result = _run(_ci_env(gitlab, CI_PAGES_URL="https://group.pages.example.org"))

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == [
        {"name": "alpha", "url": "https://group.pages.example.org/alpha", "description": "A."}
    ]


def test_http_error_names_the_status_never_the_token(gitlab: FakeGitLab) -> None:
    gitlab.status = 401

    result = _run(_ci_env(gitlab, SPECS_PAGES_BASE="https://lab.pages.example.org"))

    assert result.returncode == 1
    assert result.stdout == ""
    assert "401" in result.stderr
    assert result.stderr.startswith("list-specs-projects: ")
    assert TOKEN not in result.stdout
    assert TOKEN not in result.stderr


def test_missing_token_fails_before_any_request(gitlab: FakeGitLab) -> None:
    env = _ci_env(gitlab, SPECS_PAGES_BASE="https://lab.pages.example.org")
    del env["SPECS_INDEX_TOKEN"]

    result = _run(env)

    assert result.returncode == 1
    assert result.stdout == ""
    assert result.stderr == "list-specs-projects: SPECS_INDEX_TOKEN is not set\n"
    assert gitlab.requests == []
