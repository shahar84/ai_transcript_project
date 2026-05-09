import typer
from pathlib import Path
import project as proj
from downloader import download_video, get_video_title
from main import extract_audio, transcribe_audio, save_transcription
from llm import generate_podcast_script, save_script
from tts import synthesize_podcast
from config import settings

app = typer.Typer()


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """AI transcript project CLI."""


@app.command()
def create(name: str):
    """Create a new transcription project."""
    project_dir = proj.create_project(name)
    typer.echo(f"Project '{name}' created at {project_dir}")
    typer.echo(f"Add YouTube URLs to {project_dir / 'urls.txt'}")


@app.command()
def run(name: str):
    """Run the full pipeline for a project."""
    project_dir = proj.PROJECTS_DIR / name
    if not project_dir.exists():
        typer.echo(f"Project '{name}' not found.", err=True)
        raise typer.Exit(code=1)

    entries = proj.read_urls(name)
    if not entries:
        typer.echo("No URLs found in urls.txt.")
        return

    total = len(entries)
    processed = 0
    skipped = 0
    errored = 0

    for i, (url, video_name) in enumerate(entries, 1):
        if not video_name:
            video_name = proj.slugify(get_video_title(url))

        prefix = f"[{i}/{total}] {video_name}"

        if proj.is_complete(name, video_name):
            typer.echo(f"{prefix} — already done, skipping")
            skipped += 1
            continue

        try:
            typer.echo(f"{prefix} — downloading...")
            video_path = download_video(url, video_name, project_dir / "videos")

            typer.echo(f"{prefix} — extracting audio...")
            audio_path = extract_audio(str(video_path), str(project_dir / "output"))

            typer.echo(f"{prefix} — transcribing...")
            result = transcribe_audio(audio_path)
            save_transcription(result, str(video_path), str(project_dir / "output"))

            processed += 1
        except Exception as e:
            typer.echo(f"{prefix} — ERROR: {e}", err=True)
            errored += 1

    typer.echo(f"\nDone. {processed} processed, {skipped} skipped, {errored} failed.")


@app.command()
def script(name: str, video: str):
    """Generate a podcast script from a transcript using OpenAI."""
    if not settings.OPENAI_API_KEY:
        typer.echo("OPENAI_API_KEY is not set in your .env file.", err=True)
        raise typer.Exit(code=1)

    transcript_path = proj.PROJECTS_DIR / name / "output" / f"{video}.txt"
    if not transcript_path.exists():
        typer.echo(f"Transcript not found: {transcript_path}", err=True)
        typer.echo(f"Run 'transcript run {name}' first.", err=True)
        raise typer.Exit(code=1)

    typer.echo(f"Generating podcast script for '{video}'...")
    transcript_text = transcript_path.read_text(encoding="utf-8")
    script_text = generate_podcast_script(transcript_text)

    output_folder = proj.PROJECTS_DIR / name / "output"
    script_path = save_script(script_text, video, output_folder)
    typer.echo(f"Script saved to: {script_path}")


@app.command()
def podcast(
    name: str,
    video: str,
    voice: Path = typer.Option(..., help="Path to a WAV file with your voice sample"),
    onnx_dir: Path = typer.Option(Path("onnx_models"), help="Path to the BlueTTS ONNX model directory"),
):
    """Generate a podcast episode in your own voice using BlueTTS."""
    script_path = proj.PROJECTS_DIR / name / "output" / f"{video}-podcast-script.txt"
    if not script_path.exists():
        typer.echo(f"Podcast script not found. Run 'transcript script {name} {video}' first.", err=True)
        raise typer.Exit(code=1)

    if not voice.exists():
        typer.echo(f"Voice sample not found: {voice}", err=True)
        raise typer.Exit(code=1)

    typer.echo(f"Synthesizing podcast episode for '{video}'...")
    typer.echo("(This may take several minutes on CPU — please wait...)")

    script_text = script_path.read_text(encoding="utf-8")
    output_path = proj.PROJECTS_DIR / name / "output" / f"{video}-podcast.wav"

    result_path = synthesize_podcast(
        script_text=script_text,
        voice_sample_path=voice,
        output_path=output_path,
        onnx_dir=onnx_dir,
    )
    typer.echo(f"Podcast episode saved to: {result_path}")


if __name__ == "__main__":
    app()
