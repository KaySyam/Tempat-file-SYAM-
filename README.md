WELCOME to my repository. Learning with easy and fun for beginner.

This repository contains a simple Pacman-style game project built with Python and Pygame. It is intended as a beginner-friendly learning project for understanding game logic, input handling, and basic testing.

## Installation

We recommend using [uv](https://github.com/astral-sh/uv) for managing dependencies.

To install `uv` on macOS and Linux, run:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

For Windows, run:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Or you can install it using pip:

```bash
pip install uv
```

## Running the App

To run the application using `uv`, simply execute the following command:

```bash
uv run simplepacman.py
```

## Running Tests

Proyek ini mencakup dua jenis pengujian (Whitebox dan Blackbox).

Untuk menjalankan semua tes (Whitebox & Blackbox) menggunakan `uv`, jalankan perintah berikut:

```bash
uv run --with pygame python -m unittest discover test/
```

Untuk menjalankan hanya **Blackbox Testing (Headless/CI)**, gunakan perintah:

```bash
uv run --with pygame python -m unittest test/test_blackbox_simplepacman.py
```

### Visual Blackbox Testing (Otomatis Bermain)

Untuk melihat Blackbox Testing secara visual, di mana bot otomatis akan membuka jendela game dan memainkan Pacman, jalankan:

```bash
uv run --with pygame python test/test_visual_blackbox.py
```

