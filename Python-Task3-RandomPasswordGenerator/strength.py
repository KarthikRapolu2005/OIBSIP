"""
strength.py
-----------
Password strength evaluation for SecurePass.

The score is computed from two factors, as required by the task spec:
    1. Length of the password.
    2. Diversity of character types used (upper / lower / digits / symbols).

This module does NOT use any external libraries and never persists the
password or the score anywhere.
"""

from __future__ import annotations

import string
from dataclasses import dataclass


SYMBOLS_HINT = set("!@#$%^&*()-_=+[]{};:,.<>/?~")


@dataclass(frozen=True)
class StrengthResult:
    label: str          # "Weak" | "Medium" | "Strong"
    score: int          # 0-6 raw score, useful for progress-bar style UI
    max_score: int       # maximum possible score (for normalizing a progress bar)
    color: str           # hex color suggestion for the GUI


def _character_diversity(password: str) -> int:
    """Returns how many of the 4 character classes are present (0-4)."""
    diversity = 0
    if any(ch in string.ascii_uppercase for ch in password):
        diversity += 1
    if any(ch in string.ascii_lowercase for ch in password):
        diversity += 1
    if any(ch in string.digits for ch in password):
        diversity += 1
    if any(ch in SYMBOLS_HINT for ch in password):
        diversity += 1
    return diversity


def evaluate_strength(password: str) -> StrengthResult:
    """
    Computes a Weak / Medium / Strong rating for `password`.

    Scoring model (max_score = 6):
        Length contribution (0-3 points):
            len < 8   -> 0
            8 <= len < 12  -> 1
            12 <= len < 16 -> 2
            len >= 16 -> 3
        Diversity contribution (0-3 points, scaled from 0-4 classes):
            1 class  -> 0
            2 classes -> 1
            3 classes -> 2
            4 classes -> 3

    Final label:
        score <= 2 -> Weak
        3 <= score <= 4 -> Medium
        score >= 5 -> Strong
    """
    if not password:
        return StrengthResult(label="Weak", score=0, max_score=6, color="#e74c3c")

    length = len(password)
    if length < 8:
        length_points = 0
    elif length < 12:
        length_points = 1
    elif length < 16:
        length_points = 2
    else:
        length_points = 3

    diversity = _character_diversity(password)
    if diversity <= 1:
        diversity_points = 0
    elif diversity == 2:
        diversity_points = 1
    elif diversity == 3:
        diversity_points = 2
    else:
        diversity_points = 3

    score = length_points + diversity_points

    if score <= 2:
        label, color = "Weak", "#e74c3c"       # red
    elif score <= 4:
        label, color = "Medium", "#f39c12"     # amber
    else:
        label, color = "Strong", "#27ae60"     # green

    return StrengthResult(label=label, score=score, max_score=6, color=color)
