from pathlib import Path
from threading import Thread

from flask import Flask, request, redirect, render_template_string

from app.core.book_manager import add_book, get_books
from app.core.wifi_manager import connect_temporary_wifi_after_delay

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
    h2 { font-size: 20px; }
    .box { border: 1px solid #ddd; border-radius: 12px; padding: 20px; margin-top: 18px; }
    input, button { font-size: 16px; padding: 10px; margin-top: 8px; width: 100%; box-sizing: border-box; }
    button { cursor: pointer; }
    li { margin: 6px 0; }
    details { margin-top: 22px; }
    summary { cursor: pointer; font-size: 13px; color: #555; }
    .note { font-size: 13px; color: #555; }
  </style>
</head>
<body>
  <h1>DillyKindle Book Upload</h1>

  <div class="box">
    <h2>Upload Book</h2>
    <form method="post" action="/upload" enctype="multipart/form-data">
      <input type="file" name="book" accept="application/pdf,.pdf,application/epub+zip,.epub" required>
      <button type="submit">Upload Book</button>
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

  <details>
    <summary>Button for Amil to fix any issues</summary>
    <div class="box">
      <h2>Connect device to Wi-Fi</h2>
      <p class="note">
        This turns off the dillykindle hotspot and connects the Pi to the entered Wi-Fi.
        The page will disconnect after you click Connect.
      </p>
      <form method="post" action="/connect-wifi">
        <input type="text" name="ssid" placeholder="Wi-Fi SSID" required>
        <input type="password" name="password" placeholder="Wi-Fi password" required>
        <button type="submit">Connect</button>
      </form>
    </div>
  </details>
</body>
</html>
"""

CONNECTING_PAGE = """
<!doctype html>
<html>
<head>
  <title>DillyKindle Connecting</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
  <h1>DillyKindle is connecting</h1>
  <p>The hotspot will turn off now.</p>
  <p>Reconnect your computer to the Wi-Fi network you entered.</p>
  <p>Then SSH into the Pi using its new Wi-Fi IP.</p>
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

    if not filename.lower().endswith((".pdf", ".epub")):
        return "Only PDF and EPUB files are allowed", 400

    destination = UPLOAD_DIR / filename
    file.save(destination)
    add_book(destination)

    return redirect("/")


@app.route("/connect-wifi", methods=["POST"])
def connect_wifi():
    ssid = request.form.get("ssid", "").strip()
    password = request.form.get("password", "").strip()

    if not ssid or not password:
        return "SSID and password are required", 400

    worker = Thread(
        target=connect_temporary_wifi_after_delay,
        args=(ssid, password),
        daemon=True,
    )
    worker.start()

    return CONNECTING_PAGE


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
