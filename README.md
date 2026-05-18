# DillyKindle

DillyKindle is a lightweight Raspberry Pi-based e-reader app built for reading PDFs on a small, Kindle-style device.

It is designed to run full-screen, work with physical buttons, and provide a simple reading experience without unnecessary menus or distractions.

## Features

- Full-screen PDF reader
- Clean Kindle-style home screen
- Add, remove, and manage books
- Save bookmarks
- Continue reading from saved progress
- Physical button support
- Designed for Raspberry Pi and e-paper-style displays
- Local-first: books and reading data stay on the device

## Purpose

This project was built as a custom DIY e-reader.

The goal was to create a focused reading device that feels simple, personal, and hardware-driven, instead of using a general-purpose tablet or phone.

## Tech Stack

- Python
- Tkinter / CustomTkinter
- PyMuPDF
- Raspberry Pi OS
- GPIO / physical button input
- Systemd service for auto-start

## Project Structure

```text
dillykindle/
├── app/
│   ├── core/        # Book, PDF, bookmark, and progress logic
│   └── ui/          # App screens and interface
├── data/            # Library, bookmarks, and progress files
├── scripts/         # Startup scripts
├── assets/          # Fonts/images
└── main.py
