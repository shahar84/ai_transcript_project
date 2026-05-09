import typer
import project as proj

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


if __name__ == "__main__":
    app()
