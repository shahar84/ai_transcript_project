"""Podcast audio synthesis using Replicate's Gemini TTS model."""

import io
from pathlib import Path

import numpy as np
import replicate
import soundfile as sf

from config import settings

replicate.api_token = settings.REPLICATE_API_TOKEN

_MAX_CHUNK_CHARS = 250


def split_into_chunks(text: str) -> list[str]:
    """Split text into sentence-grouped chunks under _MAX_CHUNK_CHARS to stay within TTS limits."""
    sentences = text.replace("\n", " ").split(". ")
    chunks, current = [], ""
    for sentence in sentences:
        part = sentence.strip() + ". "
        would_exceed_limit = len(current) + len(part) > _MAX_CHUNK_CHARS
        chunk_is_started = bool(current)
        if would_exceed_limit and chunk_is_started:
            chunks.append(current.strip())
            current = part
        else:
            current += part
    if current.strip():
        chunks.append(current.strip())
    return chunks


def synthesize_podcast(
    script_text: str,
    output_path: str | Path,
    voice_name: str | None = None,
    prompt: str | None = None,
    language_code: str | None = None,
) -> Path:
    """Splits script into chunks, synthesizes each via Replicate, then concatenates into one WAV."""
    dest = Path(output_path)
    dest.parent.mkdir(parents=True, exist_ok=True)

    chunks = split_into_chunks(script_text)
    if not chunks:
        raise ValueError("Script text produced no chunks to synthesize.")

    audio_segments = []
    sample_rate: int = 0

    # Sequential by design — parallel calls risk Replicate rate limits
    for i, chunk in enumerate(chunks, 1):
        print(f"  Synthesizing chunk {i}/{len(chunks)}...")
        output = replicate.run(
            settings.TTS_MODEL,
            input={
                "text": chunk,
                "voice": voice_name or settings.TTS_VOICE,
                "prompt": prompt or settings.TTS_PROMPT,
                "language_code": language_code or settings.TTS_LANGUAGE,
            },
        )
        audio, sample_rate = sf.read(io.BytesIO(output.read()))
        audio_segments.append(audio)

    combined = np.concatenate(audio_segments)
    sf.write(str(dest), combined, sample_rate)
    return dest
