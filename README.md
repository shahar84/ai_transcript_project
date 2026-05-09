# AI Transcript Project

A Python application that extracts audio from video files and transcribes them using Replicate's Whisper model. The main workflow is: video → audio extraction → AI transcription.

## Prerequisites
- Python 3.10+
- [UV](https://docs.astral.sh/uv/) (fast Python package manager)
- Replicate API account and token

## Setup
1. Install UV if you don't have it:

**macOS / Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

2. Install ffmpeg (required by MoviePy for video processing):

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Download from https://ffmpeg.org/download.html or use:
```bash
choco install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update && sudo apt install ffmpeg
```

3. Install dependencies:
```bash
uv sync
```

4. Create a `.env` file from the template and add your Replicate API token:
```bash
cp .env.template .env
```
Then edit `.env` and add your actual Replicate API token

5. Create a `videos` folder and place your video file there:
```bash
mkdir videos
```
The code expects a file named `steve-interview.mp4` in the videos folder. You can either:
- Rename your video to `steve-interview.mp4`, or  
- Edit line 152 in `main.py` to use your video filename

## Usage

### Create a project
```bash
uv run transcript create my-project
```

Edit `projects/my-project/urls.txt` and add YouTube URLs:
```
# One URL per line. Name is optional — if omitted, the YouTube title is used.
https://youtube.com/watch?v=abc
https://youtube.com/watch?v=def my-interview
```

### Run the pipeline
```bash
uv run transcript run my-project
```

Re-running skips videos that have already been transcribed.

## Architecture
The application consists of three main functions in `main.py`:

- `extract_audio()` - Uses MoviePy to extract audio from video files
- `transcribe_audio()` - Sends audio to Replicate's Whisper API for transcription  
- `main()` - Orchestrates the workflow and outputs JSON results

## API Integration
Uses Replicate's incredibly-fast-whisper model for transcription. The application makes HTTP requests to `https://api.replicate.com/v1/predictions` with the audio file and language parameters.

## Output
The application creates an `output` folder with three files:
- `filename.mp3` - Extracted audio from the video
- `filename.txt` - Plain text transcription
- `filename.json` - Full transcription data with timestamps

## Troubleshooting

**MoviePy/ffmpeg errors:**
- Make sure ffmpeg is properly installed and in your PATH
- Try running `ffmpeg -version` to verify installation

**Replicate API errors:**
- Verify your API token is correct in the `.env` file
- Check your Replicate account has sufficient credits

**File not found errors:**
- Ensure your video file is in the `videos` folder
- Check the filename matches what's specified in `main.py` (line 152)
