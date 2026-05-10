# Instructor Guide: AI Transcript-to-Podcast Pipeline

A 2.5-hour hands-on coding session for beginner+ Python developers.

---

## What You're Teaching

Students build a CLI tool that takes YouTube URLs, downloads the videos, transcribes the speech with AI, rewrites the content as a podcast script, and synthesizes the audio in a chosen voice. By the end, they run three commands and get a playable podcast episode.

The point is not just to make the tool work. It is to give students a mental model for how AI pipelines are structured: each step has one job, outputs feed the next step, and the whole thing composes cleanly.

---

## Session Structure at a Glance

| Block | Steps | Time |
|---|---|---|
| Setup and first transcription | Steps 1 | 25 min |
| YouTube download | Step 2 | 20 min |
| Project organization | Step 3 | 20 min |
| CLI with Typer | Step 4 | 20 min |
| Break | — | 10 min |
| Testing | Step 5 | 20 min |
| Podcast script with OpenAI | Step 6 | 20 min |
| Voice synthesis | Step 7 | 20 min |
| Full end-to-end run + wrap-up | Step 8 | 15 min |

**Total:** ~2h 30m. The testing step (Step 5) can be shortened to 10 minutes if you run behind — it does not block the rest of the pipeline.

---

## Before the Session

Set up your own environment completely and run the full pipeline at least once. Know which API keys you need: Replicate (Steps 1 and 7) and OpenAI (Step 6). Pre-download a short video (under 5 minutes) so you can demo steps without waiting for a live download.

Have students prepare these before they arrive:
- A Replicate account at replicate.com
- An OpenAI account at platform.openai.com with a small credit balance
- ffmpeg installed and working (`ffmpeg -version` should print a version string)
- A Replicate account with a token ready (used in Steps 1 and 7)

---

## Step 1: Setup and First Transcription (25 min)

**Concept to introduce verbally first**

Before students open any file, spend 3 minutes drawing the pipeline on a whiteboard or sharing your screen with a text diagram:

```
video file --> extract audio --> send to AI --> text transcript
```

Then explain what each tool does in one sentence: MoviePy opens video files and pulls out the audio track; Replicate is a cloud platform that lets you run AI models with a single API call; Whisper is OpenAI's speech-to-text model that runs on Replicate's infrastructure.

Do not explain how the code is structured yet. Save that for after they have run it once.

**Direct students to:** `steps/step-01-setup.md`

**What to show live**

Run `uv sync` so they can see what a successful install looks like. Then run `uv run main.py` against a real video file and watch the output together. The moment they see the transcription appear in the output folder is the first "it works" moment — give it space.

**What to ask them to figure out**

After it runs: "Open `main.py`. Can you tell me which function does the transcription?" Let them find `transcribe_audio`. Then: "What does it actually send to the model — the video or just the audio? Where in the code do you see that?" They should find that `extract_audio` runs first and the MP3 path is what gets sent to Replicate.

**Common pitfalls**

- ffmpeg not installed or not on PATH. Test this before the session. On Windows this is the most common blocker.
- Replicate token not in `.env` — students put it in the wrong file or forget to copy `.env.template` first.
- MoviePy version mismatches on Python 3.12+. If `uv sync` installs cleanly, this should not appear, but watch for import errors.
- Students using a very long video for their first test. Point them toward something under 3 minutes.

---

## Step 2: YouTube Download (20 min)

**Concept to introduce verbally first**

Ask the room: "Right now, where does the video file come from?" They should say: your own computer. Then ask: "What would it take to handle 50 videos automatically?" Let them articulate the problem before you name the solution.

Introduce yt-dlp as a library, not just a command-line tool. The key idea: the same tool you use in a terminal can be called from Python code. That is how we automate it.

**Direct students to:** `steps/step-02-youtube-download.md`

**What to show live**

Open a Python shell and run `get_video_title` against a short video URL. The fact that it returns the title without downloading anything is a useful concept to land: you can ask the internet for metadata separately from the actual content.

