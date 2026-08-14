from __future__ import annotations

import json
from typing import Any

import httpx
import pytest

from booping_tracker.errors import ProviderError
from booping_tracker.providers.transport import HttpTransport, parse_response

API_URL = "https://api.linear.app/graphql"
RATE_LIMIT_BODY = json.dumps(
    {"errors": [{"message": "Ratelimit exceeded", "extensions": {"code": "RATELIMITED"}}]}
)


@pytest.fixture
def recorded(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    """Capture the one request httpx would put on the wire."""
    captured: dict[str, Any] = {}

    def fake_post(url: str, **kwargs: Any) -> httpx.Response:
        captured["url"] = url
        captured.update(kwargs)
        return httpx.Response(200, text=json.dumps({"data": {"issue": {"identifier": "LIN-1"}}}))

    monkeypatch.setattr(httpx, "post", fake_post)
    return captured


def test_the_api_key_travels_bare_in_the_authorization_header(recorded: dict[str, Any]) -> None:
    HttpTransport(api_url=API_URL, api_key="lin_api_secret").execute(
        operation="issue", query="query Issue { issue { id } }", variables={"id": "LIN-1"}
    )

    assert recorded["headers"]["Authorization"] == "lin_api_secret"


def test_the_request_posts_the_query_and_its_variables(recorded: dict[str, Any]) -> None:
    data = HttpTransport(api_url=API_URL, api_key="k").execute(
        operation="issue", query="query Issue { issue { id } }", variables={"id": "LIN-1"}
    )

    assert recorded["url"] == API_URL
    assert recorded["json"] == {
        "query": "query Issue { issue { id } }",
        "variables": {"id": "LIN-1"},
    }
    assert data == {"issue": {"identifier": "LIN-1"}}


def test_a_network_failure_is_a_provider_error_naming_the_operation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def refuse(url: str, **kwargs: Any) -> httpx.Response:
        raise httpx.ConnectError("connection refused")

    monkeypatch.setattr(httpx, "post", refuse)

    with pytest.raises(ProviderError, match="issueCreate: transport error: connection refused"):
        HttpTransport(api_url=API_URL, api_key="k").execute(
            operation="issueCreate", query="mutation {}", variables={}
        )


@pytest.mark.parametrize(
    ("status_code", "text", "expected"),
    [
        (200, json.dumps({"data": None, "errors": [{"message": "Entity not found"}]}),
         "GraphQL error: Entity not found"),
        (400, RATE_LIMIT_BODY, "rate limited by Linear"),
        (429, RATE_LIMIT_BODY, "rate limited by Linear"),
        (400, json.dumps({"errors": [{"message": "Argument Validation Error"}]}),
         "GraphQL error: Argument Validation Error"),
        (500, "<html>gateway</html>", "HTTP 500 with an unreadable body"),
        (502, json.dumps({"data": None}), "HTTP 502 from Linear"),
        (200, json.dumps({"data": None}), "response carried no data"),
    ],
)
def test_failure_responses_map_onto_provider_errors(
    status_code: int, text: str, expected: str
) -> None:
    with pytest.raises(ProviderError, match=expected):
        parse_response(operation="issue", status_code=status_code, text=text)


def test_a_rate_limited_body_outranks_its_user_error_status_code() -> None:
    """Linear answers a throttled request with 400, which would otherwise read as exit 1."""
    with pytest.raises(ProviderError) as raised:
        parse_response(operation="issue", status_code=400, text=RATE_LIMIT_BODY)

    assert "RATELIMITED" in str(raised.value)


def test_a_successful_response_returns_its_data() -> None:
    data = parse_response(
        operation="issue",
        status_code=200,
        text=json.dumps({"data": {"issue": {"identifier": "LIN-7"}}}),
    )

    assert data == {"issue": {"identifier": "LIN-7"}}
