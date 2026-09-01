# Nova — Advanced Voice Assistant
### Oasis Infobyte Python Programming Internship — Task 1 (Advanced Tier)

Nova is a modular, offline-first desktop voice assistant built in Python. It supports full voice interaction via the microphone, with an always-available text/keyboard fallback so it can be demoed anywhere — even without a microphone, speakers, or internet access.

---

## 1. Feature Checklist (maps to the Oasis Infobyte task)

**Beginner features**
| # | Requirement | Implementation |
|---|---|---|
| 1 | Capture voice input | `speech/stt.py` via `speech_recognition` + microphone |
| 2 | Respond to "Hello" | `skills/greeting.py` |
| 3 | Tell time & date | `skills/datetime_skill.py` |
| 4 | Web search (opens browser) | `skills/web_search.py` via `webbrowser` |
| 5 | Handle unrecognized speech | `speech/stt.py` returns `""`, Nova asks the user to repeat |
| 6 | Text-to-speech for all responses | `speech/tts.py` via `pyttsx3` |

**Advanced features**
| # | Requirement | Implementation |
|---|---|---|
| 7 | NLU / free-form intent parsing | `nlu/intent_parser.py` — regex-pattern intent + entity extraction |
| 8 | Send email via voice (smtplib) | `skills/email_skill.py` — env-var credentials, safe simulated mode |
| 9 | Timed reminder with audible alert | `skills/reminder.py` via `threading.Timer` |
| 10 | Live weather (OpenWeatherMap) | `skills/weather.py` via `requests` |
| 11 | General knowledge Q&A | `skills/knowledge.py` — local KB + free Wikipedia REST API fallback |
| 12 | Custom commands (config or voice) | `skills/custom_commands.py` + `config/custom_commands.json` |
| 13 | Privacy documentation | See [Section 7](#7-privacy--data-handling) below |

---

## 2. Project Structure

```
nova_assistant/
├── main.py                        # Entry point: dialog loop + intent dispatch
├── config.py                      # Loads all settings/secrets from .env
├── requirements.txt
├── .env.example                   # Template for secrets (copy to .env)
├── .gitignore
├── README.md
│
├── speech/
│   ├── tts.py                     # Text-to-speech (pyttsx3)
│   └── stt.py                     # Speech-to-text + keyboard fallback
│
├── nlu/
│   └── intent_parser.py           # Rule-based NLU: intents + entities
│
├── skills/
│   ├── greeting.py
│   ├── datetime_skill.py
│   ├── web_search.py
│   ├── weather.py
│   ├── email_skill.py
│   ├── reminder.py
│   ├── knowledge.py
│   └── custom_commands.py
│
├── utils/
│   └── logger.py                  # Console-only logger (no persistence)
│
└── config/
    ├── custom_commands.json       # User-editable trigger -> response map
    └── knowledge_base.json        # Local offline knowledge base
```

---

## 3. Installation

```bash
# 1. Clone / unzip the project, then move into it
cd nova_assistant

# 2. Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

**Notes on `PyAudio`** (needed for microphone access):
- **Windows:** `pip install pyaudio` usually works directly.
- **macOS:** `brew install portaudio` then `pip install pyaudio`.
- **Linux (Debian/Ubuntu):** `sudo apt-get install python3-pyaudio portaudio19-dev` then `pip install pyaudio`.
- If PyAudio fails to install, Nova still runs perfectly in **text mode** — no feature is lost for demo purposes.

**Notes on `pyttsx3`** (offline text-to-speech):
- **Linux:** requires `espeak` or `espeak-ng`: `sudo apt-get install espeak`.
- **Windows/macOS:** works out of the box using the built-in OS voices.
- If no TTS engine is found, Nova automatically falls back to **text-only output** (still prints every response) instead of crashing.

---

## 4. API / Credential Configuration

Copy the template and fill in your own values:

```bash
cp .env.example .env
```

| Variable | Required for | How to get it |
|---|---|---|
| `OPENWEATHER_API_KEY` | Live weather | Free key at https://openweathermap.org/api (free tier, no payment) |
| `SMTP_EMAIL` / `SMTP_PASSWORD` | Sending real email | Use a **dedicated test email account**. For Gmail, enable 2FA and generate an **App Password** — never use your real account password. |

If either is left blank, the corresponding feature **degrades gracefully**:
- No weather key → Nova explains it can't fetch live weather and tells you which variable to set.
- No email credentials → Nova runs in **SIMULATED MODE**, printing/speaking the composed email instead of sending it.

`.env` is listed in `.gitignore` and is **never** committed. No credentials are hardcoded anywhere in the source code.

---

## 5. Running the Assistant

```bash
python main.py
```

You'll be prompted to choose a mode:

```
1. Voice mode (microphone)
2. Text mode (keyboard fallback)
```

- Choose **1** to speak commands aloud (requires a working microphone + PyAudio).
- Choose **2** (default) to type commands — ideal for reliable demos/screen recordings.
- If voice mode is selected but no microphone is detected, Nova automatically continues in text mode with a clear message.

---

## 6. Example Commands

Because Nova uses NLU pattern matching (not exact keyword matching), many phrasings work:

| Feature | Example phrases |
|---|---|
| Greeting | "hello", "hey Nova", "good morning" |
| Time / Date | "what time is it", "what's today's date" |
| Web search | "search for the eiffel tower", "google python tutorials" |
| Weather | "what's the weather in Tokyo", "how's the weather" |
| Email | "send an email" *(Nova will then ask for recipient, subject, and body)* |
| Reminder | "remind me to drink water in 5 minutes", "set a timer for 10 minutes" |
| Knowledge | "who is Alan Turing", "what is machine learning", "define IoT" |
| Custom command | "add a custom command" *(Nova will ask for the trigger phrase and response)* |
| Help | "help", "what can you do" |
| Exit | "exit", "quit", "goodbye" |

Custom commands can also be added directly by editing `config/custom_commands.json`:
```json
{
  "trigger phrase": "the response Nova should say"
}
```

---

## 7. Privacy & Data Handling

Nova is designed to minimize data collection:

- **Microphone audio:** When voice mode is used, short audio clips are captured locally and sent to Google's public Speech-to-Text web API (via the `speech_recognition` library) solely to transcribe them into text. **Nova does not record, store, or log raw audio to disk at any point.** Transcribed text is processed in-memory only, for the current session.
- **Console logging:** `utils/logger.py` prints intent names and timestamps to the console for demo/debugging purposes only. Nothing is written to a log file.
- **Email:** Email is only ever sent when the user explicitly issues a "send an email" command and confirms recipient/subject/body. Nova never sends email automatically, silently, or in the background. Email content is only transmitted (via SMTP over TLS) when real credentials are configured — otherwise it runs in simulated mode and nothing leaves the machine.
- **Weather queries:** Only the city name you provide is sent to the OpenWeatherMap API — no other personal data is transmitted.
- **Knowledge queries:** Questions not found in the local, offline knowledge base are sent as search terms to Wikipedia's public REST API. No personal identifiers are attached to these requests.
- **Credentials:** API keys and email passwords are read exclusively from environment variables via `.env` (excluded from version control by `.gitignore`) and are never hardcoded or logged.
- **Custom commands / knowledge base files** are plain local JSON files stored in `config/` and never transmitted anywhere.

**Limitation to be aware of:** Speech recognition here relies on a third-party (Google) web service for transcription accuracy, which means brief audio snippets do leave your machine during voice-mode use. If full offline privacy is required, an offline recognizer (e.g., `vosk`) could be substituted into `speech/stt.py` in place of `recognize_google`.

---

## 8. Demo / Test Checklist

Use this checklist while screen-recording to show every required feature:

- [ ] **Startup** — run `python main.py`, choose text or voice mode
- [ ] **Greeting** — say/type "hello" → Nova responds with a greeting
- [ ] **Time** — "what time is it" → current time is spoken/printed
- [ ] **Date** — "what's the date" → current date is spoken/printed
- [ ] **Web search** — "search for oasis infobyte" → browser opens (or link is shown)
- [ ] **Unrecognized speech** — mumble something / stay silent in voice mode → Nova asks you to repeat
- [ ] **Weather** — "what's the weather in London" → live data (if `OPENWEATHER_API_KEY` set) or a graceful "not configured" message
- [ ] **Reminder** — "remind me to stretch in 1 minute" → wait → audible alert + spoken message fires
- [ ] **Knowledge** — "who is Isaac Newton" → answer from local KB or Wikipedia fallback
- [ ] **Custom command** — "add a custom command" → provide trigger + response → say the trigger phrase → Nova replies with your custom response
- [ ] **Email (no credentials)** — "send an email" → fill recipient/subject/body → Nova shows **SIMULATED MODE** output
- [ ] **Email (with test credentials)** — repeat with `.env` configured → Nova confirms real send via a test account
- [ ] **Exit** — "exit" or "quit" → Nova says goodbye and shuts down cleanly

---

## 9. Design Notes

- **Graceful degradation everywhere:** every external dependency (microphone, TTS engine, weather API, email server, Wikipedia) is wrapped in exception handling with a clear fallback message — the app never crashes from an unavailable service.
- **Modular architecture:** each capability is an isolated module under `skills/`, making it easy to add new skills without touching unrelated code.
- **No paid APIs:** OpenWeatherMap's free tier, Google's free web speech recognition, and Wikipedia's free public REST API are the only external services used.
