# NotebookLM Pipeline Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Extend the existing transcription project into a NotebookLM-like pipeline: YouTube URL → audio → transcript → LLM summary + key points → text-to-speech audio overview.

**Architecture:** Split `main.py` into focused modules under a `pipeline/` package, each mapping to one workshop layer students build themselves. `main.py` becomes a thin orchestrator that students receive pre-written, so they see the full system before implementing any part of it.

**Tech Stack:** Python, yt-dlp (YouTube download), Replicate Whisper (transcription, existing), OpenAI gpt-4o-mini (LLM processing), OpenAI TTS (speech synthesis), pytest (tests)

---

## Workshop Branch Strategy

After the solution is complete and merged to `master`:
- `workshop/starter` — all pipeline functions stubbed with `raise NotImplementedError`
- `workshop/layer-1` — `ingest.py` implemented, rest stubbed
- `workshop/layer-2` — `ingest.py` + `process.py` implemented, `tts.py` stubbed
- `workshop/layer-3` — everything implemented (same as master)

Students get `workshop/starter`. Each layer branch is the reference solution for that stage.

---

## Task 0: Feature Branch + Dependencies

**Files:**
- Modify: `requirements.txt`

**Step 1: Create feature branch**
```bash
git checkout -b feature/notebooklm-pipeline
```

**Step 2: Add yt-dlp to requirements**

Add `yt-dlp` as a new line in `requirements.txt`. Final file:
```
moviepy==1.0.3
requests==2.32.4
python-dotenv==1.1.1
pydantic-settings
replicate
openai
yt-dlp
```

**Step 3: Install new dependency**
```bash
pip install yt-dlp
```
Expected: installs without errors.

**Step 4: Commit**
```bash
git add requirements.txt
git commit -m "chore: add yt-dlp dependency"
```

---

## Task 1: Restructure Into Pipeline Package

