"""
skills/knowledge.py -- Answers general knowledge questions.

Strategy:
1. Check a local JSON knowledge base first (fast, offline, no API key,
   no privacy concerns -- see config/knowledge_base.json).
2. If not found locally, fall back to Wikipedia's free public REST API
   (no API key required, no paid tier) for a short summary.
3. If both fail (e.g. no internet), respond gracefully instead of
   crashing.
"""

import json
import os
import requests

from config import KNOWLEDGE_BASE_PATH


def _load_local_kb() -> dict:
    if not os.path.exists(KNOWLEDGE_BASE_PATH):
        return {}
    try:
        with open(KNOWLEDGE_BASE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _search_local_kb(topic: str, kb: dict) -> str:
    topic_norm = topic.strip().lower().rstrip("?.! ")
    for key, answer in kb.items():
        if key.lower() == topic_norm or key.lower() in topic_norm:
            return answer
    return None


def _search_wikipedia(topic: str) -> str:
    topic_clean = topic.strip().rstrip("?.! ")
    if not topic_clean:
        return None
    url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + requests.utils.quote(topic_clean)
    try:
        response = requests.get(url, timeout=8, headers={"User-Agent": "NovaVoiceAssistant/1.0"})
    except requests.exceptions.RequestException:
        return None

    if response.status_code != 200:
        return None

    try:
        data = response.json()
        extract = data.get("extract")
        return extract
    except ValueError:
        return None


def answer_question(topic: str) -> str:
    topic = (topic or "").strip()
    if not topic:
        return "What would you like to know about?"

    kb = _load_local_kb()
    local_answer = _search_local_kb(topic, kb)
    if local_answer:
        return local_answer

    wiki_answer = _search_wikipedia(topic)
    if wiki_answer:
        return wiki_answer

    return (
        f"I couldn't find a reliable answer about '{topic}' right now. "
        "This could be because I'm offline or the topic isn't in my knowledge base. "
        "You can also try a web search instead."
    )
