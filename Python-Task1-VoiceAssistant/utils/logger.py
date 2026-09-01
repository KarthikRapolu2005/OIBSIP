"""
utils/logger.py -- Minimal console logger.

PRIVACY NOTE: Nova does not write conversation transcripts, audio, or
personal data to disk anywhere in this project. This logger only
prints to the console for demo/debugging purposes and keeps nothing
persistent.
"""

from datetime import datetime


def log(event: str, detail: str = ""):
    timestamp = datetime.now().strftime("%H:%M:%S")
    if detail:
        print(f"[{timestamp}] {event}: {detail}")
    else:
        print(f"[{timestamp}] {event}")
