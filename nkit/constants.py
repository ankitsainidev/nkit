from pathlib import Path
import typer
import os

APP_NAME = "nkit"

DEFAULT_DIR = Path(typer.get_app_dir(APP_NAME)).resolve()
APP_DIR = Path(os.environ.get("APP_DIR", DEFAULT_DIR))
APP_DIR.mkdir(exist_ok=True, parents=True)
