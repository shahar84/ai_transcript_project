# Session Cheat Sheet

## Step 1 — Setup

```bash
brew install ffmpeg
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync
cp .env.template .env   # then add REPLICATE_API_TOKEN
```

Run first transcription (local video file):

```bash
uv run examples/step1_transcribe_local_file.py
```

---

## Step 2 — Download from YouTube

```bash
uv run examples/step2_download_from_youtube.py
```

---

## Step 3 — Projects (multi-video)

```bash
uv run examples/step3_projects.py
```

---

## Step 4 — Using the CLI modules directly

```bash
uv run examples/step4_using_the_cli.py
```

---

## Step 5 — The CLI

```bash
uv run transcript create my-project
# add YouTube URLs to projects/my-project/urls.txt
uv run transcript run my-project
```

---

## Step 6 — Tests

```bash
uv run pytest
uv run pytest -v
```

---

## Step 7 — Podcast Script (OpenAI)

Add to `.env`:
```
OPENAI_API_KEY=sk-...
```

```bash
uv run transcript script my-project my-video-name
# output: projects/my-project/output/my-video-name-podcast-script.txt
```

---

## Step 8 — Podcast in Your Own Voice (BlueTTS)

Record 30–60 seconds of yourself speaking (WAV, quiet room) and save it:

```bash
mkdir voices
# save your recording as voices/my-voice.wav
```

```bash
uv run transcript podcast my-project my-video-name --voice voices/my-voice.wav
# output: projects/my-project/output/my-video-name-podcast.wav
```

---

## Full pipeline recap

```
urls.txt
  --> uv run transcript run my-project        (download + transcribe)
  --> uv run transcript script my-project ...  (LLM script)
  --> uv run transcript podcast my-project ... (your voice)
  --> podcast episode .wav
```
