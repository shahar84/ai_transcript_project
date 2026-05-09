import yt_dlp
from pathlib import Path

_VIDEO_FORMAT = "mp4/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]"


def download_video(url: str, name: str, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    ydl_opts = {
        "format": _VIDEO_FORMAT,
        "outtmpl": str(output_dir / f"{name}.%(ext)s"),
        "quiet": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    downloaded = next(output_dir.glob(f"{name}.*"), None)
    if downloaded is None:
        raise FileNotFoundError(f"Download produced no file for: {url}")
    return downloaded


def get_video_title(url: str) -> str:
    with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
        info = ydl.extract_info(url, download=False)
        return info["title"]
