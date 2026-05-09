import typer
import project as proj
from downloader import download_video, get_video_title
from main import extract_audio, transcribe_audio, save_transcription

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


if __name__ == "__main__":
    app()
