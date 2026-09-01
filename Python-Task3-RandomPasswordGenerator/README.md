# SecurePass — Random Password Generator (Advanced)

A polished desktop GUI password generator built for the **Oasis Infobyte Python
Programming Internship — Task 3 (Advanced Tier)**.

SecurePass generates cryptographically secure passwords using Python's
`secrets` module, offers full control over length and character composition,
shows a live strength indicator, copies results to the clipboard
automatically, and keeps a temporary in-memory history of the last 5
passwords generated during the current session — **nothing is ever saved to
disk.**

---

## 1. Features

| # | Requirement (Oasis Task Spec) | Implementation |
|---|---|---|
| 1 | Password length input, min 8 | Spinbox (8–128) + slider (8–64), validated in `PasswordOptions.validate()` |
| 2 | Select upper / lower / numbers / symbols | Four independent checkboxes |
| 3 | At least 2 character types required | Validated live and again before generation |
| 4 | Generate password matching selected criteria | `password_generator.generate_password()` |
| 5 | Validate invalid length / selection | Inline warning label + error dialog, generation blocked until valid |
| 6 | Generate another password without restarting | "Generate Password" button reusable indefinitely |
| 7 | GUI (tkinter or PyQt5) | Built with `tkinter` + `ttk` |
| 8 | Use `secrets`, not `random` | `secrets.choice` + `secrets.SystemRandom().shuffle`; `random` is never imported |
| 9 | Slider or spinbox for length | Both provided, kept in sync |
| 10 | Checkboxes for character types | 4 `ttk.Checkbutton` widgets |
| 11 | Strength indicator (Weak/Medium/Strong) | `strength.evaluate_strength()`, color-coded progress bar |
| 12 | Guarantee ≥1 char from every selected type | Seed characters drawn first, then securely shuffled |
| 13 | Copy to clipboard (`pyperclip`), auto-copy on generation | `_auto_copy()` called immediately after generation; manual "Copy" button also available |
| 14 | Exclude ambiguous characters (0, O, l, 1, …) | Checkbox toggles `AMBIGUOUS_CHARS` filtering on all pools |
| 15 | Session history, last 5 passwords | In-memory `list`, capped at 5, shown in a `Listbox` |
| 16 | Never persist passwords to file/DB | No file/DB I/O exists anywhere in the codebase (see Security section) |

Additional polish:
- Modern dark UI theme with card-style sections.
- Live validation messages as you change options (before you even click Generate).
- Clear History button with confirmation dialog.
- Clicking a past password in history reloads it into the display (does not
  re-copy it, so today's clipboard content isn't silently overwritten).
- Full exception handling around clipboard access, spinbox parsing, and
  generation, so the app never crashes to a raw traceback.

---

## 2. Project Structure

```
securepass/
├── main.py                 # Entry point — launches the GUI
├── gui.py                  # Tkinter GUI (all widgets, event handlers)
├── password_generator.py   # Core secure password generation engine
├── strength.py              # Weak / Medium / Strong scoring logic
├── requirements.txt         # External dependency (pyperclip)
├── README.md                # This file
└── .gitignore
```

**Why this structure?**
- `password_generator.py` and `strength.py` contain pure logic with **zero**
  GUI dependencies — they can be imported and unit-tested independently of
  tkinter (see Testing Checklist below).
- `gui.py` is the only file that touches tkinter/pyperclip; it imports the
  logic modules rather than duplicating anything.
- `main.py` is a thin launcher so the app can be started with a single,
  memorable command and fails gracefully with a message box (not a terminal
  traceback) if a module is missing.

---

## 3. Security Design

This project treats password-handling security as a first-class requirement,
not an afterthought:

1. **CSPRNG only.** All randomness comes from the `secrets` module
   (`secrets.choice`, `secrets.SystemRandom().shuffle`), which is built on
   your OS's cryptographically secure random source (`os.urandom`). The
   `random` module — which is *not* safe for security purposes — is never
   imported anywhere in this codebase.
2. **Guaranteed diversity without weakening randomness.** One character is
   drawn from each *selected* category first (so the password always
   contains what the user asked for), then the rest of the password is
   filled from the combined pool and the entire result is shuffled with a
   CSPRNG-backed shuffle — so guaranteed characters aren't predictably
   placed at fixed positions.
3. **No persistence, anywhere.** Search the codebase: there is no `open(...,
   "w")`, no `sqlite3`, no `json.dump`, no logging call that includes a
   password. The "session history" feature is a plain Python `list` held in
   the `SecurePassApp` instance's memory. It is created empty when the app
   starts and is destroyed the moment the process exits — there is no save
   file to find, back up, or leak.
4. **No logging of secrets.** The app does not use the `logging` module at
   all, so there is no risk of a password ending up in a log file by
   accident.
