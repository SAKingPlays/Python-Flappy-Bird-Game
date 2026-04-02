"""
highscore.py – Persistent high-score storage backed by a local JSON file.

The module exposes two simple functions so the rest of the codebase never
has to think about file I/O or error handling around score data.
"""
from __future__ import annotations

import json
import os
from settings import HIGHSCORE_FILE


def load_high_score() -> int:
    """
    Read the saved high score from disk.

    Returns 0 if the file doesn't exist or is corrupt.
    """
    try:
        with open(HIGHSCORE_FILE, "r", encoding="utf-8") as fh:
            data = json.load(fh)
            return int(data.get("high_score", 0))
    except (FileNotFoundError, json.JSONDecodeError, ValueError, TypeError):
        return 0


def save_high_score(score: int) -> None:
    """
    Persist *score* to disk only when it beats the current saved record.

    Creates the data directory automatically if it does not exist.
    """
    current = load_high_score()
    if score <= current:
        return

    try:
        os.makedirs(os.path.dirname(HIGHSCORE_FILE), exist_ok=True)
        with open(HIGHSCORE_FILE, "w", encoding="utf-8") as fh:
            json.dump({"high_score": score}, fh)
    except OSError as exc:
        # Non-fatal – the game continues without persistence.
        print(f"[highscore] Could not save score: {exc}")
