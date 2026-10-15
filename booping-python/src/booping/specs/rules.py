from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from booping.specs.records import Record, load_record
from booping.specs.targets import Target, TargetRejection, parse_target
from booping.specs.tiers import Tier, TierName


class TargetedRule(BaseModel):
    ref: str
    title: str
    brief: str
    link: str
    tier: TierName
    path: Path
    parsed_targets: list[Target]


class RuleSkip(BaseModel):
    path: Path
    link: str
    reason: str


def _normalized(path: Path) -> Path:
    return Path(os.path.normpath(path.absolute()))


def _link(tier: Tier, path: Path) -> str:
    absolute = _normalized(path)
    anchor = _normalized(tier.anchor)
    if tier.name != "global" and absolute.is_relative_to(anchor):
        relative = absolute.relative_to(anchor).as_posix()
        return f"${{CLAUDE_PLUGIN_ROOT}}/{relative}" if tier.name == "core" else relative
    return absolute.as_posix()


def _ref(tier: Tier, number: int) -> str:
    ref = f"rule/{number:04d}"
    return f"{tier.namespace}:{ref}" if tier.namespace else ref


def _skip(tier: Tier, record: Record, reason: str) -> RuleSkip:
    return RuleSkip(path=record.path, link=_link(tier, record.path), reason=reason)


def _take(tier: Tier, record: Record) -> TargetedRule | RuleSkip | None:
    """None for a record that is not an injectable rule and raises nothing."""
    if record.frontmatter_error is not None:
        return _skip(tier, record, record.frontmatter_error)
    fm = record.frontmatter
    if fm.get("status") != "accepted":
        return None
    targets: Any = fm.get("targets")
    brief: Any = fm.get("brief")
    if targets is None and brief is None:
        return None
    if not (isinstance(brief, str) and brief.strip() and isinstance(targets, list) and targets):
        return _skip(tier, record, "targets and brief must come together")
    entries: list[object] = list(targets)  # pyright: ignore[reportUnknownArgumentType]
    if record.number is None:
        return _skip(tier, record, "filename is not NNNN-slug.md")
    parsed: list[Target] = []
    for entry in entries:
        result = parse_target(entry)
        if isinstance(result, TargetRejection):
            return _skip(tier, record, f"target {entry!r}: {result.reason}")
        parsed.append(result)
    return TargetedRule(
        ref=_ref(tier, record.number),
        title=str(fm.get("title", record.path.stem)),
        brief=" ".join(brief.split()),
        link=_link(tier, record.path),
        tier=tier.name,
        path=record.path,
        parsed_targets=parsed,
    )


def load_targeted_rules(tiers: list[Tier]) -> tuple[list[TargetedRule], list[RuleSkip]]:
    """Accepted rules carrying `targets` + `brief` from each tier's `rule/` directory,
    tiers in the order given, records by number. A record file reached through several
    tiers is taken once, by the first."""
    rules: list[TargetedRule] = []
    skips: list[RuleSkip] = []
    seen: set[Path] = set()
    for tier in tiers:
        rule_dir = tier.root / "rule"
        if not rule_dir.is_dir():
            continue
        records = [load_record(p, "rule") for p in rule_dir.glob("*.md")]
        records.sort(key=lambda r: (r.number is None, r.number or 0, r.path.name))
        for record in records:
            real = record.path.resolve()
            if real in seen:
                continue
            seen.add(real)
            taken = _take(tier, record)
            if isinstance(taken, TargetedRule):
                rules.append(taken)
            elif isinstance(taken, RuleSkip):
                skips.append(taken)
    return rules, skips
