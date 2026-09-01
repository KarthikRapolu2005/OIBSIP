"""
skills/custom_commands.py -- Allows users to define their own simple
trigger-phrase -> response commands, either by editing
config/custom_commands.json directly, or by voice/text at runtime
("add a custom command"), which is then persisted to that same file.
"""

import json
import os
from config import CUSTOM_COMMANDS_PATH


class CustomCommandManager:
    def __init__(self, path: str = CUSTOM_COMMANDS_PATH):
        self.path = path
        self.commands = self._load()

    def _load(self) -> dict:
        if not os.path.exists(self.path):
            return {}
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}

    def _save(self) -> bool:
        try:
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.commands, f, indent=2, ensure_ascii=False)
            return True
        except OSError:
            return False

    def match(self, text: str):
        """Return the response for a custom trigger phrase, or None."""
        text_norm = (text or "").strip().lower()
        for trigger, response in self.commands.items():
            if trigger.lower() in text_norm:
                return response
        return None

    def add_command(self, trigger: str, response: str) -> str:
        trigger = (trigger or "").strip()
        response = (response or "").strip()
        if not trigger or not response:
            return "I need both a trigger phrase and a response to create a custom command."

        self.commands[trigger] = response
        if self._save():
            return f"Got it! From now on, when you say '{trigger}', I'll respond: '{response}'."
        return "I created the command for this session, but couldn't save it to disk."
