from pathlib import Path
import typer

APP_NAME = "nkit"
APP_DIR = Path(typer.get_app_dir(APP_NAME)).resolve()
APP_DIR.mkdir(exist_ok=True)
