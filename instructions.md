# Instructor Guide — AI Transcript to Podcast

Students build a CLI tool that takes YouTube URLs, downloads the videos, transcribes the speech with AI, rewrites the content as a podcast script, and synthesizes the audio in a chosen voice. By the end, they run three commands and get a playable podcast episode.

The point is not just to make the tool work. It is to give students a mental model for how AI pipelines are structured: each step has one job, outputs feed the next step, and the whole thing composes cleanly.

---

## Before the Session

Run the full pipeline yourself at least once. Pre-download a short video (under 5 minutes) so you can demo steps without waiting for a live download.

Have students prepare before they arrive:
- Replicate account at replicate.com with an API token ready
- OpenAI account at platform.openai.com with a small credit balance
- ffmpeg installed and working

```bash
# Verify tools are installed
ffmpeg -version
yt-dlp --version
uv --version

# Install Python dependencies
uv sync

# Confirm .env is set up
cat .env
```

---

## Step 1 — Setup and First Transcription

### Introduce first

Before students open any file, draw the pipeline:

```
video file  -->  extract audio  -->  send to AI  -->  text transcript
```

Explain each tool in one sentence: MoviePy opens video files and pulls out the audio track; Replicate is a cloud platform that runs AI models with a single API call; Whisper is OpenAI's speech-to-text model running on Replicate's infrastructure. Do not explain the code structure yet — save that for after they have run it once.

### Show live — raw ffmpeg before the Python wrapper

```bash
# Inspect what's inside a video file
ffprobe videos/my-video.mp4

# Extract audio manually — this is exactly what MoviePy calls under the hood
ffmpeg -i videos/my-video.mp4 audio/my-video.mp3

# With better quality settings
ffmpeg -i videos/my-video.mp4 -q:a 0 -map a audio/my-video.mp3
```

> `-i` means "input". `-vn` means "no video". `extract_audio()` in Python is just calling this same command for you.

Then run the Python version:

```bash
uv sync
uv run examples/step1_transcribe_local_file.py
```

The moment they see the transcription appear is the first "it works" moment — give it space.

### Ask students

"Open `main.py`. Which function does the transcription?" → let them find `transcribe_audio`. Then: "What does it actually send to the model — the video or the audio? Where in the code do you see that?"

### Common pitfalls

- ffmpeg not on PATH — most common blocker on Windows. Test before the session.
- Replicate token not in `.env` — students forget to copy `.env.template` first.
- Students using a long video for their first test — point them to something under 3 minutes.

**Direct students to:** `steps/step-01-setup.md`

---

## Step 2 — YouTube Download

### Introduce first

Ask: "Right now, where does the video file come from?" They'll say: your own computer. Then: "What would it take to handle 50 videos automatically?" Let them articulate the problem before you name the solution.

Key idea: the same tool you use in a terminal can be called from Python code. That is how we automate it.

### Show live — raw yt-dlp before the Python wrapper

```bash
# Get video title without downloading anything
yt-dlp --get-title "https://www.youtube.com/watch?v=fl1DSmwQKKY"

# See all available formats
yt-dlp -F "https://www.youtube.com/watch?v=fl1DSmwQKKY"

# Download as mp4 to current folder
yt-dlp -f "mp4/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]" \
  "https://www.youtube.com/watch?v=fl1DSmwQKKY"

# Download to a specific folder with a specific name
yt-dlp -f "mp4/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]" \
  -o "videos/my-video.%(ext)s" \
  "https://www.youtube.com/watch?v=fl1DSmwQKKY"
```

> `%(ext)s` is a yt-dlp placeholder — not Python. yt-dlp fills in the actual extension after downloading. Then show that `downloader.py` is just wrapping these exact options.

Then run the Python version:

```bash
uv run examples/step2_download_from_youtube.py
```

### Ask students

"In `download_video`, what does `outtmpl` control?" Then: "What would happen if two videos had the same title?" — sets up why slugify matters next. Also: "Why doesn't `download_video` call `extract_audio`? Whose job is that?" — separation of concerns is a design choice, not an accident.

### Common pitfalls

- YouTube rate-limiting if too many students hit it at once — have a fallback short video URL ready.
- Students confused by `%(ext)s` — clarify it is a yt-dlp placeholder, not Python string formatting.

**Direct students to:** `steps/step-02-youtube-download.md`

---

## Step 3 — Project Organization

### Introduce first

Show what happens with no organization: everything in one folder, names clash, you can't tell what came from where. Then show the `projects/` structure. Most students will recognize it as similar to how Git repos or project folders work in any IDE.

The concept to land: **skip logic**. Ask: "What happens if you run the pipeline twice? Should it download the same video again and pay for another transcription?" Let them think through why idempotency matters before reading the code.

### Show live

```bash
uv run examples/step3_projects.py

# Or directly:
uv run transcript create my-test
```

Open the generated `projects/my-test/urls.txt` and read the format out loud. Show the folder structure in a file explorer — visual learners need to see it, not just the terminal.

### Ask students

