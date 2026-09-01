#!/usr/bin/env python3
"""
main.py
-------
Entry point for SecurePass — Random Password Generator (Oasis Infobyte,
Advanced Tier, Task 3).

Run with:
    python main.py

This file intentionally contains no business logic — it only wires together
the GUI defined in gui.py so the app is usable entirely without a terminal
once launched (e.g. by double-clicking a shortcut to this script on
platforms where .py files are associated with pythonw.exe).
"""

import sys
import tkinter as tk
from tkinter import messagebox


def main() -> None:
    try:
        from gui import launch_app
    except ImportError as exc:
        # This can only happen if the project files are moved/renamed
        # or a dependency failed to import — show a friendly message
        # instead of a bare traceback.
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "SecurePass — Startup Error",
            f"Could not load the application modules.\n\n{exc}\n\n"
            "Make sure main.py, gui.py, password_generator.py and "
            "strength.py are all in the same folder, and that "
            "dependencies are installed:\n\n    pip install -r requirements.txt",
        )
        sys.exit(1)

    launch_app()


if __name__ == "__main__":
    main()
