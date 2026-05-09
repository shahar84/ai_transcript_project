import pytest
from typer.testing import CliRunner
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
