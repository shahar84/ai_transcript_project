# Project Pipeline Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a project-based CLI workflow that downloads YouTube videos and transcribes them, with skip logic for already-processed videos.

**Architecture:** Three new modules (`project.py`, `downloader.py`, `cli.py`) wrap the existing transcription logic in `main.py`. A Typer CLI exposes two commands — `create` and `run`. Each project lives under `projects/<name>/` with its own `urls.txt`, `videos/`, and `output/` folders.

**Tech Stack:** Python 3.10+, Typer (CLI), yt-dlp (YouTube download), MoviePy + Replicate Whisper (existing), pytest (tests)

---

## Task 1: Add dependencies and test infrastructure

**Files:**
- Modify: `pyproject.toml`
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`

**Step 1: Add typer and pytest to pyproject.toml**

```toml
[project]
dependencies = [
    "moviepy==1.0.3",
    "requests==2.32.4",
    "python-dotenv==1.1.1",
    "pydantic-settings",
    "replicate",
    "openai",
    "yt-dlp",
    "typer",
]

[tool.uv]
dev-dependencies = [
    "pytest",
    "pytest-mock",
]
```

**Step 2: Run uv sync**

```bash
uv sync
```

Expected: resolves and installs typer, pytest, pytest-mock

**Step 3: Create tests/__init__.py (empty)**

**Step 4: Create tests/conftest.py**

```python
import pytest
from pathlib import Path


@pytest.fixture
def projects_dir(tmp_path, monkeypatch):
    """Redirect PROJECTS_DIR to a temp directory for all tests."""
    import project
    monkeypatch.setattr(project, "PROJECTS_DIR", tmp_path / "projects")
    return tmp_path / "projects"
```

**Step 5: Commit**

```bash
git add pyproject.toml uv.lock tests/
git commit -m "chore: add typer, pytest, and test infrastructure"
```

---

## Task 2: project.py — URL parsing and slugify

**Files:**
- Create: `project.py`
- Create: `tests/test_project.py`

**Step 1: Write failing tests**

```python
# tests/test_project.py
import pytest
from project import parse_url_line, slugify


def test_parse_url_only():
    url, name = parse_url_line("https://youtube.com/watch?v=abc")
    assert url == "https://youtube.com/watch?v=abc"
    assert name is None


def test_parse_url_with_name():
    url, name = parse_url_line("https://youtube.com/watch?v=abc steve-interview")
    assert url == "https://youtube.com/watch?v=abc"
    assert name == "steve-interview"


def test_parse_empty_line():
    url, name = parse_url_line("")
    assert url is None
    assert name is None


def test_parse_comment_line():
    url, name = parse_url_line("# this is a comment")
    assert url is None
    assert name is None


def test_slugify_basic():
    assert slugify("My Interview with Steve") == "my-interview-with-steve"


def test_slugify_special_chars():
    assert slugify("Hello! World? #1") == "hello-world-1"


def test_slugify_extra_spaces():
    assert slugify("  lots   of   spaces  ") == "lots-of-spaces"
```

**Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/test_project.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'project'`

**Step 3: Implement parse_url_line and slugify in project.py**

```python
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
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")
```

**Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/test_project.py -v
```

Expected: all 7 tests PASS

**Step 5: Commit**

```bash
git add project.py tests/test_project.py
git commit -m "feat: add URL parsing and slugify to project.py"
```

---

## Task 3: project.py — project creation, skip logic, URL reading

**Files:**
- Modify: `project.py`
- Modify: `tests/test_project.py`

**Step 1: Write failing tests**

```python
# Append to tests/test_project.py
from project import create_project, is_complete, read_urls


def test_create_project_makes_folders(projects_dir):
    create_project("my-project")
    assert (projects_dir / "my-project" / "videos").is_dir()
    assert (projects_dir / "my-project" / "output").is_dir()


def test_create_project_makes_urls_file(projects_dir):
    create_project("my-project")
    assert (projects_dir / "my-project" / "urls.txt").exists()


def test_create_project_idempotent(projects_dir):
    create_project("my-project")
    create_project("my-project")  # should not raise


def test_is_complete_false_when_no_json(projects_dir):
    create_project("my-project")
    assert not is_complete("my-project", "video1")


