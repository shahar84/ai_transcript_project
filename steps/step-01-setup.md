# Step 1: Setup and Your First Transcription

## What We're Building

In this step you will set up the project and run your first AI transcription. By the end, you will take a video file, extract its audio, and get back a full text transcript — automatically.

The pipeline looks like this:

```
video file  -->  extract audio  -->  send to AI  -->  text transcript
```

---

## Prerequisites

Before writing any code, you need a few tools installed.

### 1. Install ffmpeg

ffmpeg is a command-line tool that handles audio and video files. MoviePy (our Python library) uses it under the hood.

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Download from https://ffmpeg.org/download.html or run:
```bash
choco install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update && sudo apt install ffmpeg
```

Verify it works:
```bash
ffmpeg -version
```

### 2. Install UV

UV is a fast Python package manager. Think of it as a better `pip`.

**macOS / Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 3. Install Python dependencies

```bash
uv sync
```

This reads `pyproject.toml` and installs everything the project needs into an isolated environment.

---

## Get a Replicate API Token

We use [Replicate](https://replicate.com) to run the Whisper AI model in the cloud. You need a free account and an API token.

1. Sign up at https://replicate.com
2. Go to your account settings and copy your API token
3. Copy the template file and add your token:

```bash
cp .env.template .env
```

Open `.env` and replace the placeholder:

```
REPLICATE_API_TOKEN=your_token_here
```

**Important:** Never commit your `.env` file to Git. It is already listed in `.gitignore`.

---

## Add a Video File

Create a `videos` folder and place an MP4 file inside it:

```bash
mkdir videos
```

Then copy or download any video into that folder. The code currently expects a file called `steve-interview.mp4`, but you can use any name — just update line 76 in `main.py` to match:

```python
if __name__ == "__main__":
    main("videos/your-video.mp4")  # <-- change this
```

---

## Run It

```bash
uv run main.py
```

You should see output like:

```
Starting transcription workflow for: videos/steve-interview.mp4
--------------------------------------------------
1. Extracting audio from video...
2. Transcribing audio (this may take a moment)...
3. Saving transcription files...
--------------------------------------------------
Audio saved to: output/steve-interview.mp3
Transcription saved to: output/steve-interview.txt
Full data saved to: output/steve-interview.json
```

---

## What Just Happened?

Open `main.py` and follow the code. Three functions do all the work:

### `extract_audio(video_path)`
Uses MoviePy to open the video and write out just the audio as an MP3 file.

### `transcribe_audio(file_path)`
Sends the MP3 to Replicate's [incredibly-fast-whisper](https://replicate.com/vaibhavs10/incredibly-fast-whisper) model. Whisper is an open-source AI from OpenAI that can transcribe speech in dozens of languages.

### `save_transcription(data, video_path)`
Saves the result in two formats:
- `.txt` — plain text, easy to read
- `.json` — full data including timestamps for every word

---

## Check Your Output

Look at the files in the `output/` folder:

- Open the `.txt` file — is the transcription accurate?
- Open the `.json` file — find the `segments` key and look at the timestamps

---

## Checkpoint

Before moving on, make sure you can answer these questions:

- [ ] The transcription ran successfully and output files were created
- [ ] I understand which function does what in `main.py`
- [ ] I know where my API token is stored and why it should not be committed to Git

---

Next: [Step 2 - Downloading Videos from YouTube](./step-02-youtube-download.md)
