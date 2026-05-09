# Step 4: Building a CLI

## What We're Building

Running `uv run python` and calling functions manually is fine for development, but it is not how real tools work. In this step we build a proper command-line interface (CLI) so users can run the tool with simple commands like:

```bash
uv run transcript create my-project
uv run transcript run my-project
```

---

## What is a CLI?

A CLI (command-line interface) is a program you interact with by typing commands in a terminal. Every tool you use daily — `git`, `pip`, `ffmpeg` — is a CLI. A good CLI is:

- **Discoverable** — you can run `--help` to see what it can do
- **Predictable** — commands have consistent structure and clear names
- **Friendly** — it gives useful feedback and clear error messages

---

## Meet Typer

[Typer](https://typer.tiangolo.com/) is a Python library for building CLIs with almost no boilerplate. You write regular Python functions and Typer turns them into commands automatically.

It is already in your dependencies.

---

## The Code: `cli.py`

Open `cli.py`. The structure is simple:

```python
app = typer.Typer()

@app.command()
def create(name: str):
    """Create a new transcription project."""
    ...

@app.command()
def run(name: str):
    """Run the full pipeline for a project."""
    ...
```

The `@app.command()` decorator is what makes Typer register the function as a CLI command. The function's docstring becomes the help text.

---

## The `create` Command

```bash
uv run transcript create my-lectures
```

This calls `project.create_project("my-lectures")`, which creates the folder structure and a starter `urls.txt`. Then it prints instructions for the user.

---

## The `run` Command

```bash
uv run transcript run my-lectures
```

This is the main pipeline. For each URL in `urls.txt` it:

1. Checks if the video is already done (`is_complete`) — if yes, skips it
2. Downloads the video (`download_video`)
3. Extracts audio (`extract_audio`)
4. Transcribes audio (`transcribe_audio`)
5. Saves the output (`save_transcription`)

If any step fails, it catches the error, prints a message, and moves on to the next video. This is important — a broken URL should not crash the entire run.

---

## How Typer Knows the Command Name

Open `pyproject.toml` and look for the `[project.scripts]` section:

```toml
[project.scripts]
transcript = "cli:app"
```

This tells Python: when someone runs `transcript`, execute `app` from `cli.py`. After running `uv sync`, the `transcript` command becomes available.

---

## Try It

```bash
# See available commands
uv run transcript --help

# Create a project
uv run transcript create demo

# Add a URL to it
echo "https://www.youtube.com/watch?v=dQw4w9WgXcQ test-video" >> projects/demo/urls.txt

# Run the pipeline
uv run transcript run demo
```

---

## Re-running Is Safe

Run `transcript run demo` a second time. You will see:

```
[1/1] test-video — already done, skipping
```

The pipeline reads the existing `.json` file and skips the video. Nothing is re-downloaded or re-transcribed.

---

## Checkpoint

- [ ] I can run `uv run transcript --help` and see the available commands
- [ ] I created a project, added a URL, and ran the pipeline end-to-end
- [ ] I understand how `pyproject.toml` connects the `transcript` command to `cli.py`
- [ ] I understand why re-running is safe and how the skip logic works

---

Next: [Step 5 - Writing Tests](./step-05-testing.md)
