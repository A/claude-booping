#!/usr/bin/env python3
"""Print the CI job's group projects carrying the specs topic as `booping specs
site-index` stdin JSON. Stdlib only: it runs from a bare clone before any install."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, NoReturn


def _fail(reason: str) -> NoReturn:
    print(f"list-specs-projects: {reason}", file=sys.stderr)
    sys.exit(1)


def _env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        _fail(f"{name} is not set")
    return value


def _fetch(url: str, token: str) -> tuple[list[Any], str]:
    request = urllib.request.Request(url, headers={"PRIVATE-TOKEN": token})
    try:
        with urllib.request.urlopen(request) as response:
            body = response.read()
            next_page = response.headers.get("x-next-page") or ""
    except urllib.error.HTTPError as exc:
        _fail(f"HTTP {exc.code} from {url}")
    except urllib.error.URLError as exc:
        _fail(f"request to {url} failed: {exc.reason}")
    try:
        data = json.loads(body)
    except ValueError:
        _fail(f"response from {url} is not JSON")
    if not isinstance(data, list):
        _fail(f"response from {url} is not a JSON list")
    return data, next_page  # pyright: ignore[reportUnknownVariableType]


def main() -> None:
    api = _env("CI_API_V4_URL").rstrip("/")
    group = urllib.parse.quote(_env("CI_PROJECT_NAMESPACE"), safe="")
    token = _env("SPECS_INDEX_TOKEN")
    topic = os.environ.get("SPECS_TOPIC") or "booping-specs"
    base = os.environ.get("SPECS_PAGES_BASE") or os.environ.get("CI_PAGES_URL")
    if not base:
        _fail("SPECS_PAGES_BASE or CI_PAGES_URL must be set")
    base = base.rstrip("/")

    query = urllib.parse.urlencode(
        {"topic": topic, "archived": "false", "per_page": "100", "order_by": "path", "sort": "asc"}
    )
    projects: list[dict[str, Any]] = []
    page = "1"
    while page:
        items, page = _fetch(f"{api}/groups/{group}/projects?{query}&page={page}", token)
        projects += [
            {
                "name": item["name"],
                "url": f"{base}/{item['path']}",
                "description": item.get("description"),
            }
            for item in items
        ]
    projects.sort(key=lambda p: (p["name"].casefold(), p["name"]))
    print(json.dumps(projects, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
