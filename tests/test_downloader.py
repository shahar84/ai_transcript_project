from pathlib import Path
from unittest.mock import patch, MagicMock
from downloader import get_video_title, download_video


def make_mock_ydl(title="Test Video Title"):
    mock_ydl = MagicMock()
    mock_ydl.__enter__ = lambda s: mock_ydl
    mock_ydl.__exit__ = MagicMock(return_value=False)
    mock_ydl.extract_info.return_value = {"title": title}
    return mock_ydl


def test_get_video_title(tmp_path):
    mock_ydl = make_mock_ydl(title="My Interview")
    with patch("downloader.yt_dlp.YoutubeDL", return_value=mock_ydl):
        title = get_video_title("https://youtube.com/watch?v=abc")
    assert title == "My Interview"


def test_download_video_creates_file(tmp_path):
    output_dir = tmp_path / "videos"

    def fake_download(urls):
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "my-video.mp4").touch()

    mock_ydl = MagicMock()
    mock_ydl.__enter__ = lambda s: mock_ydl
    mock_ydl.__exit__ = MagicMock(return_value=False)
    mock_ydl.download.side_effect = fake_download

    with patch("downloader.yt_dlp.YoutubeDL", return_value=mock_ydl):
        path = download_video("https://youtube.com/watch?v=abc", "my-video", output_dir)

    assert path == output_dir / "my-video.mp4"