**What to ask them to figure out**

"In `download_video`, what does `outtmpl` control?" Let them read the code. Then: "What would happen if two videos had the same title? Would they overwrite each other?" This sets up why slugify and named projects matter in the next step.

Also ask: "Why does the downloader not call `extract_audio`? Whose job is that?" You want them to see that separation of concerns is a design choice, not an accident.

**Common pitfalls**

- YouTube rate-limiting if too many students hit the API at once. Have a fallback video URL that downloads quickly (official YouTube test videos or Creative Commons clips).
- yt-dlp format string errors on some video types. The format string in the step file is conservative — stick with it.
- Students not understanding `%(ext)s` in the output template. It is a yt-dlp placeholder, not a Python format string. Worth clarifying once.

---

## Step 3: Project Organization (20 min)

**Concept to introduce verbally first**

Show what happens when you transcribe 10 videos with no organization: everything lands in one folder, names clash, you cannot tell what came from where. Then show the `projects/` structure and ask: "Does this look familiar?" Most students will recognize it as similar to how Git repos or project folders work in any IDE.

The concept to land here is **skip logic**. Ask: "What happens if you run the pipeline twice? Should it download the same video again and pay for another transcription?" Let them think through why idempotency matters before reading the code.

**Direct students to:** `steps/step-03-projects.md`

**What to show live**

Create a project folder live, then open the generated `urls.txt` and read the format out loud. Show them the folder structure in a file explorer (not just the terminal). Visual learners need to see it.

**What to ask them to figure out**

"Find `is_complete`. What does it actually check?" They should read the function and see it looks for a `.json` file. Then: "Why `.json` and not `.txt`? Could you change it to check for `.txt` instead?" This is a design trade-off question — no wrong answer, but get them thinking about it.

Also try: "Run `slugify` on a string with emoji in it. What happens?" This usually produces a fun result and gets them curious about the implementation.

**Common pitfalls**

- Students creating projects in the wrong directory. The `PROJECTS_DIR` constant in `project.py` controls where projects land — worth pointing it out explicitly.
- Confusion about the difference between `project_name` (the folder) and `video_name` (the individual file within it). Draw the path on the board: `projects/my-project/output/my-video.json`.

---

## Step 4: CLI with Typer (20 min)

**Concept to introduce verbally first**

Ask: "Name a CLI tool you use every day." They will say `git`, `npm`, `python`, something like that. Then: "How does `git` know that `git commit` is different from `git push`?" Let them explain in their own words. Typer is the answer for Python.

Make the point that a good CLI is not just convenient — it is a contract. Users know what to expect. Commands have predictable names, `--help` always works, and errors are human-readable.

**Direct students to:** `steps/step-04-cli.md`

**What to show live**

Run `uv run transcript --help` and let the room read the output together. Then run `uv run transcript create demo`. Then immediately run it again — nothing should crash. Then run `uv run transcript run demo` with a URL in `urls.txt`, and when it completes, run it a second time so they see the "already done, skipping" message.

**What to ask them to figure out**

"Where in the code does Typer learn that the command is called `transcript`?" Point them to `pyproject.toml`. Let them find the `[project.scripts]` section. Then: "What would you change to rename the command to `pod`?" They should be able to answer without guessing.

Also ask: "What happens if the YouTube URL in `urls.txt` is broken? Does the whole run crash?" Have them read the `try/except` block in the `run` command. This is a good moment to discuss why error handling matters in a pipeline.

**Common pitfalls**

- Students who did not run `uv sync` after setting up the project scripts will not have `transcript` available. Run `uv sync` if the command is not found.
- Typer's type hints are load-bearing. If a student removes the `str` annotation from a command parameter, Typer will not know how to parse it. Mention this once so they do not accidentally delete annotations while editing.
- Windows students may need to run `python -m cli` if the entry point does not work. Have this as a backup.

---

## Break (10 min)

Good place to stop. At this point students have a working CLI that downloads, transcribes, and organizes videos. Let them try it on a YouTube URL of their own choosing during the break.

