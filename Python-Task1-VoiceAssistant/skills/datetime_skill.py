"""skills/datetime_skill.py -- Tells the current time and date."""

from datetime import datetime


def get_time() -> str:
    now = datetime.now().strftime("%I:%M %p")
    return f"The current time is {now}."


def get_date() -> str:
    today = datetime.now().strftime("%A, %B %d, %Y")
    return f"Today's date is {today}."
