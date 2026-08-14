"""A stand-in for the Linear network boundary: canned responses, recorded requests."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, cast


@dataclass(frozen=True)
class TransportCall:
    operation: str
    query: str
    variables: dict[str, Any]


class FakeTransport:
    def __init__(self, responses: Mapping[str, Any] | None = None) -> None:
        self._responses: dict[str, Any] = dict(responses or {})
        self.calls: list[TransportCall] = []

    def execute(self, *, operation: str, query: str, variables: dict[str, Any]) -> dict[str, Any]:
        self.calls.append(TransportCall(operation, query, variables))
        if operation not in self._responses:
            raise AssertionError(f"fake transport has no response for {operation}")
        response: Any = self._responses[operation]
        if isinstance(response, Exception):
            raise response
        return cast("dict[str, Any]", response)

    @property
    def operations(self) -> list[str]:
        return [call.operation for call in self.calls]

    def last(self, operation: str) -> TransportCall:
        for call in reversed(self.calls):
            if call.operation == operation:
                return call
        raise AssertionError(f"{operation} was never called")
