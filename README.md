# dillykindle

dillykindle is a small Kindle-style PDF reader app built in Python.

It is designed to run first on a laptop for development, then on a Raspberry Pi as a fullscreen reading device.

## Current features

- Portrait Kindle-like layout
- Clean white/paper UI
- Monospaced pixel/robotic-style font
- Import PDF books
- Delete imported books with confirmation
- Read PDFs page-by-page
- Save reading progress
- Add bookmarks
- View bookmarks
- Open from bookmarks
- Remove bookmarks
- F11 fullscreen toggle

## Project structure

dillykindle/
  app/
    main.py
    config.py
    core/
    ui/
  books/
  data/
  cache/
  logs/
  scripts/
    dillykindle.sh
  requirements.txt
  README.md
  .gitignore

## Important folders

app/ contains the dillykindle source code.

books/ stores imported PDFs.

data/ stores the library, reading progress, and bookmarks.

cache/ is reserved for future rendered-page caching.

logs/ is reserved for future logs.

scripts/dillykindle.sh starts the app.

## Development setup

From the project folder:

    python3 -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt

If Tkinter is missing:

    sudo apt install -y python3-tk

## Run the app

    ./scripts/dillykindle.sh

Or manually:

    source .venv/bin/activate
    python -m app.main

## GitHub workflow

After editing code:

    git status
    git add .
    git commit -m "Describe the change"
    git push

## Raspberry Pi setup

On the Raspberry Pi:

    git clone https://github.com/amilpattni/dillykindle.git
    cd dillykindle
    python3 -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    sudo apt install -y python3-tk
    ./scripts/dillykindle.sh

## Book workflow on Raspberry Pi

To add books:

1. Put PDFs on a USB drive.
2. Plug the USB into the Raspberry Pi.
3. Open dillykindle.
4. Go to edit books.
5. Choose import book.
6. Select the PDF from the USB.
7. dillykindle copies it into its internal books/ folder.

To remove books:

1. Go to edit books.
2. Select a book.
3. Choose delete selected book.
4. Confirm deletion.

dillykindle deletes only the internal imported copy.

## Notes

Do not commit .venv, books, data, cache, or logs.

Those are ignored by Git because each device should have its own local environment, books, progress, bookmarks, cache, and logs.