def test_is_complete_true_when_json_exists(projects_dir):
    create_project("my-project")
    json_path = projects_dir / "my-project" / "output" / "video1.json"
    json_path.touch()
    assert is_complete("my-project", "video1")


def test_read_urls_parses_file(projects_dir):
    create_project("my-project")
    urls_file = projects_dir / "my-project" / "urls.txt"
    urls_file.write_text(
        "# comment\n"
        "https://youtube.com/watch?v=abc\n"
        "https://youtube.com/watch?v=def my-video\n"
        "\n"
    )
    entries = read_urls("my-project")
    assert entries == [
        ("https://youtube.com/watch?v=abc", None),
        ("https://youtube.com/watch?v=def", "my-video"),
    ]
```

**Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/test_project.py -v
```

Expected: FAIL — `ImportError: cannot import name 'create_project'`

**Step 3: Add create_project, is_complete, read_urls to project.py**

```python
def create_project(name: str) -> Path:
    project_dir = PROJECTS_DIR / name
    (project_dir / "videos").mkdir(parents=True, exist_ok=True)
    (project_dir / "output").mkdir(parents=True, exist_ok=True)
    urls_file = project_dir / "urls.txt"
    if not urls_file.exists():
        urls_file.write_text(
            "# Add YouTube URLs below, one per line\n"
            "# Format: URL [optional-name]\n"
            "# Example: https://youtube.com/watch?v=abc my-video\n"
        )
    return project_dir


def is_complete(project_name: str, video_name: str) -> bool:
    json_path = PROJECTS_DIR / project_name / "output" / f"{video_name}.json"
    return json_path.exists()


def read_urls(project_name: str) -> list[tuple[str, str | None]]:
    urls_file = PROJECTS_DIR / project_name / "urls.txt"
    entries = []
    for line in urls_file.read_text().splitlines():
        url, name = parse_url_line(line)
        if url:
            entries.append((url, name))
    return entries
```

**Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/test_project.py -v
```

Expected: all 13 tests PASS

**Step 5: Commit**

```bash
git add project.py tests/test_project.py
git commit -m "feat: add project creation, skip logic, and URL reading"
```

---

## Task 4: downloader.py — yt-dlp wrapper

**Files:**
- Create: `downloader.py`
- Create: `tests/test_downloader.py`

**Step 1: Write failing tests (mocked — never hits the network)**

```python
# tests/test_downloader.py
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from downloader import get_video_title, download_video


def make_mock_ydl(title="Test Video Title", side_effect=None):
    mock_ydl = MagicMock()
    mock_ydl.__enter__ = lambda s: mock_ydl
    mock_ydl.__exit__ = MagicMock(return_value=False)
    if side_effect:
        mock_ydl.extract_info.side_effect = side_effect
    else:
        mock_ydl.extract_info.return_value = {"title": title}
    return mock_ydl


def test_get_video_title(tmp_path):
    mock_ydl = make_mock_ydl(title="My Interview")
    with patch("downloader.yt_dlp.YoutubeDL", return_value=mock_ydl):
        title = get_video_title("https://youtube.com/watch?v=abc")
    assert title == "My Interview"


def test_download_video_creates_file(tmp_path):
    output_dir = tmp_path / "videos"

    def fake_download(urls):
        (output_dir / "my-video.mp4").touch()

    mock_ydl = MagicMock()
    mock_ydl.__enter__ = lambda s: mock_ydl
    mock_ydl.__exit__ = MagicMock(return_value=False)
    mock_ydl.download.side_effect = fake_download

    with patch("downloader.yt_dlp.YoutubeDL", return_value=mock_ydl):
        path = download_video("https://youtube.com/watch?v=abc", "my-video", output_dir)

    assert path == output_dir / "my-video.mp4"
```

**Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/test_downloader.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'downloader'`

**Step 3: Implement downloader.py**

```python
import yt_dlp
from pathlib import Path


def get_video_title(url: str) -> str:
    with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
        info = ydl.extract_info(url, download=False)
        return info["title"]


def download_video(url: str, name: str, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    ydl_opts = {
        "format": "mp4/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
        "outtmpl": str(output_dir / f"{name}.%(ext)s"),
        "quiet": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    for path in output_dir.glob(f"{name}.*"):
        return path
    raise FileNotFoundError(f"Download produced no file for: {url}")
```

**Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/test_downloader.py -v
```

Expected: all 2 tests PASS

**Step 5: Commit**

```bash
git add downloader.py tests/test_downloader.py
git commit -m "feat: add yt-dlp downloader wrapper"
```

---

## Task 5: cli.py — create command

**Files:**
- Create: `cli.py`
- Create: `tests/test_cli.py`

**Step 1: Write failing test**

```python
# tests/test_cli.py
import pytest
from typer.testing import CliRunner
from unittest.mock import patch
from cli import app
import project

runner = CliRunner()


def test_create_command_makes_project(tmp_path, monkeypatch):
    monkeypatch.setattr(project, "PROJECTS_DIR", tmp_path / "projects")
    result = runner.invoke(app, ["create", "my-project"])
    assert result.exit_code == 0
    assert (tmp_path / "projects" / "my-project" / "videos").is_dir()
    assert (tmp_path / "projects" / "my-project" / "output").is_dir()
    assert "my-project" in result.output
```

**Step 2: Run test to verify it fails**

```bash
uv run pytest tests/test_cli.py::test_create_command_makes_project -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'cli'`

**Step 3: Implement cli.py with create command**

```python
import typer
from pathlib import Path
import project as proj
from downloader import download_video, get_video_title
from main import extract_audio, transcribe_audio, save_transcription

app = typer.Typer()


@app.command()
def create(name: str):
    """Create a new transcription project."""
    project_dir = proj.create_project(name)
    typer.echo(f"Project '{name}' created at {project_dir}")
    typer.echo(f"Add YouTube URLs to {project_dir / 'urls.txt'}")


if __name__ == "__main__":
    app()
```

**Step 4: Run test to verify it passes**

```bash
uv run pytest tests/test_cli.py::test_create_command_makes_project -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add cli.py tests/test_cli.py
git commit -m "feat: add Typer CLI with create command"
```

---

## Task 6: cli.py — run command

**Files:**
- Modify: `cli.py`
- Modify: `tests/test_cli.py`

**Step 1: Write failing tests**

```python
# Append to tests/test_cli.py
from unittest.mock import patch, MagicMock


def test_run_skips_completed_videos(tmp_path, monkeypatch):
    monkeypatch.setattr(project, "PROJECTS_DIR", tmp_path / "projects")
    proj.create_project("my-project")
    urls_file = tmp_path / "projects" / "my-project" / "urls.txt"
    urls_file.write_text("https://youtube.com/watch?v=abc my-video\n")
    # Mark as complete
    output_dir = tmp_path / "projects" / "my-project" / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "my-video.json").touch()

    result = runner.invoke(app, ["run", "my-project"])
    assert result.exit_code == 0
    assert "skipping" in result.output


def test_run_processes_new_video(tmp_path, monkeypatch):
    monkeypatch.setattr(project, "PROJECTS_DIR", tmp_path / "projects")
    proj.create_project("my-project")
    urls_file = tmp_path / "projects" / "my-project" / "urls.txt"
    urls_file.write_text("https://youtube.com/watch?v=abc my-video\n")

    fake_video = tmp_path / "projects" / "my-project" / "videos" / "my-video.mp4"

    with (
        patch("cli.download_video", return_value=fake_video) as mock_dl,
        patch("cli.extract_audio", return_value="output/my-video.mp3") as mock_audio,
        patch("cli.transcribe_audio", return_value={"text": "hello", "chunks": []}) as mock_tr,
        patch("cli.save_transcription") as mock_save,
    ):
        result = runner.invoke(app, ["run", "my-project"])

    assert result.exit_code == 0
    mock_dl.assert_called_once()
    mock_audio.assert_called_once()
    mock_tr.assert_called_once()
    mock_save.assert_called_once()
    assert "transcribing" in result.output


