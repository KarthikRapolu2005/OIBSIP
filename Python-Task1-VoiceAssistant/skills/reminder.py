"""
skills/reminder.py -- Sets a timed reminder that fires an audible alert
(via the TTS engine, plus a console bell) after a specified duration,
using threading.Timer so the assistant stays responsive while waiting.
"""

import threading


class ReminderManager:
    def __init__(self, tts):
        self.tts = tts
        self._active_timers = []

    def set_reminder(self, task: str, minutes: float) -> str:
        try:
            minutes = float(minutes)
        except (TypeError, ValueError):
            return "I need a valid number of minutes for the reminder."

        if minutes <= 0:
            return "The reminder time must be greater than zero minutes."

        task = (task or "your reminder").strip()
        seconds = minutes * 60

        timer = threading.Timer(seconds, self._trigger, args=(task,))
        timer.daemon = True  # don't block program exit
        timer.start()
        self._active_timers.append(timer)

        return f"Okay, I'll remind you to {task} in {minutes:g} minute(s)."

    def _trigger(self, task: str):
        alert_text = f"Reminder alert! Time to {task}."
        print("\a")  # console bell -- audible alert even without TTS audio
        try:
            self.tts.say(alert_text)
        except Exception as exc:
            print(f"[Nova] Reminder fired but TTS failed: {exc}. {alert_text}")

    def cancel_all(self):
        for timer in self._active_timers:
            timer.cancel()
        self._active_timers = []
