import typer
import arrow
from .tools import notes as helper
from .utils import catch_error

note_app = typer.Typer()


@note_app.command("show")
@catch_error
def show_notes(limit: int = 5, id: bool = typer.Option(False, "--id/--no-id")):
	notes = helper.get_recent(limit = limit)
	notes = sorted(notes, key=lambda x: x.created_at)
	
	if len(notes) == 0:
		typer.secho("Can't find any notes on local storage")

	for note in notes:
		timestamp = typer.style(str(note.created_at), fg=typer.colors.BLUE)
		msg =  timestamp + "    " + note.msg

		if id:
			msg = f"{note.id} )  "  + msg

		typer.echo(msg)

@note_app.command("remove")
@catch_error
def remove_note(id: int):
	if not helper.delete(id=id):
		typer.secho("No such id in database", fg=typer.colors.RED, bg=typer.colors.WHITE)

@note_app.command("create")
@catch_error
def create_note(msg: str, type: helper.NoteType = typer.Option("think")):
	note = helper.Note(id=None,
			ty=type,
			msg=msg,
			created_at=arrow.utcnow(),
			draft=True,
			resources=[],
			deadline=None,
			refer_id=None)
	note.save_note()
	typer.secho(f"Successfull {str(note.created_at)}", fg=typer.colors.GREEN)
	typer.secho(msg, fg=typer.colors.BLUE)
