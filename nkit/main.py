import typer

from .utils import blocking_run

from .notes_app import note_app, create_note
from .models import NoteType
from .sync_app import sync_app, sync_status

app = typer.Typer()

app.add_typer(note_app, name="notes")
app.add_typer(sync_app, name="sync")


@app.command()
@blocking_run
async def async_hey():
	typer.echo("Hey, it's Async")


@app.command()
def hey():
	typer.echo("Hey, WooHoo We're in same world")


@app.command("note")
def note(note: str, type: NoteType = typer.Option("think")):
	return create_note(note, type)


@app.command("sync")
def sync():
	return sync_status()


