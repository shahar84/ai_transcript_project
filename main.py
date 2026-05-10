"""Audio Transcription Tool

Workflow: video → audio extraction → AI transcription → saved outputs.
All outputs use the video's base filename under the output folder.
"""

from moviepy.editor import VideoFileClip
import json
import replicate
import os
from pathlib import Path

from config import settings

replicate.api_token = settings.REPLICATE_API_TOKEN


def extract_audio(video_path: str | Path, output_folder: str | Path = "output") -> Path:
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)
    audio_path = output_folder / f"{Path(video_path).stem}.mp3"
    with VideoFileClip(str(video_path)) as clip:
        clip.audio.write_audiofile(str(audio_path))
    return audio_path


def transcribe_audio(file_path: str | Path) -> dict:
    with open(file_path, "rb") as f:
        return replicate.run(
            settings.TRANSCRIBE_MODEL,
            input={"audio": f}
        )


def save_transcription(
    transcription_data: dict,
    video_path: str | Path,
    output_folder: str | Path = "output",
) -> tuple[Path, Path]:
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)
    stem = Path(video_path).stem
    text_path = output_folder / f"{stem}.txt"
    json_path = output_folder / f"{stem}.json"

    text_path.write_text(transcription_data["text"], encoding="utf-8")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(transcription_data, f, indent=2, ensure_ascii=False)

    return text_path, json_path


def main(video_path: str | Path):
    video_path = Path(video_path)
    print(f"Starting transcription workflow for: {video_path}")
    print("-" * 50)

    print("1. Extracting audio from video...")
    audio_path = extract_audio(video_path)

    print("2. Transcribing audio (this may take a moment)...")
    result = transcribe_audio(audio_path)

    print("3. Saving transcription files...")
    text_path, json_path = save_transcription(result, video_path)

    print("-" * 50)
    print(f"Audio saved to: {audio_path}")
    print(f"Transcription saved to: {text_path}")
    print(f"Full data saved to: {json_path}")

    return result


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: uv run main.py path/to/video.mp4")
        sys.exit(1)
    main(sys.argv[1])
