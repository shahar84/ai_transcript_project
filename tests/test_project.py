import pytest
from project import parse_url_line, slugify, create_project, is_transcribed, read_urls


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


def test_create_project_makes_folders(projects_dir):
    create_project("my-project")
    assert (projects_dir / "my-project" / "videos").is_dir()
    assert (projects_dir / "my-project" / "audio").is_dir()
    assert (projects_dir / "my-project" / "transcripts").is_dir()
    assert (projects_dir / "my-project" / "podcast").is_dir()


def test_create_project_makes_urls_file(projects_dir):
    create_project("my-project")
    assert (projects_dir / "my-project" / "urls.txt").exists()


def test_create_project_idempotent(projects_dir):
    create_project("my-project")
    create_project("my-project")  # should not raise


def test_is_transcribed_false_when_no_json(projects_dir):
    create_project("my-project")
    assert not is_transcribed("my-project", "video1")


def test_is_transcribed_true_when_json_exists(projects_dir):
    create_project("my-project")
    json_path = projects_dir / "my-project" / "transcripts" / "video1.json"
    json_path.touch()
    assert is_transcribed("my-project", "video1")


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
