import json

from app.config import PROGRESS_FILE


def load_progress():
    if not PROGRESS_FILE.exists() or PROGRESS_FILE.read_text().strip() == "":
        save_progress({"progress": {}})

    try:
        with open(PROGRESS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        save_progress({"progress": {}})
        return {"progress": {}}


def save_progress(progress_data):
    PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(PROGRESS_FILE, "w", encoding="utf-8") as file:
        json.dump(progress_data, file, indent=2)


def get_page(book_id):
    progress_data = load_progress()
    return progress_data.get("progress", {}).get(book_id, {}).get("page", 0)


def set_page(book_id, page):
    progress_data = load_progress()

    if "progress" not in progress_data:
        progress_data["progress"] = {}

    progress_data["progress"][book_id] = {
        "page": page
    }

    save_progress(progress_data)


def remove_progress(book_id):
    progress_data = load_progress()

    if "progress" in progress_data and book_id in progress_data["progress"]:
        del progress_data["progress"][book_id]

    save_progress(progress_data)
