import typer
import typing as t
from . import security
from Crypto.PublicKey import RSA
from .storage.local import SecretDb
from . import constants as c
from . import models

keys_app = typer.Typer()

KEY_DIR = c.APP_DIR/'pub.pem'

@keys_app.command("init")
def initialize(password: str = typer.Option(..., prompt=True, confirmation_prompt=True, hide_input=True)):
	# TODO: support key override
	if KEY_DIR.exists():
		typer.echo("key already initialized")
		raise typer.Abort()

	private_key = security.generate_rsa_key(password.encode('utf-8'))
	public_key_bytes = private_key.publickey().export_key("PEM")
	with open(KEY_DIR, "wb") as f:
		f.write(public_key_bytes)
		typer.echo(f"Stored public key at {KEY_DIR}")

@keys_app.command("add")
def add_key(key: str, title: str = typer.Option(..., prompt=True)):
	if not KEY_DIR.exists():
		typer.echo("No public key present. Initialize using `nkit keys init")
		typer.Abort()

	with SecretDb() as db:
		db.insert(models.SecretCreate(title=title, data=key))
		typer.echo(f"Saved with title: {title}")

def check_password_and_retry(password: str) -> t.Optional[RSA.RsaKey]:
	def get_public_key(password) -> bytes:
		private_key = security.generate_rsa_key(password.encode('utf-8'))
		return private_key.publickey().export_key("PEM")

	public_key_bytes = get_public_key(password)

	with open(KEY_DIR, "rb") as f:
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
def get_key(title: str, password: str = typer.Option(..., prompt=True, hide_input=True)):
	correct_password = check_password_and_retry(password)
	if correct_password is None:
		typer.echo("Password Not Correct!!")
		typer.Abort()


	with SecretDb() as db:
		secret = db.get_secret(title)
		print(secret)


@keys_app.command("list")
def list_keys(regex: str = typer.Option(default="*")):
	with SecretDb() as db:
		titles = db.titles(regex)
	for i, title in enumerate(titles):
		typer.echo(f"{i:<3} {title}")
