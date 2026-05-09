"""Podcast audio synthesis using Replicate's XTTS v2 voice cloning model."""

import io
from pathlib import Path

import numpy as np
import replicate
import requests
import soundfile as sf

from config import settings

replicate.api_token = settings.REPLICATE_API_TOKEN

_MAX_CHUNK_CHARS = 250


def _split_into_chunks(text: str) -> list[str]:
    sentences = text.replace("\n", " ").split(". ")
    chunks, current = [], ""
    for sentence in sentences:
        part = sentence.strip() + ". "
        if len(current) + len(part) > _MAX_CHUNK_CHARS and current:
            chunks.append(current.strip())
            current = part
        else:
            current += part
    if current.strip():
        chunks.append(current.strip())
    return chunks


def _fetch_audio(url: str) -> tuple[np.ndarray, int]:
    response = requests.get(url)
    response.raise_for_status()
    audio, sr = sf.read(io.BytesIO(response.content))
    return audio, sr


def synthesize_podcast(
    script_text: str,
    voice_sample_path: str | Path,
    output_path: str | Path,
) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    chunks = _split_into_chunks(script_text)
    voice_data = Path(voice_sample_path).read_bytes()

    audio_segments = []
    sample_rate = None

    for i, chunk in enumerate(chunks, 1):
        print(f"  Synthesizing chunk {i}/{len(chunks)}...")
        audio_url = replicate.run(
            settings.TTS_MODEL,
            input={
                "text": chunk,
                "speaker": io.BytesIO(voice_data),
                "language": "en",
            },
        )
        audio, sr = _fetch_audio(str(audio_url))
        audio_segments.append(audio)
        sample_rate = sr

    combined = np.concatenate(audio_segments)
    sf.write(str(output_path), combined, sample_rate)
    return output_path
