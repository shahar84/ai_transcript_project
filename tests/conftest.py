import pytest


@pytest.fixture
def projects_dir(tmp_path, monkeypatch):
    """Redirect PROJECTS_DIR to a temp directory for all tests."""
    import project
    monkeypatch.setattr(project, "PROJECTS_DIR", tmp_path / "projects")
    return tmp_path / "projects"
