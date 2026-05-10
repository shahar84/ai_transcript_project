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
uv run transcript script my-project
# combines all transcripts → projects/my-project/podcast/script.txt
```

---

## Step 8 — Podcast Audio (Gemini TTS)

```bash
uv run transcript podcast my-project
# output: projects/my-project/podcast/episode.wav

# optional: choose a different voice
uv run transcript podcast my-project --voice-name Zephyr
```

Available voices: Achernar, Achird, Algenib, Algieba, Alnilam, Aoede, Autonoe,
Callirrhoe, Charon, Despina, Enceladus, Erinome, Fenrir, Gacrux, Iapetus, Kore (default),
Laomedeia, Leda, Orus, Pulcherrima, Puck, Rasalgethi, Sadachbia, Sadaltager,
Schedar, Sulafat, Umbriel, Vindemiatrix, Zephyr, Zubenelgenubi

---

## Full pipeline recap

```
urls.txt
  --> uv run transcript run my-project      (download + transcribe)
  --> uv run transcript script my-project   (LLM script from all transcripts)
  --> uv run transcript podcast my-project  (Gemini TTS audio)
  --> projects/my-project/podcast/episode.wav
```
