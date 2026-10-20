"""A tier's tag dictionary, `{tier root}/tags.yaml` (`tag: one-line description`), and
the check of one record's `tags:` against it."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, cast

import yaml

DICTIONARY = "tags.yaml"
MALFORMED = "tags.yaml must map each tag to a one-line description"
NOT_A_LIST = "tags must be a list of strings"
_TAG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*(:[a-z0-9]+(-[a-z0-9]+)*)?$")


class MalformedDictionary(Exception):
    """`tags.yaml` exists but is not a mapping of string to string."""


def load(root: Path) -> dict[str, str] | None:
    """The tier's dictionary, or None when the tier has no `tags.yaml`."""
    path = root / DICTIONARY
    if not path.is_file():
        return None
    try:
        data: Any = yaml.safe_load(path.read_text())
    except yaml.YAMLError as exc:
        raise MalformedDictionary(MALFORMED) from exc
    if not isinstance(data, dict):
        raise MalformedDictionary(MALFORMED)
    entries = cast("dict[Any, Any]", data)
    dictionary = {k: v for k, v in entries.items() if isinstance(k, str) and isinstance(v, str)}
    if len(dictionary) != len(entries):
        raise MalformedDictionary(MALFORMED)
    return dictionary


def problems(tags: Any, dictionary: dict[str, str]) -> list[str]:
    """One message per failing tag, its first failure only; `tags` is the record's
    `tags:` value, present."""
    if not isinstance(tags, list):
        return [NOT_A_LIST]
    items = cast("list[Any]", tags)
    strings = [t for t in items if isinstance(t, str)]
    if len(strings) != len(items):
        return [NOT_A_LIST]
    found: list[str] = []
    for tag in strings:
        area = tag.split(":", 1)[0]
        if _TAG_RE.match(tag) is None:
            found.append(f"tag {tag} is not area[:sub] kebab-case")
        elif tag not in dictionary:
            found.append(f"tag {tag} is not in tags.yaml")
        elif area != tag and area not in dictionary:
            found.append(f"tag {tag} needs its area {area} in tags.yaml")
    return found
