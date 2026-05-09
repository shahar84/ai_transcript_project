# Step 3: Organizing with Projects

## What We're Building

So far everything dumps files into a single `videos/` and `output/` folder. If you process multiple videos from different topics, it all gets mixed together.

In this step we add the concept of a **project** — a named folder that keeps a set of related videos and their transcriptions organized together.

```
projects/
  my-lectures/
    urls.txt          <-- list of YouTube URLs to process
    videos/           <-- downloaded videos
    output/           <-- transcriptions
  product-demos/
    urls.txt
    videos/
    output/
```

---

## The `urls.txt` File

Each project has a `urls.txt` file where you list YouTube URLs to transcribe. The format is simple:

```
# Lines starting with # are comments and are ignored
https://youtube.com/watch?v=abc
https://youtube.com/watch?v=def my-custom-name
```

- One URL per line
- Optionally add a name after the URL (separated by a space)
- If no name is given, the YouTube video title is used automatically

---

## The Code: `project.py`

Open `project.py`. It has four functions:

### `create_project(name)`

Creates the folder structure for a new project and writes a starter `urls.txt` with instructions.

### `read_urls(project_name)`

Reads `urls.txt` and returns a list of `(url, name)` pairs, skipping blank lines and comments.

### `is_complete(project_name, video_name)`

Checks whether a video has already been transcribed by looking for its `.json` output file. This is how the pipeline avoids re-processing videos you already have.

### `slugify(text)`

Converts a title like `"My First Interview!"` into a clean filename like `my-first-interview`. No spaces, no special characters.

---

## Why slugify?

File names with spaces and special characters cause problems — in shell commands, in URLs, and across operating systems. Slugifying gives us safe, predictable filenames every time.

Try it:

```python
from project import slugify

print(slugify("How I Built a $1M Company in 90 Days!"))
# how-i-built-a-1m-company-in-90-days
```

---

## The Skip Logic

`is_complete()` is a simple but important function:

```python
def is_complete(project_name: str, video_name: str) -> bool:
    json_path = PROJECTS_DIR / project_name / "output" / f"{video_name}.json"
    return json_path.exists()
```

If the `.json` file already exists, the video is done. The pipeline skips it on the next run.

This matters because transcription costs API credits and takes time. Re-running the same video twice would waste both.

---

## Try It Yourself

```bash
uv run python
```

```python
import project as proj

# Create a project
proj.create_project("my-test")

# Read the (empty) url list
proj.read_urls("my-test")  # returns []

# Check if a video is complete
proj.is_complete("my-test", "some-video")  # returns False
```

Open `projects/my-test/urls.txt` in your editor — the starter template should be there.

---

## Checkpoint

- [ ] I understand the folder structure a project creates
- [ ] I understand why `is_complete()` exists and what problem it solves
- [ ] I can explain what `slugify` does and why it matters

---

Next: [Step 4 - Building a CLI](./step-04-cli.md)
