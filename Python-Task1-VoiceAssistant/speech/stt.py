"""
speech/stt.py
-------------
Speech-to-text input using the `speech_recognition` library and the
default system microphone, with Google's free web speech API used only
as a recognition backend (no key required for limited/demo use).

If the microphone or recognizer is unavailable for any reason (no mic,
no internet, PyAudio not installed, etc.) this module fails gracefully
and the caller should fall back to keyboard input via `text_input()`.

PRIVACY NOTE: Audio captured here is streamed to Google's public speech
recognition endpoint for transcription and is NOT stored locally by
this application. See README.md for full privacy details.
"""

import speech_recognition as sr


class SpeechToText:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone_available = self._check_microphone()

    def _check_microphone(self) -> bool:
        try:
            sr.Microphone()
            return True
        except Exception:
            return False

    def listen(self, timeout: int = 5, phrase_time_limit: int = 8):
        """
        Listen on the microphone and return recognized text, or None if
        speech could not be captured/understood. Never raises.
        """
        if not self.microphone_available:
            return None

        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                print("[Nova] Listening...")
                audio = self.recognizer.listen(
                    source, timeout=timeout, phrase_time_limit=phrase_time_limit
                )
        except sr.WaitTimeoutError:
            print("[Nova] No speech detected within timeout.")
            return None
        except Exception as exc:
            print(f"[Nova] Microphone error: {exc}")
            return None

        try:
            text = self.recognizer.recognize_google(audio)
            print(f"[You said]: {text}")
            return text
        except sr.UnknownValueError:
            # Speech was captured but could not be understood
            return ""
        except sr.RequestError as exc:
            print(f"[Nova] Speech recognition service unavailable: {exc}")
            return None
        except Exception as exc:
            print(f"[Nova] Unexpected recognition error: {exc}")
            return None


def text_input(prompt: str = "You (type here): ") -> str:
    """Keyboard fallback so the assistant can be demoed without a mic."""
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        return "exit"
