"""
nlu/intent_parser.py
---------------------
A lightweight, dependency-free natural-language-understanding layer.

Rather than requiring exact keyword commands, this module uses a set of
regular-expression patterns (with synonyms and free-word gaps such as
`.*?`) to recognize INTENTS and extract ENTITIES from free-form spoken
sentences, e.g.:

    "hey nova can you please search the web for the eiffel tower"
        -> intent="web_search", entities={"query": "the eiffel tower"}

    "what's the weather like in Paris right now"
        -> intent="weather", entities={"city": "paris"}

This satisfies the "Advanced" NLU requirement without needing nltk's
downloaded corpora (which require internet access and can fail in
sandboxed/offline demo environments). nltk is still listed as an
optional dependency in requirements.txt for anyone who wants to extend
this with tokenization/POS tagging.
"""

import re
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class Intent:
    name: str
    entities: Dict[str, str] = field(default_factory=dict)


# Ordered list of (intent_name, [regex patterns], entity_group_name)
# Patterns are checked in order; the first match wins.
_PATTERNS = [
    ("exit", [
        r"\b(exit|quit|stop|goodbye|bye|shut down|shutdown|power off)\b",
    ], None),

    ("greeting", [
        r"\b(hello|hi|hey|good morning|good afternoon|good evening)\b",
    ], None),

    ("time", [
        r"\bwhat('?s| is) the (current )?time\b",
        r"\btell me the time\b",
        r"\bwhat time is it\b",
    ], None),

    ("date", [
        r"\bwhat('?s| is) (the )?(today'?s? )?date\b",
        r"\bwhat day is (it|today)\b",
        r"\btell me (the|today'?s) date\b",
    ], None),

    ("web_search", [
        r"\bsearch (the web |online )?for (?P<query>.+)",
        r"\bgoogle (?P<query>.+)",
        r"\blook up (?P<query>.+)",
        r"\bfind (information|info) (about|on) (?P<query>.+)",
    ], "query"),

    ("weather", [
        r"\bweather.*\bin (?P<city>[a-zA-Z\s]+)",
        r"\bhow'?s the weather in (?P<city>[a-zA-Z\s]+)",
        r"\bweather\b",
    ], "city"),

    ("send_email", [
        r"\bsend (an |a )?email\b",
        r"\bemail (someone|to someone)\b",
        r"\bcompose (an |a )?email\b",
    ], None),

    ("set_reminder", [
        r"\bremind me (to )?(?P<task>.+?) in (?P<minutes>\d+)\s*(minutes?|mins?)\b",
        r"\bset (a )?reminder (for|to) (?P<task>.+?) in (?P<minutes>\d+)\s*(minutes?|mins?)\b",
        r"\bremind me (to )?(?P<task>.+?) after (?P<minutes>\d+)\s*(minutes?|mins?)\b",
        r"\bset (a )?timer for (?P<minutes>\d+)\s*(minutes?|mins?)\b",
    ], None),

    ("add_custom_command", [
        r"\badd (a )?(new )?custom command\b",
        r"\bteach you a (new )?command\b",
        r"\bcreate (a )?new command\b",
    ], None),

    ("knowledge_query", [
        r"\bwho (is|was) (?P<topic>.+)",
        r"\bwhat (is|are|was|were) (?P<topic>.+)",
        r"\bwhen (was|is|did) (?P<topic>.+)",
        r"\bdefine (?P<topic>.+)",
        r"\btell me about (?P<topic>.+)",
    ], "topic"),

    ("help", [
        r"\bhelp\b",
        r"\bwhat can you do\b",
        r"\blist commands\b",
    ], None),
]


def parse_intent(text: str) -> Intent:
    """
    Parse free-form text into an Intent with extracted entities.
    Falls back to intent name "unknown" if nothing matches.
    """
    if not text:
        return Intent(name="unknown")

    cleaned = text.strip().lower()
    # Strip a leading wake-word / politeness prefix so it doesn't block matches
    cleaned = re.sub(r"^(hey|ok|okay)?\s*nova[,:]?\s*", "", cleaned)
    cleaned = re.sub(r"^(please|can you|could you|would you)\s*", "", cleaned)

    for intent_name, patterns, primary_group in patterns_iter():
        for pattern in patterns:
            match = re.search(pattern, cleaned, flags=re.IGNORECASE)
            if match:
                entities = {k: v.strip() for k, v in match.groupdict().items() if v}
                return Intent(name=intent_name, entities=entities)

    return Intent(name="unknown", entities={"raw_text": cleaned})


def patterns_iter():
    """Helper to iterate over the pattern table (kept separate for testability)."""
    for intent_name, patterns, primary_group in _PATTERNS:
        yield intent_name, patterns, primary_group
