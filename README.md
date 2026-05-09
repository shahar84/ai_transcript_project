# AI Transcript Project

A Python tool that downloads YouTube videos and transcribes them using AI. Built step by step as a learning project.

**The full pipeline:**
```
YouTube URL  -->  download  -->  extract audio  -->  transcribe  -->  LLM script  -->  your voice  -->  podcast .wav
```

---

## Learning Path

Work through the steps in order. Each one builds on the previous.

| Step | What You Learn |
|------|---------------|
| [Step 1: Setup and Your First Transcription](steps/step-01-setup.md) | Install dependencies, get an API key, run your first transcription |
| [Step 2: Downloading Videos from YouTube](steps/step-02-youtube-download.md) | Use yt-dlp to download any YouTube video automatically |
| [Step 3: Organizing with Projects](steps/step-03-projects.md) | Group related videos into named projects with URL lists |
| [Step 4: Building a CLI](steps/step-04-cli.md) | Build a proper command-line tool with Typer |
| [Step 5: Writing Tests](steps/step-05-testing.md) | Write automated tests with pytest and mocking |
| [Step 7: Writing the Podcast Script with AI](steps/step-07-podcast-script.md) | Use OpenAI to rewrite a transcript as a podcast monologue |
| [Step 8: Generating Your Podcast in Your Own Voice](steps/step-08-voice-cloning.md) | Clone your voice locally with BlueTTS and produce a podcast episode |
| [What You Can Build Next](steps/step-06-whats-next.md) | Ideas for extending the project further |

---

## Quick Start (if you have already done the setup)

```bash
# Install dependencies
uv sync

# Create a project
uv run transcript create my-project

# Add YouTube URLs to projects/my-project/urls.txt
# Format: URL optional-name

# Run the pipeline
uv run transcript run my-project
```

Output files land in `projects/my-project/output/`:
- `video-name.txt` — plain text transcript
- `video-name.json` — full data with timestamps
- `video-name.mp3` — extracted audio

---

## Prerequisites

- Python 3.10+
- [UV](https://docs.astral.sh/uv/) — fast Python package manager
- [ffmpeg](https://ffmpeg.org/) — audio/video processing
- [Replicate](https://replicate.com) account and API token

Full setup instructions are in [Step 1](steps/step-01-setup.md).
