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
