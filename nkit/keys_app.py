import typer
import functools
import typing as t
from pathlib import Path
from . import security
from Crypto.PublicKey import RSA
from .storage.local import SecretDb
from . import constants as c
from . import models

keys_app = typer.Typer()

KEY_PATH = c.APP_DIR/'pub.pem'

def require_init(f):
	@functools.wraps(f)
	def safer(*args, **kwargs):
		if not KEY_PATH.exists():
			typer.echo("No public key present. Initialize using `nkit keys init")
			raise typer.Abort()
		f(*args, **kwargs)
	return safer


@keys_app.command("init")
def initialize(password: str = typer.Option(..., prompt=True, confirmation_prompt=True, hide_input=True)):
	# TODO: support key override
	if KEY_PATH.exists():
		typer.echo("key already initialized. Run `nkit keys reset` to remove all secrets and key")
		raise typer.Abort()

	private_key = security.generate_rsa_key(password.encode('utf-8'))
	public_key_bytes = private_key.publickey().export_key("PEM")
	with open(KEY_PATH, "wb") as f:
		f.write(public_key_bytes)
		typer.echo(f"Stored public key at {KEY_PATH}")


@keys_app.command("reset")
def reset():
	# TODO: support key override
	if KEY_PATH.exists():
		import os
		os.remove(KEY_PATH)
		typer.echo("Deleted key")
	with SecretDb() as db:
		db.delete_all()
		typer.echo("removed all secrets")


@keys_app.command("add")
@require_init
def add_key(key: str, title: str = typer.Option(..., prompt=True)):
	with open(KEY_PATH, "rb") as f:
		public_key = RSA.import_key(f.read())
	with SecretDb() as db:
		db.insert(models.SecretCreate(title=title, data=security.encrypt_large(public_key, key.encode('utf-8'))))
		typer.echo(f"Saved with title: {title}")


def check_password_and_retry(password: str) -> t.Optional[RSA.RsaKey]:
	def get_public_key(password) -> bytes:
		private_key = security.generate_rsa_key(password.encode('utf-8'))
		return private_key.publickey().export_key("PEM")

	public_key_bytes = get_public_key(password)

	with open(KEY_PATH, "rb") as f:
		stored_public_key = f.read()

	tries = 0
	while not stored_public_key == public_key_bytes and tries < 3:
		typer.echo(f"Password is incorrect. Doesn't match with public key. Retry {tries+1}")
		password = typer.prompt("Password: ", hide_input=True)
		public_key_bytes = get_public_key(password)
		tries += 1

	if not stored_public_key == public_key_bytes:
		return None
	else:
		return security.generate_rsa_key(password.encode('utf-8'))


@keys_app.command("get")
@require_init
def get_key(title: str, password: str = typer.Option(..., prompt=True, hide_input=True)):
	private_key = check_password_and_retry(password)
	if private_key is None:
		typer.echo("Password Not Correct!!")
		raise typer.Abort()


	with SecretDb() as db:
		secret = db.get_secret(title)
		if secret is None:
			typer.echo(f"No key with title: {title}")
			raise typer.Abort()
		typer.echo(security.decrypt_large(private_key, secret.data))


@keys_app.command("remove")
@require_init
def get_key(title: str):
	with SecretDb() as db:
		secret = db.get_secret(title)
		if secret is None:
			typer.echo(f"No key with title: {title}")
			raise typer.Abort()
		db.delete_secret(secret)
		typer.echo("deleted")


@keys_app.command("decrypt")
def decrypt_external(password: str = typer.Option(..., prompt=True, hide_input=True), inpath: t.Optional[Path] = typer.Option(None), outpath: t.Optional[Path] = typer.Option(None)):
	if inpath is None:
		import sys
		encrypted = sys.stdin.read().encode('utf-8')
	else:
		if not (inpath.exists() and inpath.is_file()):
			typer.echo("content path not valid")
			raise typer.Abort()
		encrypted = inpath.read_bytes()
	private_key = security.generate_rsa_key(password.encode("utf-8"))
	try:
		decrypted = security.decrypt_large(private_key, encrypted)
	except ValueError as e:
		typer.echo(f"Can't decrypt: {e}")
		raise typer.Abort()
	if outpath is None:
		typer.echo(decrypted)
	else:
		if outpath.is_dir():
			typer.echo(f"{outpath} is dir")
			raise typer.Abort()
		if outpath.exists():
			typer.echo(f"{outpath} already exists")
			override = typer.prompt(f"override [y/n]: ") == "y"
			if not override:
				raise typer.Abort()
		with open(outpath, "wb") as f:
			f.write(decrypted)
			typer.echo(f"writted to file {outpath}")


@keys_app.command("encrypt")
def encrypt_external(password: str = typer.Option(..., prompt=True, hide_input=True), inpath: t.Optional[Path] = typer.Option(None), outpath: t.Optional[Path] = typer.Option(None)):
	if inpath is None:
		import sys
		data = sys.stdin.read().encode('utf-8')
	else:
		if not (inpath.exists() and inpath.is_file()):
			typer.echo("content path not valid")
			raise typer.Abort()
		data = inpath.read_bytes()
	private_key = security.generate_rsa_key(password.encode("utf-8"))
	encrypted = security.encrypt_large(private_key.publickey(), data)

	if outpath is None:
		typer.echo(encrypted)
	else:
		if outpath.is_dir():
			typer.echo(f"{outpath} is dir")
			raise typer.Abort()
		if outpath.exists():
			typer.echo(f"{outpath} already exists")
			override = typer.prompt(f"override [y/n]: ") == "y"
			if not override:
				raise typer.Abort()
		with open(outpath, "wb") as f:
			f.write(encrypted)
			typer.echo(f"writted to file {outpath}")


@keys_app.command("list")
def list_keys(regex: t.Optional[str] = typer.Option(default=None)):
	with SecretDb() as db:
		titles = db.titles(regex)
	for i, title in enumerate(titles, start=1):
		typer.echo(f"{i:<3} {title}")
