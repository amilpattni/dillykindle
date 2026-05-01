import json

from app.config import (
    BOOKS_DIR,
    DATA_DIR,
    CACHE_DIR,
    LOGS_DIR,
    LIBRARY_FILE,
    PROGRESS_FILE,
    BOOKMARKS_FILE,
)


def write_json_if_missing(path, default_data):
    if not path.exists() or path.read_text().strip() == "":
        with open(path, "w", encoding="utf-8") as file:
            json.dump(default_data, file, indent=2)
        return

    try:
        with open(path, "r", encoding="utf-8") as file:
            json.load(file)
    except json.JSONDecodeError:
        with open(path, "w", encoding="utf-8") as file:
            json.dump(default_data, file, indent=2)


def initialize_app_files():
    BOOKS_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    (CACHE_DIR / "pages").mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    write_json_if_missing(
        LIBRARY_FILE,
        {
            "books": []
        }
    )

    write_json_if_missing(
        PROGRESS_FILE,
        {
            "progress": {}
        }
    )

    write_json_if_missing(
        BOOKMARKS_FILE,
        {
            "bookmarks": []
        }
    )
