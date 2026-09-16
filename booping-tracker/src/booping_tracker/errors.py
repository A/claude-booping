"""The two failure classes the exit-code contract distinguishes."""

from __future__ import annotations


class UserError(Exception):
    """Caller's fault: exit 1."""


class ProviderError(Exception):
    """Tracker's fault — transport, GraphQL errors, rate limiting: exit 2."""
