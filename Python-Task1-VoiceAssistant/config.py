"""
config.py
---------
Central configuration loader for Nova.

All secrets (API keys, email credentials) are read from environment
variables via python-dotenv. NOTHING is hardcoded here. If a value is
missing, the relevant skill degrades gracefully instead of crashing.
"""

import os
from dotenv import load_dotenv

# Load variables from a local .env file (if present) into os.environ
load_dotenv()

# --- Weather (OpenWeatherMap-compatible) ---
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "").strip()
OPENWEATHER_BASE_URL = os.getenv(
    "OPENWEATHER_BASE_URL", "https://api.openweathermap.org/data/2.5/weather"
)
DEFAULT_CITY = os.getenv("DEFAULT_CITY", "London")

# --- Email (SMTP) ---
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com").strip()
SMTP_PORT = int(os.getenv("SMTP_PORT", "587") or 587)
SMTP_EMAIL = os.getenv("SMTP_EMAIL", "").strip()
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "").strip()

# --- Assistant behaviour ---
ASSISTANT_NAME = os.getenv("ASSISTANT_NAME", "Nova")
TTS_RATE = int(os.getenv("TTS_RATE", "175") or 175)
TTS_VOLUME = float(os.getenv("TTS_VOLUME", "1.0") or 1.0)

# --- Paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CUSTOM_COMMANDS_PATH = os.path.join(BASE_DIR, "config", "custom_commands.json")
KNOWLEDGE_BASE_PATH = os.path.join(BASE_DIR, "config", "knowledge_base.json")


def email_configured() -> bool:
    """Return True only if both email address and password are set."""
    return bool(SMTP_EMAIL and SMTP_PASSWORD)


def weather_configured() -> bool:
    """Return True only if a weather API key is set."""
    return bool(OPENWEATHER_API_KEY)
