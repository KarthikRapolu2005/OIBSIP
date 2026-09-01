# 🩺 BMI Tracker

A polished desktop **BMI (Body Mass Index) Calculator** built with Python and Tkinter, created for the **Oasis Infobyte Python Programming Internship — Task 2 (Advanced Tier)**.

BMI Tracker goes beyond a simple calculator: it supports multiple named users, stores historical BMI records in a local SQLite database, and visualizes each user's BMI trend over time with an embedded Matplotlib chart.

---

## 1. Project Overview

BMI Tracker is a single-window desktop application where a user:
1. Enters their name, weight (kg), and height (m).
2. Clicks **Calculate BMI**.
3. Instantly sees their BMI value and health category, colour-coded for quick reading.
4. Has every calculation automatically saved to a local SQLite database under their username.
5. Can view their full calculation history in a table.
6. Can view a Matplotlib line chart of their BMI trend over time.

The app is fully self-contained — no internet connection, accounts, or passwords required.

---

## 2. Features

- Clean, modern Tkinter GUI (no command line required).
- Real-time BMI calculation using the standard formula.
- Four-category classification: Underweight, Normal, Overweight, Obese.
- Colour-coded result and category display.
- Multi-user support — any number of named users, each with their own history.
- Persistent SQLite storage that survives app restarts.
- Scrollable history table per user (date, weight, height, BMI, category).
- "View Trend" button opens a Matplotlib chart of BMI over time, with colour-coded reference bands for each category.
- Full input validation with clear, friendly error messages.
- Graceful handling of database read/write failures — the app never crashes.
- Clear/Reset button to start a fresh entry.
- Status bar showing the outcome of the last action.

---

## 3. Oasis Requirements Checklist

| # | Requirement | Status | Where it's implemented |
|---|---|---|---|
| 1 | Prompt for weight (kg) and height (m) | ✅ | `gui.py` — Weight/Height entry fields |
| 2 | Calculate BMI = weight / height² | ✅ | `bmi_logic.py` → `calculate_bmi()` |
| 3 | Classify into Underweight/Normal/Overweight/Obese | ✅ | `bmi_logic.py` → `classify_bmi()` |
| 4 | Display BMI (2 decimals) and category | ✅ | `gui.py` — large result label + category label |
| 5 | Validate non-numeric/zero/negative/invalid input | ✅ | `bmi_logic.py` → `validate_weight()`, `validate_height()`, `validate_username()` |
| 6 | GUI application using tkinter (no CLI needed) | ✅ | `main.py`, `gui.py` |
| 7 | Input fields with clear labels | ✅ | `gui.py` — labeled Username/Weight/Height fields |
| 8 | Calculate button | ✅ | `gui.py` — "Calculate BMI" button |
| 9 | Result displayed inside the GUI | ✅ | `gui.py` — result frame |
| 10 | Colour-coded category feedback | ✅ | `bmi_logic.py` → `CATEGORY_COLOURS`; applied in `gui.py` |
| 11 | Multi-user support (save records per named user) | ✅ | `database.py` — `username` column; `gui.py` username field |
| 12 | Historical BMI records stored in SQLite | ✅ | `database.py` — `bmi_records` table |
| 13 | Graph view of BMI trend using matplotlib | ✅ | `charts.py` → `TrendChartWindow` |
| 14 | Handle SQLite/DB read/write failures gracefully | ✅ | `database.py` (`DatabaseError`) + try/except in `gui.py` |

Every Beginner and Advanced requirement from the Oasis Infobyte brief is fully implemented — nothing is stubbed or simulated.

---

## 4. Technologies Used

- **Python 3.9+**
- **tkinter** / **ttk** — GUI framework (standard library)
- **sqlite3** — local database (standard library)
- **matplotlib** — trend chart, embedded via `FigureCanvasTkAgg`

No external frameworks, servers, or APIs are used.

---

## 5. Project Structure

```
bmi_calculator/
├── main.py                # Application entry point
├── database.py             # SQLite persistence layer
├── bmi_logic.py             # BMI calculation, classification, validation
├── gui.py                  # Tkinter GUI (main application window)
├── charts.py                # Matplotlib trend chart window
├── requirements.txt
├── README.md
├── .gitignore
└── data/
    └── .gitkeep            # Keeps the data/ folder in git; bmi_tracker.db is created here at runtime
```

The database file (`data/bmi_tracker.db`) is created automatically on first run using a path relative to the project files (`os.path.dirname(os.path.abspath(__file__))`), so it works no matter where the project folder is placed or run from.

---

## 6. Installation Instructions

1. Make sure Python 3.9 or newer is installed:
   ```bash
   python --version
   ```
