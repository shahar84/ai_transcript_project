import yt_dlp
from pathlib import Path


def get_video_title(url: str) -> str:
    with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
        info = ydl.extract_info(url, download=False)
        return info["title"]


def download_video(url: str, name: str, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    ydl_opts = {
        "format": "mp4/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
        "outtmpl": str(output_dir / f"{name}.%(ext)s"),
        "quiet": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    for path in output_dir.glob(f"{name}.*"):
        return path
    raise FileNotFoundError(f"Download produced no file for: {url}")