---

## Step 5: Testing (20 min)

**Concept to introduce verbally first**

Ask: "Has anyone here changed code that worked, then introduced a bug, and not noticed until much later?" Every room will nod. Tests are the answer.

Introduce pytest in one sentence: it finds functions whose names start with `test_` and runs them. That is the whole concept. Everything else is details.

The two ideas to land before they open the file:
1. **Fixtures** isolate tests from each other and from real resources on disk.
2. **Mocks** replace slow or expensive dependencies (APIs, network calls) with fake versions that respond instantly.

**Direct students to:** `steps/step-05-testing.md`

**What to show live**

Run `uv run pytest -v` so they see green passing tests. Then break one test intentionally — change an expected value in `test_slugify_basic` — and run again. Let them see the red failure output and read the diff pytest provides.

Then restore the test and run again. The point: the test suite is a safety net, and it tells you exactly what broke.

**What to ask them to figure out**

"Find `test_is_complete_true_when_json_exists`. Why does it call `json_path.touch()` instead of writing real content to the file?" They should work out that `is_complete` only checks if the file exists — not what is in it — so an empty file is enough.

Also: "Find where `monkeypatch.setattr` is used. What would happen to the real `projects/` folder if we did not do that?" This usually clicks when they realize tests would create real folders on disk and leave them there.

**This step can be shortened.** If you are behind schedule, run the tests together as a class, explain the fixture and mock concepts verbally, and skip the "write your own test" exercise. The pipeline steps that follow do not depend on students having written their own tests.

**Common pitfalls**

- Students running `pytest` without `uv run` — wrong Python environment, imports will fail.
- The intentionally tricky `test_slugify_numbers` exercise in the step file may produce a failing test depending on the slugify implementation. That is intentional — the step file says so. Warn students it is a learning moment, not a bug in the test runner.

---

## Step 6: Podcast Script with OpenAI (20 min)

**Concept to introduce verbally first**

This is where the pipeline stops being just transcription and starts being AI-powered content creation. Introduce the idea of a system prompt: the instructions you give the model before the conversation starts. The system prompt is separate from the user message — it sets the role, tone, and constraints.

Ask: "If I gave you a raw transcript and said 'turn this into a podcast', what would you do differently than if I said 'summarize this in bullet points'?" That difference is entirely controlled by the system prompt.

**Direct students to:** `steps/step-06-podcast-script.md`

**What to show live**

Run the `script` command on a transcript you already have from earlier in the session. Read the output file aloud with the class. Point out specific differences between the raw transcript and the generated script: cleaner sentences, stronger opening, no filler words.

Then — this is the most valuable demo of the session — change one line of the system prompt and run it again. Ask for a two-sentence summary instead of five minutes of content. Show that the exact same input produces completely different output based on the instruction alone. This makes prompt engineering concrete.

**What to ask them to figure out**

"Find the system prompt in `llm.py`. What would you add to make the script always end with a call to action?" Give them 3 minutes to try a change and run the command.

Then ask: "Why does the system prompt say 'no bullet points, headers, or lists'? What would go wrong if the output had markdown formatting?" They should work out that a TTS engine would read out the asterisks and pound signs literally.

**Common pitfalls**

- OpenAI API key errors. Make sure students have credit on their account — a new account with no payment method will get a 429 before they even start.
- Very long transcripts that produce scripts that are too long for TTS in Step 7. If a transcript is more than 1,500 words, the generated script may run over the chunking limit. Ask students to use a short video (under 5 minutes) for the end-to-end demo.
- Students who change the system prompt and ask for structured output (headers, JSON) will have problems in Step 7. Remind them the output needs to be plain flowing prose.

---

## Step 7: Voice Synthesis (20 min)

**Concept to introduce verbally first**

Explain that Gemini TTS is a text-to-speech model that supports named voices and style prompts. You tell it how to speak — the tone, pace, and emotion — using plain English, and it applies that to the text. No voice sample needed.

