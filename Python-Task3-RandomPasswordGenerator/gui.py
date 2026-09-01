"""
gui.py
------
Tkinter GUI for SecurePass — Random Password Generator.

SECURITY NOTE:
    Generated passwords and the in-session history list live ONLY in this
    process's memory (Python variables / a Tkinter StringVar / a Python
    list). Nothing in this file writes a password to disk, a database, or
    any log. Closing the application permanently discards the history.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List

try:
    import pyperclip
    _PYPERCLIP_AVAILABLE = True
except ImportError:  # pragma: no cover - handled gracefully in-app
    _PYPERCLIP_AVAILABLE = False

from password_generator import PasswordOptions, PasswordGenerationError, generate_password
from strength import evaluate_strength


# --------------------------------------------------------------------------- #
# Color / style constants — "professional modern" dark-accented theme
# --------------------------------------------------------------------------- #
BG_COLOR = "#1e1e2e"
CARD_COLOR = "#282a3a"
ACCENT_COLOR = "#7c5cff"
ACCENT_HOVER = "#6a4bea"
TEXT_COLOR = "#f2f2f7"
SUBTEXT_COLOR = "#a0a0b8"
ENTRY_BG = "#32334a"
ERROR_COLOR = "#e74c3c"
SUCCESS_COLOR = "#27ae60"
FONT_FAMILY = "Segoe UI"

MAX_HISTORY = 5


class SecurePassApp:
    """Main application window / controller for SecurePass."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.history: List[str] = []  # in-memory only, never written to disk

        self._configure_root()
        self._build_style()
        self._build_layout()
        self._on_toggle_changed()  # set initial validation state

    # ------------------------------------------------------------------ #
    # Setup
    # ------------------------------------------------------------------ #
    def _configure_root(self) -> None:
        self.root.title("SecurePass — Random Password Generator")
        self.root.geometry("560x760")
        self.root.minsize(520, 700)
        self.root.configure(bg=BG_COLOR)

    def _build_style(self) -> None:
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "TCheckbutton",
            background=CARD_COLOR,
            foreground=TEXT_COLOR,
            font=(FONT_FAMILY, 10),
        )
        style.map(
            "TCheckbutton",
            background=[("active", CARD_COLOR)],
            foreground=[("disabled", SUBTEXT_COLOR)],
        )

        style.configure(
            "Horizontal.TScale",
            background=CARD_COLOR,
            troughcolor=ENTRY_BG,
        )

        style.configure(
            "TSpinbox",
            fieldbackground=ENTRY_BG,
            background=ENTRY_BG,
            foreground=TEXT_COLOR,
            arrowsize=14,
        )

        style.configure(
            "Strength.Horizontal.TProgressbar",
            troughcolor=ENTRY_BG,
            background=ACCENT_COLOR,
            bordercolor=CARD_COLOR,
            lightcolor=ACCENT_COLOR,
            darkcolor=ACCENT_COLOR,
        )

    # ------------------------------------------------------------------ #
    # Layout
    # ------------------------------------------------------------------ #
    def _build_layout(self) -> None:
        outer = tk.Frame(self.root, bg=BG_COLOR, padx=24, pady=20)
        outer.pack(fill="both", expand=True)

        self._build_header(outer)
        self._build_password_display(outer)
        self._build_strength_section(outer)
        self._build_options_card(outer)
        self._build_action_buttons(outer)
        self._build_history_section(outer)
        self._build_status_bar(outer)

    def _build_header(self, parent: tk.Widget) -> None:
        title = tk.Label(
            parent,
            text="🔒 SecurePass",
            font=(FONT_FAMILY, 22, "bold"),
            bg=BG_COLOR,
            fg=TEXT_COLOR,
        )
        title.pack(anchor="w")

        subtitle = tk.Label(
            parent,
            text="Cryptographically secure password generator",
            font=(FONT_FAMILY, 10),
            bg=BG_COLOR,
            fg=SUBTEXT_COLOR,
        )
        subtitle.pack(anchor="w", pady=(0, 16))

    def _build_password_display(self, parent: tk.Widget) -> None:
        card = tk.Frame(parent, bg=CARD_COLOR, padx=16, pady=16)
        card.pack(fill="x", pady=(0, 14))

        self.password_var = tk.StringVar(value="Click “Generate Password” to begin")
        self.password_entry = tk.Entry(
            card,
            textvariable=self.password_var,
            font=("Consolas", 16, "bold"),
            bg=CARD_COLOR,
            fg=ACCENT_COLOR,
            insertbackground=TEXT_COLOR,
            relief="flat",
            justify="center",
            state="readonly",
            readonlybackground=CARD_COLOR,
        )
        self.password_entry.pack(fill="x", ipady=10)

    def _build_strength_section(self, parent: tk.Widget) -> None:
        card = tk.Frame(parent, bg=BG_COLOR)
        card.pack(fill="x", pady=(0, 14))

        row = tk.Frame(card, bg=BG_COLOR)
        row.pack(fill="x")

        tk.Label(
            row, text="Strength:", font=(FONT_FAMILY, 10, "bold"),
            bg=BG_COLOR, fg=TEXT_COLOR,
        ).pack(side="left")

        self.strength_label_var = tk.StringVar(value="—")
        self.strength_label = tk.Label(
            row,
            textvariable=self.strength_label_var,
            font=(FONT_FAMILY, 10, "bold"),
            bg=BG_COLOR,
            fg=SUBTEXT_COLOR,
        )
        self.strength_label.pack(side="left", padx=(6, 0))

        self.strength_bar = ttk.Progressbar(
            card,
            style="Strength.Horizontal.TProgressbar",
            orient="horizontal",
            mode="determinate",
            maximum=6,
            value=0,
        )
        self.strength_bar.pack(fill="x", pady=(6, 0))

    def _build_options_card(self, parent: tk.Widget) -> None:
        card = tk.Frame(parent, bg=CARD_COLOR, padx=16, pady=16)
        card.pack(fill="x", pady=(0, 14))

        # ---- Length control (slider + spinbox, kept in sync) ---------- #
        length_header = tk.Frame(card, bg=CARD_COLOR)
        length_header.pack(fill="x")

        tk.Label(
            length_header, text="Password Length", font=(FONT_FAMILY, 11, "bold"),
            bg=CARD_COLOR, fg=TEXT_COLOR,
        ).pack(side="left")

        self.length_var = tk.IntVar(value=12)

        self.length_spinbox = ttk.Spinbox(
            length_header,
            from_=8,
            to=128,
            width=5,
            textvariable=self.length_var,
            command=self._on_length_spinbox_change,
            font=(FONT_FAMILY, 10),
        )
        self.length_spinbox.pack(side="right")
        self.length_spinbox.bind("<KeyRelease>", self._on_length_spinbox_change)

        self.length_slider = ttk.Scale(
            card,
            from_=8,
            to=64,
            orient="horizontal",
            command=self._on_length_slider_change,
        )
        self.length_slider.set(12)
        self.length_slider.pack(fill="x", pady=(8, 4))

        tk.Label(
            card,
            text="Minimum 8 characters — use the spinbox for lengths above 64.",
            font=(FONT_FAMILY, 8),
            bg=CARD_COLOR,
            fg=SUBTEXT_COLOR,
        ).pack(anchor="w", pady=(0, 12))

        ttk.Separator(card, orient="horizontal").pack(fill="x", pady=(0, 12))

        # ---- Character type checkboxes --------------------------------- #
        tk.Label(
            card, text="Character Types", font=(FONT_FAMILY, 11, "bold"),
            bg=CARD_COLOR, fg=TEXT_COLOR,
        ).pack(anchor="w", pady=(0, 6))

        self.use_upper = tk.BooleanVar(value=True)
        self.use_lower = tk.BooleanVar(value=True)
        self.use_digits = tk.BooleanVar(value=True)
        self.use_symbols = tk.BooleanVar(value=False)

        checks_frame = tk.Frame(card, bg=CARD_COLOR)
        checks_frame.pack(fill="x")

        ttk.Checkbutton(
            checks_frame, text="Uppercase (A-Z)", variable=self.use_upper,
            command=self._on_toggle_changed,
        ).grid(row=0, column=0, sticky="w", pady=3, padx=(0, 12))

        ttk.Checkbutton(
            checks_frame, text="Lowercase (a-z)", variable=self.use_lower,
            command=self._on_toggle_changed,
        ).grid(row=0, column=1, sticky="w", pady=3)

        ttk.Checkbutton(
            checks_frame, text="Numbers (0-9)", variable=self.use_digits,
            command=self._on_toggle_changed,
        ).grid(row=1, column=0, sticky="w", pady=3, padx=(0, 12))

        ttk.Checkbutton(
            checks_frame, text="Symbols (!@#$…)", variable=self.use_symbols,
            command=self._on_toggle_changed,
        ).grid(row=1, column=1, sticky="w", pady=3)

        ttk.Separator(card, orient="horizontal").pack(fill="x", pady=12)

        self.exclude_ambiguous = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            card,
            text='Exclude ambiguous characters (0, O, l, 1, I, |, etc.)',
            variable=self.exclude_ambiguous,
            command=self._on_toggle_changed,
        ).pack(anchor="w")

        # Live validation message
        self.validation_var = tk.StringVar(value="")
        self.validation_label = tk.Label(
            card,
            textvariable=self.validation_var,
            font=(FONT_FAMILY, 9),
            bg=CARD_COLOR,
            fg=ERROR_COLOR,
            wraplength=460,
            justify="left",
        )
        self.validation_label.pack(anchor="w", pady=(8, 0))

    def _build_action_buttons(self, parent: tk.Widget) -> None:
        row = tk.Frame(parent, bg=BG_COLOR)
        row.pack(fill="x", pady=(0, 14))

        self.generate_btn = tk.Button(
            row,
            text="⚡ Generate Password",
            font=(FONT_FAMILY, 11, "bold"),
            bg=ACCENT_COLOR,
            fg="white",
            activebackground=ACCENT_HOVER,
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            command=self.on_generate_clicked,
            padx=10,
            pady=10,
        )
        self.generate_btn.pack(side="left", expand=True, fill="x", padx=(0, 8))

        self.copy_btn = tk.Button(
            row,
            text="📋 Copy",
            font=(FONT_FAMILY, 11, "bold"),
            bg=ENTRY_BG,
            fg=TEXT_COLOR,
            activebackground=CARD_COLOR,
            activeforeground=TEXT_COLOR,
            relief="flat",
            cursor="hand2",
            command=self.on_copy_clicked,
            padx=10,
            pady=10,
        )
        self.copy_btn.pack(side="left", fill="x")

    def _build_history_section(self, parent: tk.Widget) -> None:
        header_row = tk.Frame(parent, bg=BG_COLOR)
        header_row.pack(fill="x")

        tk.Label(
            header_row,
            text=f"Session History (last {MAX_HISTORY})",
            font=(FONT_FAMILY, 11, "bold"),
            bg=BG_COLOR,
            fg=TEXT_COLOR,
        ).pack(side="left")

        clear_btn = tk.Button(
            header_row,
            text="Clear History",
            font=(FONT_FAMILY, 9),
            bg=BG_COLOR,
            fg=ERROR_COLOR,
            relief="flat",
            cursor="hand2",
            command=self.on_clear_history_clicked,
        )
        clear_btn.pack(side="right")

        history_card = tk.Frame(parent, bg=CARD_COLOR, padx=10, pady=10)
        history_card.pack(fill="both", expand=True, pady=(6, 10))

        self.history_listbox = tk.Listbox(
            history_card,
            font=("Consolas", 10),
            bg=ENTRY_BG,
            fg=TEXT_COLOR,
            selectbackground=ACCENT_COLOR,
            relief="flat",
            height=6,
            activestyle="none",
        )
        self.history_listbox.pack(fill="both", expand=True)
        self.history_listbox.bind("<<ListboxSelect>>", self._on_history_select)

        tk.Label(
            parent,
            text="History is kept in memory only for this session and is "
                 "never written to a file or database.",
            font=(FONT_FAMILY, 8),
            bg=BG_COLOR,
            fg=SUBTEXT_COLOR,
            wraplength=500,
            justify="left",
        ).pack(anchor="w")

    def _build_status_bar(self, parent: tk.Widget) -> None:
        self.status_var = tk.StringVar(value="Ready.")
        status = tk.Label(
            parent,
            textvariable=self.status_var,
            font=(FONT_FAMILY, 9),
            bg=BG_COLOR,
            fg=SUBTEXT_COLOR,
            anchor="w",
        )
        status.pack(fill="x", pady=(10, 0))

    # ------------------------------------------------------------------ #
    # Event handlers
    # ------------------------------------------------------------------ #
    def _on_length_slider_change(self, value: str) -> None:
        int_value = int(float(value))
        self.length_var.set(int_value)
        # ``Scale.set()`` invokes its command while the options card is
        # still being built.  At that point the checkbox variables do not
        # exist yet; the final validation in ``__init__`` handles them once
        # construction is complete.
        if not hasattr(self, "use_upper"):
            return
        self._on_toggle_changed()

    def _on_length_spinbox_change(self, *_args) -> None:
        try:
            value = int(self.length_var.get())
        except (tk.TclError, ValueError):
            return
        # Keep the slider synced when its range covers the value.
        if 8 <= value <= 64:
            self.length_slider.set(value)
        self._on_toggle_changed()

    def _on_toggle_changed(self) -> None:
        """Re-validate current selections live and update UI hints."""
        options = self._collect_options(silent=True)
        try:
            options.validate()
            self.validation_var.set("")
            self.generate_btn.config(state="normal")
        except PasswordGenerationError as exc:
            self.validation_var.set(f"⚠ {exc}")
            self.generate_btn.config(state="normal")  # still allow click -> shows dialog

    def on_generate_clicked(self) -> None:
        options = self._collect_options(silent=False)
        if options is None:
            return

        try:
            options.validate()
        except PasswordGenerationError as exc:
            self._show_error(str(exc))
            return

        try:
            password = generate_password(options)
        except PasswordGenerationError as exc:
            self._show_error(str(exc))
            return
        except Exception as exc:  # unexpected failure safety net
            self._show_error(f"Unexpected error while generating password: {exc}")
            return

        self.password_var.set(password)
        self._update_strength(password)
        self._add_to_history(password)
        self._auto_copy(password)
        self.status_var.set("Password generated and copied to clipboard.")

    def on_copy_clicked(self) -> None:
        password = self.password_var.get()
        if not password or password.startswith("Click "):
            self._show_error("Generate a password first.")
            return
        self._copy_to_clipboard(password, manual=True)

    def on_clear_history_clicked(self) -> None:
        if not self.history:
            self.status_var.set("History is already empty.")
            return
        confirmed = messagebox.askyesno(
            "Clear History", "Clear the session password history?"
        )
        if confirmed:
            self.history.clear()
            self.history_listbox.delete(0, tk.END)
            self.status_var.set("History cleared.")

    def _on_history_select(self, _event) -> None:
        selection = self.history_listbox.curselection()
        if not selection:
            return
        # Listbox shows newest first; map back to stored password.
        text = self.history_listbox.get(selection[0])
        # Strip the leading "1. " style index prefix.
        password = text.split(". ", 1)[-1]
        self.password_var.set(password)
        self._update_strength(password)
        self.status_var.set("Loaded password from history (not re-copied).")

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _collect_options(self, silent: bool) -> PasswordOptions | None:
        try:
            length = int(self.length_var.get())
        except (tk.TclError, ValueError):
            if not silent:
                self._show_error("Password length must be a whole number.")
            length = 0  # will fail validation naturally

        return PasswordOptions(
            length=length,
            use_upper=self.use_upper.get(),
            use_lower=self.use_lower.get(),
            use_digits=self.use_digits.get(),
            use_symbols=self.use_symbols.get(),
            exclude_ambiguous=self.exclude_ambiguous.get(),
        )

    def _update_strength(self, password: str) -> None:
        result = evaluate_strength(password)
        self.strength_label_var.set(result.label)
        self.strength_label.config(fg=result.color)
        self.strength_bar.config(value=result.score)
        style = ttk.Style()
        style.configure("Strength.Horizontal.TProgressbar", background=result.color)

    def _add_to_history(self, password: str) -> None:
        self.history.insert(0, password)
        self.history = self.history[:MAX_HISTORY]
        self.history_listbox.delete(0, tk.END)
        for idx, pwd in enumerate(self.history, start=1):
            self.history_listbox.insert(tk.END, f"{idx}. {pwd}")

    def _auto_copy(self, password: str) -> None:
        self._copy_to_clipboard(password, manual=False)

    def _copy_to_clipboard(self, password: str, manual: bool) -> None:
        if not _PYPERCLIP_AVAILABLE:
            if manual:
                self._show_error(
                    "pyperclip is not installed. Run:\n\n    pip install pyperclip"
                )
            self.status_var.set(
                "Password generated (clipboard copy unavailable — install pyperclip)."
            )
            return

        try:
            pyperclip.copy(password)
            if manual:
                self.status_var.set("Password copied to clipboard.")
        except Exception as exc:
            # Clipboard access can fail in headless/CI environments — never crash.
            if manual:
                self._show_error(f"Could not access the system clipboard: {exc}")
            self.status_var.set("Clipboard copy failed — see error dialog.")

    def _show_error(self, message: str) -> None:
        messagebox.showerror("SecurePass — Invalid Input", message)
        self.status_var.set("Fix the highlighted issue and try again.")


def launch_app() -> None:
    """Entry point used by main.py to start the Tkinter event loop."""
    root = tk.Tk()
    try:
        app = SecurePassApp(root)  # noqa: F841 (kept alive by closures/root)
    except Exception as exc:  # pragma: no cover
        messagebox.showerror("SecurePass — Fatal Error", f"Failed to start: {exc}")
        raise
    root.mainloop()
