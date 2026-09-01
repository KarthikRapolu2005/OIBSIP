"""
main.py
-------
Entry point for the BMI Tracker desktop application.
Run with:  python main.py
"""

import tkinter as tk
from gui import BMITrackerApp


def main():
    root = tk.Tk()
    app = BMITrackerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
