# Step 2: Downloading Videos from YouTube

## What We're Building

Right now the tool only works with video files you already have on your computer. In this step we add the ability to download any YouTube video automatically.

The updated pipeline:

```
YouTube URL  -->  download video  -->  extract audio  -->  AI transcription  -->  text
```

---

## The Problem With Manual Downloads

Downloading videos by hand is tedious and does not scale. If you want to transcribe 20 YouTube videos, you do not want to download each one manually. We need to automate this.

---

## Meet yt-dlp

[yt-dlp](https://github.com/yt-dlp/yt-dlp) is a popular open-source command-line tool and Python library for downloading videos from YouTube and hundreds of other sites.

It is already in your dependencies — you can see it in `pyproject.toml`. No extra install needed.

---

## The Code: `downloader.py`

Open `downloader.py`. There are two functions:

### `download_video(url, name, output_dir)`

Downloads a YouTube video to a folder on disk.

```python
def download_video(url: str, name: str, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    ydl_opts = {
        "format": "mp4/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
        "outtmpl": str(output_dir / f"{name}.%(ext)s"),
        "quiet": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    ...
```

Key things to notice:
- `format` tells yt-dlp which video quality to prefer
- `outtmpl` is the output filename template — `%(ext)s` is replaced with the actual extension
- `quiet=True` silences verbose yt-dlp output so our own print statements stay readable

### `get_video_title(url)`

Fetches the video's title from YouTube without downloading the file. We use this later to auto-name videos when no name is given.

```python
def get_video_title(url: str) -> str:
    with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
        info = ydl.extract_info(url, download=False)
        return info["title"]
```

`download=False` is the key — this is a metadata-only request, which is much faster than a full download.

---

## Try It Yourself

Open a Python shell and test the downloader directly:

```bash
uv run python
```

```python
from pathlib import Path
from downloader import download_video, get_video_title

url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # any short video

# Get the title first
title = get_video_title(url)
print(title)

# Download it
video_path = download_video(url, "test-video", Path("videos"))
print(video_path)
```

---

## How the Pieces Connect

After downloading, we pass the video path straight into `extract_audio()` from `main.py` — that function does not care whether the video came from YouTube or your hard drive. This is good design: each function has one job and does not need to know where its input came from.

```
download_video()  -->  extract_audio()  -->  transcribe_audio()  -->  save_transcription()
```

---

## Checkpoint

- [ ] I understand the difference between `download_video` and `get_video_title`
- [ ] I understand what `download=False` does in yt-dlp
- [ ] I can download a video and find it in the `videos/` folder

---

Next: [Step 3 - Organizing with Projects](./step-03-projects.md)
