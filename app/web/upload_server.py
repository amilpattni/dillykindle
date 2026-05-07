from pathlib import Path
from flask import Flask, request, redirect, render_template_string

from app.core.book_manager import add_book, get_books

UPLOAD_DIR = Path.home() / "dillykindle_uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(__name__)

PAGE = """
<!doctype html>
<html>
<head>
  <title>DillyKindle Upload</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body { font-family: Arial, sans-serif; max-width: 720px; margin: 40px auto; padding: 0 18px; }
    h1 { font-size: 28px; }
    .box { border: 1px solid #ddd; border-radius: 12px; padding: 20px; margin-top: 18px; }
    input, button { font-size: 16px; padding: 10px; }
    button { cursor: pointer; }
    li { margin: 6px 0; }
  </style>
</head>
<body>
  <h1>DillyKindle Book Upload</h1>

  <div class="box">
    <form method="post" action="/upload" enctype="multipart/form-data">
      <input type="file" name="book" accept="application/pdf,.pdf" required>
      <button type="submit">Upload PDF</button>
    </form>
  </div>

  <div class="box">
    <h2>Books on device</h2>
    {% if books %}
      <ul>
        {% for book in books %}
          <li>{{ book["title"] }}</li>
        {% endfor %}
      </ul>
    {% else %}
      <p>No books found.</p>
    {% endif %}
  </div>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    return render_template_string(PAGE, books=get_books())

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("book")

    if file is None or file.filename.strip() == "":
        return "No file uploaded", 400

    filename = Path(file.filename).name

    if not filename.lower().endswith(".pdf"):
        return "Only PDF files are allowed", 400

    destination = UPLOAD_DIR / filename
    file.save(destination)

    add_book(destination)

    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
