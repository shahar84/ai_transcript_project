# Step 4: Using the CLI
#
# In Step 3 we wrote everything by hand in one long script.
# That works, but it's hard to reuse and easy to break.
#
# In this step we've split the code into focused modules:
#
#   project.py    -> folder setup, URL parsing, skip logic
#   downloader.py -> YouTube download
#   main.py       -> audio extraction and transcription
#   cli.py        -> the Typer CLI that ties it all together
#
# This script shows how those modules work together directly,
# so you can see the connection before using the CLI command.
#
# After this, the CLI replaces this script entirely:
#   uv run transcript create my-project
#   uv run transcript run my-project
#
# Run: uv run examples/step4_using_the_cli.py

from pathlib import Path
import project as proj
from downloader import download_video, get_video_title
from main import extract_audio, transcribe_audio, save_transcription

PROJECT_NAME = "demo-project"

# --- Part 1: Create the project ---
# This is what `uv run transcript create demo-project` does under the hood.

print(f"Creating project: {PROJECT_NAME}")
project_dir = proj.create_project(PROJECT_NAME)
print(f"  Folder ready at: {project_dir}")
print(f"  Add URLs to: {project_dir / 'urls.txt'}")

# --- Part 2: Read the URL list ---
# Reads and parses urls.txt, skipping comments and blank lines.
# Returns a list of (url, name_or_None) tuples.

entries = proj.read_urls(PROJECT_NAME)
if not entries:
    print("\nNo URLs in urls.txt yet. Add some and run again.")
    exit()

print(f"\nFound {len(entries)} URL(s).")

# --- Part 3: Process each video ---
# This is what `uv run transcript run demo-project` does under the hood.

total = len(entries)
for i, (url, video_name) in enumerate(entries, 1):

    # Resolve name from YouTube if not given, then slugify either way
    if not video_name:
        video_name = get_video_title(url)
    video_name = proj.slugify(video_name)

    prefix = f"[{i}/{total}] {video_name}"

    # Skip if the .json file in transcripts/ already exists
    if proj.is_transcribed(PROJECT_NAME, video_name):
        print(f"{prefix} - already done, skipping")
        continue

    try:
        print(f"{prefix} - downloading...")
        video_path = download_video(url, video_name, project_dir / "videos")

        print(f"{prefix} - extracting audio...")
        audio_path = extract_audio(video_path, project_dir / "audio")

        print(f"{prefix} - transcribing...")
        result = transcribe_audio(audio_path)
        save_transcription(result, video_path, project_dir / "transcripts")

    except Exception as e:
        print(f"{prefix} - ERROR: {e}")
        continue

print(f"\nAll done! Transcripts are in: {project_dir / 'transcripts'}/")
print("\nThis is exactly what the CLI does. Try it yourself:")
print(f"  uv run transcript run {PROJECT_NAME}")
