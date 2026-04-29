from pathlib import Path


class ExtraInstructions:
    @staticmethod
    def load(vault: Path | None) -> dict[str, str]:
        if vault is None:
            return {}
        booping_dir = vault / "_booping"
        if not booping_dir.is_dir():
            return {}
        result: dict[str, str] = {}
        for pattern in ("skill_*.md", "agent_*.md"):
            for md_file in sorted(booping_dir.glob(pattern)):
                result[md_file.stem] = md_file.read_text()
        return result