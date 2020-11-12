import dataset
from ..constants import APP_DIR
DB_PATH = f"sqlite:///{APP_DIR/'notes.db'}"
db = dataset.connect(DB_PATH)
