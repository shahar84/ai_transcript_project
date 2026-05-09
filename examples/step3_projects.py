# Step 3: Organizing into Projects
#
# When you have multiple videos to transcribe, things get messy fast.
# This step introduces the idea of "projects" — a named folder that
# holds everything related to a group of videos:
#   - urls.txt      list of YouTube URLs to process
#   - videos/       downloaded video files
#   - output/       transcripts and audio
#
# This script creates a project manually and processes its URL list.
# In Step 4 we will package this into a proper CLI tool.
#
# Run: uv run examples/step3_projects.py

import json
from pathlib import Path
import yt_dlp
from moviepy.editor import VideoFileClip
import replicate
from config import settings

replicate.api_token = settings.REPLICATE_API_TOKEN

PROJECT_NAME = "my-first-project"
PROJECTS_DIR = Path("projects")
project_dir = PROJECTS_DIR / PROJECT_NAME

# --- Part 1: Create the project folder structure ---
print(f"Setting up project: {PROJECT_NAME}")

(project_dir / "videos").mkdir(parents=True, exist_ok=True)
(project_dir / "output").mkdir(parents=True, exist_ok=True)

# Create a urls.txt if it doesn't exist yet
urls_file = project_dir / "urls.txt"
if not urls_file.exists():
    urls_file.write_text(
        "# Add YouTube URLs below, one per line\n"
        "# Format: URL optional-name\n"
        "# Example:\n"
        "# https://www.youtube.com/watch?v=dQw4w9WgXcQ rick-astley\n"
    )
    print(f"\nCreated {urls_file}")
    print("Add your YouTube URLs to it and run this script again.")
    exit()

# --- Part 2: Read and parse the URL list ---
# Each line can be:
#   https://youtube.com/...              <- URL only, name comes from YouTube title
#   https://youtube.com/... my-name      <- URL + custom name

def parse_line(line):
    line = line.strip()
    if not line or line.startswith("#"):
        return None, None
    parts = line.split(" ", 1)
    return parts[0], parts[1].strip() if len(parts) > 1 else None

entries = []
for line in urls_file.open():
    url, name = parse_line(line)
    if url:
        entries.append((url, name))

if not entries:
    print("No URLs found in urls.txt. Add some and try again.")
    exit()

print(f"\nFound {len(entries)} URL(s) to process.")

# --- Part 3: Process each URL ---
for i, (url, name) in enumerate(entries, 1):
    print(f"\n[{i}/{len(entries)}] Processing...")

    # Resolve name from YouTube title if not given
    if not name:
        with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
            info = ydl.extract_info(url, download=False)
            name = info["title"].lower().replace(" ", "-")

    print(f"  Name: {name}")

    # Skip if already done — the .json file is the completion marker
    json_path = project_dir / "output" / f"{name}.json"
    if json_path.exists():
        print(f"  Already done, skipping.")
        continue

    # Download
    print(f"  Downloading...")
    ydl_opts = {
        "format": "mp4/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
        "outtmpl": str(project_dir / "videos" / f"{name}.%(ext)s"),
        "quiet": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    video_path = next((project_dir / "videos").glob(f"{name}.*"))

    # Extract audio
    print(f"  Extracting audio...")
    audio_path = project_dir / "output" / f"{name}.mp3"
    with VideoFileClip(str(video_path)) as clip:
        clip.audio.write_audiofile(str(audio_path))

    # Transcribe
    print(f"  Transcribing...")
    with open(audio_path, "rb") as f:
        result = replicate.run(settings.TRANSCRIBE_MODEL, input={"audio": f})

    # Save
    (project_dir / "output" / f"{name}.txt").write_text(result["text"], encoding="utf-8")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"  Done. Transcript saved to output/{name}.txt")

print(f"\nAll done! Find your files in: {project_dir}/output/")
