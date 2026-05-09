"""Podcast script generation using OpenAI."""

from pathlib import Path

from openai import OpenAI

from config import settings

_SYSTEM_PROMPT = (
    "You are a podcast script writer. Transform the provided transcript into an engaging "
    "monologue for a single speaker. Use a conversational, warm tone. Keep the key insights "
    "but make them flow naturally when spoken aloud. Aim for 3-5 minutes of speaking time "
    "(roughly 450-750 words). Start with a hook that draws the listener in. End with a clear "
    "takeaway. Write continuous flowing speech — no bullet points, headers, or lists."
)


def generate_podcast_script(transcript_text: str) -> str:
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": f"Here is the transcript:\n\n{transcript_text}"},
        ],
    )
    return response.choices[0].message.content


def save_script(script_text: str, video_name: str, output_folder: Path) -> Path:
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)
    script_path = output_folder / f"{video_name}-podcast-script.txt"
    script_path.write_text(script_text, encoding="utf-8")
    return script_path
