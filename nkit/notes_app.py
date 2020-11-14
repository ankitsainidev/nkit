import typer
import arrow
from .models import NoteCreate
from .exceptions import CrudException
from . import models
from .storage.local import NoteDb
from .utils import catch_error

note_app = typer.Typer()


@note_app.command("show")
@catch_error
def show_notes(limit: int = 5, id: bool = typer.Option(False, "--id/--no-id")):
	with NoteDb() as db:
		notes = db.get_recent(limit = limit)
	notes = sorted(notes, key=lambda x: x.created_at)
	
	if len(notes) == 0:
		typer.secho("Can't find any notes on local storage")

	for i, note in enumerate(notes):
		created = typer.style(note.created_at.format('YYYY-MM-DD HH:mm'), fg=typer.colors.BLUE if i%2==0 else typer.colors.BRIGHT_BLUE)
		task = typer.style(f"{note.ty.name:<12}", fg=typer.colors.BLUE if i%2==0 else typer.colors.BRIGHT_BLUE)
		msg =  created + f" {note.created_at.humanize():<10}  " + task + f" - {note.msg}"
		if id:
			msg = f"{note.id:<5}- "  + msg

		typer.echo(msg)

@note_app.command("remove")
@catch_error
def remove_note(id: int):
	try:
		with NoteDb() as db:
			db.delete_by_id(id=id)
	except CrudException as e:
		typer.secho(str(e), fg=typer.colors.RED, bg=typer.colors.WHITE)

@note_app.command("create")
@catch_error
def create_note(msg: str, type: models.NoteType = typer.Option("think")):
	note = NoteCreate(
			ty=type,
			msg=msg,
			created_at=arrow.utcnow(),
			draft=True,
			resources=[],
			deadline=None,
			refer_id=None)

	with NoteDb() as db:
		db.insert(note)

	typer.secho(f"Successfull {str(note.created_at)}", fg=typer.colors.GREEN)
	typer.secho(msg, fg=typer.colors.BLUE)
