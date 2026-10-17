from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from booping.specs.records import load_record
from booping.specs.tiers import Tier


class SpecValue(BaseModel):
    ref: str
    title: str
    summary: str
    non_value: bool = False


def has_specs(tier: Tier) -> bool:
    """A tier holds specs once any of its type directories exists."""
    return any((tier.root / type_).is_dir() for type_ in tier.types)


def load_values(tiers: list[Tier]) -> list[SpecValue]:
    """Value records of the global and project tiers, global first, records by number.
    A record with a broken name or frontmatter is left to `booping specs check`."""
    values: list[SpecValue] = []
    seen: set[Path] = set()
    for tier in tiers:
        value_dir = tier.root / "value"
        if tier.name == "core" or not value_dir.is_dir():
            continue
        records = [load_record(p, "value") for p in value_dir.glob("*.md")]
        records = [r for r in records if r.number is not None and r.frontmatter_error is None]
        records.sort(key=lambda r: r.number or 0)
        for record in records:
            real = record.path.resolve()
            if real in seen:
                continue
            seen.add(real)
            ref = f"value/{record.number:04d}"
            fm = record.frontmatter
            values.append(
                SpecValue(
                    ref=f"{tier.namespace}:{ref}" if tier.namespace else ref,
                    title=" ".join(str(fm.get("title", record.path.stem)).split()),
                    summary=" ".join(str(fm.get("summary", "")).split()),
                    non_value=fm.get("kind") == "non-value",
                )
            )
    return values
