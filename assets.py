"""
assets.py – Procedural asset generation and caching.

All pygame surfaces and fonts are generated here so the game works
out-of-the-box with zero external image or sound files.  If you later
add real PNG / WAV assets, swap the generation functions for load calls.

Usage
-----
    from assets import AssetManager
    assets = AssetManager()          # call after pygame.init()
"""
from __future__ import annotations

import math
from typing import Optional

import pygame

import settings as S


# ─── helpers ─────────────────────────────────────────────────────────────────

def _blend(a: tuple, b: tuple, t: float) -> tuple:
    """Linear-interpolate two RGB tuples."""
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


# ─── bird frame generation ────────────────────────────────────────────────────

def _draw_bird_frame(frame: int) -> pygame.Surface:
    """
    Generate one wing-animation frame for the bird sprite.

    frame 0 – wing raised
    frame 1 – wing level
    frame 2 – wing lowered
    """
    SIZE = 52
    cx, cy = SIZE // 2, SIZE // 2 + 2
    surf = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)

    # ── body ──────────────────────────────────────────────────────────────────
    # Outer body
    pygame.draw.circle(surf, S.BIRD_GOLD,   (cx,     cy),     17)
    pygame.draw.circle(surf, S.BIRD_YELLOW, (cx - 1, cy - 1), 15)

    # Belly highlight
    belly = pygame.Surface((18, 11), pygame.SRCALPHA)
    pygame.draw.ellipse(belly, (255, 245, 160, 200), (0, 0, 18, 11))
    surf.blit(belly, (cx - 9, cy + 2))

    # ── wing ─────────────────────────────────────────────────────────────────
    wing_positions = [
        # frame 0 – up
        [(-3, -4), (-10, -16), (-20, -12), (-16, -2)],
        # frame 1 – mid
        [(-2,  2), (-10,  -5), (-22,  -1), (-14,  6)],
        # frame 2 – down
        [(-2,  5), ( -8,  14), (-18,  11), (-13,  2)],
    ]
    pts = [(cx + dx, cy + dy) for dx, dy in wing_positions[frame]]
    pygame.draw.polygon(surf, S.BIRD_ORANGE, pts)
    # wing highlight
    hi_pts = [pts[0], (pts[1][0]+3, pts[1][1]+3), (pts[2][0]+3, pts[2][1]+2)]
    pygame.draw.polygon(surf, (255, 190, 60), hi_pts)

    # ── beak ──────────────────────────────────────────────────────────────────
    beak = [(cx+14, cy-2), (cx+23, cy-1), (cx+14, cy+5)]
    pygame.draw.polygon(surf, S.BIRD_ORANGE, beak)
    pygame.draw.polygon(surf, (200, 110, 0), [(cx+14, cy+1), (cx+23, cy-1), (cx+14, cy+5)])

    # ── eye ───────────────────────────────────────────────────────────────────
    pygame.draw.circle(surf, S.BIRD_WHITE, (cx + 7, cy - 6), 5)
    pygame.draw.circle(surf, S.BIRD_DARK,  (cx + 8, cy - 6), 3)
    pygame.draw.circle(surf, S.BIRD_WHITE, (cx + 9, cy - 8), 1)  # specular

    return surf


# ─── pipe surface ─────────────────────────────────────────────────────────────

def _make_pipe_body(width: int, height: int) -> pygame.Surface:
    """Render a single pipe body (no cap) of the given dimensions."""
    surf = pygame.Surface((width, height))
    # Base fill
    surf.fill(S.PIPE_BODY)
    # Left shadow stripe
    pygame.draw.rect(surf, S.PIPE_DARK, (0, 0, 8, height))
    # Right highlight stripe
    pygame.draw.rect(surf, S.PIPE_LIGHT, (width - 8, 0, 8, height))
    # Horizontal ribbing every 20 px
    for y in range(0, height, 20):
        pygame.draw.line(surf, S.PIPE_DARK, (8, y), (width - 8, y), 1)
    return surf


def _make_pipe_cap(width: int) -> pygame.Surface:
    """Render the rounded end-cap that sits at the mouth of a pipe."""
    cap_h = 26
    surf = pygame.Surface((width + 12, cap_h))
    surf.fill(S.PIPE_CAP)
    pygame.draw.rect(surf, S.PIPE_DARK,  (0, 0, 10, cap_h))
    pygame.draw.rect(surf, S.PIPE_LIGHT, (width + 2, 0, 10, cap_h))
    pygame.draw.line(surf, S.PIPE_DARK,  (10, 0), (width + 2, 0), 2)
    pygame.draw.line(surf, S.PIPE_LIGHT, (10, cap_h - 1), (width + 2, cap_h - 1), 2)
    return surf


# ─── sky gradient ─────────────────────────────────────────────────────────────

def _make_sky_gradient(width: int, height: int) -> pygame.Surface:
    """Pre-bake a vertical sky gradient to avoid per-pixel work each frame."""
    surf = pygame.Surface((width, height))
    for y in range(height):
        t = y / height
        colour = _blend(S.SKY_TOP, S.SKY_BOTTOM, t)
        pygame.draw.line(surf, colour, (0, y), (width, y))
    return surf


# ─── mountain silhouettes ─────────────────────────────────────────────────────

def _make_mountain_layer(width: int, height: int, colour: tuple,
                          peaks: int = 6, seed: int = 0) -> pygame.Surface:
    """Generate a mountain-ridge silhouette for parallax scrolling."""
    import random
    rng = random.Random(seed)

    surf = pygame.Surface((width * 2, height), pygame.SRCALPHA)
    step = width * 2 // peaks
    pts = [(0, height)]
    for i in range(peaks + 1):
        x = i * step
        y = rng.randint(int(height * 0.15), int(height * 0.70))
        pts.append((x, y))
        if i < peaks:
            mx = x + step // 2
            pts.append((mx, rng.randint(int(height * 0.40), height - 20)))
    pts.append((width * 2, height))
    pygame.draw.polygon(surf, colour, pts)
    return surf


