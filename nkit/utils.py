import functools
import asyncio as aio
import typer
import traceback

def blocking_run(f):
	@functools.wraps(f)
	def block_fn(*args, **kwargs):
		aio.run(f(*args, **kwargs))
	return block_fn

def catch_error(f):
	@functools.wraps(f)
	def smooth(*args, **kwargs):
		try:
			f(*args, **kwargs)
		except Exception as e:
			typer.secho(f"Failure: {e}", fg=typer.colors.RED, err=True)
			show_tb = typer.prompt(f"See full traceback? ([y, yes]/[n, any])", default="n").lower() in ["y", "yes"]
			if show_tb:
				traceback.print_exc()
			else:
				raise typer.Abort()
	return smooth