"Find `is_transcribed`. What does it actually check?" → they should see it looks for a `.json` file. Then: "Why `.json` and not `.txt`? Could you use `.txt` instead?" — no wrong answer, but gets them thinking about design trade-offs.

Bonus: "Run `slugify` on a string with emoji in it. What happens?" — fun result, gets them curious about the implementation.

### Common pitfalls

- Students creating projects in the wrong directory — `PROJECTS_DIR` in `project.py` controls where they land, worth pointing out.
- Confusion between `project_name` (the folder) and `video_name` (the file inside it) — draw the path: `projects/my-project/transcripts/my-video.json`.

**Direct students to:** `steps/step-03-projects.md`

---

## Step 4 — CLI with Typer

### Introduce first

Ask: "Name a CLI tool you use every day." They'll say `git`, `npm`, `python`. Then: "How does `git` know that `git commit` is different from `git push`?" Let them explain. Typer is the Python answer.

A good CLI is a contract: predictable command names, `--help` always works, errors are human-readable.

### Show live

```bash
# See all commands and help text
uv run transcript --help

# Create a project
uv run transcript create demo

# Add a URL
echo "https://www.youtube.com/watch?v=fl1DSmwQKKY claude-video" >> projects/demo/urls.txt

# Run the pipeline
uv run transcript run demo

# Run it again — watch it skip already-done videos
uv run transcript run demo
```

### Ask students

"Where does Typer learn that the command is called `transcript`?" → point them to `pyproject.toml`, the `[project.scripts]` section. Then: "What would you change to rename the command to `pod`?"

Also: "What happens if the URL in `urls.txt` is broken? Does the whole run crash?" → have them read the `try/except` block in the `run` command. Good moment to discuss error handling in pipelines.

### Common pitfalls

- `transcript: command not found` → run `uv sync` first.
- Typer's type hints are load-bearing — if a student deletes the `str` annotation from a parameter, Typer won't know how to parse it.
- Windows backup: `python -m cli` if the entry point doesn't work.

**Direct students to:** `steps/step-04-cli.md`

---

## Step 5 — Tests

### Introduce first

Ask: "Has anyone changed code that worked, introduced a bug, and not noticed until much later?" Every room will nod. Tests are the answer.

Pytest in one sentence: it finds functions whose names start with `test_` and runs them. That is the whole concept.

Two ideas to land before they open the file:
- **Fixtures** isolate tests from each other and from real files on disk.
- **Mocks** replace slow/expensive dependencies (APIs, network) with fake versions that respond instantly.

### Show live

```bash
# Run all tests
uv run pytest -v

# Break a test on purpose — change the expected value in test_slugify_basic, then:
uv run pytest tests/test_project.py::test_slugify_basic -v

# Fix it and run again — back to green
uv run pytest -v

# Run a single file
uv run pytest tests/test_project.py -v
```

The 30-second break-fix-green cycle makes testing feel like a superpower rather than a chore.

### Ask students

"Find `test_is_transcribed_true_when_json_exists`. Why does it call `json_path.touch()` instead of writing real content?" → `is_transcribed` only checks existence, not content — an empty file is enough.

"Find `monkeypatch.setattr`. What would happen to the real `projects/` folder if we didn't use it?" → tests would create real folders on disk and leave them there.

> **This step can be shortened** if you're running behind. Run the tests together as a class, explain fixtures and mocks verbally, skip the "write your own test" exercise. The pipeline steps after this don't depend on it.

### Common pitfalls

- Running `pytest` without `uv run` — wrong Python environment, imports will fail.
- The `test_slugify_numbers` exercise in the step file is intentionally tricky — warn students it's a learning moment, not a bug in pytest.

**Direct students to:** `steps/step-05-testing.md`

---

## Step 6 — Podcast Script with OpenAI

### Introduce first

This is where the pipeline stops being transcription and starts being AI-powered content creation. Introduce the system prompt: the instructions you give the model before the conversation starts. It sets the role, tone, and constraints — separate from the user message.

Ask: "If I said 'turn this transcript into a podcast', what would you do differently than if I said 'summarize this in bullet points'?" That difference is entirely in the system prompt.

### Show live

```bash
uv run transcript script demo
```

Read the output file aloud. Point out specific differences from the raw transcript: cleaner sentences, stronger opening, no filler words.

Then — **the most valuable demo of the session** — change one line of the system prompt in `llm.py` and run it again. Ask for a two-sentence summary. Same input, completely different output. This makes prompt engineering concrete.

```bash
uv run examples/step5_podcast_script.py
```

### Ask students

"Find the system prompt in `llm.py`. What would you add to make it always end with a call to action?" Give them 3 minutes to try it and run the command.

Then: "Why does the prompt say 'no bullet points, headers, or lists'? What would go wrong?" → a TTS engine reads the asterisks and pound signs literally. Connects directly to the next step.

### Common pitfalls

