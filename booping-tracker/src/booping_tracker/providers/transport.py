"""GraphQL transport for the Linear API, and the failure mapping every operation shares."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Protocol, cast

import httpx

from booping_tracker.errors import ProviderError

RATE_LIMIT_CODE = "RATELIMITED"
TIMEOUT_SECONDS = 30.0


class Transport(Protocol):
    def execute(
        self, *, operation: str, query: str, variables: dict[str, Any]
    ) -> dict[str, Any]: ...


@dataclass(frozen=True)
class HttpTransport:
    api_url: str
    api_key: str
    timeout: float = TIMEOUT_SECONDS

    def execute(self, *, operation: str, query: str, variables: dict[str, Any]) -> dict[str, Any]:
        try:
            response = httpx.post(
                self.api_url,
                json={"query": query, "variables": variables},
                # A personal API key goes in bare: `Bearer` is the OAuth/MCP shape, which
                # this endpoint rejects.
                headers={"Authorization": self.api_key, "Content-Type": "application/json"},
                timeout=self.timeout,
            )
        except httpx.HTTPError as exc:
            raise ProviderError(f"{operation}: transport error: {exc}") from exc
        return parse_response(
            operation=operation, status_code=response.status_code, text=response.text
        )


def parse_response(*, operation: str, status_code: int, text: str) -> dict[str, Any]:
    """The response's `data`, or the failure it maps onto."""
    payload = _decode(operation, status_code, text)
    errors = _errors(payload)

    # Linear answers a throttled request with HTTP 400 and a RATELIMITED code, so the
    # status alone would read as a user error.
    if _rate_limited(payload, errors):
        raise ProviderError(f"{operation}: rate limited by Linear ({RATE_LIMIT_CODE})")

    messages = [
        message
        for error in errors
        if isinstance(message := error.get("message"), str) and message
    ]
    if messages:
        raise ProviderError(f"{operation}: GraphQL error: {'; '.join(messages)}")
    if errors:
        raise ProviderError(f"{operation}: GraphQL error with no message")
    if status_code >= 400:
        raise ProviderError(f"{operation}: HTTP {status_code} from Linear")

    data = payload.get("data")
    if not isinstance(data, dict):
        raise ProviderError(f"{operation}: response carried no data")
    return cast("dict[str, Any]", data)


def _decode(operation: str, status_code: int, text: str) -> dict[str, Any]:
    try:
        payload: Any = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ProviderError(
            f"{operation}: HTTP {status_code} with an unreadable body: {exc}"
        ) from exc
    if not isinstance(payload, dict):
        raise ProviderError(f"{operation}: HTTP {status_code} with a non-object body")
    return cast("dict[str, Any]", payload)


def _errors(payload: dict[str, Any]) -> list[dict[str, Any]]:
    raw: Any = payload.get("errors")
    if not isinstance(raw, list):
        return []
    return [
        cast("dict[str, Any]", item) for item in cast("list[Any]", raw) if isinstance(item, dict)
    ]


def _rate_limited(payload: dict[str, Any], errors: list[dict[str, Any]]) -> bool:
    codes: list[Any] = [payload.get("code"), payload.get("error")]
    for error in errors:
        extensions: Any = error.get("extensions")
        block = cast("dict[str, Any]", extensions) if isinstance(extensions, dict) else {}
        codes += [error.get("code"), error.get("type"), block.get("code"), block.get("type")]
    return any(isinstance(code, str) and code.upper() == RATE_LIMIT_CODE for code in codes)
