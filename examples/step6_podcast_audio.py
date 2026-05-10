# Step 6: Generating Podcast Audio with Gemini TTS
#
# You have a podcast script. Now we turn it into audio using
# Google's Gemini TTS model running on Replicate.
#
# The challenge: TTS models have a character limit per request.
# We solve this by splitting the script into sentence-sized chunks,
# synthesizing each one separately, then joining the audio together.
#
# This script reads the script from podcast/script.txt, synthesizes
# each chunk, and writes the final episode to podcast/episode.wav.
#
# Run: uv run examples/step6_podcast_audio.py

import io
from pathlib import Path

import numpy as np
import replicate
import soundfile as sf

from config import settings
from tts import split_into_chunks

replicate.api_token = settings.REPLICATE_API_TOKEN

PROJECT_NAME = "my-first-project"
PROJECTS_DIR = Path("projects")

VOICE = "Kore"          # change this to try different voices
STYLE_PROMPT = "Speak in an engaging, conversational podcast tone."

# --- Part 1: Load the script ---
script_path = PROJECTS_DIR / PROJECT_NAME / "podcast" / "script.txt"

if not script_path.exists():
    print(f"Script not found at {script_path}")
    print(f"Run 'uv run transcript script {PROJECT_NAME}' first.")
    exit()

script_text = script_path.read_text(encoding="utf-8")
print(f"Script loaded ({len(script_text)} characters)")

# --- Part 2: Split into chunks ---
# The TTS model has a character limit per request.
# We split on sentence boundaries so the audio joins cleanly.

chunks = split_into_chunks(script_text)
print(f"Split into {len(chunks)} chunks")

# --- Part 3: Synthesize each chunk ---
audio_segments = []
sample_rate: int = 0

for i, chunk in enumerate(chunks, 1):
    print(f"  Synthesizing chunk {i}/{len(chunks)}...")
    output = replicate.run(
        settings.TTS_MODEL,
        input={
            "text": chunk,
            "voice": VOICE,
            "prompt": STYLE_PROMPT,
            "language_code": "en-US",
        },
    )
    audio, sample_rate = sf.read(io.BytesIO(output.read()))
    audio_segments.append(audio)

# --- Part 4: Join and save ---
combined = np.concatenate(audio_segments)
output_path = PROJECTS_DIR / PROJECT_NAME / "podcast" / "episode.wav"
sf.write(str(output_path), combined, sample_rate)

print(f"\nPodcast episode saved to: {output_path}")
print("\nThis is exactly what the CLI does. Try it yourself:")
print(f"  uv run transcript podcast {PROJECT_NAME}")