# ─── ground tile ─────────────────────────────────────────────────────────────

def _make_ground_tile(width: int, height: int) -> pygame.Surface:
    """Ground strip with a grass top and a dirt body."""
    surf = pygame.Surface((width, height))
    surf.fill(S.GROUND_DARK)
    pygame.draw.rect(surf, S.GROUND_LIGHT, (0, 2, width, height - 2))
    pygame.draw.rect(surf, S.GRASS_COLOR,  (0, 0, width, 6))
    # Texture lines
    for x in range(0, width, 18):
        pygame.draw.line(surf, S.GROUND_DARK, (x, 6), (x, height), 1)
    return surf


# ─── fonts ───────────────────────────────────────────────────────────────────

def _load_fonts() -> dict[str, pygame.font.Font]:
    """Load system fonts, falling back to the default pygame font."""
    preferred = ["Arial", "Helvetica", "FreeSansBold", "DejaVuSans"]

    def pick(size: int) -> pygame.font.Font:
        for name in preferred:
            try:
                f = pygame.font.SysFont(name, size, bold=True)
                if f:
                    return f
            except Exception:
                pass
        return pygame.font.Font(None, size)

    return {
        "huge":   pick(S.FONT_HUGE),
        "large":  pick(S.FONT_LARGE),
        "medium": pick(S.FONT_MEDIUM),
        "small":  pick(S.FONT_SMALL),
        "tiny":   pick(S.FONT_TINY),
    }


# ─── sound generation (numpy optional) ───────────────────────────────────────

def _make_sounds() -> dict[str, Optional[pygame.mixer.Sound]]:
    """
    Generate simple synthesised sound effects.
    Returns an empty dict if numpy or the mixer is unavailable.
    """
    sounds: dict[str, Optional[pygame.mixer.Sound]] = {}
    try:
        import numpy as np

        sample_rate = 44100

        def _sine_burst(freq: float, dur: float, vol: float = 0.4,
                        fade: bool = True) -> pygame.mixer.Sound:
            frames = int(sample_rate * dur)
            t = np.linspace(0, dur, frames, endpoint=False)
            wave = np.sin(2 * np.pi * freq * t)
            if fade:
                envelope = np.linspace(1.0, 0.0, frames) ** 0.5
                wave *= envelope
            wave = (wave * vol * 32767).astype(np.int16)
            stereo = np.column_stack([wave, wave])
            return pygame.sndarray.make_sound(stereo)

        def _noise_burst(dur: float, vol: float = 0.3) -> pygame.mixer.Sound:
            frames = int(sample_rate * dur)
            noise = np.random.uniform(-1, 1, frames)
            envelope = np.exp(-np.linspace(0, 6, frames))
            noise = (noise * envelope * vol * 32767).astype(np.int16)
            stereo = np.column_stack([noise, noise])
            return pygame.sndarray.make_sound(stereo)

        sounds["flap"]  = _sine_burst(520, 0.08, vol=0.25)
        sounds["score"] = _sine_burst(880, 0.12, vol=0.30)
        sounds["hit"]   = _noise_burst(0.18, vol=0.50)
        sounds["die"]   = _sine_burst(220, 0.35, vol=0.35)

    except Exception:
        # numpy absent or mixer not initialised – silently degrade.
        pass

    return sounds


# ─── AssetManager ────────────────────────────────────────────────────────────

class AssetManager:
    """
    Singleton-style container for all game assets.

    Instantiate once after ``pygame.init()``; pass the instance to every
    object that needs sprites, fonts, or sounds.
    """

    def __init__(self) -> None:
        self._load()

    # ── public accessors ──────────────────────────────────────────────────────

    def play(self, name: str) -> None:
        """Play a sound effect by name; silently ignores missing sounds."""
        snd = self.sounds.get(name)
        if snd:
            snd.play()

    # ── internal ──────────────────────────────────────────────────────────────

    def _load(self) -> None:
        # Bird animation frames
        self.bird_frames: list[pygame.Surface] = [
            _draw_bird_frame(i) for i in range(S.BIRD_FRAME_COUNT)
        ]

        # Pipe surfaces (generated on demand by PipePair; stored here as cache)
        self.pipe_cap_surf: pygame.Surface = _make_pipe_cap(S.PIPE_WIDTH)

        # Background layers
        self.sky: pygame.Surface = _make_sky_gradient(S.SCREEN_WIDTH, S.SCREEN_HEIGHT)

        mtn_h = S.SCREEN_HEIGHT // 3
        self.mountain_far  = _make_mountain_layer(S.SCREEN_WIDTH, mtn_h,
                                                   S.MOUNTAIN_FAR,  peaks=5, seed=1)
        self.mountain_near = _make_mountain_layer(S.SCREEN_WIDTH, mtn_h // 2 + 20,
                                                   S.MOUNTAIN_NEAR, peaks=7, seed=2)
        self.ground_tile: pygame.Surface = _make_ground_tile(S.SCREEN_WIDTH * 2,
                                                              S.GROUND_HEIGHT)

        # Fonts
        self.fonts: dict[str, pygame.font.Font] = _load_fonts()

        # Sounds
        self.sounds: dict = _make_sounds()

    def make_pipe_body(self, height: int) -> pygame.Surface:
        """Return a freshly rendered pipe body surface of *height* pixels."""
        return _make_pipe_body(S.PIPE_WIDTH, height)
