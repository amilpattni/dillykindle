import json
import uuid

from app.config import BOOKMARKS_FILE


def load_bookmarks():
    if not BOOKMARKS_FILE.exists() or BOOKMARKS_FILE.read_text().strip() == "":
        save_bookmarks({"bookmarks": []})

    try:
        with open(BOOKMARKS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        save_bookmarks({"bookmarks": []})
        return {"bookmarks": []}


def save_bookmarks(bookmark_data):
    BOOKMARKS_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(BOOKMARKS_FILE, "w", encoding="utf-8") as file:
        json.dump(bookmark_data, file, indent=2)


def get_bookmarks():
    return load_bookmarks().get("bookmarks", [])


def add_bookmark(book_id, book_title, page):
    bookmark_data = load_bookmarks()

    for bookmark in bookmark_data.get("bookmarks", []):
        if bookmark["book_id"] == book_id and bookmark["page"] == page:
            return bookmark

    bookmark = {
        "id": uuid.uuid4().hex,
        "book_id": book_id,
        "book_title": book_title,
        "page": page,
        "label": f"{book_title} - Page {page + 1}"
    }

    bookmark_data["bookmarks"].append(bookmark)
    save_bookmarks(bookmark_data)

    return bookmark


def remove_bookmark(bookmark_id):
    bookmark_data = load_bookmarks()
    bookmark_data["bookmarks"] = [
        bookmark for bookmark in bookmark_data.get("bookmarks", [])
        if bookmark["id"] != bookmark_id
    ]
    save_bookmarks(bookmark_data)


def remove_bookmarks_for_book(book_id):
    bookmark_data = load_bookmarks()
    bookmark_data["bookmarks"] = [
        bookmark for bookmark in bookmark_data.get("bookmarks", [])
        if bookmark["book_id"] != book_id
    ]
    save_bookmarks(bookmark_data)
