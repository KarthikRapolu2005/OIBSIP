"""skills/greeting.py -- Responds to greetings like 'hello', 'hi', 'hey'."""

import random
from config import ASSISTANT_NAME

_RESPONSES = [
    f"Hello! I'm {ASSISTANT_NAME}, your voice assistant. How can I help you today?",
    f"Hi there! {ASSISTANT_NAME} here, ready to help.",
    "Hey! What can I do for you?",
]


def handle_greeting() -> str:
    return random.choice(_RESPONSES)
