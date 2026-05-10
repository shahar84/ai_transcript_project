# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python CLI tool that downloads YouTube videos, transcribes them using Replicate's Whisper model, generates a podcast script with OpenAI, and synthesizes audio using Gemini TTS via Replicate. Videos are organised into named projects, each with its own URL list, downloaded videos, transcripts, and podcast output.

**Full pipeline:** YouTube URL → download (yt-dlp) → extract audio (MoviePy) → transcribe (Whisper via Replicate) → generate podcast script (OpenAI GPT-4o-mini) → synthesize audio (Gemini TTS via Replicate) → `podcast/episode.wav`

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

Copy `.env.template` to `.env` and fill in your API keys:
```bash
cp .env.template .env
```

Required keys:
- `REPLICATE_API_TOKEN` — for transcription (Whisper) and audio synthesis (Gemini TTS)
- `OPENAI_API_KEY` — for podcast script generation

Optional TTS settings (defaults shown):
- `TTS_VOICE=Kore`
- `TTS_PROMPT=Speak in an engaging, conversational podcast tone.`
- `TTS_LANGUAGE=en-US`

## Running the CLI

```bash
uv run transcript create my-project    # scaffold a new project
uv run transcript run my-project       # download + transcribe all URLs
uv run transcript script my-project    # generate podcast script from all transcripts
uv run transcript podcast my-project   # synthesize podcast audio
uv run transcript podcast my-project --voice-name Zephyr  # use a specific voice
```

Edit `projects/my-project/urls.txt` to add YouTube URLs (one per line, optional name after a space).

## Architecture

```
cli.py          Typer CLI — create, run, script, podcast commands
project.py      Project scaffolding, URL parsing, skip logic (is_transcribed)
downloader.py   yt-dlp wrapper — download videos, resolve titles
main.py         Audio extraction (MoviePy) and transcription (Replicate Whisper)
llm.py          OpenAI podcast script generation and saving
tts.py          Replicate Gemini TTS synthesis — chunking and audio concatenation
config.py       Pydantic settings loaded from .env
```

**Project folder structure:**
```
projects/
  my-project/
    urls.txt         YouTube URLs, one per line (format: URL optional-name)
    videos/          Downloaded video files
    audio/           Extracted .mp3 files
    transcripts/     .txt and .json per video (Whisper output)
    podcast/
      script.txt     Generated podcast script (all transcripts combined)
      episode.wav    Final synthesized audio
```

**Reference schemas:** `schemas/gemini-tts-input.json` — Gemini TTS model input schema

## Key Design Decisions

- **Folder separation:** `audio/`, `transcripts/`, and `podcast/` are kept separate so each pipeline stage reads only its own inputs with no cross-contamination.
- **Script command combines all transcripts:** `transcript script` reads every `.txt` in `transcripts/` and sends them together to OpenAI, producing one podcast script per project.
- **Skip logic:** a video is considered transcribed when its `.json` file exists in `transcripts/`. Re-running a project skips already-transcribed videos.
- **Always slugify:** video names are always slugified (even when user-provided) to prevent filename issues.
- **TTS chunking:** Gemini TTS has a character limit per request. `tts.split_into_chunks()` splits on sentence boundaries and accumulates up to 250 chars. Named booleans (`would_exceed_limit`, `chunk_is_started`) are intentional for student readability.
- **Sequential TTS synthesis:** chunks are synthesized one at a time by design — parallel calls risk Replicate rate limits.

## Teaching Context

This is a course project for a 2.5-hour hands-on session. Students are beginner+ Python developers. See `instructions.md` for the full instructor guide and `steps/` for the step-by-step student materials.

- `steps/step-01-setup.md` through `steps/step-08-whats-next.md` — student step files
- `examples/step1_*.py` through `examples/step6_*.py` — worked examples per step
- `instructions.md` — instructor session guide with timing, talking points, and pitfalls
- `CHEATSHEET.md` — quick command reference for students

## Tests

```bash
uv run pytest tests/ -v
```

Test fixtures (sample video files) live in `tests/fixtures/`. All tests mock external APIs (Replicate, OpenAI) and use `tmp_path` / `monkeypatch` to avoid touching real project folders.
