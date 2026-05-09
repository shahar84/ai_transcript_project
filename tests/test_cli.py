import pytest
from unittest.mock import patch
from typer.testing import CliRunner
from cli import app
import project
import project as proj

runner = CliRunner()


def test_create_command_makes_project(tmp_path, monkeypatch):
    monkeypatch.setattr(project, "PROJECTS_DIR", tmp_path / "projects")
    result = runner.invoke(app, ["create", "my-project"])
    assert result.exit_code == 0
    assert (tmp_path / "projects" / "my-project" / "videos").is_dir()
    assert (tmp_path / "projects" / "my-project" / "output").is_dir()
    assert "my-project" in result.output


def test_run_skips_completed_videos(tmp_path, monkeypatch):
    monkeypatch.setattr(project, "PROJECTS_DIR", tmp_path / "projects")
    monkeypatch.setattr(proj, "PROJECTS_DIR", tmp_path / "projects")
    proj.create_project("my-project")
    urls_file = tmp_path / "projects" / "my-project" / "urls.txt"
    urls_file.write_text("https://youtube.com/watch?v=abc my-video\n")
    output_dir = tmp_path / "projects" / "my-project" / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "my-video.json").touch()

    result = runner.invoke(app, ["run", "my-project"])
    assert result.exit_code == 0
    assert "skipping" in result.output


def test_run_processes_new_video(tmp_path, monkeypatch):
    monkeypatch.setattr(project, "PROJECTS_DIR", tmp_path / "projects")
    monkeypatch.setattr(proj, "PROJECTS_DIR", tmp_path / "projects")
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
    monkeypatch.setattr(proj, "PROJECTS_DIR", tmp_path / "projects")
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
    monkeypatch.setattr(proj, "PROJECTS_DIR", tmp_path / "projects")
    result = runner.invoke(app, ["run", "nonexistent"])
    assert result.exit_code == 1
