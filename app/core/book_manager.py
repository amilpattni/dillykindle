import filecmp
import json
import shutil
import uuid
from pathlib import Path

from app.config import BOOKS_DIR, LIBRARY_FILE
from app.core.bookmark_manager import remove_bookmarks_for_book
from app.core.progress_manager import remove_progress


def load_library():
    if not LIBRARY_FILE.exists() or LIBRARY_FILE.read_text().strip() == "":
        save_library({"books": []})

    try:
        with open(LIBRARY_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        save_library({"books": []})
        return {"books": []}


def save_library(library):
    LIBRARY_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(LIBRARY_FILE, "w", encoding="utf-8") as file:
        json.dump(library, file, indent=2)


def get_books():
    return load_library().get("books", [])


def get_book(book_id):
    for book in get_books():
        if book["id"] == book_id:
            return book

    return None


def get_book_by_path(path):
    selected_path = str(Path(path).resolve())

    for book in get_books():
        existing_path = str(Path(book["path"]).resolve())
        if existing_path == selected_path:
            return book

    return None


def is_inside_books_dir(path):
    try:
        Path(path).resolve().relative_to(BOOKS_DIR.resolve())
        return True
    except ValueError:
        return False


def files_match(path_one, path_two):
    path_one = Path(path_one)
    path_two = Path(path_two)

    if not path_one.exists() or not path_two.exists():
        return False

    if path_one.stat().st_size != path_two.stat().st_size:
        return False

    return filecmp.cmp(path_one, path_two, shallow=False)


def get_destination_for_import(source):
    BOOKS_DIR.mkdir(parents=True, exist_ok=True)

    source = Path(source).resolve()
    books_dir = BOOKS_DIR.resolve()

    if is_inside_books_dir(source):
        return source

    destination = books_dir / source.name

    if not destination.exists():
        return destination

    if files_match(source, destination):
        return destination

    counter = 2

    while True:
        candidate = books_dir / f"{source.stem}_{counter}{source.suffix}"

        if not candidate.exists():
            return candidate

        if files_match(source, candidate):
            return candidate

        counter += 1


def add_book(source_path):
    source = Path(source_path).resolve()

    if not source.exists():
        raise FileNotFoundError("Selected file does not exist.")

    if source.suffix.lower() not in {".pdf", ".epub"}:
        raise ValueError("Only PDF and EPUB files are supported right now.")

    destination = get_destination_for_import(source)
    existing_book = get_book_by_path(destination)

    if existing_book is not None:
        return existing_book

    if not destination.exists():
        shutil.copy2(source, destination)

    book_id = uuid.uuid4().hex
    title = destination.stem.replace("_", " ").replace("-", " ").strip()

    book = {
        "id": book_id,
        "title": title,
        "filename": destination.name,
        "path": str(destination),
        "type": "pdf"
    }

    library = load_library()
    library["books"].append(book)
    save_library(library)

    return book


def remove_book(book_id, delete_file=False):
    book = get_book(book_id)

    if book is None:
        return

    book_path = Path(book["path"]).resolve()

    library = load_library()
    library["books"] = [
        current_book for current_book in library.get("books", [])
        if current_book["id"] != book_id
    ]
    save_library(library)

    remove_progress(book_id)
    remove_bookmarks_for_book(book_id)

    if delete_file and book_path.exists() and is_inside_books_dir(book_path):
        book_path.unlink()