Split `main.py` into focused modules. Students will receive `pipeline/transcribe.py` pre-filled (it's already built), and stub out the rest.

**Files:**
- Create: `pipeline/__init__.py`
- Create: `pipeline/transcribe.py`
- Modify: `main.py`
- Create: `tests/__init__.py`
- Create: `tests/test_transcribe.py`

**Step 1: Create pipeline package**
```bash
mkdir -p pipeline tests
touch pipeline/__init__.py tests/__init__.py
```

**Step 2: Create `pipeline/transcribe.py`**

Move the three functions from `main.py` into this file:

```python
import json
import os
import replicate
from moviepy.editor import VideoFileClip
from pathlib import Path

from config import settings


def extract_audio(video_path: str, output_folder: str = "output") -> str:
    os.makedirs(output_folder, exist_ok=True)
    stem = Path(video_path).stem
    audio_path = os.path.join(output_folder, f"{stem}.mp3")
    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(audio_path)
    return audio_path


def transcribe_audio(file_path: str) -> dict:
    return replicate.run(
        settings.TRANSCRIBE_MODEL,
        input={"audio": open(file_path, "rb")}
    )


def save_transcription(transcription_data: dict, source_path: str, output_folder: str = "output") -> tuple[str, str]:
    os.makedirs(output_folder, exist_ok=True)
    stem = Path(source_path).stem

    text_path = os.path.join(output_folder, f"{stem}.txt")
    with open(text_path, "w", encoding="utf-8") as f:
        f.write(transcription_data["text"])

    json_path = os.path.join(output_folder, f"{stem}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(transcription_data, f, indent=2, ensure_ascii=False)

    return text_path, json_path
```

**Step 3: Write `tests/test_transcribe.py`**

```python
import json
import os
import pytest
from unittest.mock import patch, MagicMock


def test_extract_audio_creates_output_dir(tmp_path):
    video_path = "videos/date.mp4"
    output_folder = str(tmp_path / "output")

    with patch("pipeline.transcribe.VideoFileClip") as MockClip:
        mock_clip = MagicMock()
        MockClip.return_value = mock_clip

        from pipeline.transcribe import extract_audio
        result = extract_audio(video_path, output_folder)

        assert os.path.isdir(output_folder)
        assert result == os.path.join(output_folder, "date.mp3")
        mock_clip.audio.write_audiofile.assert_called_once()


def test_save_transcription_writes_both_files(tmp_path):
    from pipeline.transcribe import save_transcription

    data = {"text": "Hello world", "chunks": []}
    text_path, json_path = save_transcription(data, "videos/interview.mp4", str(tmp_path))

    assert os.path.exists(text_path)
    assert open(text_path).read() == "Hello world"

    assert os.path.exists(json_path)
    saved = json.loads(open(json_path).read())
    assert saved["text"] == "Hello world"
```

**Step 4: Run tests**
```bash
pytest tests/test_transcribe.py -v
```
Expected: 2 passed.

**Step 5: Replace `main.py` with a clean orchestrator**

```python
"""NotebookLM-style pipeline: YouTube URL or local video → transcript → summary → audio overview."""

import sys
from pipeline.transcribe import extract_audio, transcribe_audio, save_transcription
from pipeline.ingest import download_from_youtube
from pipeline.process import summarize, extract_key_points
from pipeline.tts import synthesize


def is_url(source: str) -> bool:
    return source.startswith("http://") or source.startswith("https://")


def main(source: str) -> dict:
    print(f"Starting pipeline for: {source}")
    print("-" * 50)

    # Layer 1 — Ingestion
    if is_url(source):
        print("1. Downloading from YouTube...")
        video_path = download_from_youtube(source)
    else:
        video_path = source
        print(f"1. Using local file: {video_path}")

    print("2. Extracting audio...")
    audio_path = extract_audio(video_path)

    print("3. Transcribing audio (this may take a moment)...")
    result = transcribe_audio(audio_path)
    text_path, json_path = save_transcription(result, video_path)

    # Layer 2 — LLM Processing
    print("4. Summarizing with LLM...")
    transcript = result["text"]
    summary = summarize(transcript)
    key_points = extract_key_points(transcript)

    print("\nSummary:")
    print(summary)
    print("\nKey Points:")
    for i, point in enumerate(key_points, 1):
        print(f"  {i}. {point}")

    # Layer 3 — Text-to-Speech
    print("\n5. Generating audio overview...")
    from pathlib import Path
    stem = Path(video_path).stem
    speech_path = synthesize(summary, filename=f"{stem}-overview")
    print(f"Audio overview saved to: {speech_path}")

    return {
        "transcript": text_path,
        "summary": summary,
        "key_points": key_points,
        "audio_overview": speech_path,
    }


if __name__ == "__main__":
    source = sys.argv[1] if len(sys.argv) > 1 else "videos/date.mp4"
    main(source)
```

**Step 6: Commit**
```bash
git add pipeline/ tests/ main.py
git commit -m "refactor: extract pipeline package from main.py"
```

---

## Task 2: YouTube Ingestion (`pipeline/ingest.py`)

**Files:**
- Create: `pipeline/ingest.py`
- Create: `tests/test_ingest.py`

**Step 1: Create stub**

```python
# pipeline/ingest.py
import os
import yt_dlp


def download_from_youtube(url: str, output_folder: str = "videos") -> str:
    """Download a YouTube video and return the local file path.

    Args:
        url: Full YouTube video URL
        output_folder: Directory to save the video file

    Returns:
        Absolute path to the downloaded video file
    """
    raise NotImplementedError
```

**Step 2: Write `tests/test_ingest.py`**

```python
import pytest
from unittest.mock import patch, MagicMock


def test_download_creates_output_folder(tmp_path):
    from pipeline.ingest import download_from_youtube

    with patch("pipeline.ingest.yt_dlp.YoutubeDL") as MockYDL:
        mock_ydl = MagicMock()
        MockYDL.return_value.__enter__ = lambda s: mock_ydl
        MockYDL.return_value.__exit__ = MagicMock(return_value=False)
        mock_ydl.extract_info.return_value = {"title": "test-video", "ext": "mp4"}
        mock_ydl.prepare_filename.return_value = str(tmp_path / "test-video.mp4")

        result = download_from_youtube("https://youtube.com/watch?v=abc", str(tmp_path))

        assert result == str(tmp_path / "test-video.mp4")
        mock_ydl.extract_info.assert_called_once_with(
            "https://youtube.com/watch?v=abc", download=True
        )


def test_download_calls_ydl_with_mp4_format(tmp_path):
    from pipeline.ingest import download_from_youtube

    with patch("pipeline.ingest.yt_dlp.YoutubeDL") as MockYDL:
        mock_ydl = MagicMock()
        MockYDL.return_value.__enter__ = lambda s: mock_ydl
        MockYDL.return_value.__exit__ = MagicMock(return_value=False)
        mock_ydl.extract_info.return_value = {"title": "test", "ext": "mp4"}
        mock_ydl.prepare_filename.return_value = str(tmp_path / "test.mp4")

        download_from_youtube("https://youtube.com/watch?v=abc", str(tmp_path))

        call_kwargs = MockYDL.call_args[0][0]
        assert call_kwargs["format"] == "mp4"
```

**Step 3: Run tests — verify they fail**
```bash
pytest tests/test_ingest.py -v
```
Expected: FAIL with `NotImplementedError`.

**Step 4: Implement `download_from_youtube`**

```python
import os
import yt_dlp


def download_from_youtube(url: str, output_folder: str = "videos") -> str:
    os.makedirs(output_folder, exist_ok=True)
    ydl_opts = {
        "format": "mp4",
        "outtmpl": f"{output_folder}/%(title)s.%(ext)s",
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)
```

**Step 5: Run tests — verify they pass**
```bash
pytest tests/test_ingest.py -v
```
Expected: 2 passed.

**Step 6: Commit**
```bash
git add pipeline/ingest.py tests/test_ingest.py
git commit -m "feat: add YouTube ingestion via yt-dlp"
```

---

## Task 3: Update Config for OpenAI

**Files:**
- Modify: `config.py`

**Step 1: Add OpenAI model settings to `Settings` class**

In `config.py`, add three new fields after `OPENAI_API_KEY`:
```python
OPENAI_API_KEY: str = None
OPENAI_CHAT_MODEL: str = "gpt-4o-mini"
OPENAI_TTS_MODEL: str = "tts-1"
OPENAI_TTS_VOICE: str = "alloy"
```

**Step 2: Commit**
```bash
git add config.py
git commit -m "chore: add OpenAI model config fields"
```

---

## Task 4: LLM Processing (`pipeline/process.py`)

**Files:**
- Create: `pipeline/process.py`
- Create: `tests/test_process.py`

**Step 1: Create stub**

```python
# pipeline/process.py
import json
from openai import OpenAI
from config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def summarize(transcript: str) -> str:
    """Summarize a transcript into 2-3 paragraphs.

    Args:
        transcript: Full transcript text

    Returns:
        Summary as a plain string
    """
    raise NotImplementedError


def extract_key_points(transcript: str) -> list[str]:
    """Extract the 5 most important points from a transcript.

    Args:
        transcript: Full transcript text

    Returns:
        List of key point strings
    """
    raise NotImplementedError


def answer_question(transcript: str, question: str) -> str:
    """Answer a question based solely on the transcript content.

    Args:
        transcript: Full transcript text
        question: User's question

    Returns:
        Answer as a plain string
    """
    raise NotImplementedError
```

**Step 2: Write `tests/test_process.py`**

```python
import json
import pytest
from unittest.mock import patch, MagicMock


def _mock_completion(content: str):
    response = MagicMock()
    response.choices = [MagicMock()]
    response.choices[0].message.content = content
    return response


def test_summarize_returns_string():
    from pipeline.process import summarize

    with patch("pipeline.process.client") as mock_client:
        mock_client.chat.completions.create.return_value = _mock_completion("Short summary.")

        result = summarize("Some long transcript text here.")

        assert isinstance(result, str)
        assert result == "Short summary."
        mock_client.chat.completions.create.assert_called_once()


def test_extract_key_points_returns_list():
    from pipeline.process import extract_key_points

    payload = json.dumps({"points": ["Point A", "Point B", "Point C"]})

    with patch("pipeline.process.client") as mock_client:
        mock_client.chat.completions.create.return_value = _mock_completion(payload)

        result = extract_key_points("Some transcript.")

        assert isinstance(result, list)
        assert result == ["Point A", "Point B", "Point C"]


def test_answer_question_returns_string():
    from pipeline.process import answer_question

    with patch("pipeline.process.client") as mock_client:
        mock_client.chat.completions.create.return_value = _mock_completion("The answer is 42.")

        result = answer_question("Transcript text.", "What is the answer?")

        assert isinstance(result, str)
        assert result == "The answer is 42."
```

**Step 3: Run tests — verify they fail**
```bash
pytest tests/test_process.py -v
```
Expected: 3 FAILED with `NotImplementedError`.

**Step 4: Implement `summarize`**

```python
def summarize(transcript: str) -> str:
    response = client.chat.completions.create(
        model=settings.OPENAI_CHAT_MODEL,
        messages=[
            {"role": "system", "content": "You summarize transcripts clearly and concisely."},
            {"role": "user", "content": f"Summarize this transcript in 2-3 paragraphs:\n\n{transcript}"},
        ],
    )
    return response.choices[0].message.content
```

**Step 5: Run `test_summarize_returns_string` — verify it passes**
```bash
pytest tests/test_process.py::test_summarize_returns_string -v
```
Expected: PASSED.

**Step 6: Implement `extract_key_points`**

```python
def extract_key_points(transcript: str) -> list[str]:
    response = client.chat.completions.create(
        model=settings.OPENAI_CHAT_MODEL,
        messages=[
            {"role": "system", "content": 'Respond ONLY with valid JSON: {"points": ["...", "..."]}'},
            {"role": "user", "content": f"Extract the 5 most important points:\n\n{transcript}"},
        ],
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)["points"]
```

**Step 7: Run `test_extract_key_points_returns_list` — verify it passes**
```bash
pytest tests/test_process.py::test_extract_key_points_returns_list -v
```
Expected: PASSED.

**Step 8: Implement `answer_question`**

```python
def answer_question(transcript: str, question: str) -> str:
    response = client.chat.completions.create(
        model=settings.OPENAI_CHAT_MODEL,
        messages=[
            {"role": "system", "content": "Answer questions based only on the provided transcript. If the answer is not in the transcript, say so."},
            {"role": "user", "content": f"Transcript:\n{transcript}\n\nQuestion: {question}"},
        ],
    )
    return response.choices[0].message.content
```

**Step 9: Run all process tests**
```bash
pytest tests/test_process.py -v
```
Expected: 3 passed.

**Step 10: Commit**
```bash
git add pipeline/process.py tests/test_process.py
git commit -m "feat: add LLM processing (summarize, key points, Q&A)"
```

---

## Task 5: Text-to-Speech (`pipeline/tts.py`)

**Files:**
- Create: `pipeline/tts.py`
- Create: `tests/test_tts.py`

**Step 1: Create stub**

```python
# pipeline/tts.py
import os
from openai import OpenAI
from config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def synthesize(text: str, output_folder: str = "output", filename: str = "speech") -> str:
    """Convert text to speech and save as an MP3 file.

    Args:
        text: Text to synthesize
        output_folder: Directory to save the audio file
        filename: Output filename without extension

    Returns:
        Path to the generated MP3 file
    """
    raise NotImplementedError
```

**Step 2: Write `tests/test_tts.py`**

```python
import os
import pytest
from unittest.mock import patch, MagicMock


def test_synthesize_returns_output_path(tmp_path):
    from pipeline.tts import synthesize

    with patch("pipeline.tts.client") as mock_client:
        mock_client.audio.speech.create.return_value = MagicMock(content=b"fake audio")

        result = synthesize("Hello world", str(tmp_path), "test-output")

        assert result == os.path.join(str(tmp_path), "test-output.mp3")


def test_synthesize_writes_audio_file(tmp_path):
    from pipeline.tts import synthesize

    with patch("pipeline.tts.client") as mock_client:
        mock_client.audio.speech.create.return_value = MagicMock(content=b"fake audio bytes")

        synthesize("Hello world", str(tmp_path), "test-output")

        output_file = tmp_path / "test-output.mp3"
        assert output_file.exists()
        assert output_file.read_bytes() == b"fake audio bytes"


def test_synthesize_calls_openai_with_correct_params(tmp_path):
    from pipeline.tts import synthesize

    with patch("pipeline.tts.client") as mock_client:
        mock_client.audio.speech.create.return_value = MagicMock(content=b"audio")

        synthesize("Say something", str(tmp_path), "out")

        mock_client.audio.speech.create.assert_called_once()
        call_kwargs = mock_client.audio.speech.create.call_args[1]
        assert call_kwargs["input"] == "Say something"
```

**Step 3: Run tests — verify they fail**
```bash
pytest tests/test_tts.py -v
```
Expected: 3 FAILED with `NotImplementedError`.

**Step 4: Implement `synthesize`**

```python
def synthesize(text: str, output_folder: str = "output", filename: str = "speech") -> str:
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, f"{filename}.mp3")

    response = client.audio.speech.create(
        model=settings.OPENAI_TTS_MODEL,
        voice=settings.OPENAI_TTS_VOICE,
        input=text,
    )

    with open(output_path, "wb") as f:
        f.write(response.content)

    return output_path
```

**Step 5: Run tests — verify they pass**
```bash
pytest tests/test_tts.py -v
```
Expected: 3 passed.

**Step 6: Run full test suite**
```bash
pytest tests/ -v
```
Expected: all tests pass.

**Step 7: Commit**
```bash
git add pipeline/tts.py tests/test_tts.py
git commit -m "feat: add text-to-speech via OpenAI TTS"
```

---

## Task 6: Smoke Test Full Pipeline

**Step 1: Test with a local file first**
```bash
python main.py videos/date.mp4
```
Expected: runs all 5 steps, prints summary and key points, saves audio overview to `output/date-overview.mp3`.

**Step 2: Test with a YouTube URL (short video)**
```bash
python main.py "https://www.youtube.com/watch?v=jNQXAC9IVRw"
```
Expected: downloads video, runs full pipeline.

**Step 3: Commit**
```bash
git add main.py
git commit -m "feat: wire full notebooklm pipeline in main.py"
```

---

## Task 7: Open PR + Workshop Branches

> This task happens after the PR is reviewed and merged to master.

**Step 1: Open PR**
```bash
gh pr create --title "feat: NotebookLM pipeline (ingestion, LLM, TTS)" \
  --body "Extends transcription tool into a full NotebookLM-like pipeline for workshop use."
```

**Step 2: After merge — create workshop starter branch**
```bash
git checkout master && git pull
git checkout -b workshop/starter
```

In `pipeline/ingest.py`, `pipeline/process.py`, and `pipeline/tts.py`, replace each function body with:
```python
raise NotImplementedError("TODO: implement this")
```
Keep all docstrings and type hints intact.

```bash
git add pipeline/
git commit -m "chore: stub pipeline functions for workshop starter"
git push -u origin workshop/starter
```

**Step 3: Create layer solution branches**
```bash
# Layer 1 solution: ingest working, process + tts stubbed
git checkout master
git checkout -b workshop/layer-1
# fill in only ingest.py from master
git push -u origin workshop/layer-1

# Layer 2 solution: ingest + process working, tts stubbed
git checkout master
git checkout -b workshop/layer-2
# fill in ingest.py + process.py from master
git push -u origin workshop/layer-2

# Layer 3 = master (everything working)
```
