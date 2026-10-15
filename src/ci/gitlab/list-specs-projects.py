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


def _pages_url(api: str, project_id: int, token: str) -> str | None:
    """The project's live Pages URL (unique domains included), or None without Pages."""
    request = urllib.request.Request(f"{api}/projects/{project_id}/pages", headers={"PRIVATE-TOKEN": token})
    try:
        with urllib.request.urlopen(request) as response:
            data = json.loads(response.read())
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        _fail(f"HTTP {exc.code} from {api}/projects/{project_id}/pages")
    except (urllib.error.URLError, ValueError):
        return None
    url = data.get("url") if isinstance(data, dict) else None
    return url.rstrip("/") if isinstance(url, str) and url else None


def main() -> None:
    api = _env("CI_API_V4_URL").rstrip("/")
    group = urllib.parse.quote(_env("CI_PROJECT_NAMESPACE"), safe="")
    token = _env("SPECS_INDEX_TOKEN")
    topic = os.environ.get("SPECS_TOPIC") or "booping-specs"
    # Fallback base for a project whose Pages URL the API does not return.
    base = (os.environ.get("SPECS_PAGES_BASE") or "").rstrip("/") or None

    query = urllib.parse.urlencode(
        {"topic": topic, "archived": "false", "per_page": "100", "order_by": "path", "sort": "asc"}
    )
    projects: list[dict[str, Any]] = []
    page = "1"
    while page:
        items, page = _fetch(f"{api}/groups/{group}/projects?{query}&page={page}", token)
        for item in items:
            url = _pages_url(api, item["id"], token) or (f"{base}/{item['path']}" if base else None)
            if url is None:
                continue
            projects.append({"name": item["name"], "url": url, "description": item.get("description")})
    projects.sort(key=lambda p: (p["name"].casefold(), p["name"]))
    print(json.dumps(projects, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
