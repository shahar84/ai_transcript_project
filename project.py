from pathlib import Path
import re

PROJECTS_DIR = Path("projects")


def parse_url_line(line: str) -> tuple[str | None, str | None]:
    line = line.strip()
    if not line or line.startswith("#"):
        return None, None
    parts = line.split(" ", 1)
    url = parts[0]
    name = parts[1].strip() if len(parts) > 1 else None
    return url, name


def slugify(text: str) -> str:
    lowered = text.lower().strip()
    no_special = re.sub(r"[^\w\s-]", "", lowered)
    hyphenated = re.sub(r"[\s_]+", "-", no_special)
    deduplicated = re.sub(r"-+", "-", hyphenated)
    return deduplicated.strip("-")
