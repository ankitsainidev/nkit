from pathlib import Path
import typer
import os
import tempfile

APP_NAME = "nkit"

DEFAULT_DIR = Path(typer.get_app_dir(APP_NAME)).resolve()

DEBUG = os.environ.get("DEBUG", "0") != "0"
TESTING = os.environ.get("TESTING", "0") != "0"

if TESTING:
	APP_DIR = Path(tempfile.mkdtemp(suffix=APP_NAME))
else:
	APP_DIR = DEFAULT_DIR

if DEBUG:
	APP_DIR = DEFAULT_DIR/".debug"

APP_DIR.mkdir(exist_ok=True, parents=True)
