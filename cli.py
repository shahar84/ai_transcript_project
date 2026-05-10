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
            video_name = get_video_title(url)
        video_name = proj.slugify(video_name)

        prefix = f"[{i}/{total}] {video_name}"

        if proj.is_transcribed(name, video_name):
            typer.echo(f"{prefix} — already done, skipping")
            skipped += 1
            continue

        try:
            typer.echo(f"{prefix} — downloading...")
            video_path = download_video(url, video_name, project_dir / "videos")

            typer.echo(f"{prefix} — extracting audio...")
            audio_path = extract_audio(str(video_path), str(project_dir / "audio"))

            typer.echo(f"{prefix} — transcribing...")
            result = transcribe_audio(audio_path)
            save_transcription(result, str(video_path), str(project_dir / "transcripts"))

            processed += 1
        except Exception as e:
            typer.echo(f"{prefix} — ERROR: {e}", err=True)
            errored += 1

    typer.echo(f"\nDone. {processed} processed, {skipped} skipped, {errored} failed.")


@app.command()
def script(name: str):
    """Generate a podcast script by combining all transcripts in the project."""
    if not settings.OPENAI_API_KEY:
        typer.echo("OPENAI_API_KEY is not set in your .env file.", err=True)
        raise typer.Exit(code=1)

    transcripts_dir = proj.PROJECTS_DIR / name / "transcripts"
    if not transcripts_dir.exists():
        typer.echo(f"Transcripts folder not found. Run 'transcript run {name}' first.", err=True)
        raise typer.Exit(code=1)

    txt_files = sorted(transcripts_dir.glob("*.txt"))
    if not txt_files:
        typer.echo(f"No transcripts found in {transcripts_dir}. Run 'transcript run {name}' first.", err=True)
        raise typer.Exit(code=1)

    combined = "\n\n".join(f.read_text(encoding="utf-8") for f in txt_files)
    typer.echo(f"Generating podcast script from {len(txt_files)} transcript(s)...")
    script_text = generate_podcast_script(combined)

    script_path = save_script(script_text, proj.PROJECTS_DIR / name / "podcast")
    typer.echo(f"Script saved to: {script_path}")


@app.command()
def podcast(
    name: str,
    voice_name: str = typer.Option(None, help="Voice name to use (default from config)"),
):
    """Generate a podcast episode using Gemini TTS."""
    script_path = proj.PROJECTS_DIR / name / "podcast" / "script.txt"
    if not script_path.exists():
        typer.echo(f"Podcast script not found. Run 'transcript script {name}' first.", err=True)
        raise typer.Exit(code=1)

    typer.echo("Synthesizing podcast episode...")

    script_text = script_path.read_text(encoding="utf-8")
    output_path = proj.PROJECTS_DIR / name / "podcast" / "episode.wav"

    result_path = synthesize_podcast(
        script_text=script_text,
        output_path=output_path,
        voice_name=voice_name,
    )
    typer.echo(f"Podcast episode saved to: {result_path}")


if __name__ == "__main__":
    app()