2. (Recommended) Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

---

## 7. Installing Requirements

From inside the `bmi_calculator/` folder:

```bash
pip install -r requirements.txt
```

> Note: `tkinter` and `sqlite3` ship with standard Python installations and are not listed in `requirements.txt`. On some Linux distributions you may need to install tkinter separately, e.g. `sudo apt-get install python3-tk`.

---

## 8. How to Run

From inside the `bmi_calculator/` folder:

```bash
python main.py
```

The application window will open, and `data/bmi_tracker.db` will be created automatically on first launch.

---

## 9. How to Use the Application

1. **Enter a username** in the "Username" field (e.g. `avi`).
2. **Enter weight** in kilograms and **height** in meters.
3. Click **Calculate BMI**.
4. The BMI value and category appear instantly, colour-coded:
   - 🔵 Blue = Underweight
   - 🟢 Green = Normal
   - 🟠 Amber = Overweight
   - 🔴 Red = Obese
5. The record is automatically saved and appears in the **History** table on the right.
6. Change the weight/height and click **Calculate BMI** again to add more records for the same user.
7. Click **View Trend** to open a chart of that user's BMI over time.
8. Type a different username to switch users — their own saved history loads automatically.
9. Click **Clear / Reset** to clear the form and start over.

---

## 10. Database Explanation

BMI Tracker uses a local SQLite database file at `data/bmi_tracker.db`, created automatically the first time the app runs. It contains a single table:

```sql
CREATE TABLE bmi_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    weight REAL NOT NULL,
    height REAL NOT NULL,
    bmi REAL NOT NULL,
    category TEXT NOT NULL,
    timestamp TEXT NOT NULL
);
```

- Each row represents one BMI calculation for one user.
- Multiple users are supported simply by storing different `username` values — there are no accounts or passwords.
- All reads/writes go through `database.py`, which wraps every SQLite call in `try/except` and raises a friendly `DatabaseError` that the GUI catches and displays without crashing.

---

## 11. BMI Calculation Formula

```
BMI = weight (kg) / (height (m) × height (m))
```

Classification used:

| BMI Range | Category |
|---|---|
| < 18.5 | Underweight |
| 18.5 – 24.9 | Normal |
| 25 – 29.9 | Overweight |
| ≥ 30 | Obese |

---

## 12. Testing Checklist

Manually verified scenarios:

- [x] Valid normal BMI (e.g. 70 kg, 1.75 m → ~22.86, Normal)
- [x] Underweight result (e.g. 45 kg, 1.75 m → ~14.69, Underweight)
- [x] Overweight result (e.g. 85 kg, 1.75 m → ~27.76, Overweight)
- [x] Obese result (e.g. 100 kg, 1.70 m → ~34.60, Obese)
- [x] Invalid text input in weight/height fields (e.g. "abc") → friendly error, no crash
- [x] Zero weight → rejected with clear message
- [x] Negative weight → rejected with clear message
- [x] Zero height → rejected with clear message (also avoids divide-by-zero)
- [x] Empty username → rejected with clear message
- [x] Multiple users → each has an independent history
- [x] Saving records → confirmed persisted across app restarts
- [x] Retrieving history → correct records shown when switching usernames
- [x] Graph generation → trend chart renders correctly with 2+ records
- [x] Graph with < 2 records → shows a friendly "not enough history" message instead of crashing
- [x] Database failure handling → simulated by making `data/` read-only; app shows an error dialog/status message but continues running instead of crashing

---

## 13. Demo Video Instructions

Suggested 2–3 minute demo script:

1. Launch the application: `python main.py`.
2. Enter username `demo_user`.
3. Enter weight `70` and height `1.75`, click **Calculate BMI** — show the Normal (green) result.
4. Enter weight `95` and height `1.70`, click **Calculate BMI** again — show the Obese (red) result and note both records now appear in History.
5. Click **View Trend** — show the Matplotlib chart with both points plotted.
6. Change the username to `another_user`, enter new values, calculate — show that history is independent per user.
7. Switch back to `demo_user` — show their history reloads correctly.
8. Optionally, enter invalid input (e.g. weight = `-5` or `abc`) to demonstrate validation and graceful error handling.
9. Click **Clear / Reset** to reset the form.

---

## 14. Limitations / Disclaimer

BMI Tracker is an **educational programming project** built for the Oasis Infobyte internship. It is **not medical advice** and should not be used for real health or clinical decisions. BMI itself is a simple screening metric — it does not account for muscle mass, body composition, age, sex, or other individual health factors. Please consult a qualified healthcare professional for any health-related concerns.
