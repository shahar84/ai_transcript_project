# Step 5: Writing Tests

## What We're Building

Good code needs tests. Tests let you change code with confidence, catch bugs before users do, and prove that your code actually works the way you think it does.

In this step we write automated tests for the project using [pytest](https://docs.pytest.org/) — the most popular Python testing framework.

---

## Why Test?

Without tests:
- You do not know if a change broke something else
- You cannot refactor safely
- You have to test manually every single time

With tests:
- Run `uv run pytest` and know in seconds whether everything still works
- Refactor freely — the tests catch regressions
- New contributors can verify their changes immediately

---

## Run the Tests

```bash
uv run pytest
```

You should see all tests pass. To see more detail:

```bash
uv run pytest -v
```

---

## The Test Files

Open the `tests/` folder. There are three test files:

| File | Tests for |
|------|-----------|
| `test_project.py` | `project.py` — URL parsing, slugify, project creation |
| `test_downloader.py` | `downloader.py` — download and title functions |
| `test_cli.py` | `cli.py` — the `create` and `run` commands |

---

## Reading a Test: `test_project.py`

A pytest test is just a function whose name starts with `test_`. pytest finds and runs them automatically.

```python
def test_slugify_basic():
    assert slugify("My Interview with Steve") == "my-interview-with-steve"
```

This test calls `slugify` with a known input and asserts the output is what we expect. Simple.

```python
def test_is_complete_true_when_json_exists(projects_dir):
    create_project("my-project")
    json_path = projects_dir / "my-project" / "output" / "video1.json"
    json_path.touch()          # create an empty file
    assert is_complete("my-project", "video1")
```

This test creates a real folder structure, drops a `.json` file in it, and checks that `is_complete()` returns `True`. It works with real files — no fake file systems.

---

## The `projects_dir` Fixture

Notice how many tests take `projects_dir` as a parameter. This is a **fixture** — a piece of shared setup that pytest injects automatically.

Open `tests/conftest.py`:

```python
@pytest.fixture
def projects_dir(tmp_path, monkeypatch):
    import project
    monkeypatch.setattr(project, "PROJECTS_DIR", tmp_path / "projects")
    return tmp_path / "projects"
```

`tmp_path` is a built-in pytest fixture that gives each test its own empty temporary directory. `monkeypatch.setattr` points `project.PROJECTS_DIR` at that temp directory for the duration of the test.

This means tests never touch your real `projects/` folder — they run in isolation and clean up automatically.

---

## Mocking External Dependencies

We cannot call the real YouTube API or Replicate API in tests — they are slow, they cost money, and they require the internet. Instead we use **mocks**: fake objects that pretend to be the real thing.

From `test_downloader.py`:

```python
def test_get_video_title(tmp_path):
    mock_ydl = make_mock_ydl(title="My Interview")
    with patch("downloader.yt_dlp.YoutubeDL", return_value=mock_ydl):
        title = get_video_title("https://youtube.com/watch?v=abc")
    assert title == "My Interview"
```

`patch` temporarily replaces `yt_dlp.YoutubeDL` with our fake object. The function being tested does not know the difference — it calls the same methods and gets back fake results. The test runs instantly, offline, for free.

---

## Testing the CLI: `test_cli.py`

Typer comes with a `CliRunner` that lets you invoke CLI commands in tests without actually running a subprocess:

```python
runner = CliRunner()

def test_create_command_makes_project(tmp_path, monkeypatch):
    monkeypatch.setattr(proj, "PROJECTS_DIR", tmp_path / "projects")
    result = runner.invoke(app, ["create", "my-project"])
    assert result.exit_code == 0
    assert "my-project" in result.output
```

`runner.invoke(app, ["create", "my-project"])` is equivalent to running `transcript create my-project` but in-process, so we can inspect the output and exit code.

---

## Write Your Own Test

Try adding a new test to `test_project.py`:

```python
def test_slugify_numbers():
    assert slugify("Episode 42 - The Final Chapter") == "episode-42---the-final-chapter"
```

Wait — does that pass? Run `uv run pytest -v` and check. If it fails, look at the `slugify` implementation in `project.py` and think about what the correct expected output should be. Fix the test.

---

## Checkpoint

- [ ] All tests pass with `uv run pytest`
- [ ] I understand what a fixture is and why `projects_dir` uses `tmp_path`
- [ ] I understand why we mock external APIs in tests
- [ ] I added at least one new test of my own

---

Next: [Step 6 - Writing the Podcast Script with AI](./step-06-podcast-script.md)
