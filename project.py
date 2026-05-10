from pathlib import Path
import re

PROJECTS_DIR = Path("projects")


def parse_url_line(line: str) -> tuple[str | None, str | None]:
    """Parse a urls.txt line in the format 'URL [optional-name]'. Returns (None, None) for blanks/comments."""
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


def create_project(name: str) -> Path:
    project_dir = PROJECTS_DIR / name
    (project_dir / "videos").mkdir(parents=True, exist_ok=True)
    (project_dir / "audio").mkdir(parents=True, exist_ok=True)
    (project_dir / "transcripts").mkdir(parents=True, exist_ok=True)
    (project_dir / "podcast").mkdir(parents=True, exist_ok=True)
    urls_file = project_dir / "urls.txt"
    if not urls_file.exists():
        urls_file.write_text(
            "# Add YouTube URLs below, one per line\n"
            "# Format: URL [optional-name]\n"
            "# Example: https://youtube.com/watch?v=abc my-video\n"
        )
    return project_dir


def is_transcribed(project_name: str, video_name: str) -> bool:
    json_path = PROJECTS_DIR / project_name / "transcripts" / f"{video_name}.json"
    return json_path.exists()


def read_urls(project_name: str) -> list[tuple[str, str | None]]:
    urls_file = PROJECTS_DIR / project_name / "urls.txt"
    entries = []
    with urls_file.open() as f:
        for line in f:
            url, name = parse_url_line(line)
            if url:
                entries.append((url, name))
    return entries
