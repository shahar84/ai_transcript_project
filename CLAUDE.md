# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python CLI tool that downloads YouTube videos and transcribes them using Replicate's Whisper model. Videos are organised into named projects, each with its own URL list, downloaded videos, and transcription outputs.

**Pipeline:** YouTube URL → download (yt-dlp) → extract audio (MoviePy) → transcribe (Whisper via Replicate) → save .txt + .json

## Setup

Install ffmpeg:
```bash
brew install ffmpeg          # macOS
choco install ffmpeg         # Windows
sudo apt install ffmpeg      # Linux
```

Install dependencies:
```bash
uv sync
```

Copy `.env.template` to `.env` and add your Replicate API token:
```bash
cp .env.template .env
```

## Running the CLI

```bash
uv run transcript create my-project    # scaffold a new project
uv run transcript run my-project       # download + transcribe all URLs
```

Edit `projects/my-project/urls.txt` to add YouTube URLs (one per line, optional name after a space).

## Architecture

```
cli.py          Typer CLI — create and run commands
project.py      Project scaffolding, URL parsing, skip logic
downloader.py   yt-dlp wrapper — download videos, resolve titles
main.py         Audio extraction (MoviePy) and transcription (Replicate)
config.py       Pydantic settings loaded from .env
```

**Project folder structure:**
```
projects/
  my-project/
    urls.txt       YouTube URLs, one per line
    videos/        Downloaded video files
    output/        .mp3, .txt, .json per video
```

**Skip logic:** a video is considered complete when its `.json` output file exists. Re-running a project skips completed videos.

## Tests

```bash
uv run pytest tests/ -v
```

Test fixtures (sample video files) live in `tests/fixtures/`.
