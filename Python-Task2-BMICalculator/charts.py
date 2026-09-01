"""
charts.py
---------
Matplotlib chart creation and embedding into a Tkinter window.
Displays a user's BMI trend over time.
"""

import tkinter as tk
from tkinter import ttk

import matplotlib
matplotlib.use("TkAgg")  # Ensure matplotlib uses the Tkinter backend

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from datetime import datetime


class TrendChartWindow:
    """A separate Toplevel window that shows a matplotlib BMI trend chart."""

    def __init__(self, parent, username: str, records: list):
        self.window = tk.Toplevel(parent)
        self.window.title(f"BMI Trend - {username}")
        self.window.geometry("700x520")
        self.window.minsize(500, 400)

        self._build(username, records)

    def _build(self, username: str, records: list):
        container = ttk.Frame(self.window, padding=10)
        container.pack(fill="both", expand=True)

        if not records or len(records) < 2:
            # Graceful handling of insufficient history
            msg = (
                "Not enough history to plot a trend yet.\n\n"
                f"User '{username}' has {len(records)} record(s).\n"
                "At least 2 records are needed to show a trend line.\n\n"
                "Calculate a few more BMI entries for this user and try again."
            )
            label = ttk.Label(
                container, text=msg, justify="center", font=("Segoe UI", 11)
            )
            label.pack(expand=True)
            return

        # Parse timestamps and BMI values
        dates = []
        bmis = []
        for rec in records:
            try:
                dt = datetime.strptime(rec["timestamp"], "%Y-%m-%d %H:%M:%S")
            except (ValueError, KeyError):
                continue
            dates.append(dt)
            bmis.append(rec["bmi"])

        if len(dates) < 2:
            label = ttk.Label(
                container,
                text="Not enough valid history to plot a trend.",
                font=("Segoe UI", 11),
            )
            label.pack(expand=True)
            return

        fig = Figure(figsize=(6.5, 4.8), dpi=100)
        ax = fig.add_subplot(111)

        ax.plot(dates, bmis, marker="o", linestyle="-", color="#2563EB", linewidth=2)

        # Reference bands for BMI categories
        ax.axhspan(0, 18.5, color="#3B82F6", alpha=0.08)
        ax.axhspan(18.5, 25, color="#22C55E", alpha=0.08)
        ax.axhspan(25, 30, color="#F59E0B", alpha=0.08)
        ax.axhspan(30, max(40, max(bmis) + 5), color="#EF4444", alpha=0.08)

        ax.set_title(f"BMI Trend for {username}", fontsize=13, fontweight="bold")
        ax.set_xlabel("Date")
        ax.set_ylabel("BMI")
        ax.grid(True, linestyle="--", alpha=0.4)

        fig.autofmt_xdate(rotation=30)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d\n%H:%M"))

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
