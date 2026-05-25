# DillyKindle

DillyKindle is a Raspberry Pi-based e-reader built to feel like a small, focused Kindle-style device. It runs a custom Python reading app on an e-paper display and supports local PDF reading, bookmarks, physical button navigation, and wireless book uploads through its own Wi-Fi hotspot.

![DillyKindle device photo](assets/device-photo.jpg)

## Overview

DillyKindle is designed as a standalone reading device rather than a normal desktop app. When the Raspberry Pi boots, it launches directly into the reader interface. Books are stored locally, reading progress is saved automatically, and the device can create its own hotspot so new books can be uploaded from another device through a browser.

## Features

- Custom Python e-reader interface
- PDF rendering with PyMuPDF
- E-paper display support
- Physical button navigation
- Bookmark and reading progress storage
- Local book library management
- Wi-Fi hotspot mode for wireless book uploads
- Browser-based upload page for adding books
- Automatic startup using systemd
- Lightweight file-based storage using JSON

## Hardware

The project uses:

- Raspberry Pi Zero 2 W
- E-paper display
- Physical navigation buttons
- Pico/GPIO-based button input system
- MicroSD card for OS, app files, and book storage
- Planned rechargeable battery/power-management setup
- Planned custom enclosure

## Software Stack

The main software components are:

- Python for the main application
- PyMuPDF for rendering PDF pages
- JSON files for storing library data, bookmarks, and progress
- Local HTTP server for browser-based book uploads
- Raspberry Pi hotspot configuration for direct wireless access
- systemd service for launching the app automatically on boot

## How It Works

On startup, the Raspberry Pi launches the DillyKindle application automatically. The home screen lets the user open books, continue reading, manage the library, and access saved bookmarks.

Books can be added wirelessly by connecting another device to the DillyKindle hotspot and opening the local upload page in a browser. Uploaded files are saved directly to the device library and become available in the reader interface.

Inside the reader, physical buttons are used to move between pages, open books, save bookmarks, and return to the home screen.

## Project Goals

The goal of DillyKindle is to build a simple, dedicated e-reader from scratch using accessible hardware and custom software. The project focuses on making a device that is portable, readable, offline-first, and easy to load books onto without depending on a normal computer workflow.

Future improvements include rechargeable battery integration, battery percentage display in software, a lighter operating system setup, improved power/sleep behavior, and a finished physical case.

## Status

The core software is functional. PDF reading, bookmarks, local storage, physical navigation, automatic startup, and hotspot-based book uploads are working or in active integration. The remaining work is mostly hardware refinement, power management, and enclosure design.