5. **Clipboard is best-effort and explicit.** Copying uses `pyperclip`,
   which relies on your OS clipboard. If `pyperclip` isn't installed or the
   clipboard is unavailable (e.g., a headless environment), the app
   degrades gracefully with a status message instead of crashing — it never
   silently fails or masks the issue.
6. **Fail closed, not open.** Every validation path (length, character
   selection count, empty pool after ambiguous-exclusion) raises a
   descriptive `PasswordGenerationError` and generation is refused rather
   than silently producing a weaker password than requested.

---

## 4. Installation

```bash
# 1. Clone or download the project, then move into it
cd securepass

# 2. (Recommended) create a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

> `tkinter` ships with the standard CPython installer on Windows/macOS. On
> some Linux distributions you may need to install it separately, e.g.:
> `sudo apt-get install python3-tk`

---

## 5. Running the App

```bash
python main.py
```

The GUI opens immediately — no further terminal interaction is required.
Everything (length, character types, generation, copying, history) is
controlled from the window itself.

---

## 6. Testing Checklist

Manual QA checklist to verify every requirement before recording your demo:

- [ ] Launch app — window opens with sensible defaults (length 12,
      upper/lower/digits checked, symbols unchecked).
- [ ] Set length below 8 (e.g., via spinbox) → warning appears, Generate
      still shows a clear error dialog if clicked.
- [ ] Uncheck all but one character type → warning: "select at least 2".
- [ ] Check exactly 2 types → warning disappears, Generate works.
- [ ] Generate with all 4 types checked, length 20 → password contains at
      least one uppercase, one lowercase, one digit, one symbol (inspect by
      eye or paste into a text editor).
- [ ] Generate repeatedly → password changes every time; no crashes.
- [ ] Check "Exclude ambiguous characters" → resulting passwords never
      contain `0 O 1 l I |` etc.
- [ ] Uncheck all types except "Symbols" and enable "Exclude ambiguous" with
      only that one type still selected → still correctly blocked at "select
      at least 2 types" (ambiguous-exclusion check doesn't bypass the
      2-type rule).
- [ ] Generate a password → paste (Ctrl+V) into another application →
      confirms clipboard auto-copy worked.
- [ ] Click "Copy" manually after selecting a history item → clipboard
      updates to that value.
- [ ] Generate 6+ passwords → history list only ever shows the most recent
      5, newest first.
- [ ] Click "Clear History" → confirmation dialog appears; confirming empties
      the list.
- [ ] Strength label reads "Weak" for a short, single-type password;
      "Strong" for a long password using all 4 character types.
- [ ] Resize the window → layout remains usable (no overlapping widgets).
- [ ] Close and relaunch the app → history is empty again (proves nothing
      was persisted).

### Optional automated smoke test for the logic layer

Since `password_generator.py` and `strength.py` have no GUI dependencies,
you can sanity-check them directly from a Python shell without opening the
GUI:

```bash
python -c "
from password_generator import PasswordOptions, generate_password
from strength import evaluate_strength

opts = PasswordOptions(length=16, use_upper=True, use_lower=True,
                        use_digits=True, use_symbols=True,
                        exclude_ambiguous=True)
pwd = generate_password(opts)
print('Password:', pwd)
print('Length OK:', len(pwd) == 16)
print('Strength:', evaluate_strength(pwd).label)
"
```

---

## 7. Demo Checklist (for the Oasis Infobyte submission video)

1. Show the project folder structure briefly (main.py, gui.py,
   password_generator.py, strength.py).
2. Run `python main.py` from a terminal to show it launches cleanly.
3. Demonstrate the length slider and spinbox both moving together.
4. Toggle character type checkboxes; show the live validation message when
   fewer than 2 types are selected.
5. Try a length under 8 and show the validation message.
6. Generate a password with all 4 types selected — point out the strength
   indicator turning "Strong" and the color change.
7. Paste the clipboard content somewhere (e.g., Notepad) to prove
   auto-copy-on-generate works.
8. Toggle "Exclude ambiguous characters" and generate again — zoom in to
   show no `0/O/1/l/I` characters appear.
9. Generate several passwords back-to-back and show the history panel
   only keeps the last 5, newest on top.
10. Click a history entry to show it reloads into the main display.
11. Click "Clear History" and confirm the dialog, then show the list empty.
12. Briefly open `password_generator.py` on screen and highlight the
    `import secrets` line plus the absence of `import random` anywhere in
    the project, to visibly prove the CSPRNG requirement.
13. Close the app and mention/show that no password file or database was
    created anywhere in the project folder (e.g., `ls` / `dir` before and
    after running).

---

## 8. Tech Stack

- **Python 3.9+**
- **tkinter / ttk** — GUI
- **secrets** — cryptographically secure random generation
- **string** — character pool definitions
- **pyperclip** — clipboard access
- **dataclasses / typing** — clean, typed internal data structures

No external APIs, no paid services, no network access required.
