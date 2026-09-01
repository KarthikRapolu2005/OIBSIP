"""
speech/tts.py
-------------
Text-to-speech output using pyttsx3 (fully offline, no paid API).

Every response Nova gives is spoken AND printed to the console, so the
project is easy to demonstrate in a screen recording even if system
audio is not captured.
"""

import pyttsx3
from config import TTS_RATE, TTS_VOLUME, ASSISTANT_NAME


class TextToSpeech:
    def __init__(self):
        self._engine_ok = True
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty("rate", TTS_RATE)
            self.engine.setProperty("volume", TTS_VOLUME)
        except Exception as exc:
            # If no audio backend is available (e.g. headless server),
            # fall back to text-only mode instead of crashing.
            self._engine_ok = False
            print(f"[Nova] TTS engine unavailable, falling back to text-only mode ({exc})")

    def say(self, text: str):
        """Speak text out loud (if possible) and always print it."""
        print(f"{ASSISTANT_NAME}: {text}")
        if not self._engine_ok:
            return
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as exc:
            print(f"[Nova] (speech playback failed, continuing in text mode: {exc})")
            self._engine_ok = False
