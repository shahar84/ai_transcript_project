# Step 1: Transcribe a Local Video File
#
# The simplest version of the pipeline.
# Give it a video file -> it extracts the audio -> transcribes it -> saves the results.
#
# What you need:
#   - A video file (we use the sample in tests/fixtures/)
#   - A Replicate API token in your .env file
#
# Run: uv run examples/step1_transcribe_local_file.py

import json
from pathlib import Path
from moviepy.editor import VideoFileClip
import replicate
from config import settings

replicate.api_token = settings.REPLICATE_API_TOKEN

VIDEO_PATH = "tests/fixtures/date.mp4"  # change this to your video
OUTPUT_FOLDER = Path("output")
OUTPUT_FOLDER.mkdir(exist_ok=True)

video_name = Path(VIDEO_PATH).stem

# --- Part 1: Extract audio from the video ---
# Video files contain both video and audio tracks.
# Whisper (our transcription model) only needs the audio.
# MoviePy splits them apart for us.

print("Step 1: Extracting audio from video...")
audio_path = OUTPUT_FOLDER / f"{video_name}.mp3"

with VideoFileClip(VIDEO_PATH) as clip:
    clip.audio.write_audiofile(str(audio_path))

print(f"  Audio saved to: {audio_path}")

# --- Part 2: Transcribe the audio ---
# We send the audio file to Replicate's Whisper model.
# Whisper is an AI model made by OpenAI that converts speech to text.
# Replicate hosts it for us so we don't need to run it locally.

print("Step 2: Transcribing audio (this may take a moment)...")

with open(audio_path, "rb") as f:
    result = replicate.run(
        settings.TRANSCRIBE_MODEL,
        input={"audio": f}
    )

# The result is a dictionary with:
#   "text"   -> the full transcript as a single string
#   "chunks" -> list of segments with timestamps (when each word was spoken)

# --- Part 3: Save the results ---
print("Step 3: Saving results...")

text_path = OUTPUT_FOLDER / f"{video_name}.txt"
json_path = OUTPUT_FOLDER / f"{video_name}.json"

text_path.write_text(result["text"], encoding="utf-8")
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print(f"\nDone!")
print(f"  Plain text -> {text_path}")
print(f"  With timestamps -> {json_path}")
print(f"\nPreview of transcript:\n")
print(result["text"][:300])
