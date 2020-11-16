import typer
import typing as t
import hashlib
from . import security
from . import constants as c

keys_app = typer.Typer()

KEYS_DIR = c.APP_DIR/'keys'
KEYS_DIR.mkdir(exist_ok=True)

@keys_app.command("init")
def add_key(password: str = typer.Option(..., prompt=True, confirmation_prompt=True, hide_input=True)):
	private_key = security.generate_rsa_key(password.encode('utf-8'))
	public_key_bytes = private_key.publickey().export_key("PEM")
	public_key_dir = KEYS_DIR/"pub.pem"
	with open(public_key_dir, "wb") as f:
		f.write(public_key_bytes)
		typer.echo(f"Stored public key at {public_key_dir}")

@keys_app.command("add")
def add_key(title: str, key: str):
	pass