- OpenAI 429 error — account has no credits. New accounts without a payment method hit this immediately.
- Very long transcripts produce scripts too long for TTS — use videos under 5 minutes for the end-to-end demo.
- Students who change the prompt to request structured output (headers, JSON) will break Step 7 — remind them the output needs to be plain flowing prose.

**Direct students to:** `steps/step-06-podcast-script.md`

---

## Step 7 — Voice Synthesis

### Introduce first

Gemini TTS supports named voices and style prompts. You describe how it should sound in plain English. No voice sample or recording needed.

Set up the chunking problem before showing code: "The script is 600 words. The API only accepts 250 characters at a time. How do you solve this without breaking the audio at weird points?" Give them 2 minutes. Someone will say "split by sentences" — that's exactly what the code does.

### Show live

```bash
# Default voice (Kore)
uv run transcript podcast demo

# Try different voices
uv run transcript podcast demo --voice-name Zephyr
uv run transcript podcast demo --voice-name Aoede
```

Play each WAV so the room can hear the difference. Changing one flag changes the entire voice — good demo of how model parameters work.

```bash
uv run examples/step6_podcast_audio.py
```

### Ask students

"Open `tts.py` and find `split_into_chunks`. Why does it split on sentence boundaries rather than just cutting every 250 characters?" → cutting mid-sentence produces broken-sounding audio at the join points.

"Why does it convert audio to a NumPy array instead of saving each chunk as a separate WAV file?" → concatenating binary WAV files is messy; joining arrays and writing once is cleaner.

### Common pitfalls

- Script with abbreviations (`e.g.`, `%`, `$`) will produce garbled audio — have students scan their script before running.
- Replicate takes 10-30 seconds per chunk — a long script takes several minutes total. Don't use a long video for this step.
- soundfile write errors on Windows with spaces in the project path — use simple names with no spaces.

**Direct students to:** `steps/step-07-voice-cloning.md`

---

## Wrap-Up — Full Pipeline End to End

Run the full pipeline as a class on a URL nobody has processed yet.

```bash
uv run transcript create demo-final
# add a URL to projects/demo-final/urls.txt
uv run transcript run demo-final
uv run transcript script demo-final
uv run transcript podcast demo-final
```

Then draw the full pipeline one more time:

```
YouTube URL
  --> yt-dlp         download video        → videos/
  --> MoviePy        extract audio         → audio/
  --> Whisper        transcribe speech     → transcripts/
  --> GPT-4o-mini    rewrite as script     → podcast/script.txt
  --> Gemini TTS     synthesize audio      → podcast/episode.wav
```

Each arrow is one function call. Each function has one job. That is the architecture.

Direct students to `steps/step-08-whats-next.md` — ask: "Which of these would you actually build?" Good closing discussion.

---

## Tips for Keeping Students Unblocked

**Ask before you answer.** When a student is stuck, ask "what does the error say?" before looking at their screen. The actual cause is almost always in the last few lines — most beginners stop reading after the first line.

**Fix forward.** If a student is blocked on Step 3 and the class is on Step 5, give them a working version of the file and move them forward. They can review the diff later.

**Surface the pattern, not the solution.** If two students ask the same question, answer it for the whole room.

**Pair early.** Put students in pairs before Step 4. One types, one reads the step file. Swap roles at each step.

**Name the mental model explicitly.** Every few steps, stop and say: "Here is where we are in the pipeline." Point to the diagram.

**The TTS step surprises people.** When students hear an AI voice read text they wrote, it lands differently than anything else in the session. Let that moment breathe.

---

## Available TTS Voices

Default: **Kore**

```
Achernar  Achird      Algenib    Algieba    Alnilam    Aoede
Autonoe   Callirrhoe  Charon     Despina    Enceladus  Erinome
Fenrir    Gacrux      Iapetus    Laomedeia  Leda       Orus
Pulcherrima  Puck     Rasalgethi Sadachbia  Sadaltager Schedar
Sulafat   Umbriel     Vindemiatrix  Zephyr  Zubenelgenubi
```

---

## API Keys

| Service   | Used in       | Where to get it                        |
|-----------|---------------|----------------------------------------|
| Replicate | Steps 1 and 7 | replicate.com → Account → API Tokens   |
| OpenAI    | Step 6        | platform.openai.com → API Keys         |

Both go in `.env`:

```
REPLICATE_API_TOKEN=your_token_here
OPENAI_API_KEY=sk-...
```

Never commit `.env` to Git. Already in `.gitignore` — but say it out loud anyway.

---

## Common Issues and Fixes

| Problem | Fix |
|---|---|
| `ffmpeg: command not found` | `brew install ffmpeg` (macOS) / `choco install ffmpeg` (Windows) |
| `transcript: command not found` | Run `uv sync` first |
| Replicate 401 error | Check `REPLICATE_API_TOKEN` in `.env` |
| OpenAI 429 error | Account has no credits — add a payment method |
| TTS audio sounds garbled | Script has abbreviations (`e.g.`, `%`) — spell them out |
| Download produces no file | Try the URL in a browser first — some videos are region-locked |
| soundfile write error on Windows | Use a project name with no spaces |
