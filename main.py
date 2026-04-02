"""
main.py – Entry point for Flappy Bird.

Run with:
    python main.py
"""
from __future__ import annotations

import sys
import pygame


def main() -> None:
    """Initialise pygame subsystems and hand control to the Game object."""
    # ── pygame init ───────────────────────────────────────────────────────────
    pygame.init()

    try:
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    except pygame.error as exc:
        # Mixer failure is non-fatal; the game runs silently.
        print(f"[audio] Mixer init failed – running without sound: {exc}")

    # ── import after init so surfaces can be created inside AssetManager ──────
    from game import Game

    game = Game()
    game.run()

    # run() only returns on quit, but be tidy anyway.
    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