The chunking concept is worth explaining before they look at the code: the model has a character limit per request, so long scripts get split into sentence-sized pieces, each piece gets synthesized separately, and then the audio arrays get joined back together.

**Direct students to:** `steps/step-07-podcast-audio.md`

**What to show live**

Run the `podcast` command. The default voice is Kore — play the output WAV for the class. Then run it again with a different voice using `--voice-name Zephyr` so they hear the difference. The fact that changing one flag changes the entire voice is a good demo of how model parameters work.

**What to ask them to figure out**

"Open `tts.py` and find `_split_into_chunks`. Why does it split on sentence boundaries rather than just cutting every 250 characters?" They should work out that cutting mid-sentence would produce audio that sounds broken at the join points.

Then: "Look at `_fetch_audio`. Why does it convert the audio to a NumPy array instead of just saving each chunk to a WAV file?" The answer is that concatenating binary WAV files is not straightforward — joining NumPy arrays and writing once is cleaner.

**Common pitfalls**

- Script with abbreviations or symbols will produce garbled audio. "e.g.", "%", "$" — the model reads them literally or skips them. Have students scan their script for these before running.
- The Replicate API takes 10-30 seconds per chunk. A long script can take several minutes total. Do not let students use a 30-minute video for this step.
- soundfile write errors on Windows if the output path has spaces. Tell students to use simple project names with no spaces.

---

## Putting It All Together (15 min)

This is the payoff. Run the full pipeline end-to-end as a class using a URL nobody has processed yet.

```bash
uv run transcript create demo-final
# add URLs to projects/demo-final/urls.txt
uv run transcript run demo-final
uv run transcript script demo-final
uv run transcript podcast demo-final
```

Walk through each command and name what just happened: download, transcribe, rewrite, synthesize. Point to the output files at each stage. Let students open the podcast WAV and listen.

Then draw the full pipeline on the board one more time:

```
YouTube URL
  --> yt-dlp: download video
  --> MoviePy: extract audio
  --> Whisper (Replicate): transcribe
  --> GPT-4o-mini (OpenAI): rewrite as script
  --> XTTS v2 (Replicate): synthesize voice
  --> episode.wav
```

Each arrow is one function call. Each function has one job. That is the architecture.

**Direct students to:** `steps/step-08-whats-next.md` — give them 5 minutes to read the ideas section. Ask: "Which of these would you actually build?" A show of hands on a few options gives you a natural closing discussion.

---

## Tips for Keeping Students Unblocked

**Ask before you answer.** When a student is stuck, ask "what does the error say?" before looking at their screen. Most beginners stop reading after the first line of an error message. The actual cause is almost always in the last few lines.

**Fix forward.** If a student is blocked on Step 3 and the class is on Step 5, do not spend 10 minutes debugging Step 3. Give them a working version of their `project.py` file and move them forward. They can review the diff later.

**Surface the pattern, not the solution.** If two students ask the same question in a row, answer it for the whole room. Do not answer the same question eight times individually — it wastes time and makes slower students feel behind.

**Pair early.** Put students in pairs before Step 4. One types, one reads the step file and asks questions. Swap roles at each step. Students who would be stuck alone are often fine in a pair.

**Name the mental model explicitly.** Beginners get lost because they do not have a framework for what they are looking at. Every 20 minutes, stop and say: "Here is where we are in the pipeline." Point to the diagram. Then continue.

**The voice cloning step surprises people.** When students hear their voice (or your voice) come out of the speaker reading text they typed, it lands differently than anything else in the session. Let that moment breathe. Do not rush to the next slide.

---

## API Key Reference

| Service | Used in | Where to get it |
|---|---|---|
| Replicate | Steps 1 and 7 | replicate.com > Account Settings > API Tokens |
| OpenAI | Step 6 | platform.openai.com > API Keys |

Both go in `.env`:

```
REPLICATE_API_TOKEN=your_token_here
OPENAI_API_KEY=sk-...
```

Students must never commit `.env` to Git. It is already in `.gitignore`, but say it out loud once anyway.
