"""
gui.py
------
Tkinter GUI for the BMI Tracker application.
Ties together bmi_logic.py (calculation/validation), database.py (persistence),
and charts.py (matplotlib trend view).
"""

import tkinter as tk
from tkinter import ttk, messagebox

import bmi_logic
from database import BMIDatabase, DatabaseError
from charts import TrendChartWindow


APP_TITLE = "BMI Tracker"
BG_COLOUR = "#F3F4F6"
CARD_COLOUR = "#FFFFFF"
ACCENT_COLOUR = "#2563EB"
TEXT_COLOUR = "#111827"
MUTED_TEXT = "#6B7280"


class BMITrackerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("880x640")
        self.root.minsize(760, 560)
        self.root.configure(bg=BG_COLOUR)

        # Initialize database; handle failure gracefully at startup
        self.db = None
        try:
            self.db = BMIDatabase()
        except DatabaseError as exc:
            messagebox.showerror(
                "Database Error",
                f"Could not initialize the database.\n\n{exc}\n\n"
                "The app will still run, but records cannot be saved or loaded.",
            )

        self._setup_style()
        self._build_layout()

    # ------------------------------------------------------------------
    # Styling
    # ------------------------------------------------------------------
    def _setup_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("TFrame", background=BG_COLOUR)
        style.configure("Card.TFrame", background=CARD_COLOUR)
        style.configure(
            "TLabel", background=BG_COLOUR, foreground=TEXT_COLOUR, font=("Segoe UI", 10)
        )
        style.configure(
            "Card.TLabel", background=CARD_COLOUR, foreground=TEXT_COLOUR, font=("Segoe UI", 10)
        )
        style.configure(
            "Title.TLabel",
            background=BG_COLOUR,
            foreground=TEXT_COLOUR,
            font=("Segoe UI", 20, "bold"),
        )
        style.configure(
            "Subtitle.TLabel",
            background=BG_COLOUR,
            foreground=MUTED_TEXT,
            font=("Segoe UI", 10),
        )
        style.configure(
            "Accent.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=8,
        )
        style.configure("TEntry", padding=6)
        style.configure(
            "Treeview",
            background=CARD_COLOUR,
            fieldbackground=CARD_COLOUR,
            rowheight=26,
            font=("Segoe UI", 9),
        )
        style.configure(
            "Treeview.Heading", font=("Segoe UI", 9, "bold")
        )

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------
    def _build_layout(self):
        # Header
        header = ttk.Frame(self.root, style="TFrame", padding=(20, 16, 20, 8))
        header.pack(fill="x")

        ttk.Label(header, text="🩺 BMI Tracker", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            header,
            text="Track your Body Mass Index over time. Educational tool - not medical advice.",
            style="Subtitle.TLabel",
        ).pack(anchor="w")

        # Main body: left = input/result, right = history
        body = ttk.Frame(self.root, style="TFrame", padding=(20, 8, 20, 20))
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        self._build_input_card(body)
        self._build_history_card(body)

        # Status bar
        self.status_var = tk.StringVar(value="Ready.")
        status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            style="Subtitle.TLabel",
            padding=(20, 4),
        )
        status_bar.pack(fill="x", side="bottom")

    # ------------------------------------------------------------------
    # Left card: inputs + result
    # ------------------------------------------------------------------
    def _build_input_card(self, parent):
        card = tk.Frame(parent, bg=CARD_COLOUR, highlightbackground="#E5E7EB",
                         highlightthickness=1, bd=0)
        card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        pad = {"padx": 18, "pady": (6, 2)}

        tk.Label(card, text="Calculate BMI", bg=CARD_COLOUR, fg=TEXT_COLOUR,
                 font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=18, pady=(18, 10))

        # Username
        tk.Label(card, text="Username", bg=CARD_COLOUR, fg=MUTED_TEXT,
                 font=("Segoe UI", 9)).pack(anchor="w", **pad)
        self.username_var = tk.StringVar()
        username_entry = ttk.Entry(card, textvariable=self.username_var, font=("Segoe UI", 11))
        username_entry.pack(fill="x", padx=18, pady=(0, 6))
        username_entry.bind("<FocusOut>", lambda e: self._refresh_history())
        username_entry.bind("<Return>", lambda e: self._refresh_history())

        # Weight
        tk.Label(card, text="Weight (kg)", bg=CARD_COLOUR, fg=MUTED_TEXT,
                 font=("Segoe UI", 9)).pack(anchor="w", **pad)
        self.weight_var = tk.StringVar()
        ttk.Entry(card, textvariable=self.weight_var, font=("Segoe UI", 11)).pack(
            fill="x", padx=18, pady=(0, 6)
        )

        # Height
        tk.Label(card, text="Height (m)", bg=CARD_COLOUR, fg=MUTED_TEXT,
                 font=("Segoe UI", 9)).pack(anchor="w", **pad)
        self.height_var = tk.StringVar()
        height_entry = ttk.Entry(card, textvariable=self.height_var, font=("Segoe UI", 11))
        height_entry.pack(fill="x", padx=18, pady=(0, 6))
        height_entry.bind("<Return>", lambda e: self._on_calculate())

        # Buttons row
        btn_row = tk.Frame(card, bg=CARD_COLOUR)
        btn_row.pack(fill="x", padx=18, pady=(14, 6))

        calc_btn = tk.Button(
            btn_row, text="Calculate BMI", command=self._on_calculate,
            bg=ACCENT_COLOUR, fg="white", font=("Segoe UI", 10, "bold"),
            relief="flat", padx=14, pady=8, cursor="hand2",
        )
        calc_btn.pack(side="left", fill="x", expand=True, padx=(0, 6))

        clear_btn = tk.Button(
            btn_row, text="Clear / Reset", command=self._on_clear,
            bg="#E5E7EB", fg=TEXT_COLOUR, font=("Segoe UI", 10, "bold"),
            relief="flat", padx=14, pady=8, cursor="hand2",
        )
        clear_btn.pack(side="left", fill="x", expand=True, padx=(6, 0))

        # Result area
        result_frame = tk.Frame(card, bg=CARD_COLOUR)
        result_frame.pack(fill="x", padx=18, pady=(18, 10))

        self.bmi_value_var = tk.StringVar(value="--")
        self.bmi_result_label = tk.Label(
            result_frame, textvariable=self.bmi_value_var, bg=CARD_COLOUR,
            fg=TEXT_COLOUR, font=("Segoe UI", 40, "bold"),
        )
        self.bmi_result_label.pack()

        self.category_var = tk.StringVar(value="Enter your details above")
        self.category_label = tk.Label(
            result_frame, textvariable=self.category_var, bg=CARD_COLOUR,
            fg=MUTED_TEXT, font=("Segoe UI", 13, "bold"),
        )
        self.category_label.pack(pady=(2, 0))

        # Error/status message inside the card
        self.error_var = tk.StringVar(value="")
        self.error_label = tk.Label(
            card, textvariable=self.error_var, bg=CARD_COLOUR, fg="#DC2626",
            font=("Segoe UI", 9), wraplength=320, justify="left",
        )
        self.error_label.pack(fill="x", padx=18, pady=(0, 18))

    # ------------------------------------------------------------------
    # Right card: history
    # ------------------------------------------------------------------
    def _build_history_card(self, parent):
        card = tk.Frame(parent, bg=CARD_COLOUR, highlightbackground="#E5E7EB",
                         highlightthickness=1, bd=0)
        card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        card.rowconfigure(1, weight=1)
        card.columnconfigure(0, weight=1)

        top_row = tk.Frame(card, bg=CARD_COLOUR)
        top_row.grid(row=0, column=0, sticky="ew", padx=18, pady=(18, 10))
        top_row.columnconfigure(0, weight=1)

        tk.Label(top_row, text="History", bg=CARD_COLOUR, fg=TEXT_COLOUR,
                 font=("Segoe UI", 13, "bold")).grid(row=0, column=0, sticky="w")

        trend_btn = tk.Button(
            top_row, text="View Trend 📈", command=self._on_view_trend,
            bg="#111827", fg="white", font=("Segoe UI", 9, "bold"),
            relief="flat", padx=10, pady=6, cursor="hand2",
        )
        trend_btn.grid(row=0, column=1, sticky="e")

        # Treeview for history
        columns = ("timestamp", "weight", "height", "bmi", "category")
        self.history_tree = ttk.Treeview(
            card, columns=columns, show="headings", height=14
        )
        self.history_tree.heading("timestamp", text="Date/Time")
        self.history_tree.heading("weight", text="Weight (kg)")
        self.history_tree.heading("height", text="Height (m)")
        self.history_tree.heading("bmi", text="BMI")
        self.history_tree.heading("category", text="Category")

        self.history_tree.column("timestamp", width=140, anchor="center")
        self.history_tree.column("weight", width=90, anchor="center")
        self.history_tree.column("height", width=90, anchor="center")
        self.history_tree.column("bmi", width=70, anchor="center")
        self.history_tree.column("category", width=100, anchor="center")

        self.history_tree.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 6))

        scrollbar = ttk.Scrollbar(card, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=1, column=1, sticky="ns", pady=(0, 6))

        self.history_hint_var = tk.StringVar(
            value="Enter a username on the left to see their saved records."
        )
        tk.Label(
            card, textvariable=self.history_hint_var, bg=CARD_COLOUR, fg=MUTED_TEXT,
            font=("Segoe UI", 9), wraplength=320, justify="left",
        ).grid(row=2, column=0, sticky="w", padx=18, pady=(0, 16))

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------
    def _on_calculate(self):
        self.error_var.set("")
        username = self.username_var.get()
        weight_str = self.weight_var.get()
        height_str = self.height_var.get()

        try:
            result = bmi_logic.compute_full_result(username, weight_str, height_str)
        except bmi_logic.ValidationError as exc:
            self.error_var.set(f"⚠ {exc}")
            self.status_var.set("Please fix the highlighted input and try again.")
            return
        except Exception as exc:  # Catch-all so the app never crashes on bad input
            self.error_var.set(f"⚠ Unexpected error: {exc}")
            self.status_var.set("An unexpected error occurred.")
            return

        # Display result
        self.bmi_value_var.set(f"{result['bmi']:.2f}")
        self.category_var.set(result["category"])
        self.category_label.configure(fg=result["colour"])
        self.bmi_result_label.configure(fg=result["colour"])

        # Save to database (graceful failure)
        if self.db is not None:
            try:
                self.db.add_record(
                    result["username"], result["weight"], result["height"],
                    result["bmi"], result["category"],
                )
                self.status_var.set(
                    f"Saved BMI {result['bmi']:.2f} ({result['category']}) for "
                    f"'{result['username']}'."
                )
            except DatabaseError as exc:
                self.error_var.set(f"⚠ Record calculated but not saved: {exc}")
                self.status_var.set("Database write failed.")
        else:
            self.status_var.set(
                f"BMI calculated: {result['bmi']:.2f} ({result['category']}). "
                "Database unavailable, record not saved."
            )

        self._refresh_history()

    def _on_clear(self):
        self.username_var.set("")
        self.weight_var.set("")
        self.height_var.set("")
        self.bmi_value_var.set("--")
        self.category_var.set("Enter your details above")
        self.category_label.configure(fg=MUTED_TEXT)
        self.bmi_result_label.configure(fg=TEXT_COLOUR)
        self.error_var.set("")
        self.status_var.set("Cleared.")
        for row in self.history_tree.get_children():
            self.history_tree.delete(row)
        self.history_hint_var.set("Enter a username on the left to see their saved records.")

    def _refresh_history(self):
        """Reload the history table for whatever username is currently entered."""
        for row in self.history_tree.get_children():
            self.history_tree.delete(row)

        username = self.username_var.get().strip()
        if not username:
            self.history_hint_var.set("Enter a username on the left to see their saved records.")
            return

        if self.db is None:
            self.history_hint_var.set("Database unavailable - history cannot be loaded.")
            return

        try:
            records = self.db.get_records_for_user(username)
        except DatabaseError as exc:
            self.history_hint_var.set(f"⚠ Could not load history: {exc}")
            return

        if not records:
            self.history_hint_var.set(f"No saved records yet for '{username}'.")
            return

        # Show most recent first in the table
        for rec in reversed(records):
            self.history_tree.insert(
                "", "end",
                values=(rec["timestamp"], rec["weight"], rec["height"],
                        f"{rec['bmi']:.2f}", rec["category"]),
            )

        self.history_hint_var.set(f"{len(records)} record(s) found for '{username}'.")

    def _on_view_trend(self):
        username = self.username_var.get().strip()
        if not username:
            messagebox.showinfo("No User Selected", "Enter a username first to view their trend.")
            return

        if self.db is None:
            messagebox.showerror("Database Unavailable", "Cannot load trend data - database unavailable.")
            return

        try:
            records = self.db.get_records_for_user(username)
        except DatabaseError as exc:
            messagebox.showerror("Database Error", f"Could not load history:\n{exc}")
            return

        TrendChartWindow(self.root, username, records)
