# Project Pipeline Design

## Overview

A project-based workflow for downloading YouTube videos and transcribing them. Each project is a named folder containing a list of YouTube URLs, downloaded videos, and transcription outputs.

## Folder Structure

```
projects/
  my-project/
    urls.txt
    videos/
    output/
```

## URL File Format

One entry per line in `urls.txt`. Name is optional — if omitted, the YouTube video title is used and slugified.

```
https://youtube.com/watch?v=abc123
https://youtube.com/watch?v=def456 steve-interview
https://youtube.com/watch?v=ghi789 product-demo
```

## Code Structure

```
cli.py          ← Typer entry point
project.py      ← project creation, URL parsing, skip logic
downloader.py   ← yt-dlp wrapper
main.py         ← existing audio extraction + transcription (unchanged)
config.py       ← existing settings (unchanged)
```

## CLI Commands

```bash
uv run cli.py create <project-name>   # scaffold project folder + empty urls.txt
uv run cli.py run <project-name>      # run full pipeline for the project
```

## Pipeline (per video)

1. Parse URL line → URL + name (fetch YouTube title if name omitted, slugify)
2. Check if `output/name.json` exists → skip if yes
3. Download video → `projects/<name>/videos/name.mp4` via yt-dlp
4. Extract audio → `projects/<name>/output/name.mp3` via MoviePy
5. Transcribe → `projects/<name>/output/name.txt` + `name.json` via Whisper

## Skip Logic

A video is considered complete if `output/name.json` exists. This is the last file written, so its presence guarantees the full pipeline succeeded.

## Error Handling

If a single video fails (bad URL, download error, transcription error), log the error and continue to the next video. A failed video will be retried on the next `run`.

## Progress Output

```
[1/3] steve-interview — already done, skipping
[2/3] product-demo — downloading...
[2/3] product-demo — transcribing...
[3/3] ceo-talk — downloading...
[3/3] ceo-talk — transcribing...
Done. 2 processed, 1 skipped.
```

## Dependencies

- `typer` — CLI framework (to be added to pyproject.toml)
- `yt-dlp` — YouTube download (already in pyproject.toml)
- `moviepy` — audio extraction (already in pyproject.toml)
- `replicate` — Whisper transcription (already in pyproject.toml)
