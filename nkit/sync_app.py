import typer

sync_app = typer.Typer()
@sync_app.command("status")
def sync_status():
	pass

@sync_app.command("reset")
def sync_reset():
	pass

@sync_app.command("pull")
def sync_pull():
	pass

@sync_app.command("push")
def sync_push():
	pass