def test_run_continues_after_error(tmp_path, monkeypatch):
    monkeypatch.setattr(project, "PROJECTS_DIR", tmp_path / "projects")
    proj.create_project("my-project")
    urls_file = tmp_path / "projects" / "my-project" / "urls.txt"
    urls_file.write_text(
        "https://youtube.com/watch?v=bad bad-video\n"
        "https://youtube.com/watch?v=good good-video\n"
    )

    fake_video = tmp_path / "projects" / "my-project" / "videos" / "good-video.mp4"

    def fail_first_succeed_second(url, name, output_dir):
        if name == "bad-video":
            raise RuntimeError("Download failed")
        return fake_video

    with (
        patch("cli.download_video", side_effect=fail_first_succeed_second),
        patch("cli.extract_audio", return_value="output/good-video.mp3"),
        patch("cli.transcribe_audio", return_value={"text": "hello", "chunks": []}),
        patch("cli.save_transcription"),
    ):
        result = runner.invoke(app, ["run", "my-project"])

    assert result.exit_code == 0
    assert "ERROR" in result.output
    assert "transcribing" in result.output


def test_run_missing_project(tmp_path, monkeypatch):
    monkeypatch.setattr(project, "PROJECTS_DIR", tmp_path / "projects")
    result = runner.invoke(app, ["run", "nonexistent"])
    assert result.exit_code != 0
```

**Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/test_cli.py -v
```

Expected: FAIL — `run` command not implemented yet

**Step 3: Add run command to cli.py**

```python
@app.command()
def run(name: str):
    """Run the full pipeline for a project."""
    project_dir = proj.PROJECTS_DIR / name
    if not project_dir.exists():
        typer.echo(f"Project '{name}' not found.", err=True)
        raise typer.Exit(code=1)

    entries = proj.read_urls(name)
    if not entries:
        typer.echo("No URLs found in urls.txt.")
        return

    total = len(entries)
    processed = 0
    skipped = 0

    for i, (url, video_name) in enumerate(entries, 1):
        if not video_name:
            video_name = proj.slugify(get_video_title(url))

        prefix = f"[{i}/{total}] {video_name}"

        if proj.is_complete(name, video_name):
            typer.echo(f"{prefix} — already done, skipping")
            skipped += 1
            continue

        try:
            typer.echo(f"{prefix} — downloading...")
            video_path = download_video(url, video_name, project_dir / "videos")

            typer.echo(f"{prefix} — extracting audio...")
            audio_path = extract_audio(str(video_path), str(project_dir / "output"))

            typer.echo(f"{prefix} — transcribing...")
            result = transcribe_audio(audio_path)
            save_transcription(result, str(video_path), str(project_dir / "output"))

            processed += 1
        except Exception as e:
            typer.echo(f"{prefix} — ERROR: {e}", err=True)

    typer.echo(f"\nDone. {processed} processed, {skipped} skipped.")
```

**Step 4: Run all tests to verify they pass**

```bash
uv run pytest tests/ -v
```

Expected: all tests PASS

**Step 5: Commit**

```bash
git add cli.py tests/test_cli.py
git commit -m "feat: add run command with skip logic and error handling"
```

---

## Task 7: Update pyproject.toml entry point and docs

**Files:**
- Modify: `pyproject.toml`
- Modify: `README.md`

**Step 1: Add script entry point to pyproject.toml**

```toml
[project.scripts]
transcript = "cli:app"
```

This lets users run `uv run transcript create my-project` instead of `uv run cli.py create my-project`.

**Step 2: Update README Usage section**

Replace the Usage section with:

```markdown
## Usage

### Create a project
```bash
uv run transcript create my-project
```

Edit `projects/my-project/urls.txt` and add YouTube URLs:
```
# One URL per line. Name is optional.
https://youtube.com/watch?v=abc
https://youtube.com/watch?v=def my-interview
```

### Run the pipeline
```bash
uv run transcript run my-project
```

Re-running skips videos that have already been transcribed.
```

**Step 3: Run uv sync to register the entry point**

```bash
uv sync
```

**Step 4: Smoke test the CLI**

```bash
uv run transcript --help
uv run transcript create test-project
```

Expected: help text shown, `projects/test-project/` created with `urls.txt`

**Step 5: Commit**

```bash
git add pyproject.toml uv.lock README.md
git commit -m "chore: add transcript CLI entry point and update README"
```
