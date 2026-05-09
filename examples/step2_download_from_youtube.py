# Step 2: Download from YouTube and Transcribe
#
# Same pipeline as Step 1, but instead of a local file
# we start with a YouTube URL and download the video first.
#
# yt-dlp is a command-line tool (and Python library) that can download
# videos from YouTube and hundreds of other sites.
#
# What you need:
#   - A YouTube URL
#   - A Replicate API token in your .env file
#
# Run: uv run examples/step2_download_from_youtube.py

import json
from pathlib import Path
import yt_dlp
from moviepy.editor import VideoFileClip
import replicate
from config import settings

replicate.api_token = settings.REPLICATE_API_TOKEN

URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # replace with your URL
OUTPUT_FOLDER = Path("output")
OUTPUT_FOLDER.mkdir(exist_ok=True)

# --- Part 1: Fetch video info (without downloading yet) ---
# Before downloading, we can ask yt-dlp for metadata:
# title, duration, uploader, etc.

print("Step 1: Fetching video info...")
with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
    info = ydl.extract_info(URL, download=False)
    title = info["title"]
    duration = info["duration"]

print(f"  Title: {title}")
print(f"  Duration: {duration} seconds")

# --- Part 2: Download the video ---
# yt-dlp picks the best available quality.
# We tell it what filename to use with "outtmpl".
# %(ext)s is a placeholder that yt-dlp fills in with the actual extension (.mp4, etc.)

print("Step 2: Downloading video...")
video_name = "downloaded-video"
video_path = OUTPUT_FOLDER / f"{video_name}.mp4"

ydl_opts = {
    "format": "mp4/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
    "outtmpl": str(OUTPUT_FOLDER / f"{video_name}.%(ext)s"),
    "quiet": True,
}
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([URL])

# find the actual downloaded file (extension may vary)
video_path = next(OUTPUT_FOLDER.glob(f"{video_name}.*"))
print(f"  Video saved to: {video_path}")

# --- Part 3: Extract audio ---
print("Step 3: Extracting audio...")
audio_path = OUTPUT_FOLDER / f"{video_name}.mp3"

with VideoFileClip(str(video_path)) as clip:
    clip.audio.write_audiofile(str(audio_path))

print(f"  Audio saved to: {audio_path}")

# --- Part 4: Transcribe ---
print("Step 4: Transcribing (this may take a moment)...")
with open(audio_path, "rb") as f:
    result = replicate.run(
        settings.TRANSCRIBE_MODEL,
        input={"audio": f}
    )

# --- Part 5: Save results ---
print("Step 5: Saving results...")
(OUTPUT_FOLDER / f"{video_name}.txt").write_text(result["text"], encoding="utf-8")
with open(OUTPUT_FOLDER / f"{video_name}.json", "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print(f"\nDone!")
print(f"\nPreview:\n")
print(result["text"][:300])
