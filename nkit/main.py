import typer

app = typer.Typer()

@app.command()
def hey():
	typer.echo("Hey, WooHoo We're in same world")
