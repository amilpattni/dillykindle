from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
BOOKS_DIR = ROOT_DIR / "books"
DATA_DIR = ROOT_DIR / "data"
CACHE_DIR = ROOT_DIR / "cache"
LOGS_DIR = ROOT_DIR / "logs"

LIBRARY_FILE = DATA_DIR / "library.json"
PROGRESS_FILE = DATA_DIR / "progress.json"
BOOKMARKS_FILE = DATA_DIR / "bookmarks.json"

APP_NAME = "DillyPie"

WINDOW_WIDTH = 520
WINDOW_HEIGHT = 780

MIN_WINDOW_WIDTH = 430
MIN_WINDOW_HEIGHT = 650
